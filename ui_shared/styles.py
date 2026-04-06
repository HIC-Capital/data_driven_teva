"""Shared CSS injected at the top of every page."""

HSG_GREEN    = "#009640"
HSG_DARK     = "#006B2B"
HSG_LIGHT    = "#E8F5EC"
HSG_MID      = "#C6E8D0"
HSG_PALE     = "#F4FAF6"

GLOBAL_CSS = """
<style>
/* ── Reset / base ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer { visibility: hidden; }

/* Remove default streamlit padding on main block */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }

/* ── Variables ──────────────────────────────────────────────── */
:root {
  --green:   #009640;
  --dark:    #006B2B;
  --light:   #E8F5EC;
  --mid:     #C6E8D0;
  --pale:    #F4FAF6;
  --text:    #111827;
  --sub:     #374151;
  --muted:   #6B7280;
  --border:  #E5E7EB;
  --bg:      #F9FAFB;
  --white:   #FFFFFF;
  --warn:    #FEF3C7;
  --warnTxt: #92400E;
  --radius:  8px;
}

/* ── Sidebar nav ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--white) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 220px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Active nav item */
section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
  background: var(--light) !important;
  color: var(--green) !important;
  font-weight: 600 !important;
  border-left: 3px solid var(--green) !important;
}
section[data-testid="stSidebar"] .stRadio > div > label {
  border-radius: 0 !important;
  padding: 0.55rem 1rem !important;
  margin: 1px 0 !important;
  cursor: pointer;
  color: var(--sub);
  font-size: 0.88rem;
  transition: background 0.15s;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
  background: var(--pale) !important;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  gap: 0 !important;
}

/* ── Inputs ─────────────────────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] > div {
  border-radius: var(--radius) !important;
  border-color: var(--border) !important;
  background: var(--white) !important;
  font-size: 0.9rem !important;
  font-family: 'Inter', sans-serif !important;
}
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="textarea"]:focus-within > div {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(0,150,64,0.1) !important;
}
label[data-testid="stWidgetLabel"] p {
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  color: var(--sub) !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton > button {
  border-radius: var(--radius) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
  background: var(--green) !important;
  color: white !important;
  border: none !important;
  padding: 0.6rem 1.4rem !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--dark) !important;
  box-shadow: 0 2px 8px rgba(0,150,64,0.25) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--white) !important;
  color: var(--sub) !important;
  border: 1px solid var(--border) !important;
}

/* ── File uploader ──────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 0.5rem !important;
  background: var(--pale) !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--green) !important;
  background: var(--light) !important;
}

/* ── Cards ──────────────────────────────────────────────────── */
.card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem 1.4rem;
  margin-bottom: 0.75rem;
}
.card:hover { border-color: #D1D5DB; box-shadow: 0 1px 6px rgba(0,0,0,0.06); }
.card-active { border-color: var(--green) !important; box-shadow: 0 0 0 2px var(--light) !important; }

/* ── Notification badge ─────────────────────────────────────── */
.notif-dot {
  display: inline-block;
  width: 8px; height: 8px;
  background: #EF4444;
  border-radius: 50%;
  margin-left: 4px;
  vertical-align: middle;
}

/* ── Section titles ─────────────────────────────────────────── */
.page-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.2rem;
}
.page-sub {
  font-size: 0.85rem;
  color: var(--muted);
  margin-bottom: 1.5rem;
}
.section-head {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--muted);
  margin: 1.5rem 0 0.6rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}

/* ── Why box (match result) ─────────────────────────────────── */
.why-box {
  background: var(--light);
  border-left: 3px solid var(--green);
  border-radius: 0 6px 6px 0;
  padding: 0.7rem 0.9rem;
  margin: 0.8rem 0 0.6rem;
  font-size: 0.85rem;
  color: #14532D;
  line-height: 1.6;
}
.why-label {
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--dark);
  margin-bottom: 3px;
}

/* ── Tags / pills ───────────────────────────────────────────── */
.tag { display:inline-block; padding:2px 9px; border-radius:20px; font-size:0.74rem; font-weight:500; margin:2px 2px 2px 0; }
.tag-green { background:var(--mid); color:var(--dark); }
.tag-warn  { background:var(--warn); color:var(--warnTxt); }
.tag-gray  { background:#F3F4F6; color:#4B5563; }
.tag-blue  { background:#EFF6FF; color:#1D4ED8; }

/* ── Score bars ─────────────────────────────────────────────── */
.sbar-wrap { display:flex; align-items:center; gap:8px; font-size:0.78rem; color:var(--muted); margin:3px 0; }
.sbar-bg   { flex:1; height:4px; background:var(--border); border-radius:2px; overflow:hidden; }
.sbar-fill { height:100%; background:var(--green); border-radius:2px; }

/* ── Notification banner ────────────────────────────────────── */
.notif-banner {
  background: var(--warn);
  border: 1px solid #FCD34D;
  border-radius: var(--radius);
  padding: 0.7rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  color: var(--warnTxt);
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

/* ── Profile field row ──────────────────────────────────────── */
.field-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid var(--border); font-size:0.88rem; }
.field-label { color:var(--muted); font-size:0.78rem; }
.field-value { color:var(--text); font-weight:500; }
.field-missing { color:#9CA3AF; font-style:italic; }

/* ── Step indicator ─────────────────────────────────────────── */
.step-dots { display:flex; gap:6px; margin-bottom:1.5rem; align-items:center; }
.step-dot { width:8px; height:8px; border-radius:50%; background:var(--border); }
.step-dot.done { background:var(--green); }
.step-dot.active { background:var(--green); opacity:0.5; width:24px; border-radius:4px; }

/* ── Message bubble ─────────────────────────────────────────── */
.msg-row { display:flex; gap:10px; margin-bottom:12px; }
.msg-avatar { width:32px; height:32px; border-radius:50%; background:var(--mid); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.8rem; color:var(--dark); flex-shrink:0; }
.msg-bubble { background:var(--pale); border:1px solid var(--border); border-radius:0 8px 8px 8px; padding:0.6rem 0.8rem; font-size:0.86rem; color:var(--text); max-width:85%; line-height:1.5; }
.msg-bubble.mine { background:var(--light); border-color:var(--mid); border-radius:8px 0 8px 8px; }
.msg-time { font-size:0.7rem; color:var(--muted); margin-top:2px; }

/* ── Suggestion chip ─────────────────────────────────────────── */
.sugg-chip {
  display:inline-flex; align-items:center; gap:5px;
  background:var(--pale); border:1px solid var(--border);
  border-radius:20px; padding:4px 12px;
  font-size:0.78rem; color:var(--sub);
  cursor:pointer; margin:3px;
  transition: all 0.15s;
}
.sugg-chip:hover { background:var(--light); border-color:var(--green); color:var(--dark); }

/* ── Tabs (override streamlit default) ──────────────────────── */
div[data-testid="stTabs"] button {
  font-size: 0.86rem !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--green) !important;
  border-bottom-color: var(--green) !important;
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def topbar(active_page: str = ""):
    """Render a consistent top bar with HSG branding and user avatar."""
    import streamlit as st
    st.markdown(f"""
    <div style="display:flex;align-items:center;padding:0.6rem 0;
                border-bottom:1px solid #E5E7EB;margin-bottom:1.4rem">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:30px;height:30px;border-radius:7px;background:#009640;
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-weight:800;font-size:0.85rem;flex-shrink:0">H</div>
        <span style="font-weight:700;font-size:0.95rem;color:#111827">HSG Thesis Match</span>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:12px">
        <span style="font-size:0.75rem;color:#6B7280">{active_page}</span>
        <div style="width:30px;height:30px;border-radius:50%;background:#E8F5EC;
                    display:flex;align-items:center;justify-content:center;
                    font-weight:700;font-size:0.78rem;color:#006B2B;cursor:pointer"
             title="Anna Müller · MBF">AM</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
