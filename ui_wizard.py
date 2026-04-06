"""
Prototype A — Multi-step Wizard
HSG Thesis Supervisor Matching

Run: python3 -m streamlit run ui_wizard.py
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="HSG Thesis Match",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# HSG Green Design System
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Fonts & base ──────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 720px; }

/* ── HSG colours ───────────────────────────────────────────────── */
:root {
    --hsg-green: #009640;
    --hsg-dark:  #006B2B;
    --hsg-light: #E8F5EC;
    --hsg-mid:   #C6E8D0;
    --text:      #1A1A1A;
    --muted:     #666666;
    --border:    #E0E0E0;
    --white:     #FFFFFF;
}

/* ── Progress bar ──────────────────────────────────────────────── */
.progress-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2rem;
}
.progress-step {
    flex: 1;
    height: 4px;
    border-radius: 2px;
    background: var(--border);
    transition: background 0.3s;
}
.progress-step.done  { background: var(--hsg-green); }
.progress-step.active{ background: var(--hsg-green); opacity: 0.5; }

/* ── Step header ───────────────────────────────────────────────── */
.step-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--hsg-green);
    margin-bottom: 0.25rem;
}
.step-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.5rem;
    line-height: 1.2;
}
.step-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    margin-bottom: 1.8rem;
}

/* ── Input overrides ───────────────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] div {
    border-radius: 8px !important;
    border-color: var(--border) !important;
    font-size: 0.95rem !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: var(--hsg-green) !important;
    box-shadow: 0 0 0 3px rgba(0,150,64,0.12) !important;
}

/* ── Buttons ───────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    transition: all 0.2s;
}
.stButton > button[kind="primary"] {
    background: var(--hsg-green);
    color: white;
    padding: 0.65rem 1.6rem;
}
.stButton > button[kind="primary"]:hover {
    background: var(--hsg-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,150,64,0.3);
}

/* ── Result cards ──────────────────────────────────────────────── */
.match-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    background: var(--white);
    position: relative;
}
.match-card:hover {
    border-color: var(--hsg-green);
    box-shadow: 0 4px 16px rgba(0,150,64,0.12);
    transition: all 0.2s;
}
.match-rank {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    border-radius: 50%;
    background: var(--hsg-green);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 10px;
}
.match-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    display: inline;
}
.match-score {
    float: right;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--hsg-green);
}
.match-score span {
    font-size: 0.8rem;
    font-weight: 400;
    color: var(--muted);
}
.why-box {
    background: var(--hsg-light);
    border-left: 3px solid var(--hsg-green);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.9rem 0 0.7rem;
    font-size: 0.88rem;
    color: #1A3A1A;
    line-height: 1.55;
}
.why-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--hsg-dark);
    margin-bottom: 0.3rem;
}
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 500;
    margin: 2px 3px 2px 0;
}
.pill-green { background: var(--hsg-mid); color: var(--hsg-dark); }
.pill-warn  { background: #FFF3CD; color: #7A5C00; }

/* ── Score bars ────────────────────────────────────────────────── */
.score-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
    font-size: 0.8rem;
    color: var(--muted);
}
.score-bar-bg {
    flex: 1;
    height: 5px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: var(--hsg-green);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RESEARCH_AREAS = [
    "Finance/Banking", "Economics", "Strategic Management", "Marketing",
    "Supply Chain Management", "Sustainability", "Entrepreneurship",
    "International Business", "Accounting", "Human Resources Management",
    "Operations Management", "Political Science", "Law & Economics",
    "Behavioral Economics", "Data Science / Machine Learning",
    "Health Economics", "Ethics", "Other",
]

PROGRAMMES = [
    "Master in Accounting and Finance (MAccFin)",
    "Master in Banking and Finance (MBF)",
    "Master in Business Innovation (MBI)",
    "Master in Economics (MEcon)",
    "Master in Finance (MF)",
    "Master in General Management (MGM)",
    "Master in Strategy and International Management (SIM)",
    "Master in Quantitative Economics and Finance (MQE)",
    "Bachelor of Arts HSG in Business Administration",
    "Bachelor of Arts HSG in Economics",
    "Bachelor of Arts HSG in International Affairs",
]

OBJECTIVES_MAP = {
    "topic":            "I am looking for a thesis topic",
    "supervision":      "I am looking for a supervisor",
    "career_start":     "I hope this thesis leads to a job/internship",
    "industry_access":  "I want a company as a collaboration partner",
    "project_guidance": "I need help structuring / managing my project",
}

STEPS = ["You", "Your Thesis", "Approach", "Goals", "Match"]

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
def _init():
    defaults = dict(
        step=0,
        first_name="", last_name="", email="",
        level="Master", programme=PROGRAMMES[0],
        research_area=RESEARCH_AREAS[0],
        thesis_title="", research_question="", motivation="",
        approach="", relevant_courses="",
        skills="", keywords="",
        objectives=[], language="English", about="", additional_notes="",
        results=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------
def _progress():
    step = st.session_state.step
    html = '<div class="progress-wrap">'
    for i in range(len(STEPS)):
        cls = "done" if i < step else ("active" if i == step else "")
        html += f'<div class="progress-step {cls}"></div>'
    html += "</div>"
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(html, unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div style="text-align:right;font-size:0.8rem;color:#666;padding-top:4px">'
            f'Step {step+1} of {len(STEPS)}</div>',
            unsafe_allow_html=True,
        )

def _header(label, title, subtitle=""):
    st.markdown(f'<div class="step-label">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="step-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def _nav(back=True, next_label="Next →", next_key="next"):
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1] if back else [3, 1])
    if back:
        if cols[0].button("← Back", key=f"back_{next_key}"):
            st.session_state.step -= 1
            st.rerun()
        if cols[1].button(next_label, type="primary", key=next_key):
            return True
    else:
        if cols[1].button(next_label, type="primary", key=next_key):
            return True
    return False

# ---------------------------------------------------------------------------
# Step 0 — Identity
# ---------------------------------------------------------------------------
def step_you():
    _header("Step 1 of 5", "Tell us about yourself",
            "We'll use this to personalise your supervisor recommendations.")
    s = st.session_state
    c1, c2 = st.columns(2)
    s.first_name = c1.text_input("First name", value=s.first_name)
    s.last_name  = c2.text_input("Last name",  value=s.last_name)
    s.email      = st.text_input("HSG email", value=s.email,
                                  placeholder="firstname.lastname@student.unisg.ch")

    s.level = st.radio("Degree level", ["Bachelor", "Master"], horizontal=True,
                        index=0 if s.level == "Bachelor" else 1)

    filtered = [p for p in PROGRAMMES if s.level.lower() in p.lower()]
    idx = filtered.index(s.programme) if s.programme in filtered else 0
    s.programme = st.selectbox("Programme", filtered, index=idx)

    if _nav(back=False, next_label="Next →", next_key="step0_next"):
        if not s.first_name or not s.last_name or not s.email:
            st.error("Please fill in your name and email.")
        else:
            st.session_state.step = 1
            st.rerun()

# ---------------------------------------------------------------------------
# Step 1 — Thesis
# ---------------------------------------------------------------------------
def step_thesis():
    _header("Step 2 of 5", "Your thesis",
            "The more specific you are, the better your matches will be.")
    s = st.session_state
    s.thesis_title = st.text_input("Working title or topic",
        value=s.thesis_title, placeholder="e.g. The effect of board diversity on firm performance")

    s.research_area = st.selectbox("Research area", RESEARCH_AREAS,
        index=RESEARCH_AREAS.index(s.research_area) if s.research_area in RESEARCH_AREAS else 0)

    s.research_question = st.text_area("Research question(s)",
        value=s.research_question, height=100,
        placeholder="What specific question do you want to answer?")

    s.motivation = st.text_area("Motivation",
        value=s.motivation, height=90,
        placeholder="Why does this topic matter to you?")

    if _nav(next_label="Next →", next_key="step1_next"):
        if not s.thesis_title or not s.research_question:
            st.error("Working title and research question are required.")
        else:
            st.session_state.step = 2
            st.rerun()

# ---------------------------------------------------------------------------
# Step 2 — Approach
# ---------------------------------------------------------------------------
def step_approach():
    _header("Step 3 of 5", "Your approach",
            "This helps match you with professors who use compatible methods.")
    s = st.session_state

    s.approach = st.text_area("Planned methodology",
        value=s.approach, height=100,
        placeholder="e.g. Quantitative analysis of panel data using Compustat, regression / IV")

    s.relevant_courses = st.text_input("Relevant courses you've taken",
        value=s.relevant_courses,
        placeholder="e.g. Econometrics, Corporate Finance, Game Theory")

    s.skills = st.text_input("Key skills (comma-separated)",
        value=s.skills,
        placeholder="e.g. Python, R, Stata, qualitative research, financial modelling")

    s.keywords = st.text_input("3–5 keywords describing your topic (comma-separated)",
        value=s.keywords,
        placeholder="e.g. corporate governance, board diversity, firm performance")

    if _nav(next_label="Next →", next_key="step2_next"):
        st.session_state.step = 3
        st.rerun()

# ---------------------------------------------------------------------------
# Step 3 — Goals
# ---------------------------------------------------------------------------
def step_goals():
    _header("Step 4 of 5", "Your goals & preferences")
    s = st.session_state

    st.markdown("**What are you looking for?** *(select all that apply)*")
    chosen = []
    cols = st.columns(2)
    for i, (key, label) in enumerate(OBJECTIVES_MAP.items()):
        col = cols[i % 2]
        if col.checkbox(label, value=key in s.objectives, key=f"obj_{key}"):
            chosen.append(key)
    s.objectives = chosen

    s.language = st.radio("Preferred thesis language", ["English", "German", "French"],
                           horizontal=True)
    s.about = st.text_area("Short bio (optional — shown to supervisors)",
        value=s.about or "", height=80,
        placeholder="2–3 sentences about your background and thesis goals")
    s.additional_notes = st.text_input("Anything else? (optional)",
        value=s.additional_notes, placeholder="Deadline, co-supervision interest, etc.")

    if _nav(next_label="Find my supervisor →", next_key="step3_next"):
        st.session_state.step = 4
        st.rerun()

# ---------------------------------------------------------------------------
# Demo results (no API needed)
# ---------------------------------------------------------------------------
DEMO_RESULTS = [
    {
        "name": "Prof. Dr. Markus Schmid",
        "score": 9.1, "topic_fit": 9, "method_fit": 9,
        "summary": (
            "Your thesis on board diversity and firm performance maps directly onto "
            "Prof. Schmid's core research agenda in corporate governance and executive compensation. "
            "He regularly supervises empirical work using financial databases like Compustat and Datastream, "
            "which aligns precisely with your stated quantitative approach."
        ),
        "strengths": [
            "Published extensively on board structures and governance outcomes",
            "Supervises panel data / regression-based empirical theses",
            "Has an open proposal on ESG and board composition",
        ],
        "red_flags": [],
    },
    {
        "name": "Prof. Dr. Björn Ambos",
        "score": 7.4, "topic_fit": 7, "method_fit": 8,
        "summary": (
            "Prof. Ambos focuses on international strategy and HQ–subsidiary dynamics, "
            "which partially overlaps with the governance dimension of your thesis if you "
            "include cross-country comparisons. His methodological approach is strongly empirical, "
            "matching your planned methods, but the primary topic fit is moderate."
        ),
        "strengths": [
            "Strong empirical methodology — panel data, survey data",
            "Cross-country governance research if scope is international",
        ],
        "red_flags": [
            "Core focus is international management, not corporate governance — confirm overlap before reaching out",
        ],
    },
    {
        "name": "Prof. Dr. Simone Westerfeld",
        "score": 6.8, "topic_fit": 6, "method_fit": 8,
        "summary": (
            "Prof. Westerfeld's work on banking regulation and financial intermediation shares "
            "methodological common ground with your project. The topic fit is indirect, "
            "but if your thesis has a financial sector angle she could be a strong supervisor."
        ),
        "strengths": [
            "Expert in empirical corporate finance methods",
            "Open to cross-disciplinary supervision",
        ],
        "red_flags": [
            "Research focus is on banking/regulation, not board governance specifically",
        ],
    },
]

def _render_result(i, r):
    score_pct  = int(r["score"] / 10 * 100)
    topic_pct  = int(r["topic_fit"] / 10 * 100)
    method_pct = int(r["method_fit"] / 10 * 100)

    strengths_html = "".join(
        f'<span class="pill pill-green">✓ {s}</span>' for s in r["strengths"]
    )
    flags_html = "".join(
        f'<span class="pill pill-warn">⚠ {f}</span>' for f in r["red_flags"]
    ) if r["red_flags"] else ""

    st.markdown(f"""
    <div class="match-card">
      <div>
        <span class="match-rank">{i}</span>
        <span class="match-name">{r["name"]}</span>
        <span class="match-score">{r["score"]}<span>/10</span></span>
      </div>

      <div class="score-row" style="margin-top:10px">
        <span style="width:110px">Topic fit</span>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{topic_pct}%"></div></div>
        <span style="width:28px;text-align:right">{r["topic_fit"]}</span>
      </div>
      <div class="score-row">
        <span style="width:110px">Method fit</span>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{method_pct}%"></div></div>
        <span style="width:28px;text-align:right">{r["method_fit"]}</span>
      </div>

      <div class="why-box">
        <div class="why-label">Why this supervisor?</div>
        {r["summary"]}
      </div>

      <div style="margin-top:8px">{strengths_html}</div>
      {"<div style='margin-top:6px'>" + flags_html + "</div>" if flags_html else ""}
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Step 4 — Results
# ---------------------------------------------------------------------------
def step_results():
    s = st.session_state

    if s.results is None:
        # Show loading state
        _header("Finding your match", "Analysing professor profiles…",
                "This takes about 20–30 seconds.")

        with st.spinner("Running semantic search + AI analysis…"):
            # Try real matching; fall back to demo data
            try:
                import os
                if not os.environ.get("OPENAI_API_KEY"):
                    raise RuntimeError("No API key — using demo results")

                from src.data_collection.questionnaire import _build_description
                from src.models.student import StudentProfile
                from src.data_collection.scrapers.constants import RESEARCH_AREA_TO_FIELD_IDS
                from src.data_processing.profile_builder import ProfileStore
                from src.matching.matcher import ThesisMatcher

                thesis_description = _build_description(
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
                    thesis_description=thesis_description,
                    skills=[x.strip() for x in s.skills.split(",") if x.strip()],
                    about=s.about or None,
                    objectives=s.objectives,
                    field_ids=RESEARCH_AREA_TO_FIELD_IDS.get(s.research_area, []),
                    keywords=[x.strip() for x in s.keywords.split(",") if x.strip()],
                    language=s.language,
                    additional_notes=s.additional_notes,
                )
                store = ProfileStore()
                matcher = ThesisMatcher(store)
                raw_results = matcher.match(profile, embed_top_k=20, final_top_k=5)

                s.results = [
                    {
                        "name": r.professor.name,
                        "score": r.claude_score or round(r.embedding_score * 10, 1),
                        "topic_fit": r.topic_fit or 5,
                        "method_fit": r.methodology_fit or 5,
                        "summary": r.summary or "",
                        "strengths": r.strengths,
                        "red_flags": r.red_flags,
                    }
                    for r in raw_results
                ]
            except Exception:
                s.results = DEMO_RESULTS   # demo mode

        st.rerun()
    else:
        _header("Step 5 of 5", f"Your top matches, {s.first_name}",
                "Based on your thesis topic, methodology, and research area.")

        for i, r in enumerate(s.results, 1):
            _render_result(i, r)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Start over", key="restart"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
# Logo / top bar
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem">
  <div style="width:36px;height:36px;border-radius:8px;background:#009640;
              display:flex;align-items:center;justify-content:center;
              color:white;font-weight:800;font-size:1rem">H</div>
  <span style="font-size:1rem;font-weight:600;color:#1A1A1A">HSG Thesis Match</span>
  <span style="margin-left:auto;font-size:0.75rem;color:#999;
               background:#F5F5F5;padding:3px 10px;border-radius:20px">Beta</span>
</div>
""", unsafe_allow_html=True)

_progress()

step = st.session_state.step
if   step == 0: step_you()
elif step == 1: step_thesis()
elif step == 2: step_approach()
elif step == 3: step_goals()
elif step == 4: step_results()
