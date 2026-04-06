"""
Prototype B — Split Dashboard
Form on the left, results on the right — feels like a real product.

Run: python3 -m streamlit run ui_dashboard.py
"""

import streamlit as st

st.set_page_config(
    page_title="HSG Thesis Match",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

:root {
    --hsg-green: #009640;
    --hsg-dark:  #006B2B;
    --hsg-light: #E8F5EC;
    --hsg-mid:   #C6E8D0;
    --text:      #1A1A1A;
    --muted:     #666666;
    --border:    #E8E8E8;
}

/* Left panel */
.left-panel {
    background: #FAFAFA;
    border-right: 1px solid var(--border);
    min-height: 100vh;
    padding: 2rem 1.5rem;
}

/* Nav tabs */
.tab-row {
    display: flex;
    gap: 4px;
    background: #F0F0F0;
    padding: 3px;
    border-radius: 8px;
    margin-bottom: 1.5rem;
}
.tab-item {
    flex: 1;
    text-align: center;
    padding: 5px 0;
    font-size: 0.78rem;
    font-weight: 500;
    border-radius: 6px;
    cursor: pointer;
    color: var(--muted);
}
.tab-item.active {
    background: white;
    color: var(--hsg-green);
    font-weight: 600;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* Section headers in form */
.form-section {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 1.2rem 0 0.5rem;
}

/* Big submit button */
.stButton > button[kind="primary"] {
    width: 100%;
    background: var(--hsg-green) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    margin-top: 0.5rem;
    transition: all 0.2s;
}
.stButton > button[kind="primary"]:hover {
    background: var(--hsg-dark) !important;
    box-shadow: 0 4px 16px rgba(0,150,64,0.3) !important;
    transform: translateY(-1px);
}
.stButton > button {
    border-radius: 8px !important;
}

/* Right panel: empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    color: var(--muted);
    text-align: center;
    gap: 12px;
}
.empty-icon {
    font-size: 3rem;
    opacity: 0.4;
}
.empty-text {
    font-size: 1rem;
    font-weight: 500;
    color: #999;
}
.empty-sub {
    font-size: 0.85rem;
    color: #BBB;
    max-width: 280px;
    line-height: 1.5;
}

/* Results header */
.results-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 1.2rem;
}
.results-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
}
.results-badge {
    background: var(--hsg-light);
    color: var(--hsg-dark);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
}

/* Match card */
.card {
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    background: white;
    margin-bottom: 0.9rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.card:hover {
    border-color: var(--hsg-green);
    box-shadow: 0 4px 20px rgba(0,150,64,0.1);
}
.card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}
.prof-name {
    font-size: 1.0rem;
    font-weight: 700;
    color: var(--text);
}
.prof-dept {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 1px;
}
.score-badge {
    background: var(--hsg-green);
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 8px;
    white-space: nowrap;
}
.score-badge small { font-size: 0.7rem; font-weight: 400; opacity: 0.85; }

/* Mini score bars */
.mini-scores {
    display: flex;
    gap: 12px;
    margin-bottom: 10px;
}
.mini-score {
    flex: 1;
}
.mini-label {
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 3px;
}
.mini-bar-bg {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.mini-bar-fill {
    height: 100%;
    background: var(--hsg-green);
    border-radius: 2px;
}

/* Why box */
.why {
    background: var(--hsg-light);
    border-left: 3px solid var(--hsg-green);
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 0.9rem;
    font-size: 0.85rem;
    color: #1A3A1A;
    line-height: 1.55;
    margin-bottom: 8px;
}
.why-lbl {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--hsg-dark);
    margin-bottom: 4px;
}
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.tag {
    font-size: 0.73rem;
    font-weight: 500;
    padding: 2px 9px;
    border-radius: 20px;
}
.tag-g { background: var(--hsg-mid); color: var(--hsg-dark); }
.tag-w { background: #FFF3CD; color: #7A5C00; }

/* Input tweaks */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    border-radius: 8px !important;
    font-size: 0.88rem !important;
}
label[data-testid="stWidgetLabel"] p { font-size: 0.83rem !important; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------
DEMO = [
    dict(
        name="Prof. Dr. Markus Schmid",
        dept="School of Finance",
        score=9.1, topic=9, method=9,
        summary=(
            "Your thesis on board diversity maps directly onto Prof. Schmid's core research "
            "in corporate governance and executive compensation. He regularly supervises empirical "
            "work using Compustat and Datastream, matching your quantitative approach precisely."
        ),
        strengths=["Corporate governance expert", "Panel data / regression methods", "Open proposal on ESG & boards"],
        flags=[],
    ),
    dict(
        name="Prof. Dr. Björn Ambos",
        dept="School of Management",
        score=7.4, topic=7, method=8,
        summary=(
            "Prof. Ambos's international strategy research overlaps with your thesis if you include "
            "cross-country governance comparisons. His empirical approach (panel & survey data) fits your "
            "methods, though his primary focus is HQ–subsidiary dynamics, not board governance."
        ),
        strengths=["Strong empirical methodology", "Cross-country data experience"],
        flags=["Core focus is international management — confirm overlap before reaching out"],
    ),
    dict(
        name="Prof. Dr. Simone Westerfeld",
        dept="School of Finance",
        score=6.8, topic=6, method=8,
        summary=(
            "Prof. Westerfeld's banking and financial intermediation research shares methodological "
            "common ground. The topic fit is indirect, but if your thesis has a financial sector angle "
            "she could be a strong fit for the empirical design."
        ),
        strengths=["Empirical corporate finance methods", "Open to cross-disciplinary work"],
        flags=["Focus is on banking/regulation, not board governance"],
    ),
]

RESEARCH_AREAS = [
    "Finance/Banking", "Economics", "Strategic Management", "Marketing",
    "Supply Chain Management", "Sustainability", "Entrepreneurship",
    "International Business", "Accounting", "Human Resources Management",
    "Data Science / Machine Learning", "Health Economics", "Other",
]

PROGRAMMES = [
    "Master in Accounting and Finance (MAccFin)",
    "Master in Banking and Finance (MBF)",
    "Master in Finance (MF)",
    "Master in Economics (MEcon)",
    "Master in General Management (MGM)",
    "Master in Strategy and International Management (SIM)",
    "Master in Quantitative Economics and Finance (MQE)",
    "Bachelor of Arts HSG in Business Administration",
    "Bachelor of Arts HSG in Economics",
]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# ---------------------------------------------------------------------------
# Layout: topbar + two columns
# ---------------------------------------------------------------------------

# Top nav bar
st.markdown("""
<div style="display:flex;align-items:center;padding:0.6rem 1.2rem;
            border-bottom:1px solid #ECECEC;margin:-1rem -1rem 1.5rem;
            background:white;position:sticky;top:0;z-index:100">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:32px;height:32px;border-radius:7px;background:#009640;
                display:flex;align-items:center;justify-content:center;
                color:white;font-weight:800;font-size:0.9rem">H</div>
    <span style="font-weight:700;font-size:0.95rem;color:#1A1A1A">HSG Thesis Match</span>
  </div>
  <div style="margin-left:auto;display:flex;gap:20px;align-items:center">
    <span style="font-size:0.8rem;color:#666">For students</span>
    <span style="font-size:0.75rem;background:#E8F5EC;color:#006B2B;
                 font-weight:600;padding:3px 10px;border-radius:20px">Beta</span>
  </div>
</div>
""", unsafe_allow_html=True)

left, divider, right = st.columns([5, 0.05, 7])

# ============================================================
# LEFT — Form
# ============================================================
with left:
    st.markdown('<div style="max-width:440px">', unsafe_allow_html=True)

    st.markdown('<div style="font-size:1.35rem;font-weight:700;color:#1A1A1A;margin-bottom:0.2rem">Find your supervisor</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.85rem;color:#666;margin-bottom:1.4rem">Fill in your thesis details. We\'ll find the best match from HSG\'s faculty.</div>', unsafe_allow_html=True)

    # ── Identity ──
    st.markdown('<div class="form-section">About you</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    first = c1.text_input("First name", placeholder="Anna")
    last  = c2.text_input("Last name",  placeholder="Müller")
    email = st.text_input("HSG email", placeholder="anna.mueller@student.unisg.ch")
    level = st.radio("Level", ["Bachelor", "Master"], horizontal=True)
    prog  = st.selectbox("Programme", [p for p in PROGRAMMES if level.lower() in p.lower()])

    # ── Thesis ──
    st.markdown('<div class="form-section">Your thesis</div>', unsafe_allow_html=True)
    title = st.text_input("Working title", placeholder="e.g. Board diversity and firm performance")
    area  = st.selectbox("Research area", RESEARCH_AREAS)
    rq    = st.text_area("Research question(s)", height=80,
                          placeholder="What specific question do you want to answer?")
    motivation = st.text_area("Motivation", height=70,
                               placeholder="Why does this topic matter to you?")

    # ── Approach ──
    st.markdown('<div class="form-section">Approach & skills</div>', unsafe_allow_html=True)
    approach = st.text_area("Methodology", height=70,
                             placeholder="e.g. Panel data regression using Compustat")
    skills   = st.text_input("Skills (comma-separated)",
                              placeholder="Python, R, Stata, qualitative methods")
    keywords = st.text_input("Keywords (3–5, comma-separated)",
                              placeholder="corporate governance, board diversity, firm performance")
    courses  = st.text_input("Relevant courses",
                              placeholder="e.g. Econometrics, Corporate Finance")

    # ── Submit ──
    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("Find my supervisor →", type="primary", key="go")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RIGHT — Results
# ============================================================
with right:
    if not go and st.session_state.results is None:
        # Empty state
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🎓</div>
          <div class="empty-text">Your matches will appear here</div>
          <div class="empty-sub">Fill in your thesis details on the left and click <strong>Find my supervisor</strong>.</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Trigger matching
        if go:
            with st.spinner("Running AI matching…"):
                try:
                    import os
                    if not os.environ.get("OPENAI_API_KEY"):
                        raise RuntimeError("demo mode")
                    from src.data_collection.questionnaire import _build_description
                    from src.models.student import StudentProfile
                    from src.data_collection.scrapers.constants import RESEARCH_AREA_TO_FIELD_IDS
                    from src.data_processing.profile_builder import ProfileStore
                    from src.matching.matcher import ThesisMatcher

                    desc = _build_description(
                        research_question=rq, motivation=motivation,
                        approach=approach, relevant_courses=courses,
                        references="", data_strategy="",
                    )
                    profile = StudentProfile(
                        first_name=first, last_name=last, email=email,
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
                            name=r.professor.name, dept="",
                            score=r.claude_score or round(r.embedding_score * 10, 1),
                            topic=r.topic_fit or 5, method=r.methodology_fit or 5,
                            summary=r.summary or "",
                            strengths=r.strengths, flags=r.red_flags,
                        )
                        for r in raw
                    ]
                except Exception:
                    st.session_state.results = DEMO

        results = st.session_state.results or DEMO
        name_str = first if first else "you"

        st.markdown(f"""
        <div class="results-header">
          <div class="results-title">Top matches for {name_str}</div>
          <div class="results-badge">{len(results)} supervisors</div>
        </div>
        """, unsafe_allow_html=True)

        for i, r in enumerate(results, 1):
            tp = int(r["topic"] / 10 * 100)
            mp = int(r["method"] / 10 * 100)
            strengths_html = "".join(f'<span class="tag tag-g">✓ {s}</span>' for s in r["strengths"])
            flags_html = "".join(f'<span class="tag tag-w">⚠ {f}</span>' for f in r["flags"])

            st.markdown(f"""
            <div class="card">
              <div class="card-top">
                <div>
                  <div class="prof-name">#{i} &nbsp;{r["name"]}</div>
                  <div class="prof-dept">{r.get("dept","")}</div>
                </div>
                <div class="score-badge">{r["score"]}<small>/10</small></div>
              </div>

              <div class="mini-scores">
                <div class="mini-score">
                  <div class="mini-label">Topic fit</div>
                  <div class="mini-bar-bg"><div class="mini-bar-fill" style="width:{tp}%"></div></div>
                </div>
                <div class="mini-score">
                  <div class="mini-label">Method fit</div>
                  <div class="mini-bar-bg"><div class="mini-bar-fill" style="width:{mp}%"></div></div>
                </div>
              </div>

              <div class="why">
                <div class="why-lbl">Why this supervisor?</div>
                {r["summary"]}
              </div>

              <div class="tags">
                {strengths_html}
                {flags_html}
              </div>
            </div>
            """, unsafe_allow_html=True)
