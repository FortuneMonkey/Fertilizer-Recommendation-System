"""Visual system and reusable UI components for the Fertilizer Recommendation app.

Import this module from Streamlit pages and call ``inject_css()`` once per page.
The helper function names and signatures are kept compatible with the original UI.
"""
from __future__ import annotations

import html
import math
from typing import Iterable, Sequence

import streamlit as st


# -----------------------------------------------------------------------------
# Design system
# -----------------------------------------------------------------------------
CSS = r"""
<style>
/* --------------------------------------------------------------------------
   LIQUID GLASS DESIGN SYSTEM
   Frosted, layered surfaces with a soft eucalyptus / forest-green accent.
   -------------------------------------------------------------------------- */
:root {
  color-scheme: light;
  --ink: #152C22;
  --ink-soft: #345044;
  --muted: #71877B;
  --muted-strong: #536D60;
  --green: #176344;
  --green-deep: #10472F;
  --green-bright: #3E9870;
  --mint: #DDF2E5;
  --aqua: #D9F0EE;
  --line: rgba(255,255,255,.76);
  --line-soft: rgba(90,130,105,.16);
  --canvas: #EAF2EC;
  --glass: rgba(255,255,255,.50);
  --glass-strong: rgba(255,255,255,.70);
  --glass-subtle: rgba(255,255,255,.34);
  --glass-border: rgba(255,255,255,.82);
  --glass-shadow: 0 18px 50px rgba(27,67,45,.10), 0 3px 12px rgba(27,67,45,.045);
  --glass-shadow-hover: 0 24px 60px rgba(27,67,45,.15), 0 5px 18px rgba(27,67,45,.07);
  --amber: #94600D;
  --amber-wash: rgba(255,244,220,.76);
  --red: #A64040;
  --red-wash: rgba(255,235,233,.78);
  --blue: #356D88;
  --blue-wash: rgba(232,246,251,.78);
  --radius-sm: 12px;
  --radius-md: 18px;
  --radius-lg: 25px;
  --ease: cubic-bezier(.2,.75,.25,1);
}

/* ---- Ambient background and app canvas ---- */
html, body, [class*="stApp"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", sans-serif;
  color: var(--ink);
}
.stApp {
  position: relative;
  isolation: isolate;
  min-height: 100vh;
  background:
    radial-gradient(ellipse at 8% 7%, rgba(186,226,195,.72) 0, rgba(186,226,195,0) 34rem),
    radial-gradient(ellipse at 92% 9%, rgba(180,226,223,.64) 0, rgba(180,226,223,0) 32rem),
    radial-gradient(ellipse at 76% 88%, rgba(214,226,244,.66) 0, rgba(214,226,244,0) 38rem),
    linear-gradient(145deg, #EDF4EE 0%, #E8F1EC 45%, #EDF3F4 100%);
  background-attachment: fixed;
}
.stApp::before {
  content: "";
  position: fixed;
  inset: -15%;
  z-index: -1;
  pointer-events: none;
  opacity: .58;
  filter: blur(42px);
  background:
    radial-gradient(circle at 22% 25%, rgba(255,255,255,.82) 0 7%, transparent 24%),
    radial-gradient(circle at 72% 22%, rgba(179,224,208,.52) 0 8%, transparent 26%),
    radial-gradient(circle at 54% 78%, rgba(255,255,255,.62) 0 6%, transparent 23%);
}
.block-container {
  position: relative;
  z-index: 1;
  max-width: 1380px;
  /* Keep the first page section safely below the floating glass navbar. */
  padding: 7rem 2.2rem 4.5rem;
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stVerticalBlock"] { gap: .95rem; }
[data-testid="stElementContainer"] { min-width: 0; }
[data-testid="stMarkdownContainer"] p { line-height: 1.65; }
[data-testid="stMarkdownContainer"] a {
  color: var(--green-deep);
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}
[data-testid="stMarkdownContainer"] a:hover { color: var(--green-bright); }

/* ---- Frosted liquid-glass navigation ---- */
.st-key-topbar {
  position: fixed;
  inset: 10px 18px auto 18px;
  z-index: 1000;
  min-height: 66px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 max(1.2rem, calc((100vw - 1340px) / 2 + 1.2rem));
  border: 1px solid rgba(255,255,255,.86);
  border-radius: 21px;
  background: linear-gradient(115deg, rgba(255,255,255,.76), rgba(255,255,255,.48));
  -webkit-backdrop-filter: blur(26px) saturate(175%);
  backdrop-filter: blur(26px) saturate(175%);
  box-shadow: 0 12px 36px rgba(28,67,45,.11), inset 0 1px 0 rgba(255,255,255,.95);
}
.st-key-topbar::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(110deg, rgba(255,255,255,.42), transparent 38%, rgba(255,255,255,.12) 72%, transparent);
}
.st-key-topbar [data-testid="stHorizontalBlock"] {
  width: 100%;
  max-width: 1340px;
  margin: 0 auto;
  gap: .35rem;
  align-items: center;
}
.st-key-topbar [data-testid="stMarkdownContainer"] p { margin: 0; }
.st-key-topbar [data-testid="stMarkdown"],
.st-key-topbar [data-testid="stMarkdownContainer"],
.st-key-topbar [data-testid="stElementContainer"] { margin: 0 !important; }
.st-key-topbar [data-testid="stColumn"] { min-width: 0 !important; justify-content: center; }
.st-key-topbar [data-testid="stColumn"]:first-child { margin-right: auto; }
.brand {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  color: var(--ink);
  font-size: 1rem;
  font-weight: 780;
  letter-spacing: -.04em;
  white-space: nowrap;
}
.brand-name { display: inline-block; }
.logo {
  width: 39px;
  height: 39px;
  flex: 0 0 39px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255,255,255,.50);
  border-radius: 14px;
  background: linear-gradient(145deg, #3D9870 0%, #176344 58%, #10472F 100%);
  box-shadow: 0 7px 17px rgba(23,99,68,.24), inset 0 1px 0 rgba(255,255,255,.32);
}
[data-testid="stPageLink-NavLink"] {
  min-height: 39px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: .45rem .95rem;
  border: 1px solid transparent;
  border-radius: 12px;
  color: var(--muted-strong);
  font-size: .87rem;
  font-weight: 650;
  transition: all .2s var(--ease);
}
[data-testid="stPageLink-NavLink"] p { white-space: nowrap; margin: 0; }
[data-testid="stPageLink-NavLink"]:hover {
  border-color: rgba(255,255,255,.88);
  background: rgba(255,255,255,.58);
  color: var(--green-deep);
  box-shadow: 0 4px 14px rgba(28,67,45,.07), inset 0 1px 0 rgba(255,255,255,.9);
}
[data-testid="stPageLink-NavLink"][aria-current="page"] {
  border-color: rgba(255,255,255,.94);
  background: linear-gradient(135deg, rgba(255,255,255,.86), rgba(226,244,232,.72));
  color: var(--green-deep);
  font-weight: 760;
  box-shadow: 0 4px 13px rgba(28,67,45,.075), inset 0 1px 0 #fff;
}

/* ---- Page title and section hierarchy ---- */
div.ph {
  position: relative;
  overflow: hidden;
  margin: .25rem 0 1.75rem;
  padding: 1.45rem 1.65rem 1.5rem;
  border: 1px solid rgba(255,255,255,.84);
  border-radius: var(--radius-lg);
  background: linear-gradient(118deg, rgba(255,255,255,.68), rgba(255,255,255,.36));
  -webkit-backdrop-filter: blur(22px) saturate(155%);
  backdrop-filter: blur(22px) saturate(155%);
  box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.96);
}
div.ph::after {
  content: "";
  position: absolute;
  top: -75px;
  right: -30px;
  width: 250px;
  height: 190px;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(ellipse, rgba(188,231,205,.35), transparent 68%);
}
div.ph h1 {
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 0;
  color: var(--ink);
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 810;
  line-height: 1.16;
  letter-spacing: -.06em;
}
div.ph p {
  position: relative;
  z-index: 1;
  max-width: 760px;
  margin: .55rem 0 0;
  color: var(--muted);
  font-size: .97rem;
  line-height: 1.65;
}
div.sec {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin: 2.15rem 0 .95rem;
}
div.sec h2 {
  margin: 0;
  padding: 0;
  color: var(--ink);
  font-size: 1.14rem;
  font-weight: 760;
  letter-spacing: -.03em;
}
div.sec small { color: var(--muted); font-size: .83rem; font-weight: 460; }
div.sec .num {
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255,255,255,.9);
  border-radius: 10px;
  background: linear-gradient(145deg, rgba(255,255,255,.9), rgba(219,241,226,.72));
  color: var(--green-deep);
  font-size: .76rem;
  font-weight: 780;
  box-shadow: 0 4px 12px rgba(28,67,45,.07), inset 0 1px 0 #fff;
}

/* ---- Glass content panels and KPI cards ---- */
[class*="st-key-card-"] {
  position: relative;
  overflow: hidden;
  padding: 1.25rem 1.35rem;
  border: 1px solid rgba(255,255,255,.86) !important;
  border-radius: var(--radius-md) !important;
  background: linear-gradient(145deg, rgba(255,255,255,.70), rgba(255,255,255,.39)) !important;
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  backdrop-filter: blur(22px) saturate(160%);
  box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.9);
  transition: border-color .22s var(--ease), box-shadow .22s var(--ease), transform .22s var(--ease);
}
[class*="st-key-card-"]:hover {
  border-color: rgba(255,255,255,.98) !important;
  box-shadow: var(--glass-shadow-hover), inset 0 1px 0 #fff;
  transform: translateY(-2px);
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: 16px;
  margin: .4rem 0 1.2rem;
}
.kpi {
  position: relative;
  isolation: isolate;
  min-width: 0;
  overflow: hidden;
  padding: 20px 21px 18px;
  border: 1px solid rgba(255,255,255,.9);
  border-radius: 21px;
  background: linear-gradient(145deg, rgba(255,255,255,.78) 0%, rgba(255,255,255,.43) 100%);
  -webkit-backdrop-filter: blur(24px) saturate(165%);
  backdrop-filter: blur(24px) saturate(165%);
  box-shadow: 0 12px 32px rgba(28,67,45,.085), inset 0 1px 0 rgba(255,255,255,.98);
  transition: transform .22s var(--ease), box-shadow .22s var(--ease), border-color .22s var(--ease);
}
.kpi::before {
  content: "";
  position: absolute;
  z-index: -1;
  top: -52px;
  right: -38px;
  width: 145px;
  height: 125px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(194,231,205,.5), rgba(194,231,205,0) 70%);
}
.kpi::after {
  content: "";
  position: absolute;
  top: 0;
  left: 18px;
  right: 18px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.98), transparent);
}
.kpi:hover { transform: translateY(-3px); border-color: #fff; box-shadow: var(--glass-shadow-hover), inset 0 1px 0 #fff; }
.kpi-l { color: var(--muted-strong); font-size: .71rem; font-weight: 780; text-transform: uppercase; letter-spacing: .085em; }
.kpi-v {
  margin: .46rem 0 .2rem;
  color: var(--green-deep);
  font-size: clamp(1.8rem, 3vw, 2.3rem);
  font-weight: 830;
  line-height: 1.12;
  letter-spacing: -.06em;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  text-shadow: 0 1px 0 rgba(255,255,255,.55);
}
.kpi.amber .kpi-v { color: var(--amber); }
.kpi.amber::before { background: radial-gradient(circle, rgba(255,224,164,.55), rgba(255,224,164,0) 70%); }
.kpi.plain .kpi-v { color: var(--ink); }
.kpi.plain::before { background: radial-gradient(circle, rgba(218,228,224,.58), rgba(218,228,224,0) 70%); }
.kpi-h { color: var(--muted); font-size: .82rem; line-height: 1.5; }
.bar { height: 7px; overflow: hidden; margin-top: 14px; border: 1px solid rgba(255,255,255,.65); border-radius: 999px; background: rgba(40,84,57,.09); }
.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #176344 0%, #56AE83 72%, #9ACCA9 100%);
  box-shadow: 0 0 10px rgba(62,152,112,.22);
}

/* ---- Chips, detail cards, tiles and empty states ---- */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin: 2px 5px 2px 0;
  padding: 5px 10px;
  border: 1px solid rgba(255,255,255,.92);
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255,255,255,.82), rgba(221,242,229,.65));
  color: var(--green-deep);
  font-size: .75rem;
  font-weight: 730;
  line-height: 1.2;
  white-space: nowrap;
  box-shadow: 0 3px 9px rgba(28,67,45,.055), inset 0 1px 0 #fff;
}
.chip.warn { background: linear-gradient(135deg, rgba(255,255,255,.86), var(--amber-wash)); color: var(--amber); }
.chip.muted { background: rgba(255,255,255,.55); color: #586C60; }
.chip.danger { background: var(--red-wash); color: var(--red); }
.chip.info { background: var(--blue-wash); color: var(--blue); }
.badge {
  width: 33px;
  height: 33px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 11px;
  border: 1px solid rgba(255,255,255,.95);
  border-radius: 11px;
  background: linear-gradient(145deg, rgba(255,255,255,.92), rgba(216,241,224,.72));
  color: var(--green-deep);
  font-size: .88rem;
  font-weight: 780;
  box-shadow: 0 4px 12px rgba(28,67,45,.07), inset 0 1px 0 #fff;
}
.card-t { margin: 0 0 5px; color: var(--ink); font-size: 1rem; font-weight: 760; letter-spacing: -.025em; }
.card-p { margin: 0 0 6px; color: var(--muted); font-size: .9rem; line-height: 1.62; }
.mono { color: #647A6C; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .79rem; overflow-wrap: anywhere; }
.tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 135px), 1fr));
  gap: 12px;
  margin: .45rem 0 1.1rem;
}
.tile {
  position: relative;
  min-width: 0;
  overflow: hidden;
  padding: 15px 16px 14px;
  border: 1px solid rgba(255,255,255,.9);
  border-radius: 17px;
  background: linear-gradient(145deg, rgba(255,255,255,.74), rgba(255,255,255,.39));
  -webkit-backdrop-filter: blur(18px) saturate(155%);
  backdrop-filter: blur(18px) saturate(155%);
  box-shadow: 0 8px 24px rgba(28,67,45,.065), inset 0 1px 0 rgba(255,255,255,.95);
  transition: transform .2s var(--ease), border-color .2s var(--ease), box-shadow .2s var(--ease);
}
.tile:hover { transform: translateY(-2px); border-color: #fff; box-shadow: 0 14px 30px rgba(28,67,45,.11), inset 0 1px 0 #fff; }
.tile-n { color: var(--muted-strong); font-size: .69rem; font-weight: 780; text-transform: uppercase; letter-spacing: .08em; }
.tile-v { margin-top: 3px; color: var(--green-deep); font-size: 1.67rem; font-weight: 820; line-height: 1.25; letter-spacing: -.05em; font-variant-numeric: tabular-nums; }
.tile-u { margin-top: 1px; color: var(--muted); font-size: .74rem; }
.empty { padding: 2rem 1rem 1rem; text-align: center; }
.empty .ico {
  width: 60px;
  height: 60px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 13px;
  border: 1px solid rgba(255,255,255,.95);
  border-radius: 19px;
  background: linear-gradient(145deg, rgba(255,255,255,.9), rgba(216,241,224,.7));
  box-shadow: 0 8px 22px rgba(28,67,45,.08), inset 0 1px 0 #fff;
}
.empty h3 { margin: 0 0 .4rem; padding: 0; color: var(--ink); font-size: 1.12rem; font-weight: 760; letter-spacing: -.03em; }
.empty p { max-width: 520px; margin: 0 auto .8rem; color: var(--muted); font-size: .9rem; line-height: 1.6; }
.item-t { color: var(--ink); font-size: .98rem; font-weight: 750; }
.item-m { margin-top: 8px; padding-bottom: 8px; }

/* ---- Buttons and controls: glossy, tactile glass ---- */
.stButton > button, .stDownloadButton > button,
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
  min-height: 43px;
  padding: .49rem 1.05rem;
  border-radius: 13px;
  font-size: .87rem;
  font-weight: 710;
  transition: transform .17s var(--ease), box-shadow .17s var(--ease), background .17s var(--ease), border-color .17s var(--ease);
}
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(1px) scale(.99); }
[data-testid="stBaseButton-primary"] {
  border: 1px solid rgba(255,255,255,.55) !important;
  background: linear-gradient(135deg, #28845D 0%, #176344 55%, #10472F 100%) !important;
  color: #fff !important;
  box-shadow: 0 7px 16px rgba(23,99,68,.21), inset 0 1px 0 rgba(255,255,255,.25);
}
[data-testid="stBaseButton-primary"]:hover {
  border-color: rgba(255,255,255,.82) !important;
  background: linear-gradient(135deg, #32966A 0%, #176344 55%, #10472F 100%) !important;
  box-shadow: 0 10px 22px rgba(23,99,68,.26), inset 0 1px 0 rgba(255,255,255,.3);
  transform: translateY(-1px);
}
[data-testid="stBaseButton-secondary"] {
  border: 1px solid rgba(255,255,255,.92) !important;
  background: linear-gradient(145deg, rgba(255,255,255,.82), rgba(255,255,255,.48)) !important;
  color: var(--ink-soft) !important;
  -webkit-backdrop-filter: blur(14px) saturate(150%);
  backdrop-filter: blur(14px) saturate(150%);
  box-shadow: 0 5px 14px rgba(28,67,45,.065), inset 0 1px 0 #fff;
}
[data-testid="stBaseButton-secondary"]:hover {
  border-color: #fff !important;
  background: rgba(255,255,255,.86) !important;
  color: var(--green-deep) !important;
  box-shadow: 0 8px 18px rgba(28,67,45,.10), inset 0 1px 0 #fff;
  transform: translateY(-1px);
}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color: var(--muted-strong); font-size: .81rem; font-weight: 710; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  border: 1px solid rgba(255,255,255,.94) !important;
  border-radius: 13px !important;
  background: rgba(255,255,255,.64) !important;
  -webkit-backdrop-filter: blur(16px) saturate(145%);
  backdrop-filter: blur(16px) saturate(145%);
  box-shadow: 0 4px 13px rgba(28,67,45,.045), inset 0 1px 0 rgba(255,255,255,.95) !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
  border-color: rgba(65,151,105,.70) !important;
  box-shadow: 0 0 0 3px rgba(62,152,112,.13), 0 5px 14px rgba(28,67,45,.055), inset 0 1px 0 #fff !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input { color: var(--ink); }
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color: var(--ink-soft); }
[data-testid="stSlider"] [role="slider"] { border-color: var(--green) !important; box-shadow: 0 0 0 4px rgba(62,152,112,.14); }

/* ---- Tabs, expanders, alerts and uploaders ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 5px;
  padding: 5px;
  border: 1px solid rgba(255,255,255,.88);
  border-radius: 15px;
  background: rgba(255,255,255,.36);
  -webkit-backdrop-filter: blur(18px) saturate(155%);
  backdrop-filter: blur(18px) saturate(155%);
  box-shadow: 0 5px 16px rgba(28,67,45,.045), inset 0 1px 0 rgba(255,255,255,.95);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 39px;
  padding: 0 15px;
  border-radius: 11px;
  color: var(--muted-strong);
  font-size: .84rem;
  font-weight: 690;
}
[data-testid="stTabs"] [aria-selected="true"] {
  border: 1px solid rgba(255,255,255,.96) !important;
  background: linear-gradient(145deg, rgba(255,255,255,.95), rgba(236,248,239,.82)) !important;
  color: var(--green-deep) !important;
  box-shadow: 0 4px 12px rgba(28,67,45,.07), inset 0 1px 0 #fff;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: transparent; }
[data-testid="stExpander"] details {
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.9) !important;
  border-radius: 15px !important;
  background: rgba(255,255,255,.52);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  backdrop-filter: blur(18px) saturate(150%);
  box-shadow: 0 7px 20px rgba(28,67,45,.055), inset 0 1px 0 rgba(255,255,255,.95);
}
[data-testid="stExpander"] summary { color: var(--ink-soft); font-weight: 700; }
[data-testid="stAlert"] {
  border: 1px solid rgba(255,255,255,.9) !important;
  border-radius: 15px !important;
  -webkit-backdrop-filter: blur(16px) saturate(150%);
  backdrop-filter: blur(16px) saturate(150%);
  box-shadow: 0 6px 18px rgba(28,67,45,.055), inset 0 1px 0 rgba(255,255,255,.85);
}
[data-testid="stAlert"] p { color: var(--ink-soft); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { background: var(--blue-wash); }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: rgba(226,246,232,.8); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: var(--amber-wash); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) { background: var(--red-wash); }
[data-testid="stFileUploader"] section {
  border: 1.5px dashed rgba(88,145,108,.46);
  border-radius: 16px;
  background: rgba(255,255,255,.44);
  -webkit-backdrop-filter: blur(15px) saturate(145%);
  backdrop-filter: blur(15px) saturate(145%);
}
[data-testid="stFileUploader"] section:hover { border-color: #68A782; background: rgba(255,255,255,.68); }

/* ---- Dataframes, tables and chart surfaces ---- */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.9);
  border-radius: 16px;
  background: rgba(255,255,255,.56);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  backdrop-filter: blur(18px) saturate(150%);
  box-shadow: 0 8px 24px rgba(28,67,45,.065), inset 0 1px 0 rgba(255,255,255,.95);
}
[data-testid="stDataFrame"] [role="grid"] { border: 0; }
[data-testid="stTable"] table { border-collapse: collapse; }
[data-testid="stTable"] th { background: rgba(222,239,226,.68); color: var(--ink-soft); font-size: .79rem; font-weight: 760; }
[data-testid="stTable"] td { background: rgba(255,255,255,.28); color: var(--ink-soft); font-size: .84rem; }
[data-testid="stTable"] th, [data-testid="stTable"] td { padding: .7rem .8rem; border-color: rgba(111,148,122,.15); }
[data-testid="stVegaLiteChart"], [data-testid="stPlotlyChart"], [data-testid="stPyplot"] {
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.88);
  border-radius: 16px;
  background: rgba(255,255,255,.48);
  -webkit-backdrop-filter: blur(16px) saturate(145%);
  backdrop-filter: blur(16px) saturate(145%);
  box-shadow: 0 8px 24px rgba(28,67,45,.055), inset 0 1px 0 rgba(255,255,255,.92);
}

/* ---- Fine details and accessibility ---- */
hr { height: 1px; border: 0 !important; background: linear-gradient(90deg, transparent, rgba(92,135,104,.28), transparent); margin: 1.6rem 0 !important; }
:focus-visible { outline: 3px solid rgba(62,152,112,.34); outline-offset: 2px; }
::selection { background: rgba(178,222,190,.72); color: var(--green-deep); }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; }
}

/* ---- Responsive layouts ---- */
@media (max-width: 900px) {
  .block-container { padding: 6rem 1.35rem 3rem; }
  .st-key-topbar { inset: 8px 10px auto 10px; padding: 0 .8rem; }
  .st-key-topbar [data-testid="stColumn"]:first-child { margin-right: .35rem; }
  .brand { gap: 8px; font-size: .92rem; }
  .logo { width: 35px; height: 35px; flex-basis: 35px; }
  [data-testid="stPageLink-NavLink"] { padding: .4rem .65rem; font-size: .82rem; }
}
@media (max-width: 650px) {
  .block-container { padding: 5.55rem 1rem 2.5rem; }
  .st-key-topbar { inset: 7px 7px auto 7px; min-height: 59px; padding: 0 .55rem; border-radius: 17px; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { gap: .1rem; }
  .st-key-topbar [data-testid="stColumn"]:first-child {
    flex: 0 0 40px !important;
    width: 40px !important;
    min-width: 40px !important;
    margin-right: .1rem;
  }
  .st-key-topbar [data-testid="stColumn"]:nth-child(2),
  .st-key-topbar [data-testid="stColumn"]:nth-child(3),
  .st-key-topbar [data-testid="stColumn"]:nth-child(4) {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
  }
  .st-key-topbar [data-testid="stColumn"]:last-child { display: none; }
  .brand-name { display: none; }
  .logo { width: 33px; height: 33px; flex-basis: 33px; border-radius: 12px; }
  [data-testid="stPageLink-NavLink"] { min-height: 34px; padding: .34rem .42rem; font-size: .73rem; }
  div.ph { padding: 1.1rem 1.15rem 1.2rem; margin-bottom: 1.25rem; border-radius: 20px; }
  div.ph p { font-size: .9rem; }
  div.sec { margin-top: 1.7rem; }
  .kpis { grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
  .kpi { padding: 15px 13px; border-radius: 17px; }
  .kpi-v { font-size: 1.62rem; }
  .tiles { grid-template-columns: repeat(2, minmax(0,1fr)); gap: 9px; }
  .tile { padding: 13px 13px 12px; }
}
@media (max-width: 390px) {
  .st-key-topbar [data-testid="stHorizontalBlock"] { gap: 0; }
  [data-testid="stPageLink-NavLink"] { padding-left: .32rem; padding-right: .32rem; font-size: .69rem; }
  .kpis { grid-template-columns: 1fr; }
}
</style>
"""


LEAF = (
    '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false">'
    '<path d="M5 19c0-8.5 5-13.5 14-14 0 9-5 14-14 14z"/>'
    '<path d="M5 19c3-5 6-8.5 10-10.5"/></svg>'
)


def _text(value: object) -> str:
    """Escape dynamic text before placing it in an HTML fragment."""
    return html.escape(str(value), quote=True)


def inject_css() -> None:
    """Inject the app-wide design system. Call once near the top of each page."""
    st.markdown(CSS, unsafe_allow_html=True)


def card(key: str):
    """Return a white, bordered Streamlit container. ``key`` must be page-unique."""
    return st.container(border=True, key=f"card-{key}")


def top_bar(pages: dict) -> None:
    """Render the fixed brand/navigation bar. ``pages`` maps page keys to ``st.Page`` objects."""
    with st.container(key="topbar"):
        brand, overview, database, recommendations, _spacer = st.columns(
            [3.2, 1.15, 1.1, 1.75, 2.8],
            vertical_alignment="center",
        )
        brand.markdown(
            f'<div class="brand"><span class="logo">{LEAF.format(s=20, c="#FFFFFF")}</span>'
            '<span class="brand-name">Fertilizer Recommendation</span></div>',
            unsafe_allow_html=True,
        )
        overview.page_link(pages["overview"], label="Overview")
        database.page_link(pages["database"], label="Database")
        recommendations.page_link(pages["recommendations"], label="Recommendations")


def page_header(title: str, subtitle: str) -> None:
    """Render a page title and supporting description."""
    st.markdown(
        f'<div class="ph"><h1>{_text(title)}</h1><p>{_text(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def section(title: str, number=None, note: str = "") -> None:
    """Render a section heading with an optional number and note."""
    badge = f'<span class="num">{_text(number)}</span>' if number is not None else ""
    small = f"<small>{_text(note)}</small>" if note else ""
    st.markdown(
        f'<div class="sec">{badge}<h2>{_text(title)}</h2>{small}</div>',
        unsafe_allow_html=True,
    )


def kpi(label: str, value, hint: str = "", share=None, tone: str = "") -> str:
    """Return an HTML KPI card. ``share`` is an optional progress value from 0 to 1."""
    bar = ""
    if share is not None:
        try:
            progress = float(share)
            if math.isfinite(progress):
                progress = min(1.0, max(0.0, progress))
                bar = f'<div class="bar"><span style="width:{progress * 100:.1f}%"></span></div>'
        except (TypeError, ValueError):
            pass
    safe_tone = " ".join(part for part in str(tone).split() if part.isalnum() or part in {"-", "_"})
    return (
        f'<div class="kpi {safe_tone}"><div class="kpi-l">{_text(label)}</div>'
        f'<div class="kpi-v">{_text(value)}</div><div class="kpi-h">{_text(hint)}</div>{bar}</div>'
    )


def kpi_grid(cards: Iterable[str]) -> None:
    """Render a responsive grid of KPI HTML returned by :func:`kpi`."""
    st.markdown(f'<div class="kpis">{"".join(cards)}</div>', unsafe_allow_html=True)


def chip(text: str, tone: str = "") -> str:
    """Return a compact status chip. Supported tones: warn, muted, danger, info."""
    safe_tone = " ".join(part for part in str(tone).split() if part.isalnum() or part in {"-", "_"})
    return f'<span class="chip {safe_tone}">{_text(text)}</span>'


def card_text(title: str, text: str, badge=None) -> None:
    """Render a compact title/description pair, optionally with a badge."""
    mark = f'<div class="badge">{_text(badge)}</div>' if badge is not None else ""
    st.markdown(
        f'{mark}<div class="card-t">{_text(title)}</div><p class="card-p">{_text(text)}</p>',
        unsafe_allow_html=True,
    )


def tiles(items: Sequence[tuple[str, float]]) -> None:
    """Render dose tiles from ``[(name, value), ...]``; values are shown as g/tree."""
    rendered = []
    for name, value in items:
        try:
            formatted_value = f"{float(value):,.0f}"
        except (TypeError, ValueError):
            formatted_value = _text(value)
        rendered.append(
            '<div class="tile">'
            f'<div class="tile-n">{_text(name)}</div>'
            f'<div class="tile-v">{formatted_value}</div>'
            '<div class="tile-u">g/tree</div></div>'
        )
    st.markdown(f'<div class="tiles">{"".join(rendered)}</div>', unsafe_allow_html=True)


def empty_state(title: str, text: str) -> None:
    """Render a friendly empty state with the app's leaf mark."""
    st.markdown(
        f'<div class="empty"><div class="ico">{LEAF.format(s=29, c="#176044")}</div>'
        f'<h3>{_text(title)}</h3><p>{_text(text)}</p></div>',
        unsafe_allow_html=True,
    )
