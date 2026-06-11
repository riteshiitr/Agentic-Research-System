import streamlit as st
import re
import time
from agents import writer_chain, critic_chain
from tools import web_search, scrape_url

st.set_page_config(
    page_title="Orion · Deep Research",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e2ddd6; }

.stApp {
  background: #08090d;
  background-image:
    radial-gradient(ellipse 70% 45% at 15% 0%, rgba(99,102,241,0.13) 0%, transparent 65%),
    radial-gradient(ellipse 55% 40% at 90% 100%, rgba(139,92,246,0.09) 0%, transparent 60%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1100px !important; }

/* ══ HERO ══ */
.hero { padding: 3rem 0 2rem; }
.hero-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 0.68rem; font-weight: 500; letter-spacing: 0.26em;
  text-transform: uppercase; color: #818cf8; margin-bottom: 1rem; opacity: 0.9;
}
.hero h1 {
  font-family: 'Syne', sans-serif;
  font-size: clamp(2.6rem, 5.5vw, 4.4rem);
  font-weight: 800; line-height: 1.02; letter-spacing: -0.03em;
  color: #f0eef8; margin: 0 0 1rem;
}
.hero h1 em {
  font-style: normal;
  background: linear-gradient(100deg, #818cf8 10%, #c084fc 90%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 1rem; font-weight: 300; color: #7c7a8a;
  max-width: 480px; line-height: 1.7;
}

/* ══ DIVIDER ══ */
.hr {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(129,140,248,0.25), transparent);
  margin: 1.8rem 0;
}

/* ══ INPUT CARD ══ */
.input-card {
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(129,140,248,0.14);
  border-radius: 18px;
  padding: 1.8rem 2rem 1.6rem;
  margin-bottom: 1.2rem;
  backdrop-filter: blur(10px);
}

.stTextInput > div > div > input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(129,140,248,0.22) !important;
  border-radius: 10px !important;
  color: #f0eef8 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  padding: 0.75rem 1rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
  border-color: #818cf8 !important;
  box-shadow: 0 0 0 3px rgba(129,140,248,0.13) !important;
}
.stTextInput > div > div > input::placeholder { color: #4a4860 !important; }
.stTextInput > label {
  font-family: 'DM Mono', monospace !important;
  font-size: 0.7rem !important; letter-spacing: 0.16em !important;
  text-transform: uppercase !important; color: #818cf8 !important; font-weight: 500 !important;
}

/* ══ BUTTON ══ */
.stButton > button {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  color: #fff !important; font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important; font-size: 0.93rem !important;
  letter-spacing: 0.04em !important; border: none !important;
  border-radius: 10px !important; padding: 0.72rem 2rem !important;
  width: 100% !important; cursor: pointer !important;
  box-shadow: 0 4px 22px rgba(99,102,241,0.32) !important;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 30px rgba(99,102,241,0.42) !important;
  opacity: 0.94 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══ PIPELINE COLUMN HEADING ══ */
.col-heading {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem; font-weight: 700; color: #f0eef8;
  margin-bottom: 1rem; letter-spacing: -0.01em;
}

/* ══ STEP CARDS ══ */
.step-card {
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px; padding: 1.1rem 1.4rem;
  margin-bottom: 0.85rem; position: relative; overflow: hidden;
  transition: border-color 0.3s, background 0.3s;
}
.step-card::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
  border-radius:14px 0 0 14px; background: rgba(255,255,255,0.05);
  transition: background 0.3s;
}
.step-card.running { border-color: rgba(251,191,36,0.3); background: rgba(251,191,36,0.04); }
.step-card.running::before { background: #fbbf24; }
.step-card.done    { border-color: rgba(52,211,153,0.25); background: rgba(52,211,153,0.03); }
.step-card.done::before    { background: #34d399; }
.step-card.error   { border-color: rgba(248,113,113,0.3); }
.step-card.error::before   { background: #f87171; }

.step-row { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.2rem; }
.step-num {
  font-family:'DM Mono',monospace; font-size:0.65rem; font-weight:500;
  letter-spacing:0.14em; color:#818cf8; opacity:0.75;
}
.step-name {
  font-family:'Syne',sans-serif; font-size:0.92rem; font-weight:700; color:#f0eef8;
}
.step-badge {
  margin-left:auto; font-family:'DM Mono',monospace;
  font-size:0.65rem; letter-spacing:0.1em;
}
.badge-waiting { color:#3a3850; }
.badge-running { color:#fbbf24; }
.badge-done    { color:#34d399; }
.badge-error   { color:#f87171; }
.step-desc { font-size:0.79rem; color:#5f5d70; margin-top:0.15rem; }

/* ══ SECTION HEADING (results) ══ */
.section-heading {
  font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700;
  color:#f0eef8; margin:2.2rem 0 1rem; letter-spacing:-0.01em;
}
.section-label {
  font-family:'DM Mono',monospace; font-size:0.68rem; font-weight:500;
  letter-spacing:0.18em; text-transform:uppercase; color:#818cf8;
  margin:1.8rem 0 0.6rem; padding-bottom:0.5rem;
  border-bottom:1px solid rgba(129,140,248,0.12);
}

/* ══ REPORT PANEL ══ */
.report-panel {
  background: rgba(255,255,255,0.022);
  border: 1px solid rgba(129,140,248,0.18);
  border-radius: 16px; padding: 1.8rem 2.2rem; margin-top:0.75rem;
  font-size:0.91rem; line-height:1.82; color:#ccc8d8;
  white-space:pre-wrap; word-break:break-word;
}
.feedback-panel {
  background: rgba(255,255,255,0.022);
  border: 1px solid rgba(52,211,153,0.18);
  border-radius: 16px; padding: 1.8rem 2.2rem; margin-top:0.75rem;
  font-size:0.91rem; line-height:1.82; color:#ccc8d8;
  white-space:pre-wrap; word-break:break-word;
}

/* ══ URL PILL ══ */
.url-pill {
  display:inline-flex; align-items:center; gap:4px;
  background:rgba(129,140,248,0.07); border:1px solid rgba(129,140,248,0.16);
  border-radius:6px; padding:3px 9px;
  font-family:'DM Mono',monospace; font-size:0.67rem; color:#818cf8;
  margin:3px; word-break:break-all;
}

/* ══ DONE BANNER ══ */
.done-banner {
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(52,211,153,0.07); border:1px solid rgba(52,211,153,0.2);
  color:#34d399; border-radius:100px; padding:5px 16px;
  font-family:'DM Mono',monospace; font-size:0.73rem; font-weight:500;
  letter-spacing:0.05em; margin-bottom:1.4rem;
}

/* ══ STAT ROW ══ */
.stat-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:1.4rem; }
.stat-chip {
  background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
  border-radius:10px; padding:9px 16px; display:flex; flex-direction:column; gap:3px;
}
.stat-chip .num { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#f0eef8; }
.stat-chip .lbl { font-family:'DM Mono',monospace; font-size:0.58rem; color:#4a4860; letter-spacing:0.08em; text-transform:uppercase; }

/* ══ EXPANDERS ══ */
details summary {
  background:rgba(255,255,255,0.025) !important;
  border:1px solid rgba(255,255,255,0.07) !important;
  border-radius:8px !important; color:#8a88a0 !important;
  font-family:'DM Mono',monospace !important;
  font-size:0.76rem !important; padding:9px 14px !important; letter-spacing:0.06em !important;
}
details[open] summary { border-radius:8px 8px 0 0 !important; }
details > div {
  background:rgba(255,255,255,0.025) !important;
  border:1px solid rgba(255,255,255,0.07) !important;
  border-top:none !important; border-radius:0 0 8px 8px !important;
  color:#8a88a0 !important; font-size:0.78rem !important;
}

/* ══ DOWNLOAD ══ */
.stDownloadButton > button {
  background:rgba(255,255,255,0.03) !important;
  border:1px solid rgba(129,140,248,0.2) !important;
  color:#818cf8 !important; border-radius:8px !important;
  font-family:'DM Mono',monospace !important;
  font-size:0.78rem !important; padding:8px 18px !important;
  letter-spacing:0.05em !important;
}
.stDownloadButton > button:hover {
  background:rgba(129,140,248,0.07) !important; color:#c7d2fe !important;
}

/* ══ ALERTS ══ */
.stAlert { border-radius:10px !important; }

/* ══ FOOTER ══ */
.footer {
  font-family:'DM Mono',monospace; font-size:0.66rem;
  color:#2e2c3a; text-align:center; margin-top:4rem; letter-spacing:0.1em;
}

/* ══ EXAMPLE CHIPS ══ */
.ex-chip {
  display:inline-block;
  background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
  border-radius:6px; padding:0.22rem 0.7rem;
  font-size:0.75rem; color:#6b6880; font-family:'DM Sans',sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def step_card_html(num, title, desc, status="waiting"):
    badge_map = {
        "waiting": ("WAITING",  "badge-waiting"),
        "running": ("● RUNNING","badge-running"),
        "done":    ("✓ DONE",   "badge-done"),
        "error":   ("✕ ERROR",  "badge-error"),
    }
    label, bcls = badge_map.get(status, ("", ""))
    card_cls = {"running":"running","done":"done","error":"error"}.get(status,"")
    return f"""
    <div class="step-card {card_cls}">
      <div class="step-row">
        <span class="step-num">{num}</span>
        <span class="step-name">{title}</span>
        <span class="step-badge {bcls}">{label}</span>
      </div>
      <div class="step-desc">{desc}</div>
    </div>"""

def render_pipeline(slot, statuses, descs):
    titles = ["Search Agent","Reader Agent","Writer Chain","Critic Chain"]
    nums   = ["01","02","03","04"]
    html   = "".join(step_card_html(nums[i], titles[i], descs[i], statuses[i]) for i in range(4))
    slot.markdown(html, unsafe_allow_html=True)

def section_label(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)

def report_box(content, variant="report"):
    safe = content.replace("<","&lt;").replace(">","&gt;")
    cls  = "report-panel" if variant == "report" else "feedback-panel"
    st.markdown(f'<div class="{cls}">{safe}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE  (100% identical logic to your working code)
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline(topic: str, pipeline_slot):
    state, results = {}, {}
    statuses = ["waiting","waiting","waiting","waiting"]
    descs    = [
        "Gathers recent web information",
        "Scrapes & extracts deep content",
        "Drafts the full research report",
        "Reviews & scores the report",
    ]

    def upd(i, s, d=None):
        statuses[i] = s
        if d: descs[i] = d
        render_pipeline(pipeline_slot, statuses, descs)

    # Step 1 — Search
    upd(0, "running")
    try:
        state["search_results"] = web_search.invoke({"query": topic})
        urls = re.findall(r'https?://[^\s]+', state["search_results"])
        results.update({"search_results": state["search_results"], "urls": urls})
        upd(0, "done", f"Found {len(urls)} URL(s)")
    except Exception as e:
        upd(0, "error", str(e)); st.error(f"Search failed: {e}"); return None

    # Step 2 — Reader
    upd(1, "running")
    scraped, skipped = [], 0
    for url in urls:
        if "youtube.com" in url: skipped += 1; continue
        try:
            c = scrape_url.invoke({"url": url})
            if "Could not scrape" not in c and "403" not in c: scraped.append(c)
        except Exception: skipped += 1
    state["scraped_content"] = "\n\n".join(scraped) if scraped else "No successful scraping results."
    results.update({"scraped_content": state["scraped_content"],
                    "scraped_count": len(scraped), "skipped": skipped})
    upd(1, "done", f"Scraped {len(scraped)} page(s) · {skipped} skipped")

    # Step 3 — Writer
    upd(2, "running")
    combined = (f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}")
    try:
        state["report"] = writer_chain.invoke({"topic": topic, "research": combined})
        results["report"] = state["report"]
        upd(2, "done", "Report drafted")
    except Exception as e:
        upd(2, "error", str(e)); st.error(f"Writer failed: {e}"); return None

    # Step 4 — Critic
    upd(3, "running")
    try:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        results["feedback"] = state["feedback"]
        upd(3, "done", "Review complete")
    except Exception as e:
        upd(3, "error", str(e)); st.error(f"Critic failed: {e}"); return None

    return results


# ─────────────────────────────────────────────────────────────────────────────
# UI LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Multi-Agent AI System</div>
  <h1>Research <em>anything,</em><br>know everything.</h1>
  <p class="hero-sub">Four specialized AI agents collaborate — searching, scraping, writing and critiquing — to hand you a polished report, not just a list of links.</p>
</div>
<div class="hr"></div>
""", unsafe_allow_html=True)

col_left, col_gap, col_right = st.columns([5, 0.4, 4])

with col_left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-top:0.2rem;">
      <span style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#3a3850;letter-spacing:0.1em;">TRY →</span>
      <span class="ex-chip">LLM agents 2025</span>
      <span class="ex-chip">CRISPR gene editing</span>
      <span class="ex-chip">Fusion energy progress</span>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="col-heading">Pipeline</div>', unsafe_allow_html=True)
    pipeline_slot = st.empty()
    # initial idle state
    render_pipeline(
        pipeline_slot,
        ["waiting","waiting","waiting","waiting"],
        ["Gathers recent web information",
         "Scrapes & extracts deep content",
         "Drafts the full research report",
         "Reviews & scores the report"],
    )

# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-family:DM Mono,monospace;font-size:0.75rem;"
            f"color:#4a4860;letter-spacing:0.06em;margin-bottom:1rem;'>"
            f"RESEARCHING · <span style='color:#818cf8'>{topic.strip()}</span></p>",
            unsafe_allow_html=True,
        )
        t0 = time.time()
        results = run_pipeline(topic.strip(), pipeline_slot)
        elapsed = round(time.time() - t0, 1)

        if results:
            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="done-banner">✓ Completed in {elapsed}s</div>',
                unsafe_allow_html=True,
            )

            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-chip">
                <span class="num">{len(results.get("urls", []))}</span>
                <span class="lbl">URLs found</span>
              </div>
              <div class="stat-chip">
                <span class="num">{results.get("scraped_count", 0)}</span>
                <span class="lbl">Pages scraped</span>
              </div>
              <div class="stat-chip">
                <span class="num">4</span>
                <span class="lbl">Agents used</span>
              </div>
            </div>""", unsafe_allow_html=True)

            # Sources
            section_label("🔗  Sources Found")
            if results.get("urls"):
                st.markdown(
                    "".join(f'<span class="url-pill">↗ {u}</span>' for u in results["urls"]),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<span style='color:#3a3850;font-size:0.82rem'>No URLs extracted.</span>",
                            unsafe_allow_html=True)

            # Raw collapsibles
            with st.expander("RAW SEARCH OUTPUT"):
                st.text(results.get("search_results", "—"))

            with st.expander(f"SCRAPED CONTENT  ({results.get('scraped_count', 0)} page(s))"):
                cap = results.get("scraped_content", "—")
                st.text(cap[:8000] + ("…" if len(cap) > 8000 else ""))

            # Report
            section_label("✍️  Research Report")
            report_box(results.get("report", "No report generated."), "report")

            # Critic
            section_label("🔍  Critic Feedback")
            report_box(results.get("feedback", "No feedback generated."), "feedback")

            # Download
            st.markdown("<div style='margin-top:1.4rem'>", unsafe_allow_html=True)
            st.download_button(
                label="⬇  Download Full Report (.txt)",
                data=(
                    f"TOPIC: {topic.strip()}\n\n"
                    f"{'='*60}\nRESEARCH REPORT\n{'='*60}\n{results.get('report','')}\n\n"
                    f"{'='*60}\nCRITIC FEEDBACK\n{'='*60}\n{results.get('feedback','')}\n"
                ),
                file_name=f"orion_{topic.strip()[:40].replace(' ','_')}.txt",
                mime="text/plain",
            )
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer">Orion · Multi-Agent Research Pipeline · Built with LangChain + Streamlit</div>
""", unsafe_allow_html=True)
