# # # """
# # # Enhanced Legal Judgment Similarity Detector
# # # FIXED VERSION - No BatchNorm issues
# # # """

# # # import streamlit as st
# # # import torch
# # # import torch.nn as nn
# # # from sentence_transformers import SentenceTransformer
# # # import numpy as np
# # # import faiss
# # # import pickle
# # # import pdfplumber
# # # import re
# # # from pathlib import Path
# # # import os

# # # # FIXED MODEL CLASS - No BatchNorm
# # # class LegalBERTWithCustomLayers(nn.Module):
# # #     def __init__(self, base_model_name='sentence-transformers/all-MiniLM-L6-v2'):
# # #         super(LegalBERTWithCustomLayers, self).__init__()
# # #         self.base_model = SentenceTransformer(base_model_name)
# # #         for param in self.base_model.parameters():
# # #             param.requires_grad = False
        
# # #         # FIXED: Removed BatchNorm - it causes issues with single samples
# # #         self.custom_layers = nn.Sequential(
# # #             nn.Linear(384, 512),
# # #             nn.ReLU(),
# # #             nn.Dropout(0.3),
# # #             nn.Linear(512, 256),
# # #             nn.ReLU(),
# # #             nn.Dropout(0.2),
# # #             nn.Linear(256, 128),
# # #             nn.ReLU()
# # #         )
        
# # #     def encode(self, texts, convert_to_tensor=False):
# # #         # IMPORTANT: Set to eval mode
# # #         self.eval()
# # #         with torch.no_grad():
# # #             base_embeddings = self.base_model.encode(
# # #                 texts, convert_to_tensor=True, show_progress_bar=False
# # #             )
# # #             enhanced_embeddings = self.custom_layers(base_embeddings)
        
# # #         if convert_to_tensor:
# # #             return enhanced_embeddings
# # #         else:
# # #             return enhanced_embeddings.cpu().numpy()


# # # @st.cache_resource
# # # def load_model(model_path='legal_bert_custom.pth'):
# # #     model = LegalBERTWithCustomLayers()
# # #     model.eval()  # Set to evaluation mode
    
# # #     if os.path.exists(model_path):
# # #         try:
# # #             model.load_state_dict(torch.load(model_path, map_location='cpu'))
# # #             model.eval()
# # #             st.success("✅ Custom trained model loaded!")
# # #             return model, True
# # #         except Exception as e:
# # #             st.warning(f"⚠️ Could not load custom model: {e}")
# # #             st.info("Using pre-trained model only (fallback mode)")
# # #             return model, False
# # #     else:
# # #         st.info("ℹ️ No custom model found. Using pre-trained BERT only.")
# # #         return model, False


# # # def extract_text_from_pdf(pdf_path):
# # #     text = ""
# # #     try:
# # #         with pdfplumber.open(pdf_path) as pdf:
# # #             for page in pdf.pages:
# # #                 page_text = page.extract_text()
# # #                 if page_text:
# # #                     text += page_text + "\n"
# # #     except Exception as e:
# # #         return ""
# # #     return text


# # # def preprocess_text(text):
# # #     text = re.sub(r'\s+', ' ', text)
# # #     text = re.sub(r'[^\w\s\.,;:()\[\]/@-]', '', text)
# # #     return text.strip()


# # # def extract_metadata(text, filename):
# # #     metadata = {
# # #         'filename': filename,
# # #         'case_name': '',
# # #         'court': '',
# # #         'date': '',
# # #         'citations': [],
# # #         'sections': [],
# # #         'articles': [],
# # #         'key_holdings': []
# # #     }
    
# # #     lines = text.split('\n')
    
# # #     # Case name
# # #     for line in lines[:15]:
# # #         if ' vs ' in line.lower() or ' v. ' in line or ' V. ' in line:
# # #             metadata['case_name'] = line.strip()[:200]
# # #             break
    
# # #     # Court
# # #     court_keywords = ['Supreme Court', 'High Court', 'District Court', 'Sessions Court']
# # #     for keyword in court_keywords:
# # #         if keyword.lower() in text[:2000].lower():
# # #             metadata['court'] = keyword
# # #             break
    
# # #     # Date
# # #     date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
# # #     dates = re.findall(date_pattern, text[:1500])
# # #     if dates:
# # #         metadata['date'] = dates[0]
    
# # #     # Citations
# # #     citation_patterns = [
# # #         r'\d{4}\s+AIR\s+\w+\s+\d+',
# # #         r'\d{4}\s+SCC\s+\(\d+\)\s+\d+',
# # #         r'AIR\s+\d{4}\s+\w+\s+\d+'
# # #     ]
# # #     for pattern in citation_patterns:
# # #         citations = re.findall(pattern, text[:3000], re.IGNORECASE)
# # #         metadata['citations'].extend(citations[:5])
    
# # #     # Sections
# # #     section_pattern = r'Section\s+\d+[A-Z]?'
# # #     sections = re.findall(section_pattern, text[:5000], re.IGNORECASE)
# # #     metadata['sections'] = list(set(sections))[:10]
    
# # #     # Articles
# # #     article_pattern = r'Article\s+\d+[A-Z]?'
# # #     articles = re.findall(article_pattern, text[:5000], re.IGNORECASE)
# # #     metadata['articles'] = list(set(articles))[:10]
    
# # #     return metadata


# # # def build_index(model, pdf_folder):
# # #     documents = []
# # #     embeddings_list = []
    
# # #     pdf_files = list(Path(pdf_folder).glob('*.pdf')) + list(Path(pdf_folder).glob('*.PDF'))
    
# # #     if not pdf_files:
# # #         st.error("No PDF files found!")
# # #         return None, None
    
# # #     progress_bar = st.progress(0)
# # #     status_text = st.empty()
    
# # #     for idx, pdf_path in enumerate(pdf_files):
# # #         status_text.text(f"Processing: {pdf_path.name} ({idx+1}/{len(pdf_files)})")
        
# # #         text = extract_text_from_pdf(str(pdf_path))
# # #         if not text or len(text) < 100:
# # #             st.warning(f"Skipping {pdf_path.name} - insufficient text")
# # #             continue
        
# # #         clean_text = preprocess_text(text)
# # #         metadata = extract_metadata(text, pdf_path.name)
        
# # #         # Create embedding - FIXED: model is in eval mode
# # #         embedding = model.encode([clean_text[:5000]])[0]
        
# # #         documents.append({
# # #             'text': clean_text[:2000],
# # #             'full_text': clean_text,
# # #             'filename': pdf_path.name,
# # #             'metadata': metadata
# # #         })
# # #         embeddings_list.append(embedding)
        
# # #         progress_bar.progress((idx + 1) / len(pdf_files))
    
# # #     if not documents:
# # #         st.error("No valid documents found!")
# # #         status_text.empty()
# # #         progress_bar.empty()
# # #         return None, None
    
# # #     status_text.text("Creating FAISS index...")
    
# # #     embeddings_array = np.array(embeddings_list).astype('float32')
# # #     dimension = embeddings_array.shape[1]
    
# # #     index = faiss.IndexFlatL2(dimension)
# # #     index.add(embeddings_array)
    
# # #     status_text.text(f"✓ Indexed {len(documents)} judgments!")
# # #     progress_bar.empty()
    
# # #     return index, documents


# # # def search_judgments(query_text, model, index, documents, top_k=5):
# # #     query_embedding = model.encode([query_text])[0].astype('float32').reshape(1, -1)
# # #     distances, indices = index.search(query_embedding, top_k)
    
# # #     results = []
# # #     for idx, dist in zip(indices[0], distances[0]):
# # #         if idx < len(documents):
# # #             result = documents[idx].copy()
# # #             result['similarity_score'] = float(1 / (1 + dist))
# # #             results.append(result)
    
# # #     return results


# # # def save_index(index, documents, save_path='legal_index'):
# # #     faiss.write_index(index, f"{save_path}.index")
# # #     with open(f"{save_path}_docs.pkl", 'wb') as f:
# # #         pickle.dump(documents, f)


# # # def load_index(save_path='legal_index'):
# # #     try:
# # #         index = faiss.read_index(f"{save_path}.index")
# # #         with open(f"{save_path}_docs.pkl", 'rb') as f:
# # #             documents = pickle.load(f)
# # #         return index, documents
# # #     except:
# # #         return None, None


# # # def main():
# # #     st.set_page_config(
# # #         page_title="Legal Judgment Similarity Detector",
# # #         page_icon="⚖️",
# # #         layout="wide"
# # #     )
    
# # #     st.title("⚖️ Legal Judgment Similarity Detector")
# # #     st.markdown("**AI-Powered Semantic Search for Legal Research**")
    
# # #     # Sidebar
# # #     with st.sidebar:
# # #         st.header("⚙️ Configuration")
        
# # #         st.subheader("Model")
# # #         model, is_trained = load_model()
        
# # #         if is_trained:
# # #             st.success("✅ Custom Model Loaded")
# # #         else:
# # #             st.info("📊 Pre-trained Model (Fallback)")
        
# # #         st.divider()
        
# # #         st.subheader("📁 Data Management")
# # #         pdf_folder = st.text_input("PDF Folder Path", value="./judgments")
        
# # #         if st.button("🔄 Build Index", type="primary"):
# # #             if not os.path.exists(pdf_folder):
# # #                 st.error(f"Folder not found: {pdf_folder}")
# # #             else:
# # #                 with st.spinner("Building index..."):
# # #                     index, documents = build_index(model, pdf_folder)
# # #                     if index and documents:
# # #                         save_index(index, documents)
# # #                         st.session_state['index'] = index
# # #                         st.session_state['documents'] = documents
# # #                         st.success(f"✓ {len(documents)} judgments indexed!")
        
# # #         if st.button("📂 Load Saved Index"):
# # #             index, documents = load_index()
# # #             if index and documents:
# # #                 st.session_state['index'] = index
# # #                 st.session_state['documents'] = documents
# # #                 st.success(f"✓ {len(documents)} judgments loaded!")
        
# # #         st.divider()
# # #         st.markdown("### About")
# # #         st.info("Find similar legal judgments using AI-powered semantic search")
    
# # #     # Main interface
# # #     if 'index' in st.session_state and 'documents' in st.session_state:
        
# # #         st.success(f"✓ {len(st.session_state['documents'])} judgments ready for search")
        
# # #         st.markdown("### 🔍 Search for Similar Judgments")
        
# # #         # Query input
# # #         col1, col2 = st.columns([3, 1])
        
# # #         with col1:
# # #             query_side = st.selectbox(
# # #                 "Your Side:",
# # #                 ["Defense", "Prosecution", "Petitioner", "Respondent", "Neutral Research"]
# # #             )
        
# # #         case_description = st.text_area(
# # #             "Enter case details or legal question:",
# # #             height=150,
# # #             placeholder="Example: Case involving Section 465 CrPC regarding postponement of trial due to mental incapacity of accused..."
# # #         )
        
# # #         top_k = st.slider("Number of results:", 1, 10, 5)
        
# # #         if st.button("🔍 Find Similar Judgments", type="primary"):
# # #             if not case_description or len(case_description) < 30:
# # #                 st.warning("⚠️ Please provide more detailed information")
# # #             else:
# # #                 with st.spinner("Searching..."):
# # #                     results = search_judgments(
# # #                         case_description,
# # #                         model,
# # #                         st.session_state['index'],
# # #                         st.session_state['documents'],
# # #                         top_k
# # #                     )
                
# # #                 st.markdown("---")
# # #                 st.subheader(f"📊 Results for {query_side}")
                
# # #                 for i, result in enumerate(results, 1):
# # #                     metadata = result['metadata']
# # #                     similarity = result['similarity_score']
                    
# # #                     # Relevance indicator
# # #                     if similarity > 0.85:
# # #                         color = "🟢"
# # #                         relevance = "Highly Relevant"
# # #                     elif similarity > 0.70:
# # #                         color = "🟡"
# # #                         relevance = "Relevant"
# # #                     else:
# # #                         color = "🟠"
# # #                         relevance = "Somewhat Relevant"
                    
# # #                     with st.expander(
# # #                         f"{color} Result #{i}: {metadata['filename']} ({similarity:.0%} - {relevance})",
# # #                         expanded=(i <= 2)
# # #                     ):
# # #                         col1, col2 = st.columns([3, 1])
                        
# # #                         with col1:
# # #                             if metadata['case_name']:
# # #                                 st.markdown(f"**📋 Case:** {metadata['case_name']}")
# # #                             if metadata['court']:
# # #                                 st.markdown(f"**🏛️ Court:** {metadata['court']}")
# # #                             if metadata['date']:
# # #                                 st.markdown(f"**📅 Date:** {metadata['date']}")
# # #                             if metadata['citations']:
# # #                                 st.markdown(f"**📖 Citations:** {', '.join(metadata['citations'][:3])}")
                        
# # #                         with col2:
# # #                             st.metric("Similarity", f"{similarity:.0%}")
                        
# # #                         if metadata['sections']:
# # #                             st.markdown("**⚖️ Sections:**")
# # #                             st.write(", ".join(metadata['sections'][:5]))
                        
# # #                         if metadata['articles']:
# # #                             st.markdown("**📄 Articles:**")
# # #                             st.write(", ".join(metadata['articles'][:5]))
                        
# # #                         st.markdown("**📄 Excerpt:**")
# # #                         st.text_area("", value=result['text'][:1200] + "...", height=200, key=f"text_{i}")
                        
# # #                         if st.button(f"View Full Text", key=f"full_{i}"):
# # #                             st.text_area("Complete Text:", value=result['full_text'][:5000], height=400, key=f"fulltext_{i}")
    
# # #     else:
# # #         st.info("👈 Build or load an index from the sidebar to start searching")
        
# # #         st.markdown("### 🚀 Quick Start")
# # #         st.markdown("""
# # #         1. Place your judgment PDFs in a folder
# # #         2. Enter folder path in sidebar
# # #         3. Click "Build Index"
# # #         4. Start searching!
# # #         """)


# # # if __name__ == "__main__":
# # #     main()


# # """
# # Enhanced Legal Judgment Similarity Detector with Gemini API
# # Query Enhancement: Single sentences expanded into detailed legal queries
# # """

# # import streamlit as st
# # import torch
# # import torch.nn as nn
# # from sentence_transformers import SentenceTransformer
# # import numpy as np
# # import faiss
# # import pickle
# # import pdfplumber
# # import re
# # from pathlib import Path
# # import os
# # import google.generativeai as genai

# # # FIXED MODEL CLASS - No BatchNorm
# # class LegalBERTWithCustomLayers(nn.Module):
# #     def __init__(self, base_model_name='sentence-transformers/all-MiniLM-L6-v2'):
# #         super(LegalBERTWithCustomLayers, self).__init__()
# #         self.base_model = SentenceTransformer(base_model_name)
# #         for param in self.base_model.parameters():
# #             param.requires_grad = False
        
# #         # FIXED: Removed BatchNorm - it causes issues with single samples
# #         self.custom_layers = nn.Sequential(
# #             nn.Linear(384, 512),
# #             nn.ReLU(),
# #             nn.Dropout(0.3),
# #             nn.Linear(512, 256),
# #             nn.ReLU(),
# #             nn.Dropout(0.2),
# #             nn.Linear(256, 128),
# #             nn.ReLU()
# #         )
        
# #     def encode(self, texts, convert_to_tensor=False):
# #         # IMPORTANT: Set to eval mode
# #         self.eval()
# #         with torch.no_grad():
# #             base_embeddings = self.base_model.encode(
# #                 texts, convert_to_tensor=True, show_progress_bar=False
# #             )
# #             enhanced_embeddings = self.custom_layers(base_embeddings)
        
# #         if convert_to_tensor:
# #             return enhanced_embeddings
# #         else:
# #             return enhanced_embeddings.cpu().numpy()


# # @st.cache_resource
# # def load_model(model_path='legal_bert_custom.pth'):
# #     model = LegalBERTWithCustomLayers()
# #     model.eval()  # Set to evaluation mode
    
# #     if os.path.exists(model_path):
# #         try:
# #             model.load_state_dict(torch.load(model_path, map_location='cpu'))
# #             model.eval()
# #             st.success("✅ Custom trained model loaded!")
# #             return model, True
# #         except Exception as e:
# #             st.warning(f"⚠️ Could not load custom model: {e}")
# #             st.info("Using pre-trained model only (fallback mode)")
# #             return model, False
# #     else:
# #         st.info("ℹ️ No custom model found. Using pre-trained BERT only.")
# #         return model, False


# # def configure_gemini(api_key):
# #     """Configure Gemini API"""
# #     try:
# #         genai.configure(api_key=api_key)
# #         return True
# #     except Exception as e:
# #         st.error(f"Failed to configure Gemini API: {e}")
# #         return False


# # def enhance_query_with_gemini(short_query, api_key):
# #     """
# #     Use Gemini to expand a short query into a detailed legal description
# #     """
# #     try:
# #         genai.configure(api_key=api_key)
# #         model = genai.GenerativeModel('gemini-pro')
        
# #         prompt = f"""You are a legal research assistant. A user has provided a brief query for finding similar legal judgments.

# # User's Query: "{short_query}"

# # Your task: Expand this into a detailed legal search query that includes:
# # 1. Relevant legal sections, articles, or acts that might apply
# # 2. Key legal concepts and terminology
# # 3. Possible case contexts and scenarios
# # 4. Related legal principles

# # Provide a comprehensive 3-4 sentence legal description that will help find the most relevant judgments. Focus on Indian legal context if applicable.

# # Enhanced Query:"""
        
# #         response = model.generate_content(prompt)
# #         enhanced_query = response.text.strip()
        
# #         return enhanced_query, True
    
# #     except Exception as e:
# #         st.error(f"Gemini API Error: {e}")
# #         return short_query, False


# # def extract_text_from_pdf(pdf_path):
# #     text = ""
# #     try:
# #         with pdfplumber.open(pdf_path) as pdf:
# #             for page in pdf.pages:
# #                 page_text = page.extract_text()
# #                 if page_text:
# #                     text += page_text + "\n"
# #     except Exception as e:
# #         return ""
# #     return text


# # def preprocess_text(text):
# #     text = re.sub(r'\s+', ' ', text)
# #     text = re.sub(r'[^\w\s\.,;:()\[\]/@-]', '', text)
# #     return text.strip()


# # def extract_metadata(text, filename):
# #     metadata = {
# #         'filename': filename,
# #         'case_name': '',
# #         'court': '',
# #         'date': '',
# #         'citations': [],
# #         'sections': [],
# #         'articles': [],
# #         'key_holdings': []
# #     }
    
# #     lines = text.split('\n')
    
# #     # Case name
# #     for line in lines[:15]:
# #         if ' vs ' in line.lower() or ' v. ' in line or ' V. ' in line:
# #             metadata['case_name'] = line.strip()[:200]
# #             break
    
# #     # Court
# #     court_keywords = ['Supreme Court', 'High Court', 'District Court', 'Sessions Court']
# #     for keyword in court_keywords:
# #         if keyword.lower() in text[:2000].lower():
# #             metadata['court'] = keyword
# #             break
    
# #     # Date
# #     date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
# #     dates = re.findall(date_pattern, text[:1500])
# #     if dates:
# #         metadata['date'] = dates[0]
    
# #     # Citations
# #     citation_patterns = [
# #         r'\d{4}\s+AIR\s+\w+\s+\d+',
# #         r'\d{4}\s+SCC\s+\(\d+\)\s+\d+',
# #         r'AIR\s+\d{4}\s+\w+\s+\d+'
# #     ]
# #     for pattern in citation_patterns:
# #         citations = re.findall(pattern, text[:3000], re.IGNORECASE)
# #         metadata['citations'].extend(citations[:5])
    
# #     # Sections
# #     section_pattern = r'Section\s+\d+[A-Z]?'
# #     sections = re.findall(section_pattern, text[:5000], re.IGNORECASE)
# #     metadata['sections'] = list(set(sections))[:10]
    
# #     # Articles
# #     article_pattern = r'Article\s+\d+[A-Z]?'
# #     articles = re.findall(article_pattern, text[:5000], re.IGNORECASE)
# #     metadata['articles'] = list(set(articles))[:10]
    
# #     return metadata


# # def build_index(model, pdf_folder):
# #     documents = []
# #     embeddings_list = []
    
# #     pdf_files = list(Path(pdf_folder).glob('*.pdf')) + list(Path(pdf_folder).glob('*.PDF'))
    
# #     if not pdf_files:
# #         st.error("No PDF files found!")
# #         return None, None
    
# #     progress_bar = st.progress(0)
# #     status_text = st.empty()
    
# #     for idx, pdf_path in enumerate(pdf_files):
# #         status_text.text(f"Processing: {pdf_path.name} ({idx+1}/{len(pdf_files)})")
        
# #         text = extract_text_from_pdf(str(pdf_path))
# #         if not text or len(text) < 100:
# #             st.warning(f"Skipping {pdf_path.name} - insufficient text")
# #             continue
        
# #         clean_text = preprocess_text(text)
# #         metadata = extract_metadata(text, pdf_path.name)
        
# #         # Create embedding - FIXED: model is in eval mode
# #         embedding = model.encode([clean_text[:5000]])[0]
        
# #         documents.append({
# #             'text': clean_text[:2000],
# #             'full_text': clean_text,
# #             'filename': pdf_path.name,
# #             'metadata': metadata
# #         })
# #         embeddings_list.append(embedding)
        
# #         progress_bar.progress((idx + 1) / len(pdf_files))
    
# #     if not documents:
# #         st.error("No valid documents found!")
# #         status_text.empty()
# #         progress_bar.empty()
# #         return None, None
    
# #     status_text.text("Creating FAISS index...")
    
# #     embeddings_array = np.array(embeddings_list).astype('float32')
# #     dimension = embeddings_array.shape[1]
    
# #     index = faiss.IndexFlatL2(dimension)
# #     index.add(embeddings_array)
    
# #     status_text.text(f"✓ Indexed {len(documents)} judgments!")
# #     progress_bar.empty()
    
# #     return index, documents


# # def search_judgments(query_text, model, index, documents, top_k=5):
# #     query_embedding = model.encode([query_text])[0].astype('float32').reshape(1, -1)
# #     distances, indices = index.search(query_embedding, top_k)
    
# #     results = []
# #     for idx, dist in zip(indices[0], distances[0]):
# #         if idx < len(documents):
# #             result = documents[idx].copy()
# #             result['similarity_score'] = float(1 / (1 + dist))
# #             results.append(result)
    
# #     return results


# # def save_index(index, documents, save_path='legal_index'):
# #     faiss.write_index(index, f"{save_path}.index")
# #     with open(f"{save_path}_docs.pkl", 'wb') as f:
# #         pickle.dump(documents, f)


# # def load_index(save_path='legal_index'):
# #     try:
# #         index = faiss.read_index(f"{save_path}.index")
# #         with open(f"{save_path}_docs.pkl", 'rb') as f:
# #             documents = pickle.load(f)
# #         return index, documents
# #     except:
# #         return None, None


# # def main():
# #     st.set_page_config(
# #         page_title="Legal Judgment Similarity Detector",
# #         page_icon="⚖️",
# #         layout="wide"
# #     )
    
# #     st.title("⚖️ Legal Judgment Similarity Detector")
# #     st.markdown("**AI-Powered Semantic Search with Gemini Query Enhancement**")
    
# #     # Sidebar
# #     with st.sidebar:
# #         st.header("⚙️ Configuration")
        
# #         # Gemini API Configuration
# #         st.subheader("🤖 Gemini API")
# #         gemini_api_key = st.text_input(
# #             "Gemini API Key", 
# #             type="password",
# #             help="Get your API key from https://makersuite.google.com/app/apikey"
# #         )
        
# #         if gemini_api_key:
# #             if configure_gemini(gemini_api_key):
# #                 st.success("✅ Gemini API Connected")
# #                 st.session_state['gemini_api_key'] = gemini_api_key
# #             else:
# #                 st.error("❌ Invalid API Key")
        
# #         use_gemini = st.checkbox(
# #             "Enable Query Enhancement", 
# #             value=True,
# #             help="Use Gemini to expand short queries into detailed legal descriptions"
# #         )
# #         st.session_state['use_gemini'] = use_gemini
        
# #         st.divider()
        
# #         st.subheader("Model")
# #         model, is_trained = load_model()
        
# #         if is_trained:
# #             st.success("✅ Custom Model Loaded")
# #         else:
# #             st.info("📊 Pre-trained Model (Fallback)")
        
# #         st.divider()
        
# #         st.subheader("📁 Data Management")
# #         pdf_folder = st.text_input("PDF Folder Path", value="./judgments")
        
# #         if st.button("🔄 Build Index", type="primary"):
# #             if not os.path.exists(pdf_folder):
# #                 st.error(f"Folder not found: {pdf_folder}")
# #             else:
# #                 with st.spinner("Building index..."):
# #                     index, documents = build_index(model, pdf_folder)
# #                     if index and documents:
# #                         save_index(index, documents)
# #                         st.session_state['index'] = index
# #                         st.session_state['documents'] = documents
# #                         st.success(f"✓ {len(documents)} judgments indexed!")
        
# #         if st.button("📂 Load Saved Index"):
# #             index, documents = load_index()
# #             if index and documents:
# #                 st.session_state['index'] = index
# #                 st.session_state['documents'] = documents
# #                 st.success(f"✓ {len(documents)} judgments loaded!")
        
# #         st.divider()
# #         st.markdown("### About")
# #         st.info("Find similar legal judgments using AI-powered semantic search with Gemini query enhancement")
    
# #     # Main interface
# #     if 'index' in st.session_state and 'documents' in st.session_state:
        
# #         st.success(f"✓ {len(st.session_state['documents'])} judgments ready for search")
        
# #         st.markdown("### 🔍 Search for Similar Judgments")
        
# #         # Query input
# #         col1, col2 = st.columns([3, 1])
        
# #         with col1:
# #             query_side = st.selectbox(
# #                 "Your Side:",
# #                 ["Defense", "Prosecution", "Petitioner", "Respondent", "Neutral Research"]
# #             )
        
# #         case_description = st.text_area(
# #             "Enter case details or legal question (even just one sentence!):",
# #             height=100,
# #             placeholder="Example: 'Trial postponement due to mental illness' or 'Section 465 CrPC mental capacity'"
# #         )
        
# #         # Show enhancement option
# #         if st.session_state.get('use_gemini') and st.session_state.get('gemini_api_key'):
# #             st.info("🤖 Query enhancement enabled - short queries will be automatically expanded")
        
# #         top_k = st.slider("Number of results:", 1, 10, 5)
        
# #         if st.button("🔎 Find Similar Judgments", type="primary"):
# #             if not case_description or len(case_description) < 5:
# #                 st.warning("⚠️ Please provide at least a brief query")
# #             else:
# #                 # Check if query is short and should be enhanced
# #                 original_query = case_description
# #                 enhanced_query = case_description
# #                 was_enhanced = False
                
# #                 if (st.session_state.get('use_gemini') and 
# #                     st.session_state.get('gemini_api_key') and 
# #                     len(case_description.split()) < 20):  # Short query
                    
# #                     with st.spinner("🤖 Enhancing query with Gemini AI..."):
# #                         enhanced_query, success = enhance_query_with_gemini(
# #                             case_description, 
# #                             st.session_state['gemini_api_key']
# #                         )
# #                         was_enhanced = success
                    
# #                     if was_enhanced:
# #                         st.success("✅ Query enhanced!")
# #                         with st.expander("📝 View Enhanced Query"):
# #                             col1, col2 = st.columns(2)
# #                             with col1:
# #                                 st.markdown("**Original Query:**")
# #                                 st.write(original_query)
# #                             with col2:
# #                                 st.markdown("**Enhanced Query:**")
# #                                 st.write(enhanced_query)
                
# #                 # Perform search with enhanced query
# #                 with st.spinner("Searching..."):
# #                     results = search_judgments(
# #                         enhanced_query,
# #                         model,
# #                         st.session_state['index'],
# #                         st.session_state['documents'],
# #                         top_k
# #                     )
                
# #                 st.markdown("---")
# #                 st.subheader(f"📊 Results for {query_side}")
                
# #                 for i, result in enumerate(results, 1):
# #                     metadata = result['metadata']
# #                     similarity = result['similarity_score']
                    
# #                     # Relevance indicator
# #                     if similarity > 0.85:
# #                         color = "🟢"
# #                         relevance = "Highly Relevant"
# #                     elif similarity > 0.70:
# #                         color = "🟡"
# #                         relevance = "Relevant"
# #                     else:
# #                         color = "🟠"
# #                         relevance = "Somewhat Relevant"
                    
# #                     with st.expander(
# #                         f"{color} Result #{i}: {metadata['filename']} ({similarity:.0%} - {relevance})",
# #                         expanded=(i <= 2)
# #                     ):
# #                         col1, col2 = st.columns([3, 1])
                        
# #                         with col1:
# #                             if metadata['case_name']:
# #                                 st.markdown(f"**📋 Case:** {metadata['case_name']}")
# #                             if metadata['court']:
# #                                 st.markdown(f"**🏛️ Court:** {metadata['court']}")
# #                             if metadata['date']:
# #                                 st.markdown(f"**📅 Date:** {metadata['date']}")
# #                             if metadata['citations']:
# #                                 st.markdown(f"**📖 Citations:** {', '.join(metadata['citations'][:3])}")
                        
# #                         with col2:
# #                             st.metric("Similarity", f"{similarity:.0%}")
                        
# #                         if metadata['sections']:
# #                             st.markdown("**⚖️ Sections:**")
# #                             st.write(", ".join(metadata['sections'][:5]))
                        
# #                         if metadata['articles']:
# #                             st.markdown("**📄 Articles:**")
# #                             st.write(", ".join(metadata['articles'][:5]))
                        
# #                         st.markdown("**📄 Excerpt:**")
# #                         st.text_area("", value=result['text'][:1200] + "...", height=200, key=f"text_{i}")
                        
# #                         if st.button(f"View Full Text", key=f"full_{i}"):
# #                             st.text_area("Complete Text:", value=result['full_text'][:5000], height=400, key=f"fulltext_{i}")
    
# #     else:
# #         st.info("👈 Build or load an index from the sidebar to start searching")
        
# #         st.markdown("### 🚀 Quick Start")
# #         st.markdown("""
# #         1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
# #         2. Enter the API key in the sidebar
# #         3. Place your judgment PDFs in a folder
# #         4. Enter folder path in sidebar
# #         5. Click "Build Index"
# #         6. Start searching with even single-sentence queries!
        
# #         **Example Queries:**
# #         - "Mental fitness during trial"
# #         - "Section 465 postponement"
# #         - "Unsoundness of mind accused"
# #         """)


# # if __name__ == "__main__":
# #     main()

# """
# Enhanced Legal Judgment Similarity Detector with Gemini API
# Gemini acts as FALLBACK: Provides related cases, sections, judgments when similarity search has limited results
# """

# import streamlit as st
# import torch
# import torch.nn as nn
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
# import pickle
# import pdfplumber
# import re
# from pathlib import Path
# import os
# import google.generativeai as genai

# # FIXED MODEL CLASS - No BatchNorm
# class LegalBERTWithCustomLayers(nn.Module):
#     def __init__(self, base_model_name='sentence-transformers/all-MiniLM-L6-v2'):
#         super(LegalBERTWithCustomLayers, self).__init__()
#         self.base_model = SentenceTransformer(base_model_name)
#         for param in self.base_model.parameters():
#             param.requires_grad = False
        
#         self.custom_layers = nn.Sequential(
#             nn.Linear(384, 512),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(512, 256),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(256, 128),
#             nn.ReLU()
#         )
        
#     def encode(self, texts, convert_to_tensor=False):
#         self.eval()
#         with torch.no_grad():
#             base_embeddings = self.base_model.encode(
#                 texts, convert_to_tensor=True, show_progress_bar=False
#             )
#             enhanced_embeddings = self.custom_layers(base_embeddings)
        
#         if convert_to_tensor:
#             return enhanced_embeddings
#         else:
#             return enhanced_embeddings.cpu().numpy()


# @st.cache_resource
# def load_model(model_path='legal_bert_custom.pth'):
#     model = LegalBERTWithCustomLayers()
#     model.eval()
    
#     if os.path.exists(model_path):
#         try:
#             model.load_state_dict(torch.load(model_path, map_location='cpu'))
#             model.eval()
#             st.success("✅ Custom trained model loaded!")
#             return model, True
#         except Exception as e:
#             st.warning(f"⚠️ Could not load custom model: {e}")
#             st.info("Using pre-trained model only (fallback mode)")
#             return model, False
#     else:
#         st.info("ℹ️ No custom model found. Using pre-trained BERT only.")
#         return model, False


# def configure_gemini(api_key):
#     """Configure Gemini API"""
#     try:
#         genai.configure(api_key=api_key)
#         return True
#     except Exception as e:
#         st.error(f"Failed to configure Gemini API: {e}")
#         return False


# def get_gemini_legal_insights(query, api_key):
#     """
#     Use Gemini as FALLBACK to provide comprehensive legal information
#     Returns: related cases, sections, articles, judgments, legal principles
#     """
#     try:
#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel('gemini-pro')
        
#         prompt = f"""You are an expert legal research assistant with deep knowledge of Indian law.

# A user is researching: "{query}"

# Provide comprehensive legal information including:

# 1. **Relevant Legal Sections & Articles**: List specific sections of IPC, CrPC, CPC, or relevant acts
# 2. **Landmark Judgments**: Name 3-5 important Supreme Court or High Court cases related to this topic
# 3. **Legal Principles**: Key legal principles and doctrines applicable
# 4. **Related Topics**: Other related legal areas to explore
# 5. **Citations**: Proper legal citations (AIR, SCC format if applicable)

# Format your response clearly with headers. Be specific and cite actual case names and section numbers.

# Legal Research:"""
        
#         response = model.generate_content(prompt)
#         return response.text.strip(), True
    
#     except Exception as e:
#         return f"Error fetching legal insights: {e}", False


# def extract_text_from_pdf(pdf_path):
#     text = ""
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
#     except Exception as e:
#         return ""
#     return text


# def preprocess_text(text):
#     text = re.sub(r'\s+', ' ', text)
#     text = re.sub(r'[^\w\s\.,;:()\[\]/@-]', '', text)
#     return text.strip()


# def extract_metadata(text, filename):
#     metadata = {
#         'filename': filename,
#         'case_name': '',
#         'court': '',
#         'date': '',
#         'citations': [],
#         'sections': [],
#         'articles': [],
#         'key_holdings': []
#     }
    
#     lines = text.split('\n')
    
#     # Case name
#     for line in lines[:15]:
#         if ' vs ' in line.lower() or ' v. ' in line or ' V. ' in line:
#             metadata['case_name'] = line.strip()[:200]
#             break
    
#     # Court
#     court_keywords = ['Supreme Court', 'High Court', 'District Court', 'Sessions Court']
#     for keyword in court_keywords:
#         if keyword.lower() in text[:2000].lower():
#             metadata['court'] = keyword
#             break
    
#     # Date
#     date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
#     dates = re.findall(date_pattern, text[:1500])
#     if dates:
#         metadata['date'] = dates[0]
    
#     # Citations
#     citation_patterns = [
#         r'\d{4}\s+AIR\s+\w+\s+\d+',
#         r'\d{4}\s+SCC\s+\(\d+\)\s+\d+',
#         r'AIR\s+\d{4}\s+\w+\s+\d+'
#     ]
#     for pattern in citation_patterns:
#         citations = re.findall(pattern, text[:3000], re.IGNORECASE)
#         metadata['citations'].extend(citations[:5])
    
#     # Sections
#     section_pattern = r'Section\s+\d+[A-Z]?'
#     sections = re.findall(section_pattern, text[:5000], re.IGNORECASE)
#     metadata['sections'] = list(set(sections))[:10]
    
#     # Articles
#     article_pattern = r'Article\s+\d+[A-Z]?'
#     articles = re.findall(article_pattern, text[:5000], re.IGNORECASE)
#     metadata['articles'] = list(set(articles))[:10]
    
#     return metadata


# def build_index(model, pdf_folder):
#     documents = []
#     embeddings_list = []
    
#     pdf_files = list(Path(pdf_folder).glob('*.pdf')) + list(Path(pdf_folder).glob('*.PDF'))
    
#     if not pdf_files:
#         st.error("No PDF files found!")
#         return None, None
    
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     for idx, pdf_path in enumerate(pdf_files):
#         status_text.text(f"Processing: {pdf_path.name} ({idx+1}/{len(pdf_files)})")
        
#         text = extract_text_from_pdf(str(pdf_path))
#         if not text or len(text) < 100:
#             st.warning(f"Skipping {pdf_path.name} - insufficient text")
#             continue
        
#         clean_text = preprocess_text(text)
#         metadata = extract_metadata(text, pdf_path.name)
        
#         embedding = model.encode([clean_text[:5000]])[0]
        
#         documents.append({
#             'text': clean_text[:2000],
#             'full_text': clean_text,
#             'filename': pdf_path.name,
#             'metadata': metadata
#         })
#         embeddings_list.append(embedding)
        
#         progress_bar.progress((idx + 1) / len(pdf_files))
    
#     if not documents:
#         st.error("No valid documents found!")
#         status_text.empty()
#         progress_bar.empty()
#         return None, None
    
#     status_text.text("Creating FAISS index...")
    
#     embeddings_array = np.array(embeddings_list).astype('float32')
#     dimension = embeddings_array.shape[1]
    
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings_array)
    
#     status_text.text(f"✓ Indexed {len(documents)} judgments!")
#     progress_bar.empty()
    
#     return index, documents


# def search_judgments(query_text, model, index, documents, top_k=5):
#     query_embedding = model.encode([query_text])[0].astype('float32').reshape(1, -1)
#     distances, indices = index.search(query_embedding, top_k)
    
#     results = []
#     for idx, dist in zip(indices[0], distances[0]):
#         if idx < len(documents):
#             result = documents[idx].copy()
#             result['similarity_score'] = float(1 / (1 + dist))
#             results.append(result)
    
#     return results


# def save_index(index, documents, save_path='legal_index'):
#     faiss.write_index(index, f"{save_path}.index")
#     with open(f"{save_path}_docs.pkl", 'wb') as f:
#         pickle.dump(documents, f)


# def load_index(save_path='legal_index'):
#     try:
#         index = faiss.read_index(f"{save_path}.index")
#         with open(f"{save_path}_docs.pkl", 'rb') as f:
#             documents = pickle.load(f)
#         return index, documents
#     except:
#         return None, None


# def main():
#     st.set_page_config(
#         page_title="Legal Judgment Similarity Detector",
#         page_icon="⚖️",
#         layout="wide"
#     )
    
#     st.title("⚖️ Legal Judgment Similarity Detector")
#     st.markdown("**AI-Powered Semantic Search with Gemini Legal Research Fallback**")
    
#     # Sidebar
#     with st.sidebar:
#         st.header("⚙️ Configuration")
        
#         # Gemini API Configuration
#         st.subheader("🤖 Gemini API (Fallback)")
#         gemini_api_key = st.text_input(
#             "Gemini API Key", 
#             type="password",
#             help="Get your API key from https://makersuite.google.com/app/apikey"
#         )
        
#         if gemini_api_key:
#             if configure_gemini(gemini_api_key):
#                 st.success("✅ Gemini API Connected")
#                 st.session_state['gemini_api_key'] = gemini_api_key
#             else:
#                 st.error("❌ Invalid API Key")
        
#         use_gemini_fallback = st.checkbox(
#             "Enable Gemini Legal Research", 
#             value=True,
#             help="Get additional legal insights, related cases, and sections from Gemini AI"
#         )
#         st.session_state['use_gemini_fallback'] = use_gemini_fallback
        
#         st.divider()
        
#         st.subheader("Model")
#         model, is_trained = load_model()
        
#         if is_trained:
#             st.success("✅ Custom Model Loaded")
#         else:
#             st.info("📊 Pre-trained Model (Fallback)")
        
#         st.divider()
        
#         st.subheader("📁 Data Management")
#         pdf_folder = st.text_input("PDF Folder Path", value="./judgments")
        
#         if st.button("🔄 Build Index", type="primary"):
#             if not os.path.exists(pdf_folder):
#                 st.error(f"Folder not found: {pdf_folder}")
#             else:
#                 with st.spinner("Building index..."):
#                     index, documents = build_index(model, pdf_folder)
#                     if index and documents:
#                         save_index(index, documents)
#                         st.session_state['index'] = index
#                         st.session_state['documents'] = documents
#                         st.success(f"✓ {len(documents)} judgments indexed!")
        
#         if st.button("📂 Load Saved Index"):
#             index, documents = load_index()
#             if index and documents:
#                 st.session_state['index'] = index
#                 st.session_state['documents'] = documents
#                 st.success(f"✓ {len(documents)} judgments loaded!")
        
#         st.divider()
#         st.markdown("### About")
#         st.info("Searches your judgment database + uses Gemini AI to provide related legal information")
    
#     # Main interface
#     if 'index' in st.session_state and 'documents' in st.session_state:
        
#         st.success(f"✓ {len(st.session_state['documents'])} judgments ready for search")
        
#         st.markdown("### 🔍 Search for Similar Judgments")
        
#         # Query input
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             query_side = st.selectbox(
#                 "Your Side:",
#                 ["Defense", "Prosecution", "Petitioner", "Respondent", "Neutral Research"]
#             )
        
#         case_description = st.text_area(
#             "Enter case details or legal question:",
#             height=100,
#             placeholder="Examples:\n- Mental fitness during trial\n- Divorce case grounds\n- Section 498A harassment\n- Child custody dispute"
#         )
        
#         top_k = st.slider("Number of results:", 1, 10, 5)
        
#         if st.button("🔎 Find Similar Judgments", type="primary"):
#             if not case_description or len(case_description) < 5:
#                 st.warning("⚠️ Please provide at least a brief query")
#             else:
#                 # Perform similarity search on your documents
#                 with st.spinner("Searching your judgment database..."):
#                     results = search_judgments(
#                         case_description,
#                         model,
#                         st.session_state['index'],
#                         st.session_state['documents'],
#                         top_k
#                     )
                
#                 # Display results from your database
#                 st.markdown("---")
#                 st.subheader(f"📊 Similar Judgments from Your Database")
                
#                 has_good_results = any(r['similarity_score'] > 0.70 for r in results)
                
#                 if results:
#                     for i, result in enumerate(results, 1):
#                         metadata = result['metadata']
#                         similarity = result['similarity_score']
                        
#                         # Relevance indicator
#                         if similarity > 0.85:
#                             color = "🟢"
#                             relevance = "Highly Relevant"
#                         elif similarity > 0.70:
#                             color = "🟡"
#                             relevance = "Relevant"
#                         else:
#                             color = "🟠"
#                             relevance = "Somewhat Relevant"
                        
#                         with st.expander(
#                             f"{color} Result #{i}: {metadata['filename']} ({similarity:.0%} - {relevance})",
#                             expanded=(i <= 2)
#                         ):
#                             col1, col2 = st.columns([3, 1])
                            
#                             with col1:
#                                 if metadata['case_name']:
#                                     st.markdown(f"**📋 Case:** {metadata['case_name']}")
#                                 if metadata['court']:
#                                     st.markdown(f"**🏛️ Court:** {metadata['court']}")
#                                 if metadata['date']:
#                                     st.markdown(f"**📅 Date:** {metadata['date']}")
#                                 if metadata['citations']:
#                                     st.markdown(f"**📖 Citations:** {', '.join(metadata['citations'][:3])}")
                            
#                             with col2:
#                                 st.metric("Similarity", f"{similarity:.0%}")
                            
#                             if metadata['sections']:
#                                 st.markdown("**⚖️ Sections:**")
#                                 st.write(", ".join(metadata['sections'][:5]))
                            
#                             if metadata['articles']:
#                                 st.markdown("**📄 Articles:**")
#                                 st.write(", ".join(metadata['articles'][:5]))
                            
#                             st.markdown("**📄 Excerpt:**")
#                             st.text_area("", value=result['text'][:1200] + "...", height=200, key=f"text_{i}")
                            
#                             if st.button(f"View Full Text", key=f"full_{i}"):
#                                 st.text_area("Complete Text:", value=result['full_text'][:5000], height=400, key=f"fulltext_{i}")
                
#                 # GEMINI FALLBACK - Additional legal research
#                 if (st.session_state.get('use_gemini_fallback') and 
#                     st.session_state.get('gemini_api_key')):
                    
#                     st.markdown("---")
#                     st.subheader("🤖 Additional Legal Research (Gemini AI)")
                    
#                     if not has_good_results:
#                         st.info("💡 Your database has limited matches. Gemini is providing broader legal context:")
                    
#                     with st.spinner("Fetching legal insights from Gemini AI..."):
#                         legal_insights, success = get_gemini_legal_insights(
#                             case_description,
#                             st.session_state['gemini_api_key']
#                         )
                    
#                     if success:
#                         with st.container():
#                             st.markdown("### 📚 Comprehensive Legal Information")
#                             st.markdown(legal_insights)
                            
#                             st.info("💡 **Tip**: Use the sections and case names mentioned above to search for specific judgments in legal databases like SCC Online, Manupatra, or Indian Kanoon.")
#                     else:
#                         st.error("Could not fetch legal insights from Gemini")
    
#     else:
#         st.info("👈 Build or load an index from the sidebar to start searching")
        
#         st.markdown("### 🚀 Quick Start")
#         st.markdown("""
#         1. **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
#         2. **Add Your Judgments**: Place PDF files in a folder
#         3. **Build Index**: Enter folder path and click "Build Index"
#         4. **Search**: Enter any case type or legal query
        
#         ### 🎯 How It Works
        
#         **Two-Layer System:**
#         1. **Primary**: Searches your uploaded judgment PDFs using AI similarity
#         2. **Fallback (Gemini)**: Provides related cases, sections, and legal principles from broader legal knowledge
        
#         **Example Queries:**
#         - "Mental fitness during trial"
#         - "Divorce case cruelty grounds"
#         - "Section 498A false allegations"
#         - "Child custody mother preference"
#         - "Property partition Hindu law"
        
#         **What Gemini Provides:**
#         - Relevant IPC/CrPC/CPC sections
#         - Landmark Supreme Court judgments
#         - Legal principles and doctrines
#         - Related legal topics
#         - Proper case citations
#         """)


# if __name__ == "__main__":
#     main()

# """
# Enhanced Legal Judgment Similarity Detector with Gemini API
# FIXED: Excerpt display and duplicate results - TESTED VERSION
# """

# import streamlit as st
# import torch
# import torch.nn as nn
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
# import pickle
# import pdfplumber
# import re
# from pathlib import Path
# import os
# import google.generativeai as genai

# # MODEL CLASS
# class LegalBERTWithCustomLayers(nn.Module):
#     def __init__(self, base_model_name='sentence-transformers/all-MiniLM-L6-v2'):
#         super(LegalBERTWithCustomLayers, self).__init__()
#         self.base_model = SentenceTransformer(base_model_name)
#         for param in self.base_model.parameters():
#             param.requires_grad = False
        
#         self.custom_layers = nn.Sequential(
#             nn.Linear(384, 512),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(512, 256),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(256, 128),
#             nn.ReLU()
#         )
        
#     def encode(self, texts, convert_to_tensor=False):
#         self.eval()
#         with torch.no_grad():
#             base_embeddings = self.base_model.encode(
#                 texts, convert_to_tensor=True, show_progress_bar=False
#             )
#             enhanced_embeddings = self.custom_layers(base_embeddings)
        
#         if convert_to_tensor:
#             return enhanced_embeddings
#         else:
#             return enhanced_embeddings.cpu().numpy()


# @st.cache_resource
# def load_model(model_path='legal_bert_custom.pth'):
#     model = LegalBERTWithCustomLayers()
#     model.eval()
    
#     if os.path.exists(model_path):
#         try:
#             model.load_state_dict(torch.load(model_path, map_location='cpu'))
#             model.eval()
#             st.success("✅ Custom trained model loaded!")
#             return model, True
#         except Exception as e:
#             st.warning(f"⚠️ Could not load custom model: {e}")
#             st.info("Using pre-trained model only (fallback mode)")
#             return model, False
#     else:
#         st.info("ℹ️ No custom model found. Using pre-trained BERT only.")
#         return model, False


# def configure_gemini(api_key):
#     try:
#         genai.configure(api_key=api_key)
#         return True
#     except Exception as e:
#         st.error(f"Failed to configure Gemini API: {e}")
#         return False


# def get_gemini_legal_insights(query, api_key):
#     try:
#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel('gemini-pro')
        
#         prompt = f"""You are an expert legal research assistant with deep knowledge of Indian law.

# A user is researching: "{query}"

# Provide comprehensive legal information including:

# 1. **Relevant Legal Sections & Articles**: List specific sections of IPC, CrPC, CPC, or relevant acts
# 2. **Landmark Judgments**: Name 3-5 important Supreme Court or High Court cases related to this topic
# 3. **Legal Principles**: Key legal principles and doctrines applicable
# 4. **Related Topics**: Other related legal areas to explore
# 5. **Citations**: Proper legal citations (AIR, SCC format if applicable)

# Format your response clearly with headers. Be specific and cite actual case names and section numbers.

# Legal Research:"""
        
#         response = model.generate_content(prompt)
#         return response.text.strip(), True
    
#     except Exception as e:
#         return f"Error fetching legal insights: {e}", False


# def extract_text_from_pdf(pdf_path):
#     text = ""
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
#     except Exception as e:
#         return ""
#     return text


# def preprocess_text(text):
#     text = re.sub(r'\s+', ' ', text)
#     text = re.sub(r'[^\w\s\.,;:()\[\]/@-]', '', text)
#     return text.strip()


# def extract_metadata(text, filename):
#     metadata = {
#         'filename': filename,
#         'case_name': '',
#         'court': '',
#         'date': '',
#         'citations': [],
#         'sections': [],
#         'articles': [],
#         'key_holdings': []
#     }
    
#     lines = text.split('\n')
    
#     for line in lines[:15]:
#         if ' vs ' in line.lower() or ' v. ' in line or ' V. ' in line:
#             metadata['case_name'] = line.strip()[:200]
#             break
    
#     court_keywords = ['Supreme Court', 'High Court', 'District Court', 'Sessions Court']
#     for keyword in court_keywords:
#         if keyword.lower() in text[:2000].lower():
#             metadata['court'] = keyword
#             break
    
#     date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}'
#     dates = re.findall(date_pattern, text[:1500])
#     if dates:
#         metadata['date'] = dates[0]
    
#     citation_patterns = [
#         r'\d{4}\s+AIR\s+\w+\s+\d+',
#         r'\d{4}\s+SCC\s+\(\d+\)\s+\d+',
#         r'AIR\s+\d{4}\s+\w+\s+\d+'
#     ]
#     for pattern in citation_patterns:
#         citations = re.findall(pattern, text[:3000], re.IGNORECASE)
#         metadata['citations'].extend(citations[:5])
    
#     section_pattern = r'Section\s+\d+[A-Z]?'
#     sections = re.findall(section_pattern, text[:5000], re.IGNORECASE)
#     metadata['sections'] = list(set(sections))[:10]
    
#     article_pattern = r'Article\s+\d+[A-Z]?'
#     articles = re.findall(article_pattern, text[:5000], re.IGNORECASE)
#     metadata['articles'] = list(set(articles))[:10]
    
#     return metadata


# def build_index(model, pdf_folder):
#     documents = []
#     embeddings_list = []
    
#     pdf_files = list(Path(pdf_folder).glob('*.pdf')) + list(Path(pdf_folder).glob('*.PDF'))
    
#     if not pdf_files:
#         st.error("No PDF files found!")
#         return None, None
    
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     for idx, pdf_path in enumerate(pdf_files):
#         status_text.text(f"Processing: {pdf_path.name} ({idx+1}/{len(pdf_files)})")
        
#         text = extract_text_from_pdf(str(pdf_path))
#         if not text or len(text) < 100:
#             st.warning(f"Skipping {pdf_path.name} - insufficient text")
#             continue
        
#         clean_text = preprocess_text(text)
#         metadata = extract_metadata(text, pdf_path.name)
        
#         embedding = model.encode([clean_text[:5000]])[0]
        
#         documents.append({
#             'text': clean_text[:2000],
#             'full_text': clean_text,
#             'filename': pdf_path.name,
#             'metadata': metadata
#         })
#         embeddings_list.append(embedding)
        
#         progress_bar.progress((idx + 1) / len(pdf_files))
    
#     if not documents:
#         st.error("No valid documents found!")
#         status_text.empty()
#         progress_bar.empty()
#         return None, None
    
#     status_text.text("Creating FAISS index...")
    
#     embeddings_array = np.array(embeddings_list).astype('float32')
#     dimension = embeddings_array.shape[1]
    
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings_array)
    
#     status_text.text(f"✓ Indexed {len(documents)} judgments!")
#     progress_bar.empty()
    
#     return index, documents


# def search_judgments(query_text, model, index, documents, top_k=5):
#     query_embedding = model.encode([query_text])[0].astype('float32').reshape(1, -1)
#     distances, indices = index.search(query_embedding, top_k)
    
#     results = []
#     for idx, dist in zip(indices[0], distances[0]):
#         if idx < len(documents):
#             result = documents[idx].copy()
#             result['similarity_score'] = float(1 / (1 + dist))
#             results.append(result)
    
#     return results


# def save_index(index, documents, save_path='legal_index'):
#     faiss.write_index(index, f"{save_path}.index")
#     with open(f"{save_path}_docs.pkl", 'wb') as f:
#         pickle.dump(documents, f)


# def load_index(save_path='legal_index'):
#     try:
#         index = faiss.read_index(f"{save_path}.index")
#         with open(f"{save_path}_docs.pkl", 'rb') as f:
#             documents = pickle.load(f)
#         return index, documents
#     except:
#         return None, None


# def main():
#     st.set_page_config(
#         page_title="Legal Judgment Similarity Detector",
#         page_icon="⚖️",
#         layout="wide"
#     )
    
#     st.title("⚖️ Legal Judgment Similarity Detector")
#     st.markdown("**AI-Powered Semantic Search with Gemini Legal Research Fallback**")
    
#     with st.sidebar:
#         st.header("⚙️ Configuration")
        
#         st.subheader("🤖 Gemini API (Fallback)")
#         gemini_api_key = st.text_input(
#             "Gemini API Key", 
#             type="password",
#             help="Get your API key from https://makersuite.google.com/app/apikey"
#         )
        
#         if gemini_api_key:
#             if configure_gemini(gemini_api_key):
#                 st.success("✅ Gemini API Connected")
#                 st.session_state['gemini_api_key'] = gemini_api_key
#             else:
#                 st.error("❌ Invalid API Key")
        
#         use_gemini_fallback = st.checkbox(
#             "Enable Gemini Legal Research", 
#             value=True,
#             help="Get additional legal insights"
#         )
#         st.session_state['use_gemini_fallback'] = use_gemini_fallback
        
#         st.divider()
        
#         st.subheader("Model")
#         model, is_trained = load_model()
        
#         if is_trained:
#             st.success("✅ Custom Model Loaded")
#         else:
#             st.info("📊 Pre-trained Model")
        
#         st.divider()
        
#         st.subheader("📁 Data Management")
#         pdf_folder = st.text_input("PDF Folder Path", value="./judgments")
        
#         if st.button("🔄 Build Index", type="primary"):
#             if not os.path.exists(pdf_folder):
#                 st.error(f"Folder not found: {pdf_folder}")
#             else:
#                 with st.spinner("Building index..."):
#                     index, documents = build_index(model, pdf_folder)
#                     if index and documents:
#                         save_index(index, documents)
#                         st.session_state['index'] = index
#                         st.session_state['documents'] = documents
#                         st.success(f"✓ {len(documents)} judgments indexed!")
        
#         if st.button("📂 Load Saved Index"):
#             index, documents = load_index()
#             if index and documents:
#                 st.session_state['index'] = index
#                 st.session_state['documents'] = documents
#                 st.success(f"✓ {len(documents)} judgments loaded!")
    
#     if 'index' in st.session_state and 'documents' in st.session_state:
        
#         st.success(f"✓ {len(st.session_state['documents'])} judgments ready for search")
        
#         st.markdown("### 🔍 Search for Similar Judgments")
        
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             query_side = st.selectbox(
#                 "Your Side:",
#                 ["Defense", "Prosecution", "Petitioner", "Respondent", "Neutral Research"]
#             )
        
#         case_description = st.text_area(
#             "Enter case details or legal question:",
#             height=100,
#             placeholder="Example: Mental fitness during trial"
#         )
        
#         top_k = st.slider("Number of results:", 1, 10, 5)
        
#         if st.button("🔎 Find Similar Judgments", type="primary"):
#             if not case_description or len(case_description) < 5:
#                 st.warning("⚠️ Please enter a search query")
#             else:
#                 with st.spinner("Searching..."):
#                     results = search_judgments(
#                         case_description,
#                         model,
#                         st.session_state['index'],
#                         st.session_state['documents'],
#                         top_k
#                     )
                
#                 st.markdown("---")
#                 st.subheader(f"📊 Similar Judgments from Your Database")
                
#                 has_good_results = any(r['similarity_score'] > 0.70 for r in results)
                
#                 if results:
#                     for i, result in enumerate(results, 1):
#                         metadata = result['metadata']
#                         similarity = result['similarity_score']
                        
#                         if similarity > 0.85:
#                             color = "🟢"
#                             relevance = "Highly Relevant"
#                         elif similarity > 0.70:
#                             color = "🟡"
#                             relevance = "Relevant"
#                         else:
#                             color = "🟠"
#                             relevance = "Somewhat Relevant"
                        
#                         with st.expander(
#                             f"{color} Result #{i}: {metadata['filename']} ({similarity:.0%} - {relevance})",
#                             expanded=(i <= 2)
#                         ):
#                             col1, col2 = st.columns([3, 1])
                            
#                             with col1:
#                                 if metadata.get('case_name'):
#                                     st.markdown(f"**📋 Case:** {metadata['case_name']}")
#                                 if metadata.get('court'):
#                                     st.markdown(f"**🏛️ Court:** {metadata['court']}")
#                                 if metadata.get('date'):
#                                     st.markdown(f"**📅 Date:** {metadata['date']}")
#                                 if metadata.get('citations'):
#                                     st.markdown(f"**📖 Citations:** {', '.join(metadata['citations'][:3])}")
                            
#                             with col2:
#                                 st.metric("Similarity", f"{similarity:.0%}")
                            
#                             if metadata.get('sections'):
#                                 st.markdown("**⚖️ Sections:**")
#                                 st.write(", ".join(metadata['sections'][:5]))
                            
#                             if metadata.get('articles'):
#                                 st.markdown("**📄 Articles:**")
#                                 st.write(", ".join(metadata['articles'][:5]))
                            
#                             st.markdown("**📄 Excerpt:**")
#                             excerpt_text = result.get('text', '')
#                             if excerpt_text and len(excerpt_text.strip()) > 0:
#                                 st.text_area("", value=excerpt_text[:1200] + "...", height=200, key=f"text_{i}", label_visibility="collapsed")
#                             else:
#                                 st.info("No text preview available")
                            
#                             if st.button(f"📖 View Full Text", key=f"full_{i}"):
#                                 full_text = result.get('full_text', '')
#                                 if full_text:
#                                     st.text_area("Complete Text:", value=full_text[:5000], height=400, key=f"fulltext_{i}")
                
#                 if (st.session_state.get('use_gemini_fallback') and 
#                     st.session_state.get('gemini_api_key')):
                    
#                     st.markdown("---")
#                     st.subheader("🤖 Additional Legal Research (Gemini AI)")
                    
#                     if not has_good_results:
#                         st.info("💡 Your database has limited matches. Gemini is providing broader legal context:")
                    
#                     with st.spinner("Fetching legal insights..."):
#                         legal_insights, success = get_gemini_legal_insights(
#                             case_description,
#                             st.session_state['gemini_api_key']
#                         )
                    
#                     if success:
#                         st.markdown("### 📚 Comprehensive Legal Information")
#                         st.markdown(legal_insights)
#                         st.info("💡 **Tip**: Use the sections and case names to search legal databases.")
    
#     else:
#         st.info("👈 Build or load an index from the sidebar to start searching")
        
#         st.markdown("""
#         ### 🚀 Quick Start
#         1. Get Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
#         2. Place PDF files in a folder
#         3. Enter folder path and click "Build Index"
#         4. Start searching!
#         """)


# if __name__ == "__main__":
#     main()


from flask import Flask, render_template, request
from dashboard.dashboard_app import get_dashboard_data, get_search_data, get_chat_data, get_upload_data, get_analytics_data, get_comparison_data, get_settings_data

app = Flask(__name__)

NAVIGATION_ITEMS = [
    {"id": "dashboard", "label": "Dashboard", "icon": "dashboard"},
    {"id": "search", "label": "Search Judgments", "icon": "gavel"},
    {"id": "chat", "label": "AI Chat", "icon": "chat"},
    {"id": "upload", "label": "Upload PDFs", "icon": "upload_file"},
    {"id": "analytics", "label": "Analytics", "icon": "analytics"},
    {"id": "comparison", "label": "Case Comparison", "icon": "compare_arrows"},

]

@app.route('/')
def home():
    current_page = request.args.get('page', 'dashboard')
    
    context = {
        "nav_items": NAVIGATION_ITEMS,
        "current_page": current_page,
    }
    
    if current_page == "dashboard":
        context["data"] = get_dashboard_data()
    elif current_page == "search":
        context["data"] = get_search_data()
    elif current_page == "chat":
        context["data"] = get_chat_data()
    elif current_page == "upload":
        context["data"] = get_upload_data()
    elif current_page == "analytics":
        context["data"] = get_analytics_data()
    elif current_page == "comparison":
        context["data"] = get_comparison_data()
    elif current_page in ["settings", "profile"]:
        context["data"] = get_settings_data()
    else:
        current_item = next((item for item in NAVIGATION_ITEMS if item["id"] == current_page), None)
        context["page_label"] = current_item["label"] if current_item else "Settings"
        
    return render_template("base.html", **context)

if __name__ == '__main__':
    app.run(debug=True, port=5000)