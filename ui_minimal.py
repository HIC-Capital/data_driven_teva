"""
Prototype C — Minimal / Landing page feel
Full-width, clean, the result cards are the hero.

Run: python3 -m streamlit run ui_minimal.py
"""

import streamlit as st

st.set_page_config(
    page_title="HSG Thesis Match",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 680px; padding-top: 0; padding-bottom: 4rem; }

:root {
    --green:  #009640;
    --dark:   #006B2B;
    --light:  #E8F5EC;
    --mid:    #C6E8D0;
    --text:   #111111;
    --muted:  #666;
    --border: #E8E8E8;
}

/* ── Hero banner ────────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #006B2B 0%, #009640 60%, #00BA50 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    color: white;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '🎓';
    font-size: 7rem;
    position: absolute;
    right: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.15;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 0.4rem;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 0.9rem;
    opacity: 0.85;
    line-height: 1.5;
    max-width: 380px;
}

/* ── Section labels ─────────────────────────────────────────── */
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--green);
    margin: 1.8rem 0 0.5rem;
}

/* ── Inputs ─────────────────────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    border-radius: 8px !important;
    font-size: 0.9rem !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 0.83rem !important;
    font-weight: 500;
    color: #333;
}

/* ── Submit button ──────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    width: 100%;
    background: var(--green) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.8rem 1rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em;
    margin-top: 0.8rem;
    transition: all 0.2s;
}
.stButton > button[kind="primary"]:hover {
    background: var(--dark) !important;
    box-shadow: 0 6px 20px rgba(0,150,64,0.35) !important;
    transform: translateY(-2px);
}
.stButton > button {
    border-radius: 8px !important;
}

/* ── Divider ────────────────────────────────────────────────── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* ── Results section ────────────────────────────────────────── */
.results-intro {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.results-sub {
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
}

/* ── Match card ─────────────────────────────────────────────── */
.mcard {
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    background: white;
    margin-bottom: 1rem;
    transition: all 0.2s;
}
.mcard:hover {
    border-color: var(--green);
    box-shadow: 0 6px 24px rgba(0,150,64,0.12);
    transform: translateY(-2px);
}
.mcard-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}
.rank-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px; height: 26px;
    background: var(--green);
    color: white;
    font-weight: 700;
    font-size: 0.8rem;
    border-radius: 50%;
    margin-right: 8px;
    flex-shrink: 0;
}
.prof-name { font-size: 1.05rem; font-weight: 700; color: var(--text); }
.prof-meta { font-size: 0.77rem; color: var(--muted); margin-top: 1px; }
.big-score {
    font-size: 2rem;
    font-weight: 800;
    color: var(--green);
    line-height: 1;
}
.big-score small { font-size: 0.8rem; font-weight: 400; color: var(--muted); }

/* Score pills row */
.score-pills { display: flex; gap: 6px; margin-bottom: 12px; }
.score-pill {
    font-size: 0.76rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: var(--light);
    color: var(--dark);
}

/* Why box */
.why-card {
    background: var(--light);
    border-left: 4px solid var(--green);
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1rem;
    margin-bottom: 10px;
}
.why-lbl {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--dark);
    margin-bottom: 5px;
}
.why-text {
    font-size: 0.87rem;
    color: #1A3A1A;
    line-height: 1.6;
}

/* Strength / flag tags */
.tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.tag { font-size: 0.74rem; font-weight: 500; padding: 3px 10px; border-radius: 20px; }
.tag-g { background: var(--mid); color: var(--dark); }
.tag-w { background: #FFF3CD; color: #7A5C00; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RESEARCH_AREAS = [
    "Finance/Banking", "Economics", "Strategic Management", "Marketing",
    "Supply Chain Management", "Sustainability", "Entrepreneurship",
    "International Business", "Accounting", "Human Resources Management",
    "Data Science / Machine Learning", "Health Economics", "Ethics", "Other",
]
PROGRAMMES = [
    "Master in Banking and Finance (MBF)",
    "Master in Finance (MF)",
    "Master in Economics (MEcon)",
    "Master in General Management (MGM)",
    "Master in Accounting and Finance (MAccFin)",
    "Master in Strategy and International Management (SIM)",
    "Master in Quantitative Economics and Finance (MQE)",
    "Bachelor of Arts HSG in Business Administration",
    "Bachelor of Arts HSG in Economics",
    "Bachelor of Arts HSG in International Affairs",
]
DEMO = [
    dict(
        name="Prof. Dr. Markus Schmid", meta="School of Finance · Corporate Governance",
        score=9.1, topic=9, method=9,
        summary=(
            "Your thesis on board diversity and firm performance maps directly onto "
            "Prof. Schmid's core research agenda in corporate governance and executive compensation. "
            "He regularly supervises quantitative work using Compustat and Datastream — "
            "exactly the empirical approach you described."
        ),
        strengths=["Corporate governance expert", "Panel data & regression", "Open proposal on ESG & boards"],
        flags=[],
    ),
    dict(
        name="Prof. Dr. Björn Ambos", meta="School of Management · International Strategy",
        score=7.4, topic=7, method=8,
        summary=(
            "Prof. Ambos specialises in international strategy and HQ–subsidiary dynamics. "
            "The topic overlap is moderate, but his empirical methods (panel & survey data) "
            "match your approach well. Consider if a cross-country governance angle would strengthen the fit."
        ),
        strengths=["Strong empirical methodology", "Cross-country data experience"],
        flags=["Primary focus is international management — confirm topic overlap"],
    ),
    dict(
        name="Prof. Dr. Simone Westerfeld", meta="School of Finance · Banking & Regulation",
        score=6.8, topic=6, method=8,
        summary=(
            "Prof. Westerfeld's banking research shares methodological common ground with your project. "
            "If your thesis includes a financial-sector angle, she could be a strong supervisory fit "
            "for the empirical design side."
        ),
        strengths=["Empirical corporate finance methods", "Open to cross-disciplinary work"],
        flags=["Focus is banking/regulation, not board governance — topic fit is indirect"],
    ),
]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "results" not in st.session_state:
    st.session_state.results = None

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">University of St. Gallen</div>
  <div class="hero-title">Find your<br>thesis supervisor</div>
  <div class="hero-sub">AI-powered matching across HSG's faculty. Describe your thesis — we'll find who fits.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Form (always visible, collapses visually after submit)
# ---------------------------------------------------------------------------
if not st.session_state.show_results:
    with st.form("match_form"):
        st.markdown('<div class="section-label">About you</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        first = c1.text_input("First name", placeholder="Anna")
        last  = c2.text_input("Last name",  placeholder="Müller")
        level = st.radio("Level", ["Bachelor", "Master"], horizontal=True)
        prog  = st.selectbox("Programme", PROGRAMMES)

        st.markdown('<div class="section-label">Your thesis</div>', unsafe_allow_html=True)
        title = st.text_input("Working title",
                               placeholder="e.g. The effect of board diversity on firm performance")
        area  = st.selectbox("Research area", RESEARCH_AREAS)
        rq    = st.text_area("Research question(s)", height=90,
                              placeholder="What specific question do you want to answer?")
        motivation = st.text_area("Motivation", height=75,
                                   placeholder="Why does this topic matter to you personally?")

        st.markdown('<div class="section-label">Approach & skills</div>', unsafe_allow_html=True)
        approach = st.text_area("Planned methodology", height=75,
                                 placeholder="e.g. Quantitative panel data analysis using Compustat, regression, IV")
        c3, c4 = st.columns(2)
        skills   = c3.text_input("Skills", placeholder="Python, R, Stata…")
        keywords = c4.text_input("Keywords", placeholder="governance, diversity, performance…")

        submitted = st.form_submit_button("Find my supervisor →", type="primary")

    if submitted:
        if not first or not title or not rq:
            st.error("Please fill in your name, thesis title, and research question.")
        else:
            st.session_state.student_name = first
            with st.spinner("Searching HSG faculty and running AI analysis…"):
                try:
                    import os
                    if not os.environ.get("OPENAI_API_KEY"):
                        raise RuntimeError("demo")
                    from src.data_collection.questionnaire import _build_description
                    from src.models.student import StudentProfile
                    from src.data_processing.profile_builder import ProfileStore
                    from src.matching.matcher import ThesisMatcher

                    desc = _build_description(
                        research_question=rq, motivation=motivation,
                        approach=approach, relevant_courses="",
                        references="", data_strategy="",
                    )
                    profile = StudentProfile(
                        first_name=first, last_name=last, email="",
                        level=level, programme=prog, research_area=area,
                        thesis_title=title, thesis_description=desc,
                        skills=[x.strip() for x in skills.split(",") if x.strip()],
                        keywords=[x.strip() for x in keywords.split(",") if x.strip()],
                        objectives=[], field_ids=[],
                    )
                    store = ProfileStore()
                    raw = ThesisMatcher(store).match(profile, embed_top_k=20, final_top_k=5)
                    st.session_state.results = [
                        dict(
                            name=r.professor.name, meta="",
                            score=r.claude_score or round(r.embedding_score * 10, 1),
                            topic=r.topic_fit or 5, method=r.methodology_fit or 5,
                            summary=r.summary or "", strengths=r.strengths, flags=r.red_flags,
                        )
                        for r in raw
                    ]
                except Exception:
                    st.session_state.results = DEMO

            st.session_state.show_results = True
            st.rerun()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if st.session_state.show_results:
    results = st.session_state.results or DEMO
    name = st.session_state.student_name or "you"

    st.markdown(f'<div class="results-intro">Your top matches, {name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="results-sub">Ranked by topic fit, methodology alignment, and research profile similarity.</div>', unsafe_allow_html=True)

    for i, r in enumerate(results, 1):
        s_html = "".join(f'<span class="tag tag-g">✓ {s}</span>' for s in r["strengths"])
        f_html = "".join(f'<span class="tag tag-w">⚠ {f}</span>' for f in r["flags"])
        st.markdown(f"""
        <div class="mcard">
          <div class="mcard-header">
            <div>
              <div><span class="rank-pill">{i}</span><span class="prof-name">{r["name"]}</span></div>
              <div class="prof-meta" style="margin-left:34px">{r.get("meta","")}</div>
            </div>
            <div style="text-align:right">
              <div class="big-score">{r["score"]}<small>/10</small></div>
            </div>
          </div>

          <div class="score-pills">
            <span class="score-pill">Topic fit &nbsp;{r["topic"]}/10</span>
            <span class="score-pill">Method fit &nbsp;{r["method"]}/10</span>
          </div>

          <div class="why-card">
            <div class="why-lbl">Why this supervisor?</div>
            <div class="why-text">{r["summary"]}</div>
          </div>

          <div class="tags">
            {s_html}
            {f_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Search again"):
        st.session_state.show_results = False
        st.session_state.results = None
        st.rerun()
