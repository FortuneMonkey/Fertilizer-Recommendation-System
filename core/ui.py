"""Look and feel: styles and small reusable components."""
import streamlit as st

CSS = """
<style>
:root {
  --ink:#16261E; --muted:#5C6C63; --line:#DDE5DF; --green:#17533A; --leaf:#E4F0E8; --soft:#F4F6F3;
  --amber:#8A4B08; --amber-bg:#FFF1DB;
  --shadow:0 1px 2px rgba(16,40,28,.05), 0 6px 20px rgba(16,40,28,.05);
}
header[data-testid="stHeader"] {display:none;}
.stApp {background:var(--soft);}
.block-container {max-width:1240px; padding:6.2rem 2rem 4rem;}

/* ---- top bar ---- */
.st-key-topbar {position:fixed; top:0; left:0; right:0; z-index:1000; height:64px; display:flex; flex-direction:column; justify-content:center;
  padding:0 2rem; background:rgba(255,255,255,.94); backdrop-filter:blur(8px); border-bottom:1px solid var(--line);}
.st-key-topbar [data-testid="stHorizontalBlock"] {width:100%; max-width:1176px; margin:0 auto; gap:.25rem; align-items:center;}
.st-key-topbar [data-testid="stMarkdownContainer"] p {margin:0;}
.st-key-topbar [data-testid="stMarkdown"], .st-key-topbar [data-testid="stMarkdownContainer"], .st-key-topbar [data-testid="stElementContainer"] {margin:0 !important;}
.st-key-topbar [data-testid="stColumn"] {flex:0 0 auto !important; width:auto !important; min-width:0 !important;}
.st-key-topbar [data-testid="stColumn"]:first-child {margin-right:1.4rem;}
.st-key-topbar [data-testid="stColumn"]:last-child {display:none;}
.brand {display:flex; align-items:center; gap:12px; font-weight:700; font-size:1.02rem; color:var(--ink); letter-spacing:-.01em; white-space:nowrap;}
[data-testid="stPageLink-NavLink"] p {white-space:nowrap;}
@media (max-width: 820px) {.brand-name {display:none;} .st-key-topbar {padding:0 1rem;} .block-container {padding-left:1rem; padding-right:1rem;}}
.logo {width:34px; height:34px; border-radius:10px; background:var(--green); display:inline-flex; align-items:center; justify-content:center;}
[data-testid="stPageLink-NavLink"] {border-radius:9px; padding:.42rem .9rem; color:var(--muted); font-weight:500; justify-content:center;}
[data-testid="stPageLink-NavLink"]:hover {background:var(--leaf); color:var(--green);}
[data-testid="stPageLink-NavLink"][aria-current="page"] {background:var(--leaf); color:var(--green); font-weight:600;}

/* ---- headings ---- */
div.ph {margin:0 0 1.5rem;}
div.ph h1 {font-size:1.9rem; font-weight:700; letter-spacing:-.025em; margin:0; padding:0; color:var(--ink); line-height:1.2;}
div.ph p {margin:.4rem 0 0; color:var(--muted); font-size:1.02rem;}
div.sec {display:flex; align-items:center; gap:10px; margin:2.1rem 0 .85rem;}
div.sec h2 {margin:0; padding:0; font-size:1.15rem; font-weight:650; letter-spacing:-.01em; color:var(--ink);}
div.sec small {color:var(--muted); font-size:.9rem; font-weight:400;}
div.sec .num {width:26px; height:26px; border-radius:50%; background:var(--green); color:#fff; font-size:.8rem; font-weight:600;
  display:inline-flex; align-items:center; justify-content:center; flex:none;}

/* ---- cards ---- */
[class*="st-key-card-"] {border-radius:14px; background:#fff; box-shadow:var(--shadow); padding:1.15rem 1.3rem;}
.kpis {display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px;}
.kpi {background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px 20px; box-shadow:var(--shadow);}
.kpi-l {font-size:.74rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.06em;}
.kpi-v {font-size:2.2rem; font-weight:700; color:var(--green); line-height:1.15; margin:.35rem 0 .15rem; letter-spacing:-.03em;}
.kpi.amber .kpi-v {color:var(--amber);} .kpi.plain .kpi-v {color:var(--ink);}
.kpi-h {font-size:.85rem; color:var(--muted);}
.bar {height:6px; background:#E6ECE8; border-radius:3px; margin-top:12px; overflow:hidden;}
.bar span {display:block; height:100%; background:var(--green); border-radius:3px;}
.chip {display:inline-flex; align-items:center; padding:3px 11px; border-radius:99px; font-size:.78rem; font-weight:600;
  background:var(--leaf); color:var(--green); margin-right:6px;}
.chip.warn {background:var(--amber-bg); color:var(--amber);} .chip.muted {background:#ECEFED; color:#44564D;}
.badge {width:30px; height:30px; border-radius:50%; background:var(--leaf); color:var(--green); font-weight:700; font-size:.9rem;
  display:inline-flex; align-items:center; justify-content:center; margin-bottom:10px;}
.card-t {font-weight:650; font-size:1.02rem; color:var(--ink); margin-bottom:4px;}
.card-p {color:var(--muted); font-size:.93rem; line-height:1.5; margin:0 0 6px;}
.mono {font-family:ui-monospace,Consolas,monospace; font-size:.8rem; color:var(--muted); word-break:break-all;}
.tiles {display:grid; grid-template-columns:repeat(auto-fit,minmax(125px,1fr)); gap:12px; margin:.5rem 0 1.1rem;}
.tile {background:#fff; border:1px solid var(--line); border-radius:12px; padding:12px 14px; box-shadow:var(--shadow);}
.tile-n {font-size:.72rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.06em;}
.tile-v {font-size:1.65rem; font-weight:700; color:var(--green); line-height:1.25; letter-spacing:-.02em;}
.tile-u {font-size:.76rem; color:var(--muted);}
.empty {text-align:center; padding:1.6rem 1rem .6rem;}
.empty .ico {width:56px; height:56px; border-radius:16px; background:var(--leaf); display:inline-flex; align-items:center; justify-content:center; margin-bottom:14px;}
.empty h3 {margin:0 0 .35rem; font-size:1.15rem; font-weight:650; padding:0;} .empty p {margin:0 0 .8rem; color:var(--muted);}
.item-t {font-weight:650; color:var(--ink); font-size:1rem;} .item-m {margin-top:8px; padding-bottom:8px;}

/* ---- controls ---- */
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {border-radius:10px; min-height:42px; font-weight:600;}
[data-testid="stBaseButton-secondary"] {background:#fff; border:1px solid #CBD7CF; color:var(--ink); box-shadow:0 1px 1px rgba(16,40,28,.04);}
[data-testid="stBaseButton-secondary"]:hover {border-color:var(--green); color:var(--green);}
[data-testid="stBaseButton-primary"] {box-shadow:0 1px 2px rgba(16,40,28,.15);}
[data-testid="stWidgetLabel"] p {font-size:.82rem; font-weight:600; color:var(--muted);}
[data-testid="stAlertContainer"] {border-radius:12px; border:1px solid var(--line);}
[data-testid="stAlertContainer"] p {color:var(--ink);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {background:#E8F1EB;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {background:#E4F2E9;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {background:var(--amber-bg);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {background:#FBE9E9;}
[data-testid="stExpander"] details {border-radius:12px; background:#fff;}
hr {border-color:var(--line) !important; margin:1.6rem 0 !important;}
</style>
"""

LEAF = ('<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.9" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M5 19c0-8.5 5-13.5 14-14 0 9-5 14-14 14z"/>'
        '<path d="M5 19c3-5 6-8.5 10-10.5"/></svg>')


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def card(key):
    """A white, bordered card (a Streamlit container). key must be unique on the page."""
    return st.container(border=True, key=f"card-{key}")


def top_bar(pages):
    """Brand and page links in a fixed bar. pages: {key: st.Page}."""
    with st.container(key="topbar"):
        brand, a, b, c, _ = st.columns([3.2, 1.1, 1.1, 1.7, 3.3], vertical_alignment="center")
        brand.markdown(f'<div class="brand"><span class="logo">{LEAF.format(s=19, c="#fff")}</span>'
                       '<span class="brand-name">Fertilizer Recommendation</span></div>', unsafe_allow_html=True)
        a.page_link(pages["overview"], label="Overview")
        b.page_link(pages["database"], label="Database")
        c.page_link(pages["recommendations"], label="Recommendations")


def page_header(title, subtitle):
    st.markdown(f'<div class="ph"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def section(title, number=None, note=""):
    badge = f'<span class="num">{number}</span>' if number else ""
    small = f"<small>{note}</small>" if note else ""
    st.markdown(f'<div class="sec">{badge}<h2>{title}</h2>{small}</div>', unsafe_allow_html=True)


def kpi(label, value, hint="", share=None, tone=""):
    bar = f'<div class="bar"><span style="width:{share * 100:.0f}%"></span></div>' if share is not None else ""
    return (f'<div class="kpi {tone}"><div class="kpi-l">{label}</div><div class="kpi-v">{value}</div>'
            f'<div class="kpi-h">{hint}</div>{bar}</div>')


def kpi_grid(cards):
    st.markdown(f'<div class="kpis">{"".join(cards)}</div>', unsafe_allow_html=True)


def chip(text, tone=""):
    return f'<span class="chip {tone}">{text}</span>'


def card_text(title, text, badge=None):
    mark = f'<div class="badge">{badge}</div>' if badge else ""
    st.markdown(f'{mark}<div class="card-t">{title}</div><p class="card-p">{text}</p>', unsafe_allow_html=True)


def tiles(items):
    """items: [(name, value)] -> a row of dose tiles."""
    html = "".join(f'<div class="tile"><div class="tile-n">{name}</div><div class="tile-v">{value:,.0f}</div>'
                   '<div class="tile-u">g/tree</div></div>' for name, value in items)
    st.markdown(f'<div class="tiles">{html}</div>', unsafe_allow_html=True)


def empty_state(title, text):
    st.markdown(f'<div class="empty"><div class="ico">{LEAF.format(s=28, c="#17533A")}</div>'
                f'<h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)
