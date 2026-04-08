"""
HSG Thesis Match — Main App
Biddit-style dark sidebar + Compass-style content panels.

Run: python3 -m streamlit run app.py
"""

import os
import streamlit as st
from datetime import datetime as _dt

st.set_page_config(
    page_title="HSG Thesis Match",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Streamlit secrets into os.environ so all agents pick them up automatically
for _key in ("NVIDIA_API_KEY", "NIM_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    try:
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = st.secrets[_key]
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

RESEARCH_AREAS = [
    "Accounting", "Arts Administration", "Behavioral Science/Organizational Behaviour",
    "Business Communication", "Business Education", "Business Law/Legal Environment",
    "Computer Science", "Conflict", "Consulting", "Data Analytics",
    "E-Business/E-commerce", "Economics", "Energy Management", "Entrepreneurship",
    "Ethics", "Finance/Banking", "Health Services", "History",
    "Hotel/Restaurant/Tourism", "Human Resources Management", "Insurance",
    "International Business", "International Politics", "Leadership", "Management",
    "Manufacturing and Technology", "Marketing", "Media", "Mixed Methods",
    "Operations Management", "Philosophy", "Politics", "Public Management",
    "Qualitative Methods", "Quantitative Methods", "Real Estate", "Society",
    "Sports Management", "Statistics", "Strategic Management", "Supply Chain",
    "Sustainability", "Taxation", "Transport/Logistics",
]

HSG_BACHELOR_PROGRAMMES = [
    "Bachelor of Arts HSG in Business Administration (B.A. HSG)",
    "Bachelor of Arts HSG in Economics (B.A. HSG)",
    "Bachelor of Arts HSG in International Affairs (B.A. HSG)",
    "Bachelor of Arts HSG in Business Innovation (B.A. HSG)",
    "Bachelor of Science HSG in Nursing Science (B.Sc. HSG)",
]

HSG_MASTER_PROGRAMMES = [
    "Master in Accounting and Finance (MAcFin)",
    "Master in Banking and Finance (MBF)",
    "Master in Business Innovation (MBI)",
    "Master in Economics (MEcon)",
    "Master in General Management (MGM)",
    "Master in International Affairs and Governance (MIA)",
    "Master in Law and Economics (MLE)",
    "Master in Marketing Management (MiMM)",
    "Master in Quantitative Economics and Finance (MiQE/F)",
    "Master in Strategy and International Management (SIM)",
    "Master in Computer Science (MCS)",
    "Master in Management, Organization Studies and Cultural Theory (MOK)",
    "Master in International Law (MIL)",
    "Master in Law (MLaw)"
]

# Dynamic examples per programme context
PROGRAMME_CONTEXT = {
    # Economics
    "MEcon": {
        "title_ex":   "e.g. Trade liberalisation and wage inequality in Switzerland",
        "rq_ex":      "e.g. Does import competition from China increase wage dispersion across Swiss manufacturing firms?",
        "method_ex":  "e.g. Panel data OLS/IV regression using Swiss Federal Statistical Office data (2000–2022)",
        "skills_ex":  "e.g. Stata, R, Python, econometrics, causal inference",
        "kw_ex":      "e.g. trade, wage inequality, labour markets, import competition",
        "area_default": "Economics",
    },
    "MQE": {
        "title_ex":   "e.g. Machine learning approaches to forecasting Swiss GDP growth",
        "rq_ex":      "e.g. Do random forest models outperform ARIMA in short-horizon GDP nowcasting?",
        "method_ex":  "e.g. Cross-validated ML models (XGBoost, LASSO) vs. benchmark econometric models",
        "skills_ex":  "e.g. Python, R, time-series analysis, machine learning, statsmodels",
        "kw_ex":      "e.g. GDP forecasting, machine learning, nowcasting, LASSO",
        "area_default": "Quantitative Methods",
    },
    # Finance
    "MBF": {
        "title_ex":   "e.g. ESG ratings and the cost of debt for Swiss listed firms",
        "rq_ex":      "e.g. Do higher ESG scores lead to lower credit spreads in the Swiss corporate bond market?",
        "method_ex":  "e.g. Panel regression on Refinitiv/Bloomberg ESG and bond spread data (2015–2024)",
        "skills_ex":  "e.g. Python, Bloomberg Terminal, Datastream, Excel, panel regression",
        "kw_ex":      "e.g. ESG, cost of debt, credit spreads, sustainable finance",
        "area_default": "Finance/Banking",
    },
    "MF": {
        "title_ex":   "e.g. Momentum strategies and transaction costs on the SIX Swiss Exchange",
        "rq_ex":      "e.g. Are momentum profits in Swiss equities driven by illiquid small-caps or robust after costs?",
        "method_ex":  "e.g. Portfolio sorting, Fama-French factor models, transaction cost estimation",
        "skills_ex":  "e.g. Python, R, asset pricing, CRSP/Compustat, factor models",
        "kw_ex":      "e.g. momentum, asset pricing, transaction costs, Swiss equities",
        "area_default": "Finance/Banking",
    },
    "MAccFin": {
        "title_ex":   "e.g. Earnings management around IFRS 16 adoption in European retail",
        "rq_ex":      "e.g. Did IFRS 16 reduce discretionary accruals by constraining off-balance-sheet leasing?",
        "method_ex":  "e.g. Difference-in-differences using Compustat Europe, Jones model accruals",
        "skills_ex":  "e.g. Stata, Compustat, accounting research methods, accrual models",
        "kw_ex":      "e.g. earnings management, IFRS 16, accruals, lease accounting",
        "area_default": "Accounting",
    },
    # Management
    "MGM": {
        "title_ex":   "e.g. Digital transformation and organisational resilience in Swiss SMEs",
        "rq_ex":      "e.g. How do Swiss SMEs that adopted digital tools before 2020 compare in crisis resilience?",
        "method_ex":  "e.g. Mixed-methods: survey of 80 SMEs + 8 in-depth case study interviews",
        "skills_ex":  "e.g. Survey design, NVivo, SPSS, qualitative coding, interview methodology",
        "kw_ex":      "e.g. digital transformation, SMEs, organisational resilience, Switzerland",
        "area_default": "Strategic Management",
    },
    "MM": {
        "title_ex":   "e.g. Psychological safety and team innovation in remote-first organisations",
        "rq_ex":      "e.g. Does remote work reduce psychological safety and thereby hinder innovation output?",
        "method_ex":  "e.g. Quantitative survey (Edmondson scale) + mediation analysis (PROCESS macro)",
        "skills_ex":  "e.g. Survey design, SPSS/R, mediation analysis, organisational behaviour",
        "kw_ex":      "e.g. psychological safety, remote work, team innovation, OB",
        "area_default": "Behavioral Science/Organizational Behaviour",
    },
    "SIM": {
        "title_ex":   "e.g. Home-region orientation and performance in Swiss multinational firms",
        "rq_ex":      "e.g. Do Swiss MNCs with higher home-region sales concentration outperform more globally diversified peers?",
        "method_ex":  "e.g. Panel regression on Fortune 500 Swiss firms, geographic segment reporting",
        "skills_ex":  "e.g. R, international business theory, qualitative case studies, panel data",
        "kw_ex":      "e.g. multinational corporations, home-region orientation, internationalisation",
        "area_default": "International Business",
    },
    # Marketing
    "MMM": {
        "title_ex":   "e.g. Influencer authenticity and purchase intention on Instagram",
        "rq_ex":      "e.g. Does perceived authenticity of nano-influencers increase purchase intention more than macro-influencers?",
        "method_ex":  "e.g. Online experiment (2×2 design) + PLS-SEM structural model",
        "skills_ex":  "e.g. SmartPLS, survey design, experimental design, R, consumer behaviour",
        "kw_ex":      "e.g. influencer marketing, authenticity, purchase intention, social media",
        "area_default": "Marketing",
    },
    # Supply Chain
    "MSCM": {
        "title_ex":   "e.g. Near-shoring decisions and supply chain resilience post-COVID",
        "rq_ex":      "e.g. Did Swiss manufacturers who near-shored suppliers recover faster from COVID disruptions?",
        "method_ex":  "e.g. Event study + multiple case studies of Swiss manufacturing firms",
        "skills_ex":  "e.g. Supply chain modelling, R, case study methodology, SAP",
        "kw_ex":      "e.g. near-shoring, supply chain resilience, COVID, Swiss manufacturing",
        "area_default": "Supply Chain",
    },
    # Health
    "MHEc": {
        "title_ex":   "e.g. Hospital competition and quality of care in the Swiss DRG system",
        "rq_ex":      "e.g. Does greater hospital market competition reduce readmission rates under Swiss DRG pricing?",
        "method_ex":  "e.g. Panel data regression with HHI instrument, Swiss hospital statistics",
        "skills_ex":  "e.g. Stata, health economics, SwissDRG data, causal inference",
        "kw_ex":      "e.g. hospital competition, DRG, health outcomes, Switzerland",
        "area_default": "Health Services",
    },
    # Default / fallback
    "_default": {
        "title_ex":   "e.g. The impact of X on Y — be as specific as possible",
        "rq_ex":      "e.g. Does X cause Y, and through what mechanism?",
        "method_ex":  "e.g. Quantitative / qualitative / mixed — describe your planned approach",
        "skills_ex":  "e.g. Python, R, Stata, qualitative research, financial modelling",
        "kw_ex":      "e.g. governance, performance, innovation, sustainability",
        "area_default": None,
    },
}

def _ctx(programme: str) -> dict:
    """Get placeholder context for a given programme."""
    for key, ctx in PROGRAMME_CONTEXT.items():
        if key != "_default" and key in programme:
            return ctx
    return PROGRAMME_CONTEXT["_default"]

DEMO_MATCHES = [
    dict(name="Prof. Dr. Michèle Müller-Itten", dept="School of Management",
         focus="Innovation Management · Technology Entrepreneurship · Digital Strategy",
         score=9.4, topic=9, method=9,
         summary="Prof. Müller-Itten's research on corporate innovation and digital transformation maps directly onto your thesis. She regularly supervises empirical and qualitative work on strategy and innovation, and has an open proposal on AI adoption in financial services.",
         strengths=["Digital transformation & innovation expert", "Supervises mixed-method theses", "Open proposal on AI & strategy"],
         flags=[]),
    dict(name="Prof. Dr. Markus Schmid", dept="School of Finance",
         focus="Corporate Governance · Executive Compensation · Empirical Finance",
         score=9.1, topic=9, method=9,
         summary="Your thesis on ESG and cost of debt maps directly onto Prof. Schmid's research on corporate governance and capital structure. He regularly supervises empirical work using Datastream and Compustat, which aligns precisely with your panel regression approach.",
         strengths=["Corporate governance & ESG expert", "Supervises panel data empirical theses", "Open proposal on sustainable finance"],
         flags=[]),
    dict(name="Prof. Dr. Björn Ambos", dept="School of Management",
         focus="International Strategy · HQ–Subsidiary Relations · MNCs",
         score=7.4, topic=7, method=8,
         summary="Prof. Ambos's work on international strategy and cross-country firm data overlaps if your thesis includes a cross-border angle. His empirical approach fits your methods, though the primary topic fit is moderate.",
         strengths=["Strong empirical methods", "Cross-country data experience"],
         flags=["Core focus is int'l management — confirm overlap before reaching out"]),
    dict(name="Prof. Dr. Simone Westerfeld", dept="School of Finance",
         focus="Banking · Financial Intermediation · Regulation",
         score=6.8, topic=6, method=8,
         summary="Prof. Westerfeld's banking research shares methodological ground. If your thesis has a financial sector angle she could supervise the empirical design even if the primary topic is governance.",
         strengths=["Empirical corporate finance methods", "Open to cross-disciplinary work"],
         flags=["Focus is banking/regulation — topic fit is indirect"]),
]

# ── Load real data from backend ─────────────────────────────────────────────
import json as _json, os as _os

def _load_professors():
    """Load from professor_profiles.json and normalise to app format."""
    path = _os.path.join(_os.path.dirname(__file__), "data", "professor_profiles.json")
    try:
        raw = _json.load(open(path))
        result = []
        for name, p in raw.items():
            courses = []
            for c in p.get("courses", []):
                if isinstance(c, dict):
                    courses.append(c.get("title", c.get("name", str(c))))
                else:
                    courses.append(str(c))
            proposals = [t.get("title", t) if isinstance(t, dict) else str(t)
                         for t in p.get("thesis_proposals", [])]
            base_name = p.get("name", name)
            title_str = p.get("title", "")
            # Build display name: include title prefix if not already present
            if title_str and not base_name.startswith(title_str.split()[0]):
                display_name = f"{title_str} {base_name}"
            else:
                display_name = base_name
            dept_raw = p.get("department") or " · ".join(p.get("fields_of_research", [])[:2]) or "HSG Faculty"
            result.append(dict(
                name=display_name,
                dept=dept_raw,
                focus=p.get("main_focuses", []) or p.get("openalex_topics", []),
                h_index=p.get("h_index", 0),
                pubs=p.get("works_count", 0),
                courses=courses[:6],
                proposals=proposals[:5],
                email=p.get("email", ""),
                title=p.get("title", "Prof."),
                profile_url=p.get("profile_url", ""),
                education=p.get("education", ""),
                career=p.get("professional_career", ""),
                publications=p.get("publications", [])[:5],
                openalex_topics=p.get("openalex_topics", []),
            ))
        return result
    except Exception:
        return []

def _load_topics():
    """Load from thesis_topics.json and normalise to app format."""
    path = _os.path.join(_os.path.dirname(__file__), "data", "thesis_topics.json")
    try:
        raw = _json.load(open(path))
        result = []
        for i, t in enumerate(raw[:100]):  # show up to 100
            method = t.get("_raw_planned_method", "")
            fields = []
            if method:
                for kw in ["quantitative", "qualitative", "theoretical", "experimental",
                            "survey", "ML", "machine learning", "econometric"]:
                    if kw.lower() in method.lower():
                        fields.append(kw.capitalize())
            if not fields:
                fields = ["Research"]
            prof_name = t.get("author", "")
            result.append(dict(
                id=t.get("sys_id", f"T-{i:03d}"),
                title=t.get("title", "Untitled"),
                author_label=prof_name or "HSG",
                company=prof_name or "HSG",
                source="professor",
                professor=prof_name,
                type="professor",
                employment="no",
                fields=fields,
                degree=t.get("level", "Master"),
                description=t.get("description", ""),
                method=method,
                contact=t.get("_raw_contact_information", ""),
                url=t.get("url", ""),
                requirements=t.get("requirements", ""),
                match_score=None,
                why_fit=None,
            ))
        return result
    except Exception:
        return []

REAL_PROFESSORS = _load_professors()
REAL_TOPICS     = _load_topics()

# Fallback demo data if files not found
_DEMO_PROFESSORS_FALLBACK = [
    dict(name="Prof. Dr. Michèle Müller-Itten", dept="School of Management",
         focus=["Innovation Management", "Digital Strategy", "Technology Entrepreneurship"],
         h_index=18, pubs=87,
         courses=["Corporate Innovation", "Digital Transformation", "Technology Strategy"],
         proposals=["AI Adoption Strategies in Financial Services", "Corporate Venturing and Innovation Output", "Digital Platform Business Models"],
         email="michele.mueller-itten@unisg.ch", title="Prof. Dr.", profile_url="", career="", education="",
         publications=[
             {"title": "Corporate Innovation Labs: Ambidexterity and Strategic Renewal", "year": 2023, "cited_by_count": 34, "topics": ["Innovation", "Corporate Strategy"]},
             {"title": "Digital Transformation and Firm Performance: A Meta-Analysis", "year": 2022, "cited_by_count": 61, "topics": ["Digital Strategy", "Performance"]},
         ], openalex_topics=["Innovation", "Digital Strategy", "Entrepreneurship"]),
    dict(name="Prof. Dr. Markus Schmid", dept="School of Finance",
         focus=["Corporate Governance", "Executive Compensation", "Empirical Finance"],
         h_index=26, pubs=224, courses=["Corporate Finance", "Empirical Corporate Finance"],
         proposals=["ESG and Cost of Capital", "Board Diversity and Firm Performance"],
         email="markus.schmid@unisg.ch", title="Prof. Dr.", profile_url="", career="", education="", publications=[], openalex_topics=[]),
    dict(name="Prof. Dr. Björn Ambos", dept="School of Management",
         focus=["International Strategy", "HQ–Subsidiary Relations", "Knowledge Transfer"],
         h_index=31, pubs=154, courses=["International Management", "Global Strategy"],
         proposals=["MNC Coordination Mechanisms", "Internationalisation of Swiss SMEs"],
         email="bjoern.ambos@unisg.ch", title="Prof. Ph.D.", profile_url="", career="", education="", publications=[], openalex_topics=[]),
]

PROFESSORS = REAL_PROFESSORS if REAL_PROFESSORS else _DEMO_PROFESSORS_FALLBACK
TOPICS     = REAL_TOPICS if REAL_TOPICS else []

DEMO_COMPANY_TOPICS = [
    dict(id="C-001", title="AI-Powered Demand Forecasting for Retail Supply Chains",
         author_label="McKinsey & Company", company="McKinsey & Company", source="company",
         professor="", employment="internship", fields=["Operations", "Machine learning"],
         degree="Master", match_score=None, why_fit=None,
         description="Develop a machine-learning demand forecasting model for a European retail client. Analyse the gap between statistical baselines and ML-based approaches, and quantify the inventory cost reduction potential.",
         method="Quantitative, ML (Python)", requirements="Python, ML fundamentals, interest in operations",
         contact="thesis@mckinsey.com", url=""),
    dict(id="C-002", title="ESG Rating Divergence and Portfolio Risk in Swiss Institutional Portfolios",
         author_label="UBS Asset Management", company="UBS Asset Management", source="company",
         professor="", employment="internship", fields=["Finance", "Quantitative"],
         degree="Master", match_score=None, why_fit=None,
         description="Analyse divergence between major ESG rating providers (MSCI, Sustainalytics, Bloomberg) and its impact on portfolio construction and risk attribution for Swiss pension funds.",
         method="Quantitative, panel data", requirements="CFA Level 1+, strong Excel/Python",
         contact="student.programs@ubs.com", url=""),
    dict(id="C-003", title="Digital Twin Implementation for Smart Manufacturing: A Readiness Assessment",
         author_label="Siemens AG", company="Siemens AG", source="company",
         professor="", employment="working_student", fields=["Operations", "Quantitative"],
         degree="Master", match_score=None, why_fit=None,
         description="Assess organisational and technological readiness of Swiss mid-size manufacturers for digital twin adoption. Develop a maturity model and pilot roadmap in collaboration with Siemens Smart Infrastructure.",
         method="Mixed methods (survey + case study)", requirements="Interest in Industry 4.0, German advantageous",
         contact="thesis.europe@siemens.com", url=""),
    dict(id="C-004", title="Customer Lifetime Value Modelling in B2B SaaS",
         author_label="Zühlke Engineering", company="Zühlke Engineering", source="company",
         professor="", employment="no", fields=["Marketing", "Quantitative"],
         degree="Bachelor & Master", match_score=None, why_fit=None,
         description="Build a predictive CLV model for a B2B software company using subscription and CRM data. Compare probabilistic (BG/NBD) and ML-based approaches in terms of accuracy and interpretability.",
         method="Quantitative, predictive modelling", requirements="Statistics, R or Python, data access provided",
         contact="research@zuehlke.com", url=""),
    dict(id="C-005", title="Cross-border M&A Value Destruction: Lessons from Swiss Acquirers",
         author_label="Credit Suisse (UBS)", company="Credit Suisse (UBS)", source="company",
         professor="", employment="no", fields=["Finance", "Quantitative"],
         degree="Master", match_score=None, why_fit=None,
         description="Examine long-run stock price performance of Swiss firms that completed cross-border acquisitions (2000–2022). Investigate whether cultural distance, deal size, and payment method predict post-M&A returns.",
         method="Event study, panel regression", requirements="Finance background, Bloomberg/Refinitiv access preferred",
         contact="", url=""),
]

ALL_TOPICS = TOPICS + DEMO_COMPANY_TOPICS

DEMO_MESSAGES = [
    dict(professor="Prof. Dr. Michèle Müller-Itten", avatar="MI",
         last="Thank you for reaching out. Your topic on AI adoption sounds very relevant to my current research.",
         time="1h ago", unread=True),
    dict(professor="Prof. Dr. Markus Schmid", avatar="MS",
         last="Thank you for your application. Could you share a short outline of your research question?",
         time="2h ago", unread=True),
    dict(professor="Prof. Dr. Björn Ambos", avatar="BA",
         last="I'd be happy to discuss your thesis. My office hours are Thursdays 14–16h.",
         time="Yesterday", unread=False),
]

# Pre-seeded conversations (populated into session state on first load)
def _make_demo_conversations():
    return {
        ("Prof. Dr. Michèle Müller-Itten", "Anna Müller"): [],
        ("Prof. Dr. Markus Schmid", "Anna Müller"): [
            {"sender": "student", "text": "Dear Prof. Schmid, I came across your research on corporate governance and ESG and I believe there is strong alignment with my thesis on ESG disclosure quality and the cost of debt. I would be very grateful for the opportunity to discuss potential supervision.", "time": "10:15"},
            {"sender": "professor", "text": "Thank you for your application. Could you share a short outline of your research question and the data sources you plan to use?", "time": "11:02"},
            {"sender": "student", "text": "Of course. My research question is: Does ESG disclosure quality reduce the cost of debt for Swiss listed firms? I plan to use Refinitiv ESG data and Bloomberg bond spreads (2015–2023).", "time": "11:20"},
        ],
        ("Prof. Dr. Björn Ambos", "Anna Müller"): [
            {"sender": "student", "text": "Dear Prof. Ambos, I am interested in the international strategy dimension of my thesis topic. Would you be open to a brief meeting during your office hours?", "time": "Yesterday 14:00"},
            {"sender": "professor", "text": "I'd be happy to discuss your thesis. My office hours are Thursdays 14–16h. You can also propose a different time by email.", "time": "Yesterday 15:30"},
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO SHARED STORE
# @st.cache_resource ensures this is created ONCE per server process and
# reused across all reruns and browser tabs. Without it, the module-level
# dict would reset on every rerun, losing all appended messages.
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def _get_demo_shared():
    return {
        "conversations":        _make_demo_conversations(),
        "confirmed_matches":    set(),
        "student_feedback":     {},
        "officially_registered": set(),
    }

_DEMO_SHARED = _get_demo_shared()

def _reset_demo_shared():
    """Restore all demo shared data to initial state."""
    _DEMO_SHARED["conversations"]        = _make_demo_conversations()
    _DEMO_SHARED["confirmed_matches"]    = set()
    _DEMO_SHARED["student_feedback"]     = {}
    _DEMO_SHARED["officially_registered"] = set()

def _is_demo(uid: str) -> bool:
    """True for demo button logins AND signups when Firebase is not configured."""
    return uid.startswith("demo_")

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def _init_state():
    defaults = dict(
        page="Home",
        # ── Auth ───────────────────────────────────────────────────────────────
        # firebase_user: None when logged out, else {"uid", "email", "token"}
        firebase_user=None,
        auth_tab="login",      # "login" | "signup"
        auth_error="",
        signup_step=1,         # 1 = credentials+role, 2 = profile details
        signup_role=None,      # "student" | "professor" — chosen at step 1
        signup_email="",
        signup_password="",
        # ── Role (set from Firebase profile after login, not a toggle) ─────────
        role="student",        # "student" | "professor"
        # ── Student profile ────────────────────────────────────────────────────
        first_name="", last_name="", email="",
        level="Master", programme="Master in Banking and Finance (MBF)",
        semester="1st semester", language="English",
        transcript_parsed=None, cv_parsed=None,
        profile_complete=False, missing_fields=[],
        # ── Professor profile ──────────────────────────────────────────────────
        prof_name="", prof_title="Prof. Dr.",
        prof_dept="",
        prof_email="",
        prof_uploaded_docs=[{
            "professor_name": "Prof. Dr. Michèle Müller-Itten",
            "document_name": "Innovation Management Course Syllabus.pdf",
            "document_type": "course_material",
            "thesis_proposals": [
                {"title": "AI Adoption Strategies in Financial Services", "description": "Examine how incumbent banks and insurers adopt AI across their value chain — from risk to customer service. Compare early movers vs late adopters.", "level": "Master", "methodology": "Mixed methods: survey + case studies", "requirements": "Interest in fintech/AI, basic statistics"},
                {"title": "Corporate Venturing and Innovation Output", "description": "Study how corporate venture capital investments affect parent company innovation metrics (patents, new products) using panel data.", "level": "Master", "methodology": "Panel regression, event study", "requirements": "Econometrics, Python or R"},
            ],
            "faq_entries": [
                {"question": "What thesis topics do you supervise?", "answer": "I focus on corporate innovation, digital transformation, and technology entrepreneurship. I supervise both qualitative and quantitative theses."},
                {"question": "What is your preferred methodology?", "answer": "I am open to mixed methods. Quantitative work should use rigorous econometric designs; qualitative work should follow structured case study methodology."},
                {"question": "How many theses do you supervise per year?", "answer": "Typically 4–6 Master theses per academic year. I have slots available for the next cohort."},
            ],
            "requirements": ["Strong motivation letter", "1-page thesis outline", "Transcript attached"],
            "key_topics": ["Innovation Management", "Digital Transformation", "AI Strategy", "Corporate Venturing"],
            "courses": ["Corporate Innovation", "Digital Transformation"],
            "summary": "Course syllabus for Corporate Innovation — extracted thesis proposals, FAQ entries, and supervision requirements.",
            "raw_insights": "Prof. Müller-Itten expects a 1-page outline before the first meeting. She prefers students who have taken Corporate Innovation or a related course. Usually responds within 2–3 days.",
        }],
        prof_faq_bank=[
            {"question": "What thesis topics do you supervise?", "answer": "Corporate innovation, digital transformation, and technology entrepreneurship. Open to quantitative and qualitative approaches."},
            {"question": "What is your preferred methodology?", "answer": "Open to mixed methods — rigorous econometrics for quant, structured case studies for qual."},
            {"question": "How many theses do you supervise?", "answer": "4–6 Master theses per academic year. Slots available for next cohort."},
        ],
        # Per-professor AI chat histories (student ↔ professor AI)
        # keyed by professor name: list of {role, content}
        prof_ai_chats={},
        active_prof_ai_chat=None,  # professor name for current AI chat
        # Professor-side inbox (separate from student messages)
        prof_active_chat=None,     # active student conversation (prof view)
        # Matching wizard state
        match_step=0,
        thesis_title="", research_area="Finance/Banking",
        research_question="", motivation="", approach="",
        relevant_courses="", skills="", keywords="", additional_notes="",
        match_results=None,
        # Topic browse
        selected_topic=None,
        topic_filter_field="All fields",
        topic_filter_degree="All",
        topic_search="",
        topic_favourites=set(),
        topic_recs=None,
        topic_recs_loading=False,
        topic_ai_generated=None,
        topic_ai_loading=False,
        # Professor browse
        selected_prof=None,
        prof_search="",
        # Shared conversations (live, both roles write to this)
        conversations={},
        confirmed_matches=set(),  # set of (prof_name, student_name)
        student_feedback={},      # {(prof_name, student_name): {"rating": int, "text": str}}
        feedback_target=None,     # conv_key being reviewed
        officially_registered=set(),  # set of conv_keys where student confirmed registration
        # Messages
        active_chat=None,
        chat_input="",
        # AI agents
        thesis_ideas=None,
        thesis_ideas_loading=False,
        email_drafts={},      # keyed by professor name
        ai_chat_history=[],   # list of {role, content}
        ai_chat_input="",
        thesis_submission_date=None,
        thesis_tasks=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
            

_init_state()
s = st.session_state

# ─────────────────────────────────────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _apply_profile_to_state(profile: dict) -> None:
    """
    After login, copy the Firebase profile dict into session state.
    Works for both student and professor profiles.
    """
    if not profile:
        return
    ss = st.session_state
    ss.role = profile.get("role", "student")
    # Student fields
    ss.first_name = profile.get("first_name", "")
    ss.last_name  = profile.get("last_name",  "")
    ss.email      = profile.get("email",      "")
    ss.level      = profile.get("level",      "Master")
    ss.programme  = profile.get("programme",  "Master in Banking and Finance (MBF)")
    ss.semester   = profile.get("semester",   "1st semester")
    ss.language   = profile.get("language",   "English")
    # Professor fields
    ss.prof_name  = profile.get("prof_name",  "")
    ss.prof_title = profile.get("prof_title", "Prof. Dr.")
    ss.prof_dept  = profile.get("prof_dept",  "")
    ss.prof_email = profile.get("prof_email", "")
    # Demo conversations are handled by _DEMO_SHARED — not here


def _build_save_profile() -> dict:
    """Collect current session state into a dict to save to Firebase."""
    ss = st.session_state
    return {
        "role":       ss.role,
        "first_name": ss.first_name,
        "last_name":  ss.last_name,
        "email":      ss.email,
        "level":      ss.level,
        "programme":  ss.programme,
        "semester":   ss.semester,
        "language":   ss.language,
        "prof_name":  ss.prof_name,
        "prof_title": ss.prof_title,
        "prof_dept":  ss.prof_dept,
        "prof_email": ss.prof_email,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AUTH  (login / signup — shown before everything else when logged out)
# ─────────────────────────────────────────────────────────────────────────────

def page_auth():
    st.markdown("""
    <style>
    .block-container { max-width:420px !important; margin:0 auto !important; padding-top:5rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:2.5rem">
      <div style="font-size:1.8rem;font-weight:700;color:#111827;letter-spacing:-0.02em">Thesis Match</div>
      <div style="font-size:0.9rem;color:#6B7280;margin-top:4px">HSG · Beta</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Choose your account")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Student Demo\nAnna Müller", use_container_width=True, type="primary", key="btn_demo_student"):
            _enter_demo_student()
            st.rerun()
    with col2:
        if st.button("Professor Demo\nProf. Dr. Müller-Itten", use_container_width=True, key="btn_demo_prof"):
            _enter_demo_professor()
            st.rerun()


# ── Signup helpers kept as stubs (no longer called) ─────────────────────────

def _finish_signup_student(**kwargs):
    pass

def _finish_signup_professor(**kwargs):
    pass


# ── Demo mode helpers ────────────────────────────────────────────────────────

def _enter_demo_student():
    """Log in as the demo student (Anna Müller) without Firebase."""
    profile = {
        "role": "student",
        "first_name": "Anna", "last_name": "Müller",
        "email": "anna.mueller@student.unisg.ch",
        "level": "Master", "programme": "Master in Banking and Finance (MBF)",
        "semester": "2nd semester", "language": "English",
        "prof_name": "", "prof_title": "", "prof_dept": "", "prof_email": "",
    }
    st.session_state.firebase_user = {"uid": "demo_student", "email": profile["email"], "token": ""}
    _apply_profile_to_state(profile)
    # Point at the shared store so both demo sessions share data
    st.session_state.conversations       = _DEMO_SHARED["conversations"]
    st.session_state.confirmed_matches   = _DEMO_SHARED["confirmed_matches"]
    st.session_state.student_feedback    = _DEMO_SHARED["student_feedback"]
    st.session_state.officially_registered = _DEMO_SHARED["officially_registered"]
    st.session_state.page = "Home"


def _enter_demo_professor():
    """Log in as the demo professor (Prof. Dr. Michèle Müller-Itten) without Firebase."""
    profile = {
        "role": "professor",
        "first_name": "", "last_name": "", "email": "michele.mueller-itten@unisg.ch",
        "level": "", "programme": "", "semester": "", "language": "",
        "prof_name":  "Michèle Müller-Itten",
        "prof_title": "Prof. Dr.",
        "prof_dept":  "School of Management",
        "prof_email": "michele.mueller-itten@unisg.ch",
    }
    st.session_state.firebase_user = {"uid": "demo_prof", "email": profile["email"], "token": ""}
    _apply_profile_to_state(profile)
    # Point at the shared store so both demo sessions share data
    st.session_state.conversations       = _DEMO_SHARED["conversations"]
    st.session_state.confirmed_matches   = _DEMO_SHARED["confirmed_matches"]
    st.session_state.student_feedback    = _DEMO_SHARED["student_feedback"]
    st.session_state.officially_registered = _DEMO_SHARED["officially_registered"]
    st.session_state.page = "Home"


# ─────────────────────────────────────────────────────────────────────────────
# Compute missing profile fields
def _missing():
    out = []
    if not st.session_state.get("transcript_parsed"):
        out.append("Grade transcript")
    if not st.session_state.get("cv_parsed"):
        out.append("CV / résumé")
    if not st.session_state.get("thesis_title"):
        out.append("Thesis title")
    return out

missing = _missing()

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────

# CSS variables only — referenced by inline styles in page functions
st.markdown("""
<style>
:root {
  --g:    #009640;
  --gd:   #006B2B;
  --gl:   #E8F5EC;
  --gm:   #C6E8D0;
  --gp:   #F4FAF6;
  --txt:  #111827;
  --sub:  #374151;
  --mut:  #6B7280;
  --bdr:  #E5E7EB;
  --bg:   #F9FAFB;
  --wh:   #FFFFFF;
  --warn: #FEF3C7;
  --wt:   #92400E;
}
.sec-head { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:var(--mut); margin:1.4rem 0 0.6rem; padding-bottom:0.4rem; border-bottom:1px solid var(--bdr); }
.tag { display:inline-block; padding:2px 9px; border-radius:2px; font-size:0.73rem; font-weight:500; margin:2px 2px 2px 0; }
.tg  { background:var(--gm); color:var(--gd); }
.tw  { background:var(--warn); color:var(--wt); }
.tb  { background:#EFF6FF; color:#1D4ED8; }
.tgr { background:#F3F4F6; color:#4B5563; }
.why { background:var(--gl); border-left:3px solid var(--g); padding:0.7rem 0.9rem; margin:0.8rem 0 0.6rem; font-size:0.85rem; color:#14532D; line-height:1.6; }
.why-lbl { font-size:0.67rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--gd); margin-bottom:4px; }
.sbar { display:flex; align-items:center; gap:8px; font-size:0.78rem; color:var(--mut); margin:3px 0; }
.sbar-bg { flex:1; height:4px; background:var(--bdr); overflow:hidden; }
.sbar-fill { height:100%; background:var(--g); }
.notif { background:var(--warn); border:1px solid #FCD34D; padding:0.65rem 0.9rem; margin-bottom:1rem; font-size:0.83rem; color:var(--wt); line-height:1.5; }
.notif strong { font-weight:600; }
.status-pill { display:inline-block; padding:3px 10px; font-size:0.73rem; font-weight:600; }
.pill-green { background:var(--gl); color:var(--gd); }
.pill-warn  { background:var(--warn); color:var(--wt); }
.dots { display:flex; gap:6px; margin-bottom:1.2rem; }
.dot  { width:8px; height:8px; background:var(--bdr); }
.dot.done   { background:var(--g); }
.dot.active { background:var(--g); opacity:0.5; width:22px; }
.list-item { padding:0.8rem 1rem; border-bottom:1px solid var(--bdr); cursor:pointer; font-size:0.87rem; }
.list-item.active { background:var(--gl); border-left:3px solid var(--g); }
.list-title { font-weight:600; color:var(--txt); font-size:0.88rem; }
.list-meta  { font-size:0.75rem; color:var(--mut); margin-top:2px; }
.detail-name { font-size:1.15rem; font-weight:700; color:var(--txt); }
.detail-sub  { font-size:0.82rem; color:var(--mut); margin-top:2px; }
.msg-row { display:flex; gap:8px; margin-bottom:10px; align-items:flex-start; }
.msg-av  { width:30px; height:30px; background:var(--gm); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.72rem; color:var(--gd); flex-shrink:0; }
.bubble  { background:var(--bg); border:1px solid var(--bdr); padding:0.55rem 0.8rem; font-size:0.85rem; color:var(--txt); max-width:82%; min-width:2.5rem; line-height:1.5; word-break:break-word; white-space:pre-wrap; }
.bubble.mine { background:var(--gl); border-color:var(--gm); }
.msg-t   { font-size:0.68rem; color:var(--mut); margin-top:2px; }
.topbar { padding:0 0 1rem; margin-bottom:1.2rem; border-bottom:1px solid var(--bdr); }
@keyframes ai-pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.7;transform:scale(1.06)} }
@keyframes ai-dots { 0%{content:'.'} 33%{content:'..'} 66%{content:'...'} 100%{content:'.'} }
.ai-running-banner {
  display:flex; align-items:center; gap:12px;
  background:#FFF0F0; border:1.5px solid #F87171;
  padding:0.75rem 1.1rem; margin-bottom:1rem;
  animation: ai-pulse 1.4s ease-in-out infinite;
}
.ai-running-banner .ai-bug {
  font-size:1.6rem; line-height:1;
}
.ai-running-banner .ai-text {
  font-size:0.88rem; font-weight:600; color:#B91C1C;
}
.element-container:has(.list-item) + .element-container > div > div > button,
.element-container:has(.list-item) + .element-container .stButton > button { display:none !important; }
.element-container:has(.topic-card) + .element-container + .element-container > div > div > button,
.element-container:has(.topic-card) + .element-container + .element-container .stButton > button { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH GATE
# ─────────────────────────────────────────────────────────────────────────────
if not s.firebase_user:
    page_auth()
    st.stop()

# ── Demo sync ────────────────────────────────────────────────────────────────
if s.firebase_user and _is_demo(s.firebase_user.get("uid", "")):
    s.conversations         = _DEMO_SHARED["conversations"]
    s.confirmed_matches     = _DEMO_SHARED["confirmed_matches"]
    s.student_feedback      = _DEMO_SHARED["student_feedback"]
    s.officially_registered = _DEMO_SHARED["officially_registered"]

# ─────────────────────────────────────────────────────────────────────────────
# JS — clickable list-item cards + sticky topics panel
# ─────────────────────────────────────────────────────────────────────────────
import streamlit.components.v1 as _components
_components.html("""
<script>
(function(){
  var doc = window.parent.document;
  function findElementContainer(el) {
    var node = el;
    while (node && !(node.classList && node.classList.contains('element-container'))) {
      node = node.parentElement;
    }
    return node;
  }
  function setup() {
    doc.querySelectorAll('.list-item:not([data-cb])').forEach(function(card) {
      card.setAttribute('data-cb', '1');
      card.style.cursor = 'pointer';
      card.addEventListener('click', function(e) {
        var ec = findElementContainer(this);
        if (!ec) return;
        var isTopic = this.classList.contains('topic-card');
        if (isTopic) {
          var rect = this.getBoundingClientRect();
          var inStar = (e.clientX - rect.left) > (rect.width - 48) && (e.clientY - rect.top) < 48;
          if (inStar) {
            var next2 = ec.nextElementSibling && ec.nextElementSibling.nextElementSibling;
            var starBtn = next2 && next2.querySelector('button');
            if (starBtn) { e.stopPropagation(); starBtn.click(); return; }
          }
          var next1 = ec.nextElementSibling;
          var selBtn = next1 && next1.querySelector('button');
          if (selBtn) selBtn.click();
        } else {
          var next = ec.nextElementSibling;
          var btn = next && next.querySelector('button');
          if (btn) btn.click();
        }
      });
    });
    var marker = doc.querySelector('.topics-layout-marker');
    if (marker && !marker.getAttribute('data-sticky')) {
      var ec = findElementContainer(marker);
      var sib = ec && ec.nextElementSibling;
      for (var i = 0; i < 8 && sib; i++) {
        var hb = sib.querySelector('[data-testid="stHorizontalBlock"]');
        if (hb) {
          hb.style.alignItems = 'flex-start';
          var cols = hb.querySelectorAll('[data-testid="stColumn"]');
          if (cols.length >= 2) {
            cols[0].style.overflowY = 'auto';
            cols[0].style.maxHeight = 'calc(100vh - 130px)';
            cols[1].style.position = 'sticky';
            cols[1].style.top = '0';
            cols[1].style.maxHeight = 'calc(100vh - 130px)';
            cols[1].style.overflowY = 'auto';
            marker.setAttribute('data-sticky', '1');
          }
          break;
        }
        sib = sib.nextElementSibling;
      }
    }
  }
  setup();
  new MutationObserver(setup).observe(doc.body, {childList: true, subtree: true});
})();
</script>
""", height=0, scrolling=False)




import contextlib

@contextlib.contextmanager
def ai_spinner(label: str):
    """Drop-in replacement for st.spinner that also shows the red bug banner."""
    st.markdown(f"""
    <div class="ai-running-banner">
      <span class="ai-bug">🪲</span>
      <span class="ai-text">AI is working — {label}</span>
    </div>""", unsafe_allow_html=True)
    with st.spinner(label):
        yield


def topbar(title, subtitle="", back=False):
    sub_html = f'<span style="font-size:0.82rem;color:var(--mut);margin-left:10px">{subtitle}</span>' if subtitle else ""
    # Show back button on every page except the dashboard itself
    is_home = (title == "Dashboard" or title == "Professor Dashboard")
    if not is_home:
        col_back, col_title = st.columns([1, 8])
        with col_back:
            if st.button("← Home", key=f"topbar_home_{title.replace(' ','_')}"):
                st.session_state["_nav_target"] = "Home"; st.rerun()
        with col_title:
            st.markdown(f"""
            <div class="topbar">
              <div style="display:flex;align-items:center">
                <span style="font-size:1.1rem;font-weight:700;color:var(--txt)">{title}</span>
                {sub_html}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="topbar">
          <div style="display:flex;align-items:center">
            <span style="font-size:1.1rem;font-weight:700;color:var(--txt)">{title}</span>
            {sub_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

def tag(label, cls="tg"):
    return f'<span class="tag {cls}">{label}</span>'


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────────────────────

def page_home():
    topbar("Dashboard")

    # ── Welcome banner ────────────────────────────────────────────────────────
    step_label = "Topic chosen" if s.thesis_title else "Not started"
    step_pct   = 30 if s.thesis_title else 5
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#006B2B,#009640);
                padding:1.2rem 1.5rem;color:white;margin-bottom:0.7rem">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.08em;opacity:0.7;margin-bottom:4px">Thesis Journey</div>
      <div style="font-size:1.1rem;font-weight:700;margin-bottom:7px">
        {"Good morning, "+s.first_name if s.first_name else "Welcome"}
      </div>
      <div style="font-size:0.82rem;opacity:0.85;margin-bottom:10px">
        {f"Your thesis: <strong>{s.thesis_title}</strong>" if s.thesis_title else "You haven't set a thesis topic yet. Use <strong>Find Supervisor</strong> to get started."}
      </div>
      <div style="background:rgba(255,255,255,0.2);height:4px;margin-bottom:5px">
        <div style="background:white;width:{step_pct}%;height:100%"></div>
      </div>
      <div style="font-size:0.7rem;opacity:0.6">Status: {step_label} · Next: Find a supervisor</div>
    </div>
    """, unsafe_allow_html=True)

    if missing:
        items = ", ".join(missing)
        st.markdown(f"""
        <div class="notif" style="margin-top:0;margin-bottom:1.2rem">
          <strong>Complete your profile</strong> to improve match quality —
          missing: <strong>{items}</strong>.
        </div>
        """, unsafe_allow_html=True)

    # ── Thesis Timeline embedded directly on dashboard ────────────────────────
    st.markdown('<div class="sec-head" style="margin-top:1rem">📅 Thesis Timeline</div>', unsafe_allow_html=True)
    page_thesis_project(embedded=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FIND SUPERVISOR  (multi-step)
# ─────────────────────────────────────────────────────────────────────────────

MATCH_STEPS = ["Thesis", "Approach", "Skills", "Results"]

def _step_dots(step):
    html = '<div class="dots">'
    for i in range(len(MATCH_STEPS)):
        cls = "done" if i < step else ("active" if i == step else "dot")
        if i < step:
            html += f'<div class="dot done" title="{MATCH_STEPS[i]}"></div>'
        elif i == step:
            html += f'<div class="dot active"></div>'
        else:
            html += f'<div class="dot"></div>'
    html += f'<span style="font-size:0.75rem;color:var(--mut);margin-left:6px">{MATCH_STEPS[min(step,len(MATCH_STEPS)-1)]}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

def page_match():
    topbar("Find Supervisor", "AI-powered matching")

    ctx = _ctx(s.programme)

    # If we have results, show them
    if s.match_results is not None:
        _show_results(ctx)
        return

    step = s.match_step

    # Pre-fill research_area from programme context
    if not s.thesis_title and ctx.get("area_default") and not s.research_area:
        s.research_area = ctx["area_default"]

    _step_dots(step)

    # ── Step 0: Thesis ────────────────────────────────────────────
    if step == 0:
        st.markdown('<div style="font-size:1.1rem;font-weight:700;color:var(--txt);margin-bottom:4px">Tell us about your thesis</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.83rem;color:var(--mut);margin-bottom:1.2rem">The more specific you are, the better the match. Use the suggestions below if you need inspiration.</div>', unsafe_allow_html=True)

        s.thesis_title = st.text_input(
            "Working title or topic *",
            value=s.thesis_title,
            placeholder=ctx["title_ex"],
        )

        area_idx = RESEARCH_AREAS.index(s.research_area) if s.research_area in RESEARCH_AREAS else 0
        s.research_area = st.selectbox("Research area *", RESEARCH_AREAS, index=area_idx)

        s.research_question = st.text_area(
            "Research question(s) *",
            value=s.research_question,
            height=90,
            placeholder=ctx["rq_ex"],
        )
        s.motivation = st.text_area(
            "Motivation",
            value=s.motivation,
            height=75,
            placeholder=f"Why does this topic matter to you? e.g. 'Having worked at a bank, I noticed that ESG ratings rarely reflected actual governance quality…'",
        )

        # Dynamic suggestions chips
        area = s.research_area
        suggestions = _title_suggestions(area)
        if suggestions:
            st.markdown('<div style="font-size:0.75rem;color:var(--mut);margin-top:0.5rem;margin-bottom:4px">Topic ideas for <strong>' + area + '</strong>:</div>', unsafe_allow_html=True)
            chips_html = "".join(f'<span class="tag tgr" style="cursor:pointer" title="Click to copy">{s2}</span>' for s2 in suggestions[:5])
            st.markdown(chips_html, unsafe_allow_html=True)

        # ── AI Thesis Idea Generator ──────────────────────────────
        st.markdown('<div class="sec-head" style="margin-top:1.4rem">Not sure what to write about?</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem;color:var(--mut);margin-bottom:0.7rem">Describe your interests below and the AI will generate 5 concrete thesis ideas tailored to your programme.</div>', unsafe_allow_html=True)

        gen_interests = st.text_area(
            "Your interests / background (free text)",
            height=65,
            placeholder="e.g. I interned at a hedge fund and am interested in how ESG ratings affect stock returns. I know Python and have taken Econometrics.",
            key="gen_interests_input",
        )
        if st.button("Generate thesis ideas with AI", key="gen_ideas_btn"):
            if not gen_interests.strip():
                st.error("Please describe your interests first.")
            else:
                with ai_spinner("Generating ideas…"):
                    try:
                        from src.agents.thesis_generator import generate_thesis_ideas
                        s.thesis_ideas = generate_thesis_ideas(
                            programme=s.programme or "Master",
                            research_area=s.research_area or area,
                            interests=gen_interests,
                            skills=s.skills or "",
                            level=s.level or "Master",
                        )
                    except Exception as e:
                        st.error(f"Could not generate ideas: {e}")

        if s.thesis_ideas:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            for idx, idea in enumerate(s.thesis_ideas, 1):
                diff_cls = {"standard": "tg", "challenging": "tw", "ambitious": "tb"}.get(idea.get("difficulty",""), "tgr")
                with st.expander(f"Idea {idx} — {idea['title']}", expanded=(idx == 1)):
                    st.markdown(f"""
                    <div style="font-size:0.82rem;color:var(--mut);margin-bottom:8px">{idea.get('why_fit','')}</div>
                    <div style="font-size:0.86rem;margin-bottom:6px"><strong>Research question:</strong> {idea['research_question']}</div>
                    <div style="font-size:0.86rem;margin-bottom:8px"><strong>Methodology:</strong> {idea['methodology']}</div>
                    <div>{"".join(f'<span class="tag tgr">{k}</span>' for k in idea.get("keywords",[]))}&nbsp;<span class="tag {diff_cls}">{idea.get('difficulty','')}</span></div>
                    """, unsafe_allow_html=True)
                    if st.button("Use this idea", key=f"use_idea_{idx}"):
                        s.thesis_title = idea["title"]
                        s.research_question = idea["research_question"]
                        s.approach = idea["methodology"]
                        s.keywords = ", ".join(idea.get("keywords", []))
                        s.thesis_ideas = None
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_next, col_no_topic = st.columns([2, 3])
        with col_next:
            if st.button("Next →", type="primary", key="step0_next"):
                if not s.thesis_title or not s.research_question:
                    st.error("Working title and research question are required.")
                else:
                    s.match_step = 1; st.rerun()
        with col_no_topic:
            st.markdown("<div style='padding-top:0.35rem'></div>", unsafe_allow_html=True)
            if st.button("I don't have a thesis subject yet →", key="no_topic_btn"):
                st.session_state["_nav_target"] = "Thesis Topics"; st.rerun()

    # ── Step 1: Approach ──────────────────────────────────────────
    elif step == 1:
        st.markdown('<div style="font-size:1.1rem;font-weight:700;margin-bottom:4px">Your approach</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.83rem;color:var(--mut);margin-bottom:1.2rem">This helps us match professors who supervise your type of research.</div>', unsafe_allow_html=True)

        s.approach = st.text_area(
            "Planned methodology *",
            value=s.approach,
            height=90,
            placeholder=ctx["method_ex"],
        )
        s.relevant_courses = st.text_input(
            "Courses that prepared you for this research",
            value=s.relevant_courses,
            placeholder="e.g. Econometrics, Corporate Finance, Game Theory, Qualitative Research Methods",
        )
        s.additional_notes = st.text_area(
            "Anything else? (supervisor preferences, co-supervision interest, timeline, etc.)",
            value=s.additional_notes,
            height=70,
            placeholder="Optional — e.g. 'I'd prefer a supervisor open to industry co-supervision' or 'I plan to start in September 2025'",
        )

        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", key="step1_back"):
            s.match_step = 0; st.rerun()
        if c2.button("Next →", type="primary", key="step1_next"):
            if not s.approach:
                st.error("Please describe your methodology.")
            else:
                s.match_step = 2; st.rerun()

    # ── Step 2: Skills ────────────────────────────────────────────
    elif step == 2:
        st.markdown('<div style="font-size:1.1rem;font-weight:700;margin-bottom:4px">Skills & keywords</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.83rem;color:var(--mut);margin-bottom:1.2rem">Used to fine-tune the match — a supervisor who works with your tools is a stronger fit.</div>', unsafe_allow_html=True)

        s.skills = st.text_input(
            "Your key skills (comma-separated)",
            value=s.skills,
            placeholder=ctx["skills_ex"],
        )
        s.keywords = st.text_input(
            "3–5 keywords for your thesis topic",
            value=s.keywords,
            placeholder=ctx["kw_ex"],
        )

        # Upload documents (optional, enrich matching)
        st.markdown('<div class="sec-head">Enrich your profile (optional)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem;color:var(--mut);margin-bottom:0.7rem">Upload your transcript and CV to improve match quality. We extract your strongest courses and skills automatically.</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            transcript_status = "✓ Uploaded" if st.session_state.get("transcript_parsed") else "Not uploaded"
            t_color = "var(--g)" if st.session_state.get("transcript_parsed") else "var(--mut)"
            st.markdown(f'<div style="font-size:0.78rem;margin-bottom:4px">Grade transcript &nbsp;<span style="color:{t_color};font-weight:600">{transcript_status}</span></div>', unsafe_allow_html=True)
            transcript_file = st.file_uploader("Upload transcript PDF", type=["pdf"], key="transcript_up", label_visibility="collapsed")
            if transcript_file:
                with ai_spinner("Scanning transcript…"):
                    try:
                        from src.data_collection.student_parsers.transcript_parser import parse_transcript
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                            tmp.write(transcript_file.read()); tmp_path = tmp.name
                        st.session_state["transcript_parsed"] = parse_transcript(tmp_path)
                        os.unlink(tmp_path)
                        st.success(f"✓ {len(st.session_state['transcript_parsed'].courses)} courses loaded")
                    except Exception as e:
                        st.warning(f"Could not parse transcript: {e}")

        with col_b:
            cv_status = "✓ Uploaded" if st.session_state.get("cv_parsed") else "Not uploaded"
            cv_color = "var(--g)" if st.session_state.get("cv_parsed") else "var(--mut)"
            st.markdown(f'<div style="font-size:0.78rem;margin-bottom:4px">CV / résumé &nbsp;<span style="color:{cv_color};font-weight:600">{cv_status}</span></div>', unsafe_allow_html=True)
            cv_file = st.file_uploader("Upload CV PDF", type=["pdf"], key="cv_up", label_visibility="collapsed")
            if cv_file:
                with ai_spinner("Scanning CV…"):
                    try:
                        from src.data_collection.student_parsers.cv_parser import parse_cv
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                            tmp.write(cv_file.read()); tmp_path = tmp.name
                        st.session_state["cv_parsed"] = parse_cv(tmp_path)
                        os.unlink(tmp_path)
                        st.success(f"✓ {len(st.session_state['cv_parsed'].experience)} experience entries loaded")
                    except Exception as e:
                        st.warning(f"Could not parse CV: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", key="step2_back"):
            s.match_step = 1; st.rerun()
        if c2.button("Find my supervisor →", type="primary", key="step2_run"):
            s.match_step = 3
            with ai_spinner("Running semantic search + AI analysis… (20–30 sec)"):
                s.match_results = _run_matching()
            st.rerun()

    # ── Reset ─────────────────────────────────────────────────────
    if step > 0:
        st.markdown("<br>", unsafe_allow_html=True)


def _title_suggestions(area: str) -> list:
    sug = {
        "Finance/Banking": [
            "ESG ratings and cost of debt",
            "Momentum strategies and transaction costs",
            "CEO pay and firm performance",
            "Bank capital requirements and lending",
            "Fintech adoption and financial inclusion",
        ],
        "Economics": [
            "Trade liberalisation and wage inequality",
            "Minimum wage and employment elasticity",
            "Political economy of fiscal consolidation",
            "Immigration and housing prices",
            "Automation and labour market polarisation",
        ],
        "Strategic Management": [
            "Digital transformation in family firms",
            "Corporate diversification and firm value",
            "Alliance portfolio diversity and innovation",
            "CEO succession and strategic change",
            "Platform competition and network effects",
        ],
        "Marketing": [
            "Influencer authenticity and purchase intent",
            "Personalisation and customer trust",
            "Brand activism and consumer response",
            "Subscription models and churn prediction",
            "Social commerce and Gen Z behaviour",
        ],
        "Sustainability": [
            "Carbon pricing and corporate capex decisions",
            "Greenwashing detection in annual reports",
            "Supply chain transparency and CSR",
            "ESG integration in institutional portfolios",
            "Climate risk and real estate valuations",
        ],
        "Data Analytics": [
            "NLP for earnings call sentiment analysis",
            "Causal ML for policy evaluation",
            "Federated learning in financial services",
            "Graph neural networks for fraud detection",
            "LLM-assisted systematic literature review",
        ],
        "Accounting": [
            "Earnings management around IFRS 16 adoption",
            "Audit quality and accrual manipulation",
            "Fair value accounting and volatility",
            "Tax avoidance and firm valuation",
            "Non-GAAP disclosures and investor reactions",
        ],
        "Human Resources Management": [
            "Remote work and psychological safety",
            "DEI initiatives and firm performance",
            "Algorithmic HR and employee trust",
            "Gig economy and wellbeing outcomes",
            "Feedback frequency and employee retention",
        ],
    }
    return sug.get(area, [])


def _run_matching() -> list:
    """Try real pipeline; fall back to demo data."""
    try:
        from src.data_collection.questionnaire import _build_description
        from src.models.student import StudentProfile
        from src.data_collection.scrapers.constants import RESEARCH_AREA_TO_FIELD_IDS
        from src.data_processing.profile_builder import ProfileStore
        from src.matching.matcher import ThesisMatcher

        desc = _build_description(
            research_question=s.research_question,
            motivation=s.motivation,
            approach=s.approach,
            relevant_courses=s.relevant_courses,
            references="",
            data_strategy="",
        )
        profile = StudentProfile(
            first_name=s.first_name, last_name=s.last_name, email=s.email,
            level=s.level, programme=s.programme,
            research_area=s.research_area,
            thesis_title=s.thesis_title,
            thesis_description=desc,
            skills=[x.strip() for x in s.skills.split(",") if x.strip()],
            keywords=[x.strip() for x in s.keywords.split(",") if x.strip()],
            objectives=[], field_ids=RESEARCH_AREA_TO_FIELD_IDS.get(s.research_area, []),
        )
        # Attach uploads
        if st.session_state.get("transcript_parsed"):
            profile.transcript = st.session_state["transcript_parsed"]
        if st.session_state.get("cv_parsed"):
            profile.cv = st.session_state["cv_parsed"]

        store = ProfileStore()
        raw = ThesisMatcher(store).match(profile, embed_top_k=20, final_top_k=5)
        return [
            dict(
                name=r.professor.name,
                dept=r.professor.fields_of_research[0] if r.professor.fields_of_research else "",
                focus=", ".join(r.professor.main_focuses[:3]),
                score=r.claude_score or round(r.embedding_score * 10, 1),
                topic=r.topic_fit or 5,
                method=r.methodology_fit or 5,
                summary=r.summary or "",
                strengths=r.strengths,
                flags=r.red_flags,
            )
            for r in raw
        ]
    except Exception as e:
        import traceback; traceback.print_exc()
        st.warning(f"[Matching error — falling back to demo] {e}")
        return DEMO_MATCHES


def _show_results(ctx):
    results = s.match_results

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem">
      <div style="font-size:1.05rem;font-weight:700;color:var(--txt)">
        Top {len(results)} matches for your thesis
      </div>
      <span class="status-pill pill-green">{len(results)} supervisors</span>
    </div>
    <div style="font-size:0.82rem;color:var(--mut);margin-bottom:1.3rem">
      Based on: <strong>{s.thesis_title or 'your thesis'}</strong> · {s.research_area}
      {"· <em>transcript used</em>" if st.session_state.get("transcript_parsed") else ""}
      {"· <em>CV used</em>" if st.session_state.get("cv_parsed") else ""}
    </div>
    """, unsafe_allow_html=True)

    for i, r in enumerate(results, 1):
        tp  = int(r.get("topic", 5) * 10)
        mp  = int(r.get("method", 5) * 10)
        s_html = "".join(f'<span class="tag tg">✓ {st2}</span>' for st2 in r.get("strengths", []))
        f_html = "".join(f'<span class="tag tw">⚠ {f}</span>' for f in r.get("flags", []))

        with st.expander(f"#{i}  {r['name']}  ·  {r.get('score', '—')}/10", expanded=(i == 1)):
            st.markdown(f"""
            <div style="font-size:0.8rem;color:var(--mut);margin-bottom:10px">{r.get('focus','')}</div>

            <div class="sbar"><span style="width:100px">Topic fit</span>
              <div class="sbar-bg"><div class="sbar-fill" style="width:{tp}%"></div></div>
              <span style="width:20px;text-align:right">{r.get("topic",5)}</span></div>
            <div class="sbar"><span style="width:100px">Method fit</span>
              <div class="sbar-bg"><div class="sbar-fill" style="width:{mp}%"></div></div>
              <span style="width:20px;text-align:right">{r.get("method",5)}</span></div>

            <div class="why">
              <div class="why-lbl">Why this supervisor?</div>
              {r.get("summary","")}
            </div>
            <div style="margin-top:6px">{s_html}{f_html}</div>
            """, unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns([1, 1, 1])
            if col_a.button("View profile", key=f"view_prof_{i}"):
                s.selected_prof = r["name"]; st.session_state["_nav_target"] = "Professors"; st.rerun()
            if col_b.button("Send message", key=f"msg_prof_{i}"):
                stud_n = f"{s.first_name} {s.last_name}"
                conv_k = (r["name"], stud_n)
                if conv_k not in s.conversations:
                    s.conversations[conv_k] = []
                s.active_chat = r["name"]; st.session_state["_nav_target"] = "Messages"; st.rerun()
            if col_c.button("Draft email →", key=f"email_prof_{i}"):
                with ai_spinner("Writing email…"):
                    try:
                        from src.agents.email_writer import draft_email
                        draft = draft_email(
                            student_first=s.first_name or "Student",
                            student_last=s.last_name or "",
                            student_programme=s.programme or "",
                            student_level=s.level or "Master",
                            thesis_title=s.thesis_title or "Research project",
                            thesis_description=s.research_question or "",
                            professor_name=r["name"],
                            professor_dept=r.get("focus", ""),
                            professor_research_focus=r.get("strengths", []),
                            match_summary=r.get("summary", ""),
                        )
                        s.email_drafts[r["name"]] = draft
                    except Exception as e:
                        s.email_drafts[r["name"]] = {"subject": "Draft email", "body": f"[AI unavailable: {e}]", "tips": []}
                st.rerun()

            if r["name"] in s.email_drafts:
                draft = s.email_drafts[r["name"]]
                st.markdown(f"""
                <div style="background:var(--gp);border:1px solid var(--bdr);padding:1rem 1.1rem;margin-top:0.7rem">
                  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;
                              color:var(--mut);margin-bottom:6px">Draft email — copy &amp; personalise</div>
                  <div style="font-size:0.8rem;color:var(--mut);margin-bottom:4px">Subject: <strong>{draft.get('subject','')}</strong></div>
                  <div style="font-size:0.84rem;color:var(--txt);white-space:pre-line;line-height:1.6">{draft.get('body','')}</div>
                  {"<div style='margin-top:10px;font-size:0.78rem;color:var(--mut)'><strong>Tips to personalise:</strong><ul style='margin:4px 0 0 16px'>" + "".join(f"<li>{t}</li>" for t in draft.get("tips",[])) + "</ul></div>" if draft.get("tips") else ""}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Search again", key="restart_match"):
        s.match_results = None; s.match_step = 0; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: THESIS TOPICS
# ─────────────────────────────────────────────────────────────────────────────

def _rank_topics_for_student(topics: list) -> list:
    """
    Two-stage ranking: OpenAI embeddings → cosine similarity → Claude reranker.
    Returns the same list with match_score and why_fit populated, sorted best-first.
    Falls back to original order if APIs unavailable.
    """
    profile_text = "\n".join(filter(None, [
        f"Programme: {s.programme} ({s.level})" if s.programme else "",
        f"Research area: {s.research_area}" if s.research_area else "",
        f"Thesis title: {s.thesis_title}" if s.thesis_title else "",
        f"Research question: {s.research_question}" if s.research_question else "",
        f"Skills: {s.skills}" if getattr(s, "skills", "") else "",
        f"Keywords: {s.keywords}" if getattr(s, "keywords", "") else "",
    ]))
    if not profile_text.strip():
        return topics

    try:
        from src.matching.embedder import embed_text, embed_batch, cosine_similarity as cos_sim

        student_vec = embed_text(profile_text)
        topic_texts = [
            t["title"] + " " + t.get("description", "") + " " + " ".join(t.get("fields", []))
            for t in topics
        ]
        topic_vecs = embed_batch(topic_texts)

        scored = sorted(
            zip(topics, [cos_sim(student_vec, v) for v in topic_vecs]),
            key=lambda x: x[1], reverse=True
        )

        # Stage 2: NIM reranker on top 20
        import json as _json
        from src.agents.llm_client import chat as _nim_chat
        top20 = scored[:20]
        candidates = [
            {"id": t["id"], "rank": i + 1, "title": t["title"],
             "description": t.get("description", "")[:200]}
            for i, (t, _) in enumerate(top20)
        ]
        try:
            raw = _nim_chat(
                messages=[{"role": "user", "content":
                    f"Student profile:\n{profile_text}\n\n"
                    f"Rerank these thesis topics by fit. Return JSON only:\n"
                    f"{{\"rankings\": [{{\"id\": \"...\", \"score\": 8.5, \"why_fit\": \"one sentence\"}}]}}\n\n"
                    f"Topics:\n{_json.dumps(candidates)}"
                }],
                system="You are a thesis matching engine. Return valid JSON only, no prose.",
                max_tokens=600,
                temperature=0.2,
            )
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            rankings = _json.loads(raw).get("rankings", [])
            score_map = {r["id"]: (r.get("score", 5.0), r.get("why_fit", "")) for r in rankings}

            result = []
            for t, emb_score in scored:
                sc, wf = score_map.get(t["id"], (round(emb_score * 10, 1), ""))
                t_copy = dict(t, match_score=sc, why_fit=wf)
                result.append(t_copy)
            result.sort(key=lambda x: x["match_score"] or 0, reverse=True)
            return result
        except Exception:
            # Fall back to embedding scores only
            return [dict(t, match_score=round(sc * 10, 1), why_fit="") for t, sc in scored]

    except Exception:
        return topics


def page_topics():
    all_pool = ALL_TOPICS + (s.topic_ai_generated or [])
    n_prof = sum(1 for t in ALL_TOPICS if t["source"] == "professor")
    n_co   = sum(1 for t in ALL_TOPICS if t["source"] == "company")
    n_ai   = len(s.topic_ai_generated or [])
    topbar("Thesis Topics", f"{n_prof} professor · {n_co} company · {n_ai} AI")

    st.markdown('<span class="topics-layout-marker"></span>', unsafe_allow_html=True)
    left, right = st.columns([2, 3], gap="medium")

    # ── Helper: filter ────────────────────────────────────────────────────────
    def _filter(pool):
        q = s.topic_search.lower()
        out = []
        for t in pool:
            haystack = (t["title"] + t.get("author_label", t.get("company", "")) + t.get("description", "")).lower()
            if q and q not in haystack:
                continue
            if s.topic_filter_field != "All fields" and s.topic_filter_field not in t.get("fields", []):
                continue
            if s.topic_filter_degree != "All" and s.topic_filter_degree not in t.get("degree", ""):
                continue
            out.append(t)
        return out

    # ── Helper: render one list card ─────────────────────────────────────────
    def _card(t, show_score=False, key_prefix="t"):
        is_active = s.selected_topic == t["id"]
        is_fav    = t["id"] in s.topic_favourites
        src_badge = {
            "professor": '<span style="background:#dcfce7;color:#166534;font-size:0.65rem;'
                         'font-weight:700;padding:1px 6px;margin-left:4px">Professor</span>',
            "company":   '<span style="background:#dbeafe;color:#1e40af;font-size:0.65rem;'
                         'font-weight:700;padding:1px 6px;margin-left:4px">Company</span>',
            "ai":        '<span style="background:#f3e8ff;color:#6b21a8;font-size:0.65rem;'
                         'font-weight:700;padding:1px 6px;margin-left:4px">AI</span>',
        }.get(t.get("source", "professor"), "")
        emp_icon = {"internship": " · Internship", "working_student": " · Working student"}.get(t.get("employment", ""), "")
        score_html = ""
        if show_score and t.get("match_score") is not None:
            score_html = f' <span style="background:var(--g);color:white;font-size:0.62rem;padding:1px 5px;font-weight:700">{t["match_score"]:.0f}/10</span>'
        author = t.get("author_label") or t.get("company", "")
        has_why = show_score and t.get("why_fit")
        star_color = "var(--g)" if is_fav else "#bbb"
        star_char  = "★" if is_fav else "☆"
        card_class = "list-item topic-card" + (" active" if is_active else "")

        st.markdown(f"""
        <div class="{card_class}" style="position:relative">
          <span style="position:absolute;top:0.5rem;right:0.7rem;font-size:1rem;
                       color:{star_color};pointer-events:none">{star_char}</span>
          <div class="list-title" style="padding-right:1.6rem">{t['title']}{src_badge}{score_html}</div>
          <div class="list-meta">{author} · {' · '.join(t.get('fields', [])[:2])}{emp_icon}</div>
          {"<div style='font-size:0.72rem;color:var(--mut);margin-top:2px;font-style:italic'>" + t['why_fit'] + "</div>" if has_why else ""}
        </div>
        """, unsafe_allow_html=True)
        # Invisible full-card overlay — selects topic
        if st.button("⠀", key=f"{key_prefix}_v_{t['id']}"):
            s.selected_topic = t["id"]; st.rerun()
        # Star toggle button — positioned at top-right via CSS
        star_label = "★" if is_fav else "☆"
        if st.button(star_label, key=f"{key_prefix}_s_{t['id']}"):
            if is_fav:
                s.topic_favourites.discard(t["id"])
            else:
                s.topic_favourites.add(t["id"])
            st.rerun()

    # ─────────────────────────────────────────────────────────────────────────
    with left:
        st.text_input("Search topics", key="topic_search_input",
                      placeholder="keyword, professor, company…",
                      value=s.topic_search)
        s.topic_search = st.session_state.topic_search_input

        fc1, fc2 = st.columns(2)
        all_fields = ["All fields"] + sorted({f for t in all_pool for f in t.get("fields", [])})
        s.topic_filter_field = fc1.selectbox("Field", all_fields,
            index=all_fields.index(s.topic_filter_field) if s.topic_filter_field in all_fields else 0,
            key="topic_field_sel")
        s.topic_filter_degree = fc2.selectbox("Degree",
            ["All", "Bachelor", "Master", "Bachelor & Master"], key="topic_deg_sel",
            index=["All", "Bachelor", "Master", "Bachelor & Master"].index(s.topic_filter_degree)
                  if s.topic_filter_degree in ["All", "Bachelor", "Master", "Bachelor & Master"] else 0)

        tabs = st.tabs(["All", "Professor", "Company", "AI Generated"])

        # ── ALL tab ──────────────────────────────────────────────────────────
        with tabs[0]:
            # Favourites pinned at top
            favs = [t for t in all_pool if t["id"] in s.topic_favourites]
            if favs:
                st.markdown('<div class="sec-head">Saved</div>', unsafe_allow_html=True)
                for t in favs:
                    _card(t, key_prefix="fav_all")

            # Recommendations section
            has_profile = bool(s.research_area or s.thesis_title or s.research_question)
            st.markdown('<div class="sec-head">Recommended for you</div>', unsafe_allow_html=True)
            if s.topic_recs_loading:
                with ai_spinner("Ranking topics for your profile…"):
                    s.topic_recs = _rank_topics_for_student(_filter(ALL_TOPICS))
                    s.topic_recs_loading = False; st.rerun()
            elif s.topic_recs is None:
                if has_profile:
                    if st.button("Get personalised recommendations", key="get_recs_all"):
                        s.topic_recs_loading = True; st.rerun()
                else:
                    st.markdown('<div style="font-size:0.8rem;color:var(--mut)">Complete your thesis profile to get recommendations.</div>', unsafe_allow_html=True)
            else:
                for t in s.topic_recs[:3]:
                    _card(t, show_score=True, key_prefix="rec_all")
                if st.button("Refresh", key="refresh_recs"):
                    s.topic_recs = None; st.rerun()

            # All results (exclude already-shown recs and favs)
            filtered_all = _filter(all_pool)
            rec_ids = {t["id"] for t in (s.topic_recs or [])[:5]}
            shown_ids = {t["id"] for t in favs} | rec_ids
            remaining = [t for t in filtered_all if t["id"] not in shown_ids]
            st.markdown(f'<div class="sec-head">All Results ({len(filtered_all)})</div>', unsafe_allow_html=True)
            if not remaining:
                st.markdown('<div style="font-size:0.85rem;color:var(--mut)">No topics match your filters.</div>', unsafe_allow_html=True)
            for t in remaining:
                _card(t, key_prefix="all")

        # ── PROFESSOR tab ─────────────────────────────────────────────────────
        with tabs[1]:
            prof_pool = [t for t in all_pool if t.get("source") == "professor"]
            favs_p = [t for t in prof_pool if t["id"] in s.topic_favourites]
            if favs_p:
                st.markdown('<div class="sec-head">Saved</div>', unsafe_allow_html=True)
                for t in favs_p:
                    _card(t, key_prefix="fav_p")

            filtered_p = _filter(prof_pool)
            shown_p = {t["id"] for t in favs_p}
            st.markdown(f'<div class="sec-head">Results ({len(filtered_p)})</div>', unsafe_allow_html=True)
            for t in [t for t in filtered_p if t["id"] not in shown_p]:
                _card(t, key_prefix="prof_tab")

        # ── COMPANY tab ───────────────────────────────────────────────────────
        with tabs[2]:
            co_pool = [t for t in all_pool if t.get("source") == "company"]
            favs_c = [t for t in co_pool if t["id"] in s.topic_favourites]
            if favs_c:
                st.markdown('<div class="sec-head">Saved</div>', unsafe_allow_html=True)
                for t in favs_c:
                    _card(t, key_prefix="fav_c")

            filtered_c = _filter(co_pool)
            shown_c = {t["id"] for t in favs_c}
            st.markdown(f'<div class="sec-head">Results ({len(filtered_c)})</div>', unsafe_allow_html=True)
            for t in [t for t in filtered_c if t["id"] not in shown_c]:
                _card(t, key_prefix="co_tab")

        # ── AI GENERATED tab ──────────────────────────────────────────────────
        with tabs[3]:
            if s.topic_ai_generated is None and not s.topic_ai_loading:
                st.markdown("""
                <div style="font-size:0.83rem;color:var(--mut);margin-bottom:0.8rem">
                Generate thesis topics tailored to your research interests and programme.
                </div>""", unsafe_allow_html=True)
                missing_for_ai = []
                if not st.session_state.get("cv_parsed"):
                    missing_for_ai.append("CV / résumé")
                if not st.session_state.get("transcript_parsed"):
                    missing_for_ai.append("Grade transcript")
                if missing_for_ai:
                    missing_str = " and ".join(missing_for_ai)
                    st.markdown(f"""
                    <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:2px;
                                padding:0.7rem 0.9rem;font-size:0.84rem;color:#991B1B;margin-bottom:0.7rem">
                      <strong>Profile incomplete.</strong> Please upload your {missing_str} first —
                      go to <strong>My Profile</strong> to add them. AI topic generation uses your
                      academic background to personalise the results.
                    </div>""", unsafe_allow_html=True)
                    if st.button("Go to My Profile →", key="ai_tab_go_profile"):
                        st.session_state["_nav_target"] = "My Profile"; st.rerun()
                else:
                    if st.button("Generate 5 topics for my profile", type="primary", key="gen_ai_topics"):
                        s.topic_ai_loading = True; st.rerun()
            elif s.topic_ai_loading:
                with ai_spinner("Generating personalised thesis topics…"):
                    try:
                        from src.agents.thesis_generator import generate_thesis_ideas
                        raw = generate_thesis_ideas(
                            programme=s.programme or "Master",
                            research_area=s.research_area or "General Management",
                            interests=getattr(s, "motivation", "") or getattr(s, "keywords", "") or "",
                            skills=getattr(s, "skills", "") or "",
                            level=s.level or "Master",
                            n=5,
                        )
                        s.topic_ai_generated = [
                            dict(
                                id=f"AI-{i:03d}", source="ai",
                                title=idea["title"],
                                author_label="AI Generated", company="AI Generated",
                                professor="", employment="no",
                                fields=idea.get("keywords", [])[:3],
                                degree=s.level or "Master",
                                description=idea.get("research_question", ""),
                                method=idea.get("methodology", ""),
                                requirements="", contact="", url="",
                                match_score=None,
                                why_fit=idea.get("why_fit", ""),
                                difficulty=idea.get("difficulty", "standard"),
                            )
                            for i, idea in enumerate(raw)
                        ]
                    except Exception as exc:
                        st.error(f"Generation failed: {exc}")
                    finally:
                        s.topic_ai_loading = False
                st.rerun()
            else:
                ai_favs = [t for t in (s.topic_ai_generated or []) if t["id"] in s.topic_favourites]
                if ai_favs:
                    st.markdown('<div class="sec-head">Saved</div>', unsafe_allow_html=True)
                    for t in ai_favs:
                        _card(t, key_prefix="fav_ai")

                filtered_ai = _filter(s.topic_ai_generated or [])
                shown_ai = {t["id"] for t in ai_favs}
                st.markdown(f'<div class="sec-head">Generated ({len(filtered_ai)})</div>', unsafe_allow_html=True)
                for t in [t for t in filtered_ai if t["id"] not in shown_ai]:
                    _card(t, show_score=True, key_prefix="ai_tab")

                if st.button("Regenerate", key="regen_ai"):
                    s.topic_ai_generated = None; st.rerun()

    # ─────────────────────────────────────────────────────────────────────────
    with right:
        all_pool_r = ALL_TOPICS + (s.topic_ai_generated or [])
        # Merge in ranked versions if available
        if s.topic_recs:
            rec_by_id = {t["id"]: t for t in s.topic_recs}
            all_pool_r = [rec_by_id.get(t["id"], t) for t in all_pool_r]

        selected = next((t for t in all_pool_r if t["id"] == s.selected_topic), None)

        if not selected:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:55vh;color:var(--mut);text-align:center;gap:10px">
              <div style="font-weight:500">Select a topic to see details</div>
              <div style="font-size:0.82rem;opacity:0.7">Browse the list on the left</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            src = selected.get("source", "professor")
            src_colors = {
                "professor": ("Professor", "#dcfce7", "#166534"),
                "company":   ("Company",   "#dbeafe", "#1e40af"),
                "ai":        ("AI Generated", "#f3e8ff", "#6b21a8"),
            }
            src_label, src_bg, src_fg = src_colors.get(src, ("Topic", "#f0f0f0", "#333"))
            emp_map = {"internship": "Internship included", "working_student": "Working student position", "no": "", "open": "Employment possible"}
            emp_label = emp_map.get(selected.get("employment", "no"), "")
            fields_tags = "".join(tag(f, "tb") for f in selected.get("fields", []))
            author = selected.get("author_label") or selected.get("company", "")
            is_fav = selected["id"] in s.topic_favourites

            # Header row: source badge + star
            h1, h2 = st.columns([5, 1])
            with h1:
                st.markdown(f"""
                <span style="background:{src_bg};color:{src_fg};font-size:0.7rem;font-weight:700;
                             padding:2px 8px;letter-spacing:0.04em">{src_label}</span>
                {"<span style='background:#fef9c3;color:#854d0e;font-size:0.7rem;font-weight:700;padding:2px 8px;margin-left:4px'>"+emp_label+"</span>" if emp_label else ""}
                """, unsafe_allow_html=True)
            with h2:
                star_lbl = "★ Saved" if is_fav else "☆ Save"
                if st.button(star_lbl, key="detail_star"):
                    if is_fav:
                        s.topic_favourites.discard(selected["id"])
                    else:
                        s.topic_favourites.add(selected["id"])
                    st.rerun()

            st.markdown(f"""
            <div class="detail-header" style="margin-top:0.5rem">
              <div class="detail-name">{selected['title']}</div>
              <div class="detail-sub" style="margin-top:4px">{author} &nbsp;·&nbsp; {selected.get('degree','Master')}</div>
              <div style="margin-top:8px">{fields_tags}</div>
            </div>
            """, unsafe_allow_html=True)

            # Match score bar (if available)
            if selected.get("match_score") is not None:
                score = selected["match_score"]
                pct = int(score * 10)
                why = selected.get("why_fit", "")
                st.markdown(f"""
                <div style="margin-bottom:0.8rem">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
                    <div style="font-size:0.72rem;font-weight:700;color:var(--g)">Match {score:.0f}/10</div>
                    <div style="flex:1;height:4px;background:var(--bdr)">
                      <div style="width:{pct}%;height:4px;background:var(--g)"></div>
                    </div>
                  </div>
                  {"<div style='font-size:0.78rem;color:var(--mut);font-style:italic'>"+why+"</div>" if why else ""}
                </div>
                """, unsafe_allow_html=True)

            # Description
            desc = selected.get("description", "")
            if desc:
                st.markdown(f"""
                <div style="font-size:0.88rem;color:var(--sub);line-height:1.7;margin-bottom:1rem">{desc}</div>
                """, unsafe_allow_html=True)

            # Method + Requirements expandable
            method = selected.get("method", "")
            reqs   = selected.get("requirements", "")
            if method or reqs:
                with st.expander("Further Details"):
                    if method:
                        st.markdown(f"**Method:** {method}")
                    if reqs:
                        st.markdown(f"**Requirements:** {reqs}")
                    url = selected.get("url", "")
                    if url:
                        st.markdown(f"[View original posting]({url})")
                    contact = selected.get("contact", "")
                    if contact and src == "company":
                        st.markdown(f"**Contact:** {contact}")

            # Action buttons
            st.markdown("<br>", unsafe_allow_html=True)
            ac1, ac2 = st.columns(2)
            with ac1:
                btn_label = "Use this topic →" if src == "ai" else "Express Interest"
                if st.button(btn_label, type="primary", key="express_interest_btn"):
                    if src == "professor" and selected.get("professor"):
                        # Navigate to Messages pre-selecting the professor
                        # Try to match professor name to PROFESSORS list
                        prof_match = next(
                            (p for p in PROFESSORS if selected["professor"].lower() in p["name"].lower()
                             or p["name"].lower().endswith(selected["professor"].lower())),
                            None
                        )
                        if prof_match:
                            s.active_chat = prof_match["name"]
                        else:
                            s.active_chat = selected["professor"]
                        stud_n2 = f"{s.first_name} {s.last_name}"
                        ck2 = (s.active_chat, stud_n2)
                        if ck2 not in s.conversations:
                            s.conversations[ck2] = []
                        st.session_state["_nav_target"] = "Messages"; st.rerun()
                    elif src == "company":
                        contact = selected.get("contact", "")
                        if contact:
                            st.info(f"Contact: {contact}")
                        else:
                            st.info("Check the company's careers page for application instructions.")
                    else:
                        # AI-generated topic — apply to thesis profile
                        s.thesis_title      = selected.get("title", "")
                        s.research_question = selected.get("description", "")
                        s.approach          = selected.get("method", "")
                        kws = selected.get("fields", [])
                        s.keywords = ", ".join(kws) if isinstance(kws, list) else kws
                        st.success("Topic added to your thesis profile! Go to **Find Supervisor** to match.")
                        st.rerun()
            with ac2:
                url = selected.get("url", "")
                if url:
                    st.markdown(f"""
                    <a href="{url}" target="_blank"
                       style="display:block;text-align:center;padding:0.45rem 1rem;
                              border:1px solid var(--bdr);font-size:0.85rem;
                              color:var(--txt);text-decoration:none;font-weight:500">
                      Further Details
                    </a>""", unsafe_allow_html=True)
                else:
                    st.button("Further Details", key="further_details_btn", disabled=not (method or reqs))


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROFESSORS  (list+detail)
# ─────────────────────────────────────────────────────────────────────────────

def page_professors():
    topbar("Professors", "HSG faculty profiles")

    left, right = st.columns([2, 3], gap="medium")

    with left:
        st.text_input("Search professors", key="prof_search_input",
                      placeholder="name, topic, keyword…",
                      value=s.prof_search)
        s.prof_search = st.session_state.prof_search_input

        st.markdown('<div class="sec-head">Faculty</div>', unsafe_allow_html=True)

        filtered_profs = [p for p in PROFESSORS
                         if not s.prof_search or s.prof_search.lower() in (p["name"] + " ".join(p["focus"])).lower()]

        # --- SCROLLABLE CONTAINER START ---
        # Adjust height (e.g., 600) to fit your UI needs
        with st.container(height=600, border=False):
            for p in filtered_profs:
                is_active = s.selected_prof == p["name"]
                active_cls = "list-item active" if is_active else "list-item"
                has_proposals = len(p.get("proposals", [])) > 0
                prop_badge = f' · <span style="color:var(--g);font-weight:600">{len(p["proposals"])} proposals</span>' if has_proposals else ""
                
                st.markdown(f"""
                <div class="{active_cls}">
                  <div class="list-title">{p['name']}</div>
                  <div class="list-meta">{p['dept']}{prop_badge}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⠀", key=f"prof_{p['name']}"):
                    s.selected_prof = p["name"]
                    st.rerun()

    with right:
        selected = next((p for p in PROFESSORS if p["name"] == s.selected_prof), None)
        if not selected:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:55vh;color:var(--mut);text-align:center;gap:10px">
              <div style="font-weight:500">Select a professor to view their profile</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            focus = selected.get("focus") or []
            if isinstance(focus, str):
                focus = [focus]
            focus_tags = "".join(tag(f, "tg") for f in focus[:5])
            courses = selected.get("courses") or []
            course_tags = "".join(tag(c, "tb") for c in courses)
            openalex_tags = "".join(tag(t, "tgr") for t in selected.get("openalex_topics", [])[:4])

            st.markdown(f"""
            <div class="detail-header">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div class="detail-name">{selected.get('title','')} {selected['name']}</div>
                  <div class="detail-sub">{selected['dept']}</div>
                  <div style="font-size:0.75rem;color:var(--mut);margin-top:2px">{selected.get('email','')}</div>
                </div>
                <div style="text-align:right">
                  <div style="font-size:1.3rem;font-weight:700;color:var(--g)">h={selected['h_index']}</div>
                  <div style="font-size:0.72rem;color:var(--mut)">{selected['pubs']} publications</div>
                  {"<a href='"+selected['profile_url']+"' target='_blank' style='font-size:0.7rem;color:var(--g)'>Alexandria profile</a>" if selected.get('profile_url') else ""}
                </div>
              </div>
              <div style="margin-top:8px">{focus_tags}</div>
              {"<div style='margin-top:4px'>"+openalex_tags+"</div>" if openalex_tags else ""}
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3, tab4 = st.tabs(["Research", "Publications", "Courses", "Thesis Proposals"])

            with tab1:
                if selected.get("career"):
                    st.markdown(f'<div style="font-size:0.83rem;color:var(--sub);line-height:1.65;margin-bottom:0.7rem">{selected["career"][:600]}{"…" if len(selected.get("career",""))>600 else ""}</div>', unsafe_allow_html=True)
                if selected.get("education"):
                    st.markdown(f'<div class="sec-head">Education</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:0.82rem;color:var(--sub);line-height:1.6">{selected["education"]}</div>', unsafe_allow_html=True)

            with tab2:
                pubs = selected.get("publications") or []
                if pubs:
                    for pub in pubs[:5]:
                        cited = pub.get("cited_by_count", 0)
                        topics_str = ", ".join(pub.get("topics", [])[:2])
                        st.markdown(f"""
                        <div style="padding:0.6rem 0;border-bottom:1px solid var(--bdr)">
                          <div style="font-size:0.85rem;font-weight:500;color:var(--txt)">{pub['title']}</div>
                          <div style="font-size:0.73rem;color:var(--mut);margin-top:2px">{pub.get('year','')} · {cited} citations · {topics_str}</div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size:0.85rem;color:var(--mut)">No publication data available.</div>', unsafe_allow_html=True)

            with tab3:
                if courses:
                    st.markdown(f'<div style="font-size:0.85rem;color:var(--sub);line-height:1.8">{course_tags}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size:0.85rem;color:var(--mut)">No course data available.</div>', unsafe_allow_html=True)

            with tab4:
                proposals = selected.get("proposals") or []
                if proposals:
                    for prop in proposals:
                        st.markdown(f"""
                        <div style="border:1px solid var(--bdr);padding:0.8rem 1rem;margin-bottom:0.6rem">
                          <div style="font-weight:600;font-size:0.88rem">{prop}</div>
                          <div style="font-size:0.75rem;color:var(--mut);margin-top:3px">Open for thesis supervision</div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size:0.85rem;color:var(--mut)">No open proposals listed.</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Send message", type="primary", key="msg_from_prof"):
                stud_n3 = f"{s.first_name} {s.last_name}"
                ck3 = (selected["name"], stud_n3)
                if ck3 not in s.conversations:
                    s.conversations[ck3] = []
                s.active_chat = selected["name"]; st.session_state["_nav_target"] = "Messages"; st.rerun()
            c2.button("Save to shortlist", key="save_prof")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MESSAGES  (shared live conversation state)
# ─────────────────────────────────────────────────────────────────────────────

def _msg_bubble(text, sender_role, initials, time_str):
    is_mine = (sender_role == "student" and s.role == "student") or \
              (sender_role == "professor" and s.role == "professor")
    if is_mine:
        st.markdown(f"""
        <div class="msg-row" style="justify-content:flex-end">
          <div>
            <div class="bubble mine">{text}</div>
            <div class="msg-t" style="text-align:right">{time_str}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row">
          <div class="msg-av">{initials}</div>
          <div>
            <div class="bubble">{text}</div>
            <div class="msg-t">{time_str}</div>
          </div>
        </div>""", unsafe_allow_html=True)


def page_messages():
    is_prof   = s.role == "professor"
    stud_name = f"{s.first_name} {s.last_name}"
    prof_display = f"{s.prof_title} {s.prof_name}" if s.prof_name else "Professor"

    topbar("Student Applications" if is_prof else "Messages",
           "Review and reply to students" if is_prof else "Conversations with supervisors")

    if st.session_state.pop("_msg_clear", False):
        st.session_state["chat_msg_input"] = ""

    _is_demo_user = _is_demo(s.firebase_user.get("uid", ""))
    _convs_dict   = _DEMO_SHARED["conversations"]   if _is_demo_user else s.conversations
    _matches_set  = _DEMO_SHARED["confirmed_matches"] if _is_demo_user else s.confirmed_matches

    left, right = st.columns([2, 3], gap="medium")

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    with left:
        if is_prof:
            prof_convs = [(k, v) for k, v in _convs_dict.items() if k[0] == prof_display]
            pending  = [(k, v) for k, v in prof_convs if k not in _matches_set]
            matched  = [(k, v) for k, v in prof_convs if k in _matches_set]

            tab_app, tab_mat = st.tabs([f"Applications ({len(pending)})", f"Matched ({len(matched)})"])

            def _prof_list_item(conv_key, msgs, tab_key):
                _, sname = conv_key
                is_active = s.prof_active_chat == sname
                last_txt = (msgs[-1]["text"][:55] + "…") if msgs else ""
                unread = bool(msgs and msgs[-1]["sender"] == "student")
                udot = ' <span style="display:inline-block;width:7px;height:7px;background:#EF4444;border-radius:50%;margin-left:4px;vertical-align:middle"></span>' if unread else ""
                is_conf_item = conv_key in s.confirmed_matches
                conf_badge = ' <span style="background:#dcfce7;color:#166534;font-size:0.62rem;font-weight:700;padding:1px 5px;margin-left:4px">Matched</span>' if is_conf_item else ""
                active_cls2 = "list-item active" if is_active else "list-item"
                st.markdown(f"""
                <div class="{active_cls2}">
                  <div class="list-title">{sname}{udot}{conf_badge}</div>
                  <div class="list-meta" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{last_txt}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("⠀", key=f"popen_{tab_key}_{sname}"):
                    s.prof_active_chat = sname; st.rerun()

            with tab_app:
                if not pending:
                    st.markdown('<div style="font-size:0.85rem;color:var(--mut);padding:1rem 0">No pending applications.</div>', unsafe_allow_html=True)
                for ck, msgs in pending:
                    _prof_list_item(ck, msgs, "app")

            with tab_mat:
                if not matched:
                    st.markdown('<div style="font-size:0.85rem;color:var(--mut);padding:1rem 0">No confirmed matches yet.</div>', unsafe_allow_html=True)
                for ck, msgs in matched:
                    _prof_list_item(ck, msgs, "mat")

        else:
            stud_convs = [(k, v) for k, v in _convs_dict.items() if k[1] == stud_name]
            st.markdown('<div class="sec-head">Professors</div>', unsafe_allow_html=True)
            if not stud_convs:
                st.markdown('<div style="font-size:0.85rem;color:var(--mut);padding:1rem 0">No conversations yet — match with a supervisor and send a message.</div>', unsafe_allow_html=True)
            for (pname, _), msgs in stud_convs:
                is_active = s.active_chat == pname
                last_txt = (msgs[-1]["text"][:55] + "…") if msgs else ""
                unread = bool(msgs and msgs[-1]["sender"] == "professor")
                udot = ' <span style="display:inline-block;width:7px;height:7px;background:#EF4444;border-radius:50%;margin-left:4px;vertical-align:middle"></span>' if unread else ""
                is_conf = (pname, stud_name) in _matches_set
                conf_badge = ' <span style="background:#dcfce7;color:#166534;font-size:0.62rem;font-weight:700;padding:1px 5px;margin-left:4px">Matched</span>' if is_conf else ""
                active_cls3 = "list-item active" if is_active else "list-item"
                st.markdown(f"""
                <div class="{active_cls3}">
                  <div class="list-title">{pname}{udot}{conf_badge}</div>
                  <div class="list-meta" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{last_txt}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("⠀", key=f"sopen_{pname}"):
                    s.active_chat = pname; st.rerun()

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    with right:
        active_str = s.prof_active_chat if is_prof else s.active_chat
        if not active_str:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                        min-height:55vh;color:var(--mut);text-align:center;gap:10px">
              <div style="font-weight:500">Select a conversation</div>
            </div>""", unsafe_allow_html=True)
        else:
            conv_key = (prof_display, active_str) if is_prof else (active_str, stud_name)
            if conv_key not in _convs_dict:
                _convs_dict[conv_key] = []
            msgs = _convs_dict[conv_key]
            is_confirmed = conv_key in _matches_set

            if is_prof:
                other_name    = active_str
                initials_o    = "".join(w[0] for w in other_name.split()[:2]).upper()
                dept_o        = "HSG Student"
                sender_role   = "professor"
            else:
                other_name    = active_str
                initials_o    = "".join(w[0] for w in other_name.replace("Prof. Dr. ","").replace("Prof. Ph.D. ","").split()[:2]).upper()
                dept_o        = "HSG Faculty"
                sender_role   = "student"

            # Header
            matched_hdr = ' <span style="background:#dcfce7;color:#166534;font-size:0.7rem;font-weight:700;padding:2px 7px;margin-left:8px">Matched</span>' if is_confirmed else ""
            h1, h2 = st.columns([4, 1])
            with h1:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding-bottom:0.9rem;
                            border-bottom:1px solid var(--bdr);margin-bottom:1rem">
                  <div class="msg-av">{initials_o}</div>
                  <div>
                    <div style="font-weight:600;font-size:0.9rem">{other_name}{matched_hdr}</div>
                    <div style="font-size:0.72rem;color:var(--mut)">{dept_o}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            with h2:
                if not is_prof:
                    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
                    if st.button("Ask AI", key="open_ai_chat_btn"):
                        s.active_prof_ai_chat = active_str
                        st.session_state["_nav_target"] = "Professor AI Chat"; st.rerun()

            # Messages
            for msg in msgs:
                _msg_bubble(msg["text"], msg["sender"], initials_o, msg["time"])

            st.markdown("<br>", unsafe_allow_html=True)
            msg_input = st.text_area("Message", placeholder="Write a message…", height=80,
                                     key="chat_msg_input", label_visibility="collapsed")

            if is_prof:
                col_send, col_ai, col_conf = st.columns([2, 2, 2])
            else:
                col_send, col_ai = st.columns([3, 2])

            with col_send:
                if st.button("Send →", type="primary", key="send_live_msg"):
                    txt = st.session_state.get("chat_msg_input", "").strip()
                    if txt:
                        _convs_dict[conv_key].append({
                            "sender": sender_role,
                            "text": txt,
                            "time": _dt.now().strftime("%H:%M"),
                        })
                        st.session_state["_msg_clear"] = True
                        st.rerun()

            # Student AI draft: only active before first student message (intro email)
            student_has_sent = not is_prof and any(m["sender"] == "student" for m in msgs)

            with col_ai:
                if not is_prof and student_has_sent:
                    st.markdown("""
                    <div style="padding:0.45rem 1rem;border:1px solid var(--bdr);
                                font-size:0.85rem;color:#C0C0C0;text-align:center;
                                background:#FAFAFA;cursor:default" title="AI draft only available for your first message">
                      AI draft
                    </div>""", unsafe_allow_html=True)
                elif st.button("AI draft", key="ai_draft_btn"):
                    last_in = next((m["text"] for m in reversed(msgs) if m["sender"] != sender_role), "")
                    target = last_in or ("their thesis supervision request" if is_prof else "")
                    with ai_spinner("Drafting…"):
                        try:
                            if is_prof:
                                from src.agents.faq_agent import draft_professor_reply
                                p_ctx = "\n".join(d.get("raw_insights","") for d in s.prof_uploaded_docs) if s.prof_uploaded_docs else ""
                                f_ctx = "\n".join(f"Q: {e['question']}\nA: {e['answer']}" for e in s.prof_faq_bank[:10]) if s.prof_faq_bank else ""
                                draft = draft_professor_reply(
                                    student_message=target or "thesis supervision",
                                    professor_name=prof_display,
                                    professor_context=(p_ctx + "\n\n" + f_ctx).strip(),
                                )
                            else:
                                from src.agents.email_writer import draft_email
                                pdata = next((p for p in PROFESSORS if other_name in p.get("name","")), {})
                                foc   = pdata.get("focus",[]) if isinstance(pdata.get("focus",[]), list) else [pdata.get("focus","")]
                                res = draft_email(
                                    student_first=s.first_name or "Student",
                                    student_last=s.last_name or "",
                                    student_programme=s.programme or "",
                                    student_level=s.level or "Master",
                                    thesis_title=s.thesis_title or "Research project",
                                    thesis_description=s.research_question or "",
                                    professor_name=other_name,
                                    professor_dept=pdata.get("dept",""),
                                    professor_research_focus=foc,
                                    match_summary="",
                                )
                                draft = res.get("body","")
                            st.session_state[f"_ai_draft_{conv_key}"] = draft
                        except Exception as exc:
                            st.session_state[f"_ai_draft_{conv_key}"] = f"[AI unavailable: {exc}]"
                    st.rerun()

            if is_prof:
                with col_conf:
                    if not is_confirmed:
                        if st.button("Confirm Match", type="secondary", key="confirm_match_btn"):
                            _matches_set.add(conv_key)
                            st.rerun()
                    else:
                        st.markdown('<span style="background:#dcfce7;color:#166534;font-size:0.78rem;font-weight:700;padding:4px 10px">Matched</span>', unsafe_allow_html=True)

            # AI draft display — scoped to this conversation
            _draft_key = f"_ai_draft_{conv_key}"
            if st.session_state.get(_draft_key):
                st.markdown(f"""
                <div style="background:var(--gp);border:1px solid var(--bdr);
                            padding:0.9rem 1rem;margin-top:0.5rem;font-size:0.84rem;
                            color:var(--txt);white-space:pre-line;line-height:1.6">
                  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                              color:var(--mut);margin-bottom:6px">AI draft — copy &amp; edit</div>
                  {st.session_state[_draft_key]}
                </div>""", unsafe_allow_html=True)
                if st.button("Clear draft", key="clear_ai_draft"):
                    del st.session_state[_draft_key]; st.rerun()

            # Registration + Feedback banner (student, confirmed)
            if not is_prof and is_confirmed:
                st.markdown("<br>", unsafe_allow_html=True)
                officially_registered = s.get("officially_registered", set())
                if conv_key in officially_registered:
                    # Already registered — show completion state
                    st.markdown(f"""
                    <div style="background:#dcfce7;border:1px solid #86efac;padding:0.9rem 1.1rem;
                                margin-bottom:0.8rem">
                      <div style="font-weight:700;font-size:0.88rem;color:#14532d;margin-bottom:4px">
                        Officially registered with {other_name}
                      </div>
                      <div style="font-size:0.82rem;color:#166534">
                        Your thesis registration is complete. Good luck with your thesis!
                      </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#dcfce7;border:1px solid #86efac;padding:0.9rem 1.1rem;
                                margin-bottom:0.8rem">
                      <div style="font-weight:700;font-size:0.88rem;color:#14532d;margin-bottom:4px">
                        Supervision confirmed with {other_name}
                      </div>
                      <div style="font-size:0.82rem;color:#166534;margin-bottom:0.7rem">
                        Next step: complete your official thesis registration on the HSG Business Platform.
                      </div>
                      <a href="https://businessplatform.unisg.ch/csp?id=ww_my_thesis" target="_blank"
                         style="display:inline-block;background:#009640;color:white;font-size:0.82rem;
                                font-weight:600;padding:0.45rem 1rem;text-decoration:none;
                                border-radius:0;letter-spacing:0.01em">
                        Register on HSG Business Platform →
                      </a>
                    </div>""", unsafe_allow_html=True)
                    if st.button("I've completed my registration ✓", key="confirm_registration_btn", type="primary"):
                        if not hasattr(s, "officially_registered") or s.officially_registered is None:
                            s.officially_registered = set()
                        s.officially_registered.add(conv_key)
                        st.rerun()
                if st.button("Leave feedback", key="leave_feedback_btn"):
                    s.feedback_target = conv_key
                    st.session_state["_nav_target"] = "Feedback"; st.rerun()

            # Professor: view AI chat history in matched view
            if is_prof and is_confirmed:
                ai_hist = s.prof_ai_chats.get(prof_display, [])
                if ai_hist:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander(f"AI chat history with student ({len(ai_hist)} messages)"):
                        for m in ai_hist[-10:]:
                            lbl = "Student" if m["role"] == "user" else "AI"
                            st.markdown(f"**{lbl}:** {m['content']}")



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MY PROFILE
# ─────────────────────────────────────────────────────────────────────────────

def page_profile():
    topbar("My Profile", "Synced with your studyond account")

    # Missing fields notifications
    if missing:
        for m in missing:
            st.markdown(f"""
            <div class="notif">
              <strong>{m} not uploaded</strong> —
              {"Upload your grade transcript to let us identify your strongest academic areas and improve match quality." if "transcript" in m.lower()
               else "Upload your CV so we can extract your skills and work experience automatically." if "cv" in m.lower() or "résumé" in m.lower()
               else f"Add your {m.lower()} to complete your profile."}
            </div>
            """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Personal", "Thesis", "Documents"])

    # ── Personal ─────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="sec-head">Identity</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        s.first_name = c1.text_input("First name", value=s.first_name)
        s.last_name  = c2.text_input("Last name",  value=s.last_name)
        s.email      = st.text_input("HSG email",  value=s.email)

        st.markdown('<div class="sec-head">Programme</div>', unsafe_allow_html=True)
        s.level = st.radio("Level", ["Bachelor", "Master"], horizontal=True,
                           index=0 if s.level == "Bachelor" else 1)
        prog_list = HSG_BACHELOR_PROGRAMMES if s.level == "Bachelor" else HSG_MASTER_PROGRAMMES
        if s.programme not in prog_list:
            s.programme = prog_list[0]
        s.programme = st.selectbox("Programme", prog_list,
                                   index=prog_list.index(s.programme) if s.programme in prog_list else 0)
        SEMESTER_OPTIONS = [
            "1st semester", "2nd semester", "3rd semester", "4th semester",
            "5th semester", "6th semester", "7th semester", "8th semester",
        ]
        sem_idx = SEMESTER_OPTIONS.index(s.semester) if s.semester in SEMESTER_OPTIONS else 1
        s.semester = st.selectbox("Current semester", SEMESTER_OPTIONS, index=sem_idx, key="semester_sel")
        s.language = st.radio("Preferred thesis language", ["English", "German", "French"],
                              horizontal=True,
                              index=["English","German","French"].index(s.language) if s.language in ["English","German","French"] else 0)

        if st.button("Save changes", type="primary", key="save_profile"):
            st.success("Profile updated.")

    # ── Thesis ────────────────────────────────────────────────────
    with tab2:
        ctx = _ctx(s.programme)
        st.markdown('<div class="sec-head">Thesis Information</div>', unsafe_allow_html=True)

        s.thesis_title = st.text_input("Working title",
            value=s.thesis_title, placeholder=ctx["title_ex"])

        area_idx = RESEARCH_AREAS.index(s.research_area) if s.research_area in RESEARCH_AREAS else 0
        s.research_area = st.selectbox("Research area", RESEARCH_AREAS, index=area_idx)

        s.research_question = st.text_area("Research question",
            value=s.research_question, height=80, placeholder=ctx["rq_ex"])

        s.skills = st.text_input("Skills (comma-separated)",
            value=s.skills, placeholder=ctx["skills_ex"])
        s.keywords = st.text_input("Keywords (comma-separated)",
            value=s.keywords, placeholder=ctx["kw_ex"])

        if s.thesis_title:
            st.markdown(f'<div style="font-size:0.78rem;color:var(--g);margin-top:4px">✓ Thesis info is used to improve your supervisor matches.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.78rem;color:var(--mut);margin-top:4px">Add your thesis topic to enable supervisor matching.</div>', unsafe_allow_html=True)

        if st.button("Save thesis info", type="primary", key="save_thesis"):
            st.success("Thesis information saved.")

    # ── Documents ─────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="sec-head">Grade Transcript</div>', unsafe_allow_html=True)

        if st.session_state.get("transcript_parsed"):
            tc = st.session_state["transcript_parsed"]
            st.markdown(f"""
            <div style="background:var(--gp);border:1px solid var(--gm);border-radius:8px;padding:0.9rem 1.1rem;margin-bottom:0.7rem">
              <div style="font-weight:600;color:var(--gd);font-size:0.88rem">✓ Transcript loaded</div>
              <div style="font-size:0.8rem;color:var(--sub);margin-top:4px">
                {len(tc.courses)} courses · GPA {tc.gpa or '—'}
                {"· Strong areas: " + ", ".join(tc.strong_areas[:3]) if hasattr(tc,'strong_areas') and tc.strong_areas else ""}
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Remove transcript", key="rm_transcript"):
                del st.session_state["transcript_parsed"]; st.rerun()
        else:
            st.markdown('<div style="font-size:0.83rem;color:var(--mut);margin-bottom:0.6rem">Upload your grade transcript to automatically identify your strongest academic areas. This improves match quality without adding more questions.</div>', unsafe_allow_html=True)
            tf = st.file_uploader("Upload transcript PDF", type=["pdf"], key="profile_transcript_up")
            if tf:
                with ai_spinner("Scanning transcript…"):
                    try:
                        from src.data_collection.student_parsers.transcript_parser import parse_transcript
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                            tmp.write(tf.read()); tmp_path = tmp.name
                        st.session_state["transcript_parsed"] = parse_transcript(tmp_path)
                        os.unlink(tmp_path)
                        st.success(f"✓ {len(st.session_state['transcript_parsed'].courses)} courses loaded")
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Could not parse transcript: {e}")

        st.markdown('<div class="sec-head">CV / Résumé</div>', unsafe_allow_html=True)

        if st.session_state.get("cv_parsed"):
            cv = st.session_state["cv_parsed"]
            st.markdown(f"""
            <div style="background:var(--gp);border:1px solid var(--gm);border-radius:8px;padding:0.9rem 1.1rem;margin-bottom:0.7rem">
              <div style="font-weight:600;color:var(--gd);font-size:0.88rem">✓ CV loaded</div>
              <div style="font-size:0.8rem;color:var(--sub);margin-top:4px">
                {len(cv.education)} education entries · {len(cv.experience)} experience entries
                {"· Skills: "+", ".join(cv.skills[:4]) if hasattr(cv,'skills') and cv.skills else ""}
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Remove CV", key="rm_cv"):
                del st.session_state["cv_parsed"]; st.rerun()
        else:
            st.markdown('<div style="font-size:0.83rem;color:var(--mut);margin-bottom:0.6rem">Upload your CV to extract skills and work experience. Used to match you with supervisors whose research complements your professional background.</div>', unsafe_allow_html=True)
            cf = st.file_uploader("Upload CV PDF", type=["pdf"], key="profile_cv_up")
            if cf:
                with ai_spinner("Scanning CV…"):
                    try:
                        from src.data_collection.student_parsers.cv_parser import parse_cv
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                            tmp.write(cf.read()); tmp_path = tmp.name
                        st.session_state["cv_parsed"] = parse_cv(tmp_path)
                        os.unlink(tmp_path)
                        st.success(f"✓ CV loaded")
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Could not parse CV: {e}")

        # ── Demo reset (only shown for demo accounts) ─────────────────────
        if _is_demo(s.firebase_user.get("uid", "") if s.firebase_user else ""):
            st.markdown('<div class="sec-head" style="margin-top:2rem">Demo Controls</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.82rem;color:var(--mut);margin-bottom:0.6rem">Reset all demo data back to the initial state — clears conversations, thesis info, CV, transcript, matches and timeline.</div>', unsafe_allow_html=True)
            if st.button("Reset demo data", key="reset_demo_btn"):
                # Reset shared store (visible to both demo sessions)
                _reset_demo_shared()
                # Reset this session's personal data
                for k in ["transcript_parsed", "cv_parsed", "thesis_title", "research_question",
                          "skills", "keywords", "additional_notes", "match_results",
                          "thesis_submission_date", "thesis_tasks", "topic_ai_generated",
                          "topic_recs", "ai_chat_history", "thesis_ideas"]:
                    st.session_state.pop(k, None)
                st.session_state.thesis_title    = ""
                st.session_state.research_question = ""
                st.session_state.skills          = ""
                st.session_state.keywords        = ""
                st.session_state.match_results   = None
                st.session_state.topic_ai_generated = None
                st.session_state.topic_recs      = None
                st.session_state.ai_chat_history = []
                st.session_state.thesis_ideas    = None
                st.session_state.conversations   = _DEMO_SHARED["conversations"]
                st.session_state.confirmed_matches = _DEMO_SHARED["confirmed_matches"]
                st.session_state.student_feedback  = _DEMO_SHARED["student_feedback"]
                st.session_state.officially_registered = _DEMO_SHARED["officially_registered"]
                st.success("Demo data reset to initial state.")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AI ASSISTANT
# ─────────────────────────────────────────────────────────────────────────────

def page_ai_assistant():
    topbar("AI Assistant", "Personalised thesis advisor")

    if st.session_state.pop("_ai_input_clear", False):
        st.session_state["ai_input_box"] = ""

    from src.agents.faq_agent import chat, build_student_context

    st.markdown("""
    <div style="font-size:0.83rem;color:var(--mut);margin-bottom:1rem">
    Ask anything about HSG thesis requirements, how to approach professors, research methodology,
    or get personalised advice based on your profile. Answers are tailored to your situation.
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    suggestions = [
        "When should I start looking for a supervisor?",
        "What should I include in my thesis proposal?",
        "How do I approach a professor I've never met?",
        "What's the difference between a Bachelor and Master thesis at HSG?",
        "Can I co-supervise with a company?",
    ]
    st.markdown('<div style="font-size:0.75rem;color:var(--mut);margin-bottom:6px">Suggested questions:</div>', unsafe_allow_html=True)
    sugg_cols = st.columns(len(suggestions))
    for j, (col, sq) in enumerate(zip(sugg_cols, suggestions)):
        with col:
            if st.button(sq, key=f"sugg_{j}"):
                s.ai_chat_history.append({"role": "user", "content": sq})
                with ai_spinner("Thinking…"):
                    ctx_str = build_student_context(s)
                    reply = chat(sq, s.ai_chat_history[:-1], ctx_str)
                s.ai_chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    st.markdown('<div style="border-top:1px solid var(--bdr);margin:0.8rem 0 1rem"></div>', unsafe_allow_html=True)

    # Chat history display
    if not s.ai_chat_history:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;color:var(--mut);font-size:0.85rem">
          No messages yet — ask a question above or type below.
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in s.ai_chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:10px">
                  <div style="background:var(--gl);border:1px solid var(--gm);padding:0.55rem 0.85rem;
                              max-width:75%;font-size:0.85rem;color:var(--txt);line-height:1.5">
                    {msg["content"]}
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start">
                  <div style="width:28px;height:28px;background:#0D3320;flex-shrink:0;
                              display:flex;align-items:center;justify-content:center;
                              font-size:0.62rem;font-weight:700;color:white">AI</div>
                  <div style="background:var(--bg);border:1px solid var(--bdr);padding:0.55rem 0.85rem;
                              max-width:82%;font-size:0.85rem;color:var(--txt);line-height:1.6">
                    {msg["content"]}
                  </div>
                </div>""", unsafe_allow_html=True)

    # Input area
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    user_input = st.text_area(
        "Your question",
        height=80,
        placeholder="e.g. How many weeks before my thesis start do I need to confirm my supervisor?",
        key="ai_input_box",
        label_visibility="collapsed",
    )
    col_send, col_clear = st.columns([6, 1])
    with col_send:
        if st.button("Send →", type="primary", key="ai_send_btn"):
            if user_input.strip():
                s.ai_chat_history.append({"role": "user", "content": user_input.strip()})
                with ai_spinner("Thinking…"):
                    ctx_str = build_student_context(s)
                    reply = chat(user_input.strip(), s.ai_chat_history[:-1], ctx_str)
                s.ai_chat_history.append({"role": "assistant", "content": reply})
                st.session_state["_ai_input_clear"] = True
                st.rerun()
    with col_clear:
        if st.button("Clear", key="ai_clear_btn"):
            s.ai_chat_history = []; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PROFESSOR PAGES
# ─────────────────────────────────────────────────────────────────────────────

def page_prof_home():
    topbar("Professor Dashboard")
    prof_display = f"{s.prof_title} {s.prof_name}" if s.prof_name else "Professor"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#006B2B,#009640);
                padding:1.2rem 1.5rem;color:white;margin-bottom:0.7rem">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.08em;opacity:0.7;margin-bottom:4px">Faculty Portal</div>
      <div style="font-size:1.1rem;font-weight:700;margin-bottom:5px">Welcome, {prof_display}</div>
      <div style="font-size:0.82rem;opacity:0.85">{s.prof_dept} &middot; {s.prof_email}</div>
    </div>
    """, unsafe_allow_html=True)

    docs_count = len(s.prof_uploaded_docs)
    faq_count  = len(s.prof_faq_bank)

    ico_upload = '<svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#009640" stroke-width="1.6"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-linecap="square"/><polyline points="17 8 12 3 7 8" stroke-linecap="square" stroke-linejoin="miter"/><line x1="12" y1="3" x2="12" y2="15" stroke-linecap="square"/></svg>'
    ico_students = '<svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#009640" stroke-width="1.6"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-linecap="square"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke-linecap="square"/></svg>'
    ico_faq = '<svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#009640" stroke-width="1.6"><circle cx="12" cy="12" r="10"/><path d="M9 9a3 3 0 1 1 4 2.83V13M12 17h.01" stroke-linecap="square"/></svg>'
    ico_msg2 = '<svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#009640" stroke-width="1.6"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-linejoin="miter"/></svg>'

    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.markdown(f"""
        <div class="dash-card">
          {ico_upload}
          <div class="dash-card-title">Upload Documents</div>
          <div class="dash-card-body">Upload syllabi, thesis themes, FAQ sheets. AI extracts structured info for students.{"<br><strong style='color:var(--g)'>"+str(docs_count)+" document"+("s" if docs_count!=1 else "")+" uploaded</strong>" if docs_count else ""}</div>
          <div class="dash-arrow"><span>Upload &amp; extract</span><span>→</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(" ", key="ph_upload", use_container_width=True):
            st.session_state["_nav_target"] = "Upload Documents"; st.rerun()

    with c2:
        st.markdown(f"""
        <div class="dash-card">
          {ico_students}
          <div class="dash-card-title">Student Applications</div>
          <div class="dash-card-body">Review and reply to students interested in your thesis proposals. Use AI to draft replies from your documents.</div>
          <div class="dash-arrow"><span>View applications</span><span>→</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(" ", key="ph_apps", use_container_width=True):
            st.session_state["_nav_target"] = "Messages"; st.rerun()

    with c3:
        st.markdown(f"""
        <div class="dash-card">
          {ico_faq}
          <div class="dash-card-title">Auto-Answer Bank</div>
          <div class="dash-card-body">Q&amp;A entries extracted from your documents. Used to auto-draft replies to common student questions.{"<br><strong style='color:var(--g)'>"+str(faq_count)+" entries</strong>" if faq_count else ""}</div>
          <div class="dash-arrow"><span>View FAQ bank</span><span>→</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(" ", key="ph_faq", use_container_width=True):
            st.session_state["_nav_target"] = "Upload Documents"; st.rerun()


def page_upload_documents():
    topbar("Upload Documents", "AI extracts thesis info automatically")

    st.markdown("""
    <div style="font-size:0.83rem;color:var(--mut);margin-bottom:1.2rem">
    Upload any file — thesis theme descriptions, course syllabi, FAQ sheets, exercise sets, research proposals.<br>
    <span style="color:var(--acc);font-weight:500">The information will be used to answer students' questions automatically when they chat with your AI assistant.</span><br><br>
    The AI reads it and extracts thesis topics, requirements, and FAQ entries automatically.
    Supports PDF, Word (.docx), and plain text files.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt", "md"],
        key="prof_doc_uploader",
        label_visibility="collapsed",
    )

    if uploaded:
        with ai_spinner(f"Reading {uploaded.name} and extracting information…"):
            try:
                from src.agents.professor_import_agent import extract_text_from_file, import_professor_document
                raw_text = extract_text_from_file(uploaded)
                prof_name = f"{s.prof_title} {s.prof_name}" if s.prof_name else "Professor"
                result = import_professor_document(raw_text, prof_name, uploaded.name)
                # Store in session
                s.prof_uploaded_docs.append(result)
                # Merge FAQ entries into the FAQ bank
                for entry in result.get("faq_entries", []):
                    s.prof_faq_bank.append(entry)
                st.success(f"Extracted from {uploaded.name}: {result.get('summary','Done.')}")
            except Exception as e:
                st.error(f"Could not process file: {e}")

    if s.prof_uploaded_docs:
        st.markdown('<div class="sec-head">Extracted documents</div>', unsafe_allow_html=True)
        for i, doc in enumerate(s.prof_uploaded_docs):
            with st.expander(f"{doc.get('document_name','Document')} — {doc.get('document_type','').replace('_',' ').title()}", expanded=(i == 0)):
                st.markdown(f'<div style="font-size:0.82rem;color:var(--mut);margin-bottom:8px">{doc.get("summary","")}</div>', unsafe_allow_html=True)

                proposals = doc.get("thesis_proposals", [])
                if proposals:
                    st.markdown('<div class="sec-head">Thesis proposals extracted</div>', unsafe_allow_html=True)
                    for p in proposals:
                        st.markdown(f"""
                        <div style="border:1px solid var(--bdr);padding:0.8rem 1rem;margin-bottom:0.5rem">
                          <div style="font-weight:600;font-size:0.88rem">{p.get('title','')}</div>
                          <div style="font-size:0.8rem;color:var(--mut);margin-top:3px">{p.get('level','')} · {p.get('methodology','')}</div>
                          <div style="font-size:0.82rem;color:var(--sub);margin-top:4px">{p.get('description','')}</div>
                          {"<div style='font-size:0.78rem;color:var(--mut);margin-top:4px'><strong>Requirements:</strong> "+p.get('requirements','')+"</div>" if p.get('requirements') else ""}
                        </div>""", unsafe_allow_html=True)

                faqs = doc.get("faq_entries", [])
                if faqs:
                    st.markdown('<div class="sec-head">FAQ entries extracted</div>', unsafe_allow_html=True)
                    for faq in faqs:
                        st.markdown(f"""
                        <div style="padding:0.6rem 0;border-bottom:1px solid var(--bdr)">
                          <div style="font-size:0.84rem;font-weight:600;color:var(--txt)">Q: {faq.get('question','')}</div>
                          <div style="font-size:0.82rem;color:var(--sub);margin-top:3px">A: {faq.get('answer','')}</div>
                        </div>""", unsafe_allow_html=True)

                topics = doc.get("key_topics", [])
                reqs   = doc.get("requirements", [])
                if topics or reqs:
                    cols = st.columns(2)
                    with cols[0]:
                        if topics:
                            st.markdown('<div style="font-size:0.78rem;font-weight:600;color:var(--mut);margin-bottom:4px">Key topics</div>', unsafe_allow_html=True)
                            st.markdown("".join(f'<span class="tag tg">{t}</span>' for t in topics), unsafe_allow_html=True)
                    with cols[1]:
                        if reqs:
                            st.markdown('<div style="font-size:0.78rem;font-weight:600;color:var(--mut);margin-bottom:4px">Requirements</div>', unsafe_allow_html=True)
                            for r in reqs:
                                st.markdown(f'<div style="font-size:0.8rem;color:var(--sub);margin-bottom:2px">· {r}</div>', unsafe_allow_html=True)

                if st.button("Remove", key=f"rm_doc_{i}"):
                    s.prof_uploaded_docs.pop(i)
                    st.rerun()

    if s.prof_faq_bank:
        st.markdown('<div class="sec-head">Full auto-answer bank ({} entries)'.format(len(s.prof_faq_bank)) + '</div>', unsafe_allow_html=True)
        for j, faq in enumerate(s.prof_faq_bank):
            st.markdown(f"""
            <div style="padding:0.55rem 0;border-bottom:1px solid var(--bdr)">
              <div style="font-size:0.83rem;font-weight:500">Q: {faq.get('question','')}</div>
              <div style="font-size:0.8rem;color:var(--mut);margin-top:2px">A: {faq.get('answer','')}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROFESSOR AI CHAT  (student ↔ professor's AI)
# ─────────────────────────────────────────────────────────────────────────────

def page_professor_ai_chat():
    prof_name = s.active_prof_ai_chat or "Professor"
    initials = "".join(w[0] for w in prof_name.replace("Prof. Dr. ","").replace("Prof. Ph.D. ","").split()[:2]).upper()

    # Back button
    if st.button("← Back to messages", key="back_prof_ai"):
        st.session_state["_nav_target"] = "Messages"; st.rerun()

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:0.9rem 0;
                border-bottom:1px solid var(--bdr);margin-bottom:1rem">
      <div style="width:32px;height:32px;background:#0D3320;display:flex;align-items:center;
                  justify-content:center;font-size:0.72rem;font-weight:700;color:white;flex-shrink:0">AI</div>
      <div>
        <div style="font-weight:600;font-size:0.9rem">AI Assistant — {prof_name}</div>
        <div style="font-size:0.72rem;color:var(--mut)">
          Answers based on {prof_name.split()[-1]}'s uploaded documents and research profile.
          Ask about thesis requirements, methodology expectations, research topics, or availability.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Build professor knowledge context from uploaded docs
    # In a real system this would be fetched from DB by prof_name.
    # For now we use whatever the current session has (demo: assume docs are loaded).
    def _prof_context_for(name: str) -> str:
        """Assemble knowledge context for the professor AI."""
        parts = []
        # From uploaded docs in session (professor's own session would populate this)
        for doc in s.prof_uploaded_docs:
            if doc.get("raw_insights"):
                parts.append(doc["raw_insights"])
            for entry in doc.get("faq_entries", []):
                parts.append(f"Q: {entry['question']}\nA: {entry['answer']}")
            for prop in doc.get("thesis_proposals", []):
                parts.append(
                    f"Thesis proposal: {prop.get('title','')} — {prop.get('description','')} "
                    f"[Level: {prop.get('level','')}] [Method: {prop.get('methodology','')}] "
                    f"[Requirements: {prop.get('requirements','')}]"
                )

        # Enrich from professor_profiles.json
        prof_data = next((p for p in PROFESSORS if name in p.get("name","")), {})
        if prof_data:
            focus = prof_data.get("focus") or []
            if isinstance(focus, str): focus = [focus]
            parts.append(f"Research focus: {', '.join(focus)}")
            for pub in (prof_data.get("publications") or [])[:3]:
                parts.append(f"Publication: {pub.get('title','')} ({pub.get('year','')})")
            for prop in (prof_data.get("proposals") or []):
                parts.append(f"Open thesis proposal: {prop}")
            for course in (prof_data.get("courses") or []):
                parts.append(f"Course taught: {course}")

        return "\n".join(parts) if parts else ""

    prof_ctx = _prof_context_for(prof_name)

    ctx_block = ("PROFESSOR CONTEXT:\n" + prof_ctx) if prof_ctx else "No documents uploaded yet — answer based on general HSG thesis guidelines."
    system = (
        f"You are the AI assistant for {prof_name} at the University of St. Gallen (HSG). "
        "Students ask you questions about working with this professor on their thesis. "
        "You answer based on the professor's research profile, uploaded documents, and known thesis proposals. "
        "Be concrete, helpful, and concise. If you don't know something specific, say so honestly. "
        "Do NOT invent information about the professor — only use what is provided.\n\n"
        + ctx_block
    )

    # Chat history for this specific professor
    if prof_name not in s.prof_ai_chats:
        s.prof_ai_chats[prof_name] = []
    history = s.prof_ai_chats[prof_name]

    # Suggested starter questions
    if not history:
        suggestions = [
            "What thesis topics are you currently supervising?",
            "What methodology do you prefer for Master theses?",
            "What background should I have before reaching out?",
            "How many students do you supervise per year?",
            "What should I include in my initial email to you?",
        ]
        st.markdown('<div style="font-size:0.75rem;color:var(--mut);margin-bottom:6px">Suggested questions:</div>', unsafe_allow_html=True)
        s_cols = st.columns(len(suggestions))
        for j, (col, sq) in enumerate(zip(s_cols, suggestions)):
            with col:
                if st.button(sq, key=f"prof_sugg_{j}"):
                    history.append({"role": "user", "content": sq})
                    with ai_spinner("Answering…"):
                        from src.agents.professor_chat_agent import ask_professor_ai
                        reply = ask_professor_ai(sq, history[:-1], system)
                    history.append({"role": "assistant", "content": reply})
                    s.prof_ai_chats[prof_name] = history
                    st.rerun()
        st.markdown('<div style="border-top:1px solid var(--bdr);margin:0.8rem 0 1rem"></div>', unsafe_allow_html=True)

    # Display chat
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin-bottom:10px">
              <div style="background:var(--gl);border:1px solid var(--gm);padding:0.55rem 0.85rem;
                          max-width:78%;font-size:0.85rem;color:var(--txt);line-height:1.5">
                {msg["content"]}
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start">
              <div style="width:28px;height:28px;background:#0D3320;flex-shrink:0;
                          display:flex;align-items:center;justify-content:center;
                          font-size:0.6rem;font-weight:700;color:white">AI</div>
              <div style="background:var(--bg);border:1px solid var(--bdr);padding:0.55rem 0.85rem;
                          max-width:82%;font-size:0.85rem;color:var(--txt);line-height:1.6">
                {msg["content"]}
              </div>
            </div>""", unsafe_allow_html=True)

    # Input
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    user_q = st.text_area(
        "Ask a question",
        height=75,
        placeholder=f"e.g. What data sources do you recommend for a thesis on corporate governance?",
        key="prof_ai_input",
        label_visibility="collapsed",
    )
    col_ask, col_clr = st.columns([5, 1])
    with col_ask:
        if st.button("Ask →", type="primary", key="prof_ai_ask"):
            if user_q.strip():
                q = user_q.strip()
                history.append({"role": "user", "content": q})
                with ai_spinner("Answering…"):
                    try:
                        from src.agents.professor_chat_agent import ask_professor_ai
                        reply = ask_professor_ai(q, history[:-1], system)
                    except Exception as e:
                        reply = f"[Error: {e}]"
                history.append({"role": "assistant", "content": reply})
                s.prof_ai_chats[prof_name] = history
                st.rerun()
    with col_clr:
        if st.button("Clear", key="prof_ai_clr"):
            s.prof_ai_chats[prof_name] = []; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FEEDBACK
# ─────────────────────────────────────────────────────────────────────────────

def page_feedback():
    conv_key = s.feedback_target
    if not conv_key:
        st.session_state["_nav_target"] = "Messages"; st.rerun()

    prof_name = conv_key[0] if conv_key else "Professor"
    topbar("Leave Feedback", f"Your experience with {prof_name}")

    existing = s.student_feedback.get(conv_key)

    if existing:
        stars = "★" * existing["rating"] + "☆" * (5 - existing["rating"])
        st.markdown(f"""
        <div style="background:var(--gp);border:1px solid var(--gm);padding:1.2rem 1.4rem;
                    max-width:540px;margin-bottom:1rem">
          <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                      color:var(--mut);margin-bottom:6px">Your feedback</div>
          <div style="font-size:1.3rem;color:#facc15;margin-bottom:6px">{stars}</div>
          <div style="font-size:0.88rem;color:var(--txt);line-height:1.6">{existing['text']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Edit feedback", key="edit_fb"):
            del s.student_feedback[conv_key]; st.rerun()
        if st.button("← Back to messages", key="fb_back"):
            st.session_state["_nav_target"] = "Messages"; st.rerun()
        return

    st.markdown(f"""
    <div style="font-size:0.85rem;color:var(--mut);margin-bottom:1.4rem">
    Your feedback helps future students find the right supervisor. Ratings are anonymous.
    </div>
    """, unsafe_allow_html=True)

    rating = st.select_slider(
        "Overall supervision experience",
        options=[1, 2, 3, 4, 5],
        value=5,
        format_func=lambda x: "★" * x + "☆" * (5 - x),
        key="fb_rating",
    )

    criteria = {
        "Availability & responsiveness": st.select_slider("Availability & responsiveness", [1,2,3,4,5], value=4, format_func=lambda x: "★"*x+"☆"*(5-x), key="fb_avail"),
        "Academic guidance quality":     st.select_slider("Academic guidance quality",     [1,2,3,4,5], value=5, format_func=lambda x: "★"*x+"☆"*(5-x), key="fb_guid"),
        "Feedback on drafts":            st.select_slider("Feedback on drafts",            [1,2,3,4,5], value=4, format_func=lambda x: "★"*x+"☆"*(5-x), key="fb_draft"),
    }

    fb_text = st.text_area(
        "Written review (optional)",
        height=110,
        placeholder=f"What was your experience working with {prof_name}? What advice would you give to future students?",
        key="fb_text_input",
    )

    col_sub, col_back = st.columns([2, 3])
    with col_sub:
        if st.button("Submit feedback", type="primary", key="submit_fb"):
            s.student_feedback[conv_key] = {"rating": rating, "criteria": criteria, "text": fb_text.strip()}
            st.success("Thank you — your feedback has been saved.")
            st.rerun()
    with col_back:
        if st.button("← Back to messages", key="fb_back2"):
            st.session_state["_nav_target"] = "Messages"; st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: THESIS PROJECT  (Trello-style timeline)
# ─────────────────────────────────────────────────────────────────────────────

import datetime as _datetime

def _build_thesis_tasks(submission_date: _datetime.date) -> list:
    """Generate timeline tasks backward from submission date."""
    sd = submission_date
    tasks = [
        # Phase 1 – Preparation
        {"id": "T01", "phase": "1 · Preparation", "title": "Choose supervisor",
         "desc": "Identify and contact a supervisor from active teaching staff.",
         "due": sd - _datetime.timedelta(weeks=20), "col": 0},
        {"id": "T02", "phase": "1 · Preparation", "title": "Agree on topic",
         "desc": "Discuss and finalise thesis topic with supervisor. Browse Topic Market Place (TMP).",
         "due": sd - _datetime.timedelta(weeks=18), "col": 0},
        {"id": "T03", "phase": "1 · Preparation", "title": "Coordinate details",
         "desc": "Agree on title, language, and expected defence date.",
         "due": sd - _datetime.timedelta(weeks=16), "col": 0},
        # Phase 2 – Registration
        {"id": "T04", "phase": "2 · Registration", "title": "Submit registration on TMP",
         "desc": "Submit thesis registration via the Thesis Management Platform dashboard.",
         "due": sd - _datetime.timedelta(weeks=14), "col": 1},
        {"id": "T05", "phase": "2 · Registration", "title": "Supervisor approval",
         "desc": "Registration auto-forwarded to supervisor for review and approval.",
         "due": sd - _datetime.timedelta(weeks=13), "col": 1},
        {"id": "T06", "phase": "2 · Registration", "title": "Programme approval",
         "desc": "Programme office confirms registration — binding deadline is set.",
         "due": sd - _datetime.timedelta(weeks=12), "col": 1},
        # Phase 3 – Writing
        {"id": "T07", "phase": "3 · Writing", "title": "Start writing",
         "desc": "Begin thesis aligned with agreed format and citation style.",
         "due": sd - _datetime.timedelta(weeks=11), "col": 2},
        {"id": "T08", "phase": "3 · Writing", "title": "Request any changes",
         "desc": "If needed, request changes to title, topic, language, or field via TMP.",
         "due": sd - _datetime.timedelta(weeks=6), "col": 2},
        {"id": "T09", "phase": "3 · Writing", "title": "Request extension (if needed)",
         "desc": "Deadline extension max 2×+3 months — must be requested 7 days before deadline.",
         "due": sd - _datetime.timedelta(weeks=2), "col": 2},
        {"id": "T10", "phase": "3 · Writing", "title": "Declaration of authorship",
         "desc": "Confirm and sign declaration of authorship before submission.",
         "due": sd - _datetime.timedelta(days=3), "col": 2},
        # Phase 4 – Submission
        {"id": "T11", "phase": "4 · Submission", "title": "Submit electronically",
         "desc": "Upload via TMP — max 40 MB, with metadata. Late = grade 1.00.",
         "due": sd, "col": 3},
        # Phase 5 – Assessment
        {"id": "T12", "phase": "5 · Assessment", "title": "Grading & report",
         "desc": "Supervisor grades and uploads assessment report to TMP.",
         "due": sd + _datetime.timedelta(weeks=4), "col": 4},
        {"id": "T13", "phase": "5 · Assessment", "title": "Grade published",
         "desc": "Grade published on one of 4 defined dates per year.",
         "due": sd + _datetime.timedelta(weeks=8), "col": 4},
        # Phase 6 – Publication
        {"id": "T14", "phase": "6 · Publication", "title": "Published in EDOK",
         "desc": "Bachelor ≥5.5 and all Master theses published in HSG library database.",
         "due": sd + _datetime.timedelta(weeks=12), "col": 5},
    ]
    # Add status based on today
    today = _datetime.date.today()
    for t in tasks:
        if today > t["due"]:
            t["default_done"] = True
        else:
            t["default_done"] = False
    return tasks


def page_thesis_project(embedded=False):
    if not embedded:
        topbar("Thesis Timeline", "Track your milestones from preparation to publication")

    # ── Setup: pick submission date ──────────────────────────────────────────
    if not s.thesis_submission_date:
        st.markdown("""
        <div style="max-width:480px;margin:2rem auto;text-align:center">
          <div style="font-size:1.15rem;font-weight:700;color:var(--txt);margin-bottom:6px">When do you plan to submit?</div>
          <div style="font-size:0.84rem;color:var(--mut);margin-bottom:1.4rem">
            Enter your target submission date. We'll build your full thesis timeline automatically
            based on the official HSG thesis process (preparation → registration → writing → submission → assessment → publication).
          </div>
        </div>
        """, unsafe_allow_html=True)
        col_c, col_d, col_e = st.columns([1, 2, 1])
        with col_d:
            sub_date = st.date_input(
                "Target submission date",
                value=_datetime.date.today() + _datetime.timedelta(weeks=20),
                min_value=_datetime.date.today(),
                key="thesis_sub_date_input",
            )
            if st.button("Build my timeline →", type="primary", key="build_timeline_btn", use_container_width=True):
                s.thesis_submission_date = sub_date
                s.thesis_tasks = _build_thesis_tasks(sub_date)
                # Init done states
                for t in s.thesis_tasks:
                    key = f"task_done_{t['id']}"
                    if key not in st.session_state:
                        st.session_state[key] = t["default_done"]
                st.rerun()
        return

    tasks = s.thesis_tasks or _build_thesis_tasks(s.thesis_submission_date)
    if s.thesis_tasks is None:
        s.thesis_tasks = tasks

    today = _datetime.date.today()
    sub_date = s.thesis_submission_date
    days_left = (sub_date - today).days

    # ── Header bar ──────────────────────────────────────────────────────────
    done_count = sum(1 for t in tasks if st.session_state.get(f"task_done_{t['id']}", t["default_done"]))
    total = len(tasks)
    pct = int(done_count / total * 100)

    col_hdr1, col_hdr2 = st.columns([4, 1])
    with col_hdr1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:0.4rem">
          <div>
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:var(--mut)">Submission target</div>
            <div style="font-size:1.05rem;font-weight:700;color:var(--txt)">{sub_date.strftime("%d %B %Y")}</div>
          </div>
          <div style="width:1px;height:36px;background:var(--bdr)"></div>
          <div>
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:var(--mut)">Days remaining</div>
            <div style="font-size:1.05rem;font-weight:700;color:{'#EF4444' if days_left < 30 else 'var(--g)'}">{max(days_left,0)} days</div>
          </div>
          <div style="width:1px;height:36px;background:var(--bdr)"></div>
          <div style="flex:1">
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:var(--mut);margin-bottom:4px">Overall progress — {done_count}/{total} tasks</div>
            <div style="background:var(--bdr);height:6px">
              <div style="background:var(--g);width:{pct}%;height:6px;transition:width 0.3s"></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_hdr2:
        if st.button("Reset timeline", key="reset_timeline_btn"):
            s.thesis_submission_date = None
            s.thesis_tasks = None
            # Clear task states
            for t in tasks:
                key = f"task_done_{t['id']}"
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    # ── Trello board ─────────────────────────────────────────────────────────
    PHASES = [
        ("1 · Preparation", 0, "#EDE9FE", "#5B21B6"),
        ("2 · Registration", 1, "#DBEAFE", "#1D4ED8"),
        ("3 · Writing", 2, "#FEF3C7", "#92400E"),
        ("4 · Submission", 3, "#FEE2E2", "#991B1B"),
        ("5 · Assessment", 4, "#D1FAE5", "#065F46"),
        ("6 · Publication", 5, "#F3F4F6", "#374151"),
    ]

    cols = st.columns(len(PHASES), gap="small")

    for (phase_name, col_idx, bg, fg), col in zip(PHASES, cols):
        phase_tasks = [t for t in tasks if t["col"] == col_idx]
        with col:
            st.markdown(f"""
            <div style="background:{bg};padding:0.5rem 0.7rem;margin-bottom:0.6rem">
              <div style="font-size:0.72rem;font-weight:700;color:{fg};text-transform:uppercase;letter-spacing:0.05em">{phase_name}</div>
              <div style="font-size:0.65rem;color:{fg};opacity:0.7;margin-top:1px">{len(phase_tasks)} tasks</div>
            </div>
            """, unsafe_allow_html=True)

            for t in phase_tasks:
                task_key = f"task_done_{t['id']}"
                if task_key not in st.session_state:
                    st.session_state[task_key] = t["default_done"]
                is_done = st.session_state[task_key]

                due = t["due"]
                is_overdue = (not is_done) and (today > due)
                is_upcoming = (not is_done) and (0 <= (due - today).days <= 14)

                if is_done:
                    card_border = f"border-left:3px solid var(--g)"
                    card_bg = "background:#F0FDF4"
                    due_color = "var(--g)"
                elif is_overdue:
                    card_border = "border-left:3px solid #EF4444"
                    card_bg = "background:#FEF2F2"
                    due_color = "#EF4444"
                elif is_upcoming:
                    card_border = "border-left:3px solid #F59E0B"
                    card_bg = "background:#FFFBEB"
                    due_color = "#92400E"
                else:
                    card_border = "border-left:3px solid var(--bdr)"
                    card_bg = "background:var(--wh)"
                    due_color = "var(--mut)"

                title_style = "text-decoration:line-through;color:var(--mut)" if is_done else "color:var(--txt)"

                st.markdown(f"""
                <div style="{card_bg};{card_border};padding:0.65rem 0.75rem;
                            margin-bottom:0.5rem;border-top:1px solid var(--bdr);
                            border-right:1px solid var(--bdr);border-bottom:1px solid var(--bdr)">
                  <div style="font-size:0.8rem;font-weight:600;{title_style};margin-bottom:3px;line-height:1.3">{t['title']}</div>
                  <div style="font-size:0.71rem;color:var(--mut);line-height:1.45;margin-bottom:6px">{t['desc']}</div>
                  <div style="font-size:0.68rem;font-weight:600;color:{due_color}">
                    {'✓ Done · ' if is_done else ('⚠ Overdue · ' if is_overdue else ('◉ Due soon · ' if is_upcoming else '○ '))}
                    {due.strftime("%d %b %Y")}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                btn_label = "✓ Mark done" if not is_done else "↩ Undo"
                if st.button(btn_label, key=f"toggle_{t['id']}"):
                    st.session_state[task_key] = not is_done
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
section[data-testid="stSidebar"] { background-color: #377E39 !important; }
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.9rem !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: rgba(255,255,255,0.20) !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
    font-size: 0.75rem !important;
    opacity: 0.6 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.25) !important; }
</style>
""", unsafe_allow_html=True)

def _unpin(fn):
    """Wrap a page function so clicking it in the sidebar clears _pinned_page."""
    def _wrapper():
        st.session_state.pop("_pinned_page", None)
        fn()
    _wrapper.__name__ = fn.__name__
    return _wrapper

if s.role == "professor":
    nav = st.navigation({
        "Professor Portal": [
            st.Page(_unpin(page_prof_home),        title="Dashboard",            default=True),
            st.Page(_unpin(page_messages),         title="Student Applications"),
            st.Page(_unpin(page_upload_documents), title="Upload Documents"),
            st.Page(_unpin(page_ai_assistant),     title="AI Assistant"),
        ]
    }, position="sidebar")
else:
    nav = st.navigation({
        "Student Portal": [
            st.Page(_unpin(page_home),             title="Dashboard",        default=True),
        ],
        "Discover": [
            st.Page(_unpin(page_match),            title="Find Supervisor"),
            st.Page(_unpin(page_topics),           title="Thesis Topics"),
            st.Page(_unpin(page_professors),       title="Professors"),
        ],
        "My Work": [
            st.Page(_unpin(page_messages),         title="Messages"),
            st.Page(_unpin(page_ai_assistant),     title="AI Assistant"),
            st.Page(_unpin(page_profile),          title="My Profile"),
        ],
    }, position="sidebar")

with st.sidebar:
    st.divider()
    if s.role == "student":
        st.caption(f"{s.first_name} {s.last_name}".strip() or s.firebase_user.get("email", ""))
        st.caption(s.programme[:40] + "…" if len(s.programme) > 40 else s.programme)
    else:
        st.caption(f"{s.prof_title} {s.prof_name}".strip() or s.firebase_user.get("email", ""))
        st.caption(s.prof_dept or "HSG Faculty")
    if st.button("Log out", key="sidebar_logout_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Persistent programmatic navigation — survives internal reruns until the user
# clicks a real sidebar link (which sets _clear_pinned via nav page wrappers).
if st.session_state.get("_nav_target"):
    st.session_state["_pinned_page"] = st.session_state.pop("_nav_target")

_pinned = st.session_state.get("_pinned_page")
if _pinned:
    if   _pinned == "Home":               page_prof_home() if s.role == "professor" else page_home()
    elif _pinned == "Messages":           page_messages()
    elif _pinned == "Professors":         page_professors()
    elif _pinned == "Thesis Topics":      page_topics()
    elif _pinned == "My Profile":         page_profile()
    elif _pinned == "Upload Documents":   page_upload_documents()
    elif _pinned == "AI Assistant":       page_ai_assistant()
    elif _pinned == "Feedback":           page_feedback()
    elif _pinned == "Professor AI Chat":  page_professor_ai_chat()
    else:                                 st.session_state.pop("_pinned_page", None)
    st.stop()

nav.run()