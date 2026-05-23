def get_dashboard_data():
    return {
        "recent_matters": [
            {
                "name": "State of NJ vs. Rodriguez",
                "category": "Criminal Defense / Discovery Review",
                "ref_id": "MAT-2024-0892",
                "status": "Ready",
                "status_color": "bg-green-100 text-green-800 border-green-200",
                "last_active": "2 hours ago"
            },
            {
                "name": "Draft_Lease_Agreement_V4.pdf",
                "category": "Commercial Real Estate / Compliance",
                "ref_id": "DOC-9912-RE",
                "status": "Analyzing",
                "status_color": "bg-blue-100 text-blue-800 border-blue-200 animate-pulse",
                "last_active": "14 mins ago"
            },
            {
                "name": "Apex Corp vs. Lunar Systems",
                "category": "IP Litigation / Motion for Summary",
                "ref_id": "MAT-2024-1105",
                "status": "Ready",
                "status_color": "bg-green-100 text-green-800 border-green-200",
                "last_active": "Yesterday"
            }
        ]
    }

def get_search_data():
    return {
        "results_count": "432",
        "results": [
            {
                "badge": "PRECEDENT",
                "badge_style": "bg-indigo-50 text-indigo-700 border-indigo-100",
                "citation": "2023 SCC OnLine SC 1421",
                "title": "Global Tech Corp vs. Unified Patent Alliance",
                "court": "Supreme Court of Justice",
                "bench": "Hon'ble Justice Roberts, Hon'ble Justice Alito",
                "date": "Oct 14, 2023",
                "topic": "Intellectual Property / SEP Licensing",
                "tags": ["Cited by 124 cases", "Followed in 12 circuits"],
                "ai_summary": "The court established a new framework for 'Fair and Reasonable' (FRAND) terms in tech licensing, shifting the burden of proof to the licensor during initial negotiations. This effectively reduces standard royalty rates by 15-20% for manufacturers."
            },
            {
                "badge": "OVERRULED",
                "badge_style": "bg-rose-50 text-rose-700 border-rose-100",
                "citation": "2022 UKSC 45",
                "title": "Inland Revenue vs. Sterling Holdings Ltd.",
                "court": "High Court of Justice (Appellate)",
                "bench": "Full Bench (5 Judges)",
                "date": "June 22, 2022",
                "topic": "Taxation / Corporate Liability",
                "tags": ["Significantly Criticized", "Cited by 89 cases"],
                "badge_critical": True,
                "ai_summary": "Crucial interpretation of offshore asset valuation. The court clarified that 'economic substance' takes precedence over 'legal form' in tax avoidance cases. This judgment was later refined by the 2024 Revenue Act."
            },
            {
                "badge": "LEADING",
                "badge_style": "bg-blue-50 text-blue-700 border-blue-100",
                "citation": "2021 F.3d 982",
                "title": "State of California vs. Eco-Mining Solutions",
                "court": "Federal Appeals Court",
                "bench": "Hon'ble Justice Sotomayor (Presiding)",
                "date": "Feb 09, 2021",
                "topic": "Environmental Compliance / Administrative Law",
                "tags": ["Key Procedural Ruling", "Cited by 212 cases"],
                "ai_summary": "Established strict liability for environmental damages caused by sub-contractors if 'due diligence' frameworks were not explicitly audited. Highly relevant for M&A due diligence workflows."
            }
        ]
    }

def get_chat_data():
    return {
        "case_name": "State of NY v. Anderson",
        "matter_no": "2024-CR-8821",
        "metadata": {
            "judge": "Hon. Catherine Vance",
            "hearing": "Oct 24, 2023 - 10:00 AM"
        },
        "context_files": [
            {"name": "Deposition_WitnessB_Fi...", "pages": "42 Pages"},
            {"name": "Forensic_Report_Digital...", "pages": "128 Pages"}
        ],
        "contradiction_rows": [
            {"source": "Deposition (P.14)", "time": "22:15", "desc": "Witness claims defendant left the premises."},
            {"source": "Forensic Report", "time": "22:38", "desc": "Keycard entry logged at exit point."}
        ],
        "hashtags": ["#Cross-Examination", "#TimelineAnalysis", "#LegalPrecedents"]
    }

def get_upload_data():
    return {
        "active_uploads": [
            {
                "id": 1,
                "name": "Affidavit_State_vs_Henderson_Final.pdf",
                "type": "uploading",
                "meta": "78% • 12.4 MB",
                "progress_pct": 78
            },
            {
                "id": 2,
                "name": "Exhibit_C_Medical_Records.pdf",
                "type": "processing",
                "meta": "Processing",
                "progress_pct": 100
            },
            {
                "id": 3,
                "name": "Deposition_TRANSCRIPT_2024_05.pdf",
                "type": "completed",
                "meta": "Indexed & Verified • 4.2 MB",
                "progress_pct": 100
            }
        ],
        "compatibility_matrix": [
            {"title": "Documents & PDFs", "ext": "PDF, DOCX, TXT, RTF", "desc": "(OCR automatically applied to scanned images).", "icon": "article"},
            {"title": "Evidence Packs", "ext": "ZIP, 7Z", "desc": "Automated extraction and folder hierarchy preservation.", "icon": "inventory_2"},
            {"title": "Email Discovery", "ext": "PST, MSG, EML", "desc": "Threads are reconstructed with AI analysis.", "icon": "mail"}
        ]
    }

def get_analytics_data():
    return {
        "metrics": {
            "judgments": {"val": "12,482", "change": "+12.5%"},
            "compliance": {"val": "94.2%", "change": "vs last month"},
            "resolution": {"val": "18.5 days", "change": "-4.2%"}
        },
        "success_rates": [
            {"label": "Won", "count": "6,120", "color": "bg-slate-900"},
            {"label": "Settled", "count": "2,142", "color": "bg-indigo-500"},
            {"label": "Lost", "count": "1,023", "color": "bg-slate-350"}
        ],
        "cited_sections": [
            {"id": "S. 302 IPC", "desc": "Punishment for murder; culpable homicide amounting to murder.", "freq": "1,240 times", "trend": "+8%", "trend_class": "text-emerald-600"},
            {"id": "Art. 21 Const.", "desc": "Protection of life and personal liberty; fundamental rights.", "freq": "1,118 times", "trend": "+15%", "trend_class": "text-emerald-600"},
            {"id": "S. 138 NI Act", "desc": "Dishonour of cheque for insufficiency of funds in accounts.", "freq": "982 times", "trend": "-2%", "trend_class": "text-rose-600"},
            {"id": "S. 498A IPC", "desc": "Husband or relative of husband of a woman subjecting her to cruelty.", "freq": "845 times", "trend": "0%", "trend_class": "text-slate-400"},
            {"id": "Art. 226 Const.", "desc": "Power of High Courts to issue certain writs for enforcement of rights.", "freq": "762 times", "trend": "+12%", "trend_class": "text-emerald-600"}
        ]
    }

def get_comparison_data():
    return {
        "cases": [
            {
                "name": "Smith v. Department of Justice",
                "meta": "2023 | Civil Rights | Federal 9th Cir.",
                "reasoning": "The court found that the administrative burden of disclosure outweighed the public interest due to specific security protocols established in the 2018 Cybersecurity Act.",
                "badge": "PROCEDURAL",
                "citations": ["Carpenter v. United States (2018)", "FOIA Section 552(b)(7)"],
                "status": "NON-COMPLIANT",
                "status_color": "text-red-600 font-bold flex items-center gap-1",
                "status_desc": "Conflicts with current State-level directives in CA/WA."
            },
            {
                "name": "Doe v. Attorney General",
                "meta": "2021 | Privacy Law | Federal 2nd Cir.",
                "reasoning": "Reasoning centered on the 'reasonable expectation of privacy' test, concluding that encrypted metadata constitutes a private domain regardless of institutional status.",
                "badge": "SUBSTANTIVE",
                "citations": ["Carpenter v. United States (2018)", "No Section 552 crossover"],
                "status": "COMPLIANT",
                "status_color": "text-slate-800 font-bold flex items-center gap-1",
                "status_desc": "Full adherence to nationwide privacy standards."
            }
        ],
        "metadata": {
            "title": "Smith v. Department of Justice et al., 455 U.S. 88 (2023)",
            "court": "United States Court of Appeals for the Ninth Circuit",
            "author": "Judge Sarah T. Kensington"
        }
    }

def get_settings_data():
    return {
        "profile": {
            "name": "Alexander Thorne",
            "role": "Senior Counsel • Corporate Litigation",
            "location": "London, UK",
            "tier": "PREMIUM"
        },
        "stats": {
            "researched": "1,428",
            "uploaded": "3,892",
            "days_remaining": 248,
            "progress_pct": 68
        },
        "ai_modes": [
            {"title": "Deep Precedent Analysis", "desc": "Cross-reference 100+ years of high-court rulings for every query.", "status": True},
            {"title": "Strict Regulatory Filter", "desc": "Only include results from current and active legislative frameworks.", "status": False},
            {"title": "Causation-First Reasoning", "desc": "Prioritize chain-of-event logic in AI-generated case summaries.", "status": True}
        ]
    }