"""
Legal Judgment Similarity Detector - FIXED VERSION
Architecture: Pre-trained BERT + Custom Trainable Layers
Strategy: Pre-trained as fallback, custom layers learn from YOUR data
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os
from pathlib import Path
import pdfplumber
import re
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# ============================================
# PART 1: CUSTOM MODEL ARCHITECTURE - FIXED
# ============================================

class LegalBERTWithCustomLayers(nn.Module):
    """
    Pre-trained BERT (frozen) + Custom trainable layers for legal domain
    
    FIXED: Separate methods for training and inference to handle gradients properly
    """
    
    def __init__(self, base_model_name='sentence-transformers/all-MiniLM-L6-v2'):
        super(LegalBERTWithCustomLayers, self).__init__()
        
        print("Loading pre-trained BERT model...")
        self.base_model = SentenceTransformer(base_model_name)
        
        # FREEZE the pre-trained model
        for param in self.base_model.parameters():
            param.requires_grad = False
        print("✓ Pre-trained model loaded and FROZEN (fallback ready)")
        
        # CUSTOM LAYERS (trainable)
        self.custom_layers = nn.Sequential(
            nn.Linear(384, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        print("✓ Custom layers initialized (ready to learn from your data)")
        
    def encode(self, texts, convert_to_tensor=False):
        """
        INFERENCE MODE: For evaluation/production use
        """
        self.eval()
        with torch.no_grad():
            base_embeddings = self.base_model.encode(
                texts, 
                convert_to_tensor=True,
                show_progress_bar=False
            )
            enhanced_embeddings = self.custom_layers(base_embeddings)
        
        if convert_to_tensor:
            return enhanced_embeddings
        else:
            return enhanced_embeddings.cpu().numpy()
    
    def forward(self, texts):
        """
        TRAINING MODE: For gradient computation
        FIX: Don't use torch.no_grad() - we need gradients!
        """
        # Get base embeddings WITHOUT no_grad context
        base_embeddings = self.base_model.encode(
            texts, 
            convert_to_tensor=True,
            show_progress_bar=False
        )
        
        # IMPORTANT: Clone and detach to prevent gradients flowing into frozen model
        # but allow gradients for custom layers
        base_embeddings = base_embeddings.clone().detach().requires_grad_(True)
        
        # Pass through custom layers (gradients flow here)
        enhanced_embeddings = self.custom_layers(base_embeddings)
        
        return enhanced_embeddings


# ============================================
# PART 2: DATA PREPARATION
# ============================================

class JudgmentPairDataset(Dataset):
    def __init__(self, judgment_texts, labels):
        self.texts = judgment_texts
        self.labels = labels
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def preprocess_text(text):
    """Clean legal text"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.,;:()\[\]/@-]', '', text)
    return text.strip()


def create_training_pairs(pdf_folder, num_pairs=200):
    """
    Create training pairs from your PDFs
    """
    print("\n📂 Reading PDFs and creating training pairs...")
    
    pdf_files = list(Path(pdf_folder).glob('*.pdf')) + list(Path(pdf_folder).glob('*.PDF'))
    
    if len(pdf_files) < 2:
        raise ValueError("Need at least 2 PDFs for training!")
    
    # Extract all judgments
    judgments = []
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        text = extract_text_from_pdf(str(pdf_path))
        if text and len(text) > 500:
            clean_text = preprocess_text(text)
            judgments.append({
                'text': clean_text,
                'filename': pdf_path.name,
                'sections': extract_sections(clean_text)
            })
    
    print(f"✓ Processed {len(judgments)} valid judgments")
    
    # Create training pairs
    pairs = []
    labels = []
    
    # Similar pairs
    print("Creating similar pairs...")
    for i in range(min(num_pairs // 2, len(judgments) * 2)):
        idx1, idx2 = np.random.choice(len(judgments), 2, replace=False)
        
        text1 = judgments[idx1]['text'][:2000]
        text2 = judgments[idx2]['text'][:2000]
        
        pairs.append((text1, text2))
        
        shared = len(judgments[idx1]['sections'] & judgments[idx2]['sections'])
        labels.append(1.0 if shared > 0 else 0.0)
    
    # Dissimilar pairs
    print("Creating dissimilar pairs...")
    for i in range(min(num_pairs // 2, len(judgments) * 2)):
        idx = np.random.choice(len(judgments))
        text = judgments[idx]['text']
        
        mid = len(text) // 2
        text1 = text[:1000]
        text2 = text[mid:mid+1000]
        
        pairs.append((text1, text2))
        labels.append(0.5)
    
    print(f"✓ Created {len(pairs)} training pairs")
    return pairs, labels, judgments


def extract_sections(text):
    """Extract legal sections mentioned in judgment"""
    sections = set()
    patterns = [
        r'Section\s+\d+[A-Z]?',
        r'Article\s+\d+[A-Z]?',
        r'Rule\s+\d+',
        r'Order\s+\d+'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text[:3000])
        sections.update(matches)
    return sections


# ============================================
# PART 3: TRAINING SYSTEM - FIXED
# ============================================

class ContrastiveLoss(nn.Module):
    """Loss function for similarity learning"""
    
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
    
    def forward(self, output1, output2, label):
        euclidean_distance = nn.functional.pairwise_distance(output1, output2)
        
        loss = torch.mean(
            label * torch.pow(euclidean_distance, 2) +
            (1 - label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2)
        )
        return loss


def train_custom_layers(model, pairs, labels, epochs=20, batch_size=4, learning_rate=0.001):
    """
    Train the custom layers - FIXED VERSION
    """
    print("\n🔥 Starting training of custom layers...")
    print(f"Training pairs: {len(pairs)}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    model = model.to(device)
    criterion = ContrastiveLoss(margin=1.0)
    
    # Only optimize custom layers
    optimizer = optim.Adam(model.custom_layers.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3)
    
    best_loss = float('inf')
    
    for epoch in range(epochs):
        model.train()  # Set to training mode
        epoch_loss = 0
        num_batches = 0
        
        # Mini-batch training
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i+batch_size]
            batch_labels = torch.FloatTensor(labels[i:i+batch_size]).to(device)
            
            texts1 = [pair[0] for pair in batch_pairs]
            texts2 = [pair[1] for pair in batch_pairs]
            
            optimizer.zero_grad()
            
            # FIXED: Use forward() which allows gradients
            embeddings1 = model(texts1)
            embeddings2 = model(texts2)
            
            loss = criterion(embeddings1, embeddings2, batch_labels)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            num_batches += 1
        
        avg_loss = epoch_loss / num_batches
        scheduler.step(avg_loss)
        
        print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
        
        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), 'legal_bert_best.pth')
            print(f"  ✓ Saved best model (loss: {best_loss:.4f})")
    
    print(f"\n✅ Training complete! Best loss: {best_loss:.4f}")
    return model


# ============================================
# PART 4: MAIN EXECUTION
# ============================================

def main():
    print("="*60)
    print("LEGAL JUDGMENT SIMILARITY DETECTOR")
    print("Architecture: Pre-trained BERT + Custom Layers")
    print("="*60)
    
    # Configuration
    PDF_FOLDER = "./judgments"
    NUM_TRAINING_PAIRS = 200
    EPOCHS = 20
    BATCH_SIZE = 4
    
    # Step 1: Initialize model
    print("\n[1/4] Initializing model...")
    model = LegalBERTWithCustomLayers()
    
    # Step 2: Create training data
    print("\n[2/4] Creating training data from your PDFs...")
    pairs, labels, judgments = create_training_pairs(PDF_FOLDER, NUM_TRAINING_PAIRS)
    
    # Step 3: Train custom layers
    print("\n[3/4] Training custom layers...")
    trained_model = train_custom_layers(
        model, 
        pairs, 
        labels, 
        epochs=EPOCHS,
        batch_size=BATCH_SIZE
    )
    
    # Step 4: Save everything
    print("\n[4/4] Saving model and data...")
    
    torch.save(trained_model.state_dict(), 'legal_bert_custom.pth')
    print("✓ Model saved: legal_bert_custom.pth")
    
    with open('judgments_data.pkl', 'wb') as f:
        pickle.dump(judgments, f)
    print("✓ Judgment data saved: judgments_data.pkl")
    
    # Test the model
    print("\n" + "="*60)
    print("TESTING THE MODEL")
    print("="*60)
    
    test_query = "Section 465 unsoundness of mind during trial"
    print(f"\nTest Query: '{test_query}'")
    
    trained_model.eval()
    with torch.no_grad():
        query_embedding = trained_model.encode([test_query])[0]
    
    print(f"✓ Generated embedding: {query_embedding.shape}")
    print(f"  Sample values: [{query_embedding[:5]}...]")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print(f"\nYour model is ready with:")
    print(f"  • Pre-trained BERT (frozen) - handles general language")
    print(f"  • Custom layers (trained) - learned from your {len(judgments)} judgments")
    print(f"  • As you add more PDFs, retrain to improve accuracy!")
    print("\nNext: Run 'streamlit run app.py' to use the model")
    

if __name__ == "__main__":
    main()