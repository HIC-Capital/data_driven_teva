# HSG Thesis Match — Claude Context

## What this is
A Streamlit prototype for matching HSG (University of St. Gallen) students with thesis supervisors.
Built for a video demo. One file runs the entire UI: **`app.py`** (~2900 lines).

## How to run
```bash
pip install -r requirements.txt
# Add API keys (see Setup below)
python3 -m streamlit run app.py
```
Opens at http://localhost:8501

## Setup — API keys
Create `.streamlit/secrets.toml` (gitignored, never commit):
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."   # only needed for embedding-based topic ranking
```
The app auto-injects these into `os.environ` on startup.

## Architecture — everything is in app.py

### State
All state lives in `st.session_state` (aliased as `s`). Both Student and Professor roles
share the **same browser session** — role switching is a radio button.

Key state variables:
- `s.role` — `"student"` or `"professor"`
- `s.conversations` — `{(prof_display_name, student_name): [{"sender", "text", "time"}]}`
- `s.confirmed_matches` — `set()` of `(prof_name, student_name)` tuples
- `s.active_chat` — currently open prof name (student view)
- `s.prof_active_chat` — currently open student name (professor view)
- `s.topic_favourites` — `set()` of topic IDs
- `s.page` — current page name (router key)

### Demo accounts
- **Student**: Anna Müller, anna.mueller@student.unisg.ch, MBF 2nd semester
- **Professor**: Prof. Dr. Michele Ittens, michele.ittens@unisg.ch, School of Management

Pre-seeded conversations in `_make_demo_conversations()` (around line 370).

### Router (bottom of file, ~line 2850)
```python
if s.role == "professor":
    if s.page == "Home":         page_prof_home()
    elif s.page == "Messages":   page_messages()
    ...
else:  # student
    if s.page == "Home":         page_home()
    elif s.page == "Match":      page_match()
    elif s.page == "Messages":   page_messages()
    elif s.page == "Thesis Topics": page_topics()
    elif s.page == "Professors": page_professors()
    elif s.page == "AI Assistant": page_ai_assistant()
    elif s.page == "Feedback":   page_feedback()
```
To add a page: write `def page_foo():`, add to the router, add a sidebar nav button.

### Key page functions
| Function | What it does |
|---|---|
| `page_home()` | Student dashboard — 8 cards linking to other pages |
| `page_prof_home()` | Professor dashboard |
| `page_match()` | 4-step wizard to find supervisor matches |
| `page_messages()` | Shared live messaging (both roles) |
| `page_topics()` | Thesis topic browser — Professor / Company / AI tabs |
| `page_professors()` | Faculty list + detail panel |
| `page_feedback()` | Star rating + review after confirmed match |
| `page_ai_assistant()` | FAQ chatbot using Claude |

### Data
- `data/professor_profiles.json` — 228 real HSG professors (scraped from Alexandria + OpenAlex)
- `data/thesis_topics.json` — thesis topics from HSG Business Platform
- `data/professors.json` — raw scrape cache (input to profile builder)

Loaded at startup by `_load_professors()` and `_load_topics()` into `PROFESSORS` and `TOPICS` lists.

### AI Agents (src/agents/)
All use Claude Sonnet 4.6 via `anthropic` SDK. Require `ANTHROPIC_API_KEY`.
- `thesis_generator.py` — generates thesis ideas from student interests
- `email_writer.py` — drafts outreach emails to professors
- `faq_agent.py` — answers student questions + drafts professor replies
- `professor_import_agent.py` — extracts structured data from professor documents

### CSS & Styling
Single `<style>` block injected via `st.markdown()` around line 510.
Design language: **sharp corners everywhere** (`border-radius: 0`), dark green sidebar (`#0D3320`),
HSG green accent (`#009640`). CSS variables defined in `:root`.

Key CSS classes:
- `.dash-card` — dashboard card (190px height, hover lift)
- `.list-item` / `.list-item.active` — sidebar list rows
- `.bubble` / `.bubble.mine` — chat message bubbles
- `.why` — green left-border info box
- `.tag .tg/.tw/.tb/.tgr` — coloured keyword tags
- `.status-pill` — inline status badges

**Invisible overlay button pattern**: after every `.dash-card` or `.list-item`, a Streamlit
button with an empty label is rendered. CSS lifts it over the card with `margin-top: -194px`
and `opacity: 0`, making the entire card clickable.

### Navigation between pages
```python
s.page = "Messages"; st.rerun()
```
Always set `s.page` then call `st.rerun()`. Never use `st.switch_page()`.

### Adding a new dashboard card
1. Add `st.markdown('<div class="dash-card">...</div>', unsafe_allow_html=True)`
2. Immediately after: `_card_btn("unique_key", "Page Name")`

### Common patterns
```python
# Topbar
topbar("Page Title", "subtitle text")

# Green tag
tag("keyword", "tg")   # tg=green, tw=yellow, tb=blue, tgr=gray

# Navigate to messages and pre-seed conversation
stud_n = f"{s.first_name} {s.last_name}"
ck = (prof_name, stud_n)
if ck not in s.conversations:
    s.conversations[ck] = []
s.active_chat = prof_name; s.page = "Messages"; st.rerun()
```

## What's NOT implemented (coming later)
- Actual email sending (all messages are local session state only)
- User authentication / persistent accounts
- Compass course data (scraper works but slow — run `python main.py --step 3` separately)
- Feedback loop into matching algorithm
