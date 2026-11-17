"""Visual system and reusable UI components for the Fertilizer Recommendation app.

Import this module from Streamlit pages and call ``inject_css()`` once per page.
Helper function names and signatures are unchanged from the original UI.

Design language: **clean liquid glass**
  * One shared material (fill, blur, specular edge, soft depth shadow) used by every
    surface, so the whole app reads as a single, consistent glass system.
  * A calm, light-filled backdrop with slow drifting colour so the blur has something
    to refract, kept low-contrast so content stays the focus.
  * Graceful fallbacks when ``backdrop-filter`` is unavailable or the user prefers
    reduced transparency / reduced motion.

Tip: for slider / toggle accents to match, set in ``.streamlit/config.toml``:
    [theme]
    base = "light"
    primaryColor = "#176344"
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
/* ==========================================================================
   1. TOKENS
   ========================================================================== */
:root {
  color-scheme: light;

  /* Ink */
  --ink: #10261D;
  --ink-soft: #2F4A3D;
  --muted: #5F766A;          /* AA-contrast on glass */
  --muted-strong: #46604F;

  /* Brand */
  --green: #176344;
  --green-deep: #0F4A31;
  --green-bright: #35966B;
  --mint: #DDF2E5;

  /* Status */
  --amber: #8A5A0A;  --amber-wash: rgba(255,243,215,.78);
  --red:   #A13B3B;  --red-wash:   rgba(255,234,231,.80);
  --blue:  #2F6784;  --blue-wash:  rgba(228,245,251,.80);

  /* The glass material ---------------------------------------------------- */
  --g-fill:        linear-gradient(145deg, rgba(255,255,255,.64) 0%, rgba(255,255,255,.30) 100%);
  --g-fill-strong: linear-gradient(145deg, rgba(255,255,255,.82) 0%, rgba(255,255,255,.48) 100%);
  --g-fill-soft:   linear-gradient(145deg, rgba(255,255,255,.46) 0%, rgba(255,255,255,.22) 100%);
  --g-blur:        blur(24px) saturate(180%);
  --g-blur-soft:   blur(16px) saturate(160%);

  /* Specular rim: bright top-left, faint mid, glint bottom-right */
  --g-edge: linear-gradient(150deg,
              rgba(255,255,255,.98) 0%,
              rgba(255,255,255,.38) 28%,
              rgba(255,255,255,.10) 62%,
              rgba(255,255,255,.80) 100%);
  --g-inset: inset 0 1px 0 rgba(255,255,255,.95),
             inset 0 -1px 0 rgba(255,255,255,.28),
             inset 0 0 22px rgba(255,255,255,.16);

  --shadow-1: 0 1px 1px rgba(20,60,40,.04), 0 6px 18px rgba(24,66,46,.07);
  --shadow-2: 0 1px 1px rgba(20,60,40,.05), 0 12px 32px rgba(24,66,46,.10),
              0 30px 60px -22px rgba(24,66,46,.14);
  --shadow-3: 0 2px 2px rgba(20,60,40,.05), 0 18px 44px rgba(24,66,46,.14),
              0 40px 80px -24px rgba(24,66,46,.18);

  --r-sm: 12px;
  --r-md: 18px;
  --r-lg: 26px;
  --ease: cubic-bezier(.2,.75,.25,1);
}

/* ==========================================================================
   2. BACKDROP  (calm colour field the glass can refract)
   ========================================================================== */
html, body, [class*="stApp"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", sans-serif;
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.stApp {
  position: relative;
  isolation: isolate;
  min-height: 100vh;
  background:
    radial-gradient(60rem 40rem at 6% 0%,   rgba(190,229,200,.80), transparent 62%),
    radial-gradient(52rem 36rem at 96% 4%,  rgba(184,228,226,.72), transparent 62%),
    radial-gradient(56rem 40rem at 82% 96%, rgba(210,224,246,.72), transparent 64%),
    radial-gradient(44rem 32rem at 10% 90%, rgba(226,240,214,.70), transparent 64%),
    linear-gradient(160deg, #EEF5F0 0%, #E7F0EB 50%, #ECF3F5 100%);
  background-attachment: fixed;
}
/* Slow-drifting light orbs */
.stApp::before {
  content: "";
  position: fixed;
  inset: -20%;
  z-index: -2;
  pointer-events: none;
  opacity: .70;
  filter: blur(54px);
  background:
    radial-gradient(circle at 20% 28%, rgba(255,255,255,.90) 0 6%,  transparent 22%),
    radial-gradient(circle at 74% 24%, rgba(170,222,205,.62) 0 8%,  transparent 25%),
    radial-gradient(circle at 56% 76%, rgba(255,255,255,.70) 0 6%,  transparent 22%),
    radial-gradient(circle at 88% 70%, rgba(176,214,236,.50) 0 7%,  transparent 24%);
  animation: drift 38s ease-in-out infinite alternate;
}
/* Ultra-fine grain: removes gradient banding and gives glass a tactile feel */
.stApp::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: .22;
  mix-blend-mode: soft-light;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}
@keyframes drift {
  from { transform: translate3d(-2%, -1%, 0) scale(1);    }
  to   { transform: translate3d(2%, 2%, 0)  scale(1.06); }
}

.block-container {
  position: relative;
  z-index: 1;
  max-width: 1380px;
  padding: 7rem 2.2rem 4.5rem;   /* clears the floating nav */
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stVerticalBlock"] { gap: 1rem; }
[data-testid="stElementContainer"] { min-width: 0; }
[data-testid="stMarkdownContainer"] p { line-height: 1.65; }
[data-testid="stMarkdownContainer"] a {
  color: var(--green-deep);
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}
[data-testid="stMarkdownContainer"] a:hover { color: var(--green-bright); }

/* ==========================================================================
   3. SHARED GLASS SURFACE
   Fill + blur + depth live here once; the rim light is a masked pseudo-element.
   ========================================================================== */
.st-key-topbar,
div.ph,
[class*="st-key-card-"],
.kpi,
.tile,
[data-testid="stMetric"] {
  background: var(--g-fill);
  -webkit-backdrop-filter: var(--g-blur);
  backdrop-filter: var(--g-blur);
  box-shadow: var(--shadow-2), var(--g-inset);
  border: 0 !important;
}
div.ph, [class*="st-key-card-"], .kpi, .tile, [data-testid="stMetric"] { position: relative; }

/* Specular rim */
.st-key-topbar::before,
div.ph::before,
[class*="st-key-card-"]::before,
.kpi::before,
.tile::before,
[data-testid="stMetric"]::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: inherit;
  padding: 1px;
  pointer-events: none;
  background: var(--g-edge);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);
}
/* Content sits above the sheen */
.kpi > *, .tile > *, div.ph > * { position: relative; z-index: 1; }
[class*="st-key-card-"] > [data-testid="stVerticalBlock"] { position: relative; z-index: 1; }

/* ==========================================================================
   4. NAVIGATION
   ========================================================================== */
.st-key-topbar {
  position: fixed;
  top: 12px;
  left: 50%;
  z-index: 1000;
  /* Spans the full viewport width minus an even 18px gap on each side (no max cap). */
  width: calc(100vw - 36px) !important;
  max-width: none !important;
  min-height: 66px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 2.2rem;
  transform: translateX(-50%);
  border-radius: 24px;
  background: var(--g-fill-strong);
  -webkit-backdrop-filter: blur(28px) saturate(190%);
  backdrop-filter: blur(28px) saturate(190%);
  box-shadow: var(--shadow-3), var(--g-inset);
}
/* soft diagonal highlight */
.st-key-topbar::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(112deg, rgba(255,255,255,.46) 0%, transparent 34%, rgba(255,255,255,.10) 70%, transparent 100%);
}
.st-key-topbar > * { position: relative; z-index: 1; }
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
  position: relative;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 13px;
  background: linear-gradient(150deg, #47A67C 0%, #176344 58%, #0F4A31 100%);
  box-shadow: 0 8px 18px rgba(23,99,68,.28),
              inset 0 1px 0 rgba(255,255,255,.45),
              inset 0 -6px 10px rgba(0,0,0,.14),
              0 0 0 1px rgba(255,255,255,.35);
}
.logo::after {   /* gloss */
  content: "";
  position: absolute;
  inset: 0 0 52% 0;
  background: linear-gradient(180deg, rgba(255,255,255,.38), rgba(255,255,255,0));
  pointer-events: none;
}
.logo svg { position: relative; z-index: 1; }

[data-testid="stPageLink-NavLink"] {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: .45rem .95rem;
  border: 1px solid transparent;
  border-radius: 13px;
  color: var(--muted-strong);
  font-size: .87rem;
  font-weight: 650;
  transition: background .2s var(--ease), color .2s var(--ease), box-shadow .2s var(--ease), border-color .2s var(--ease);
}
[data-testid="stPageLink-NavLink"] p { white-space: nowrap; margin: 0; }
[data-testid="stPageLink-NavLink"]:hover {
  border-color: rgba(255,255,255,.9);
  background: rgba(255,255,255,.55);
  color: var(--green-deep);
  box-shadow: 0 4px 14px rgba(28,67,45,.07), inset 0 1px 0 rgba(255,255,255,.95);
}
[data-testid="stPageLink-NavLink"][aria-current="page"] {
  border-color: rgba(255,255,255,.95);
  background: linear-gradient(145deg, rgba(255,255,255,.92), rgba(226,244,232,.70));
  color: var(--green-deep);
  font-weight: 760;
  box-shadow: 0 5px 14px rgba(28,67,45,.09), inset 0 1px 0 #fff, inset 0 -1px 0 rgba(120,170,140,.12);
}

/* ==========================================================================
   5. PAGE HEADER & SECTIONS
   ========================================================================== */
div.ph {
  overflow: hidden;
  margin: .25rem 0 1.75rem;
  padding: 1.55rem 1.75rem 1.6rem;
  border-radius: var(--r-lg);
  background: var(--g-fill-strong);
  animation: rise .55s var(--ease) both;
}
div.ph::after {
  content: "";
  position: absolute;
  top: -90px;
  right: -40px;
  width: 320px;
  height: 230px;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(ellipse, rgba(170,226,196,.42), transparent 68%);
}
div.ph h1 {
  margin: 0;
  padding: 0;
  color: var(--ink);
  font-size: clamp(1.8rem, 3vw, 2.45rem);
  font-weight: 820;
  line-height: 1.14;
  letter-spacing: -.055em;
}
div.ph p {
  max-width: 760px;
  margin: .6rem 0 0;
  color: var(--muted);
  font-size: .98rem;
  line-height: 1.65;
}
@keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

div.sec {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin: 2.2rem 0 1rem;
}
div.sec h2 {
  margin: 0;
  padding: 0;
  color: var(--ink);
  font-size: 1.14rem;
  font-weight: 770;
  letter-spacing: -.03em;
}
div.sec small { color: var(--muted); font-size: .83rem; font-weight: 480; }
div.sec .num {
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(145deg, rgba(255,255,255,.95), rgba(214,240,224,.72));
  color: var(--green-deep);
  font-size: .76rem;
  font-weight: 790;
  box-shadow: 0 4px 12px rgba(28,67,45,.08), inset 0 1px 0 #fff, 0 0 0 1px rgba(255,255,255,.8);
}

/* ==========================================================================
   6. CARDS, KPIs, CHIPS, TILES
   ========================================================================== */
[class*="st-key-card-"] {
  overflow: hidden;
  padding: 1.3rem 1.4rem;
  border-radius: var(--r-md) !important;
  transition: box-shadow .25s var(--ease);
}
[class*="st-key-card-"]:hover { box-shadow: var(--shadow-3), var(--g-inset); }

.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: 16px;
  margin: .4rem 0 1.2rem;
}
.kpi {
  --glow: rgba(176,228,198,.55);
  isolation: isolate;
  min-width: 0;
  overflow: hidden;
  padding: 20px 21px 18px;
  border-radius: 22px;
  background: var(--g-fill-strong);
  transition: transform .25s var(--ease), box-shadow .25s var(--ease);
}
.kpi::after {      /* tinted glow + sheen */
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(circle at 100% 0%, var(--glow), transparent 58%),
    linear-gradient(180deg, rgba(255,255,255,.34), transparent 42%);
}
.kpi:hover { transform: translateY(-3px); box-shadow: var(--shadow-3), var(--g-inset); }
.kpi-l { color: var(--muted-strong); font-size: .71rem; font-weight: 780; text-transform: uppercase; letter-spacing: .09em; }
.kpi-v {
  margin: .46rem 0 .22rem;
  color: var(--green-deep);
  font-size: clamp(1.8rem, 3vw, 2.3rem);
  font-weight: 830;
  line-height: 1.12;
  letter-spacing: -.06em;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}
.kpi.amber  { --glow: rgba(255,222,160,.60); }
.kpi.amber .kpi-v { color: var(--amber); }
.kpi.danger { --glow: rgba(255,200,196,.60); }
.kpi.danger .kpi-v { color: var(--red); }
.kpi.info   { --glow: rgba(184,224,240,.60); }
.kpi.info .kpi-v { color: var(--blue); }
.kpi.plain  { --glow: rgba(214,226,222,.62); }
.kpi.plain .kpi-v { color: var(--ink); }
.kpi-h { color: var(--muted); font-size: .82rem; line-height: 1.5; }

.bar {
  height: 8px;
  overflow: hidden;
  margin-top: 14px;
  border-radius: 999px;
  background: rgba(40,84,57,.10);
  box-shadow: inset 0 1px 2px rgba(24,66,46,.12), 0 1px 0 rgba(255,255,255,.7);
}
.bar span {
  position: relative;
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #176344 0%, #4DAA7E 70%, #97CDA8 100%);
  box-shadow: 0 0 12px rgba(62,152,112,.30), inset 0 1px 0 rgba(255,255,255,.45);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin: 2px 5px 2px 0;
  padding: 5px 11px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255,255,255,.85), rgba(221,242,229,.66));
  color: var(--green-deep);
  font-size: .75rem;
  font-weight: 740;
  line-height: 1.2;
  white-space: nowrap;
  box-shadow: 0 3px 9px rgba(28,67,45,.06), inset 0 1px 0 #fff, 0 0 0 1px rgba(255,255,255,.85);
}
.chip.warn   { background: linear-gradient(135deg, rgba(255,255,255,.88), var(--amber-wash)); color: var(--amber); }
.chip.muted  { background: rgba(255,255,255,.58); color: var(--muted-strong); }
.chip.danger { background: linear-gradient(135deg, rgba(255,255,255,.88), var(--red-wash)); color: var(--red); }
.chip.info   { background: linear-gradient(135deg, rgba(255,255,255,.88), var(--blue-wash)); color: var(--blue); }

.badge {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 11px;
  border-radius: 11px;
  background: linear-gradient(145deg, rgba(255,255,255,.95), rgba(214,240,224,.74));
  color: var(--green-deep);
  font-size: .88rem;
  font-weight: 790;
  box-shadow: 0 4px 12px rgba(28,67,45,.08), inset 0 1px 0 #fff, 0 0 0 1px rgba(255,255,255,.85);
}
.card-t { margin: 0 0 5px; color: var(--ink); font-size: 1rem; font-weight: 770; letter-spacing: -.025em; }
.card-p { margin: 0 0 6px; color: var(--muted); font-size: .9rem; line-height: 1.62; }
.mono { color: #54695C; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .79rem; overflow-wrap: anywhere; }

.tiles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 135px), 1fr));
  gap: 12px;
  margin: .45rem 0 1.1rem;
}
.tile {
  min-width: 0;
  overflow: hidden;
  padding: 15px 16px 14px;
  border-radius: 18px;
  background: var(--g-fill);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), var(--g-inset);
  transition: transform .22s var(--ease), box-shadow .22s var(--ease);
}
.tile:hover { transform: translateY(-2px); box-shadow: var(--shadow-2), var(--g-inset); }
.tile-n { color: var(--muted-strong); font-size: .69rem; font-weight: 780; text-transform: uppercase; letter-spacing: .08em; }
.tile-v { margin-top: 3px; color: var(--green-deep); font-size: 1.67rem; font-weight: 820; line-height: 1.25; letter-spacing: -.05em; font-variant-numeric: tabular-nums; }
.tile-u { margin-top: 1px; color: var(--muted); font-size: .74rem; }

.empty { padding: 2rem 1rem 1rem; text-align: center; }
.empty .ico {
  width: 62px;
  height: 62px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(255,255,255,.95), rgba(214,240,224,.72));
  box-shadow: 0 10px 24px rgba(28,67,45,.10), inset 0 1px 0 #fff, 0 0 0 1px rgba(255,255,255,.85);
}
.empty h3 { margin: 0 0 .4rem; padding: 0; color: var(--ink); font-size: 1.12rem; font-weight: 770; letter-spacing: -.03em; }
.empty p { max-width: 520px; margin: 0 auto .8rem; color: var(--muted); font-size: .9rem; line-height: 1.6; }
.item-t { color: var(--ink); font-size: .98rem; font-weight: 750; }
.item-m { margin-top: 8px; padding-bottom: 8px; }

/* ==========================================================================
   7. BUTTONS & FORM CONTROLS
   ========================================================================== */
.stButton > button, .stDownloadButton > button,
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
  min-height: 43px;
  padding: .49rem 1.1rem;
  border-radius: 14px;
  font-size: .87rem;
  font-weight: 720;
  transition: transform .18s var(--ease), box-shadow .18s var(--ease), background .18s var(--ease), border-color .18s var(--ease);
}
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(1px) scale(.992); }

[data-testid="stBaseButton-primary"] {
  border: 1px solid rgba(255,255,255,.50) !important;
  background: linear-gradient(180deg, #34996E 0%, #176344 55%, #0F4A31 100%) !important;
  color: #fff !important;
  box-shadow: 0 8px 18px rgba(23,99,68,.26),
              inset 0 1px 0 rgba(255,255,255,.42),
              inset 0 -8px 14px rgba(0,0,0,.10);
}
[data-testid="stBaseButton-primary"]:hover {
  border-color: rgba(255,255,255,.80) !important;
  background: linear-gradient(180deg, #3FA97C 0%, #1B7050 55%, #0F4A31 100%) !important;
  box-shadow: 0 12px 24px rgba(23,99,68,.30), inset 0 1px 0 rgba(255,255,255,.50), inset 0 -8px 14px rgba(0,0,0,.08);
  transform: translateY(-1px);
}
[data-testid="stBaseButton-secondary"] {
  border: 1px solid rgba(255,255,255,.95) !important;
  background: var(--g-fill-strong) !important;
  color: var(--ink-soft) !important;
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), inset 0 1px 0 #fff;
}
[data-testid="stBaseButton-secondary"]:hover {
  border-color: #fff !important;
  background: rgba(255,255,255,.90) !important;
  color: var(--green-deep) !important;
  box-shadow: 0 10px 20px rgba(28,67,45,.11), inset 0 1px 0 #fff;
  transform: translateY(-1px);
}

[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color: var(--muted-strong); font-size: .81rem; font-weight: 720; }

/* Inputs read as slightly recessed glass wells */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  border: 1px solid rgba(255,255,255,.95) !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,.55) !important;
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: inset 0 1px 3px rgba(24,66,46,.08), 0 1px 0 rgba(255,255,255,.85) !important;
  transition: border-color .18s var(--ease), box-shadow .18s var(--ease), background .18s var(--ease);
}
[data-baseweb="input"]:hover, [data-baseweb="select"] > div:hover { background: rgba(255,255,255,.70) !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
  border-color: rgba(53,150,107,.75) !important;
  background: rgba(255,255,255,.82) !important;
  box-shadow: 0 0 0 4px rgba(53,150,107,.14), inset 0 1px 2px rgba(24,66,46,.06) !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input { color: var(--ink); background: transparent !important; }
[data-baseweb="tag"] {
  border-radius: 999px !important;
  background: linear-gradient(135deg, rgba(255,255,255,.88), rgba(221,242,229,.70)) !important;
  color: var(--green-deep) !important;
}
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color: var(--ink-soft); }
[data-testid="stSlider"] [role="slider"] {
  border: 2px solid #fff !important;
  background: var(--green) !important;
  box-shadow: 0 0 0 4px rgba(53,150,107,.18), 0 3px 8px rgba(23,99,68,.30);
}

/* Dropdown / popover menus */
[data-baseweb="popover"] > div {
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.95) !important;
  border-radius: 16px !important;
  background: rgba(255,255,255,.80) !important;
  -webkit-backdrop-filter: blur(26px) saturate(185%);
  backdrop-filter: blur(26px) saturate(185%);
  box-shadow: var(--shadow-3), inset 0 1px 0 #fff !important;
}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul { background: transparent !important; }
[data-baseweb="popover"] li { border-radius: 10px; margin: 2px 6px; transition: background .15s var(--ease); }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] { background: rgba(214,240,224,.75) !important; }

/* Dialogs */
div[role="dialog"] {
  border: 1px solid rgba(255,255,255,.95);
  border-radius: 24px !important;
  background: rgba(255,255,255,.78) !important;
  -webkit-backdrop-filter: blur(30px) saturate(190%);
  backdrop-filter: blur(30px) saturate(190%);
  box-shadow: var(--shadow-3), inset 0 1px 0 #fff;
}

/* ==========================================================================
   8. TABS, EXPANDERS, ALERTS, UPLOADER, METRIC
   ========================================================================== */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 5px;
  padding: 5px;
  border-radius: 16px;
  background: var(--g-fill-soft);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), inset 0 1px 0 rgba(255,255,255,.95), 0 0 0 1px rgba(255,255,255,.7);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 39px;
  padding: 0 16px;
  border-radius: 12px;
  color: var(--muted-strong);
  font-size: .84rem;
  font-weight: 700;
  transition: background .18s var(--ease), color .18s var(--ease);
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { background: rgba(255,255,255,.45); }
[data-testid="stTabs"] [aria-selected="true"] {
  background: linear-gradient(145deg, rgba(255,255,255,.96), rgba(236,248,239,.82)) !important;
  color: var(--green-deep) !important;
  box-shadow: 0 5px 13px rgba(28,67,45,.09), inset 0 1px 0 #fff, 0 0 0 1px rgba(255,255,255,.9);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { background: transparent !important; }

[data-testid="stExpander"] details {
  overflow: hidden;
  border: 0 !important;
  border-radius: 16px !important;
  background: var(--g-fill);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), var(--g-inset), 0 0 0 1px rgba(255,255,255,.8);
}
[data-testid="stExpander"] summary { color: var(--ink-soft); font-weight: 710; }
[data-testid="stExpander"] summary:hover { color: var(--green-deep); }

[data-testid="stAlert"] {
  border: 0 !important;
  border-radius: 16px !important;
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), inset 0 1px 0 rgba(255,255,255,.9), 0 0 0 1px rgba(255,255,255,.8);
}
[data-testid="stAlert"] p { color: var(--ink-soft); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"])    { background: var(--blue-wash); }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: rgba(224,246,231,.82); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: var(--amber-wash); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"])   { background: var(--red-wash); }

[data-testid="stFileUploader"] section {
  border: 1.5px dashed rgba(70,140,100,.45);
  border-radius: 18px;
  background: var(--g-fill-soft);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  transition: border-color .2s var(--ease), background .2s var(--ease);
}
[data-testid="stFileUploader"] section:hover { border-color: #4E9E78; background: rgba(255,255,255,.66); }

[data-testid="stMetric"] { padding: 16px 18px; border-radius: 18px; }
[data-testid="stMetric"] > * { position: relative; z-index: 1; }
[data-testid="stMetricLabel"] p { color: var(--muted-strong); font-weight: 740; }
[data-testid="stMetricValue"] { color: var(--green-deep); font-weight: 820; letter-spacing: -.04em; }

/* ==========================================================================
   9. DATA SURFACES
   ========================================================================== */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  overflow: hidden;
  border-radius: 18px;
  background: rgba(255,255,255,.52);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), inset 0 1px 0 rgba(255,255,255,.95), 0 0 0 1px rgba(255,255,255,.85);
}
[data-testid="stDataFrame"] [role="grid"] { border: 0; }
[data-testid="stTable"] table { border-collapse: collapse; }
[data-testid="stTable"] th { background: rgba(220,238,226,.70); color: var(--ink-soft); font-size: .79rem; font-weight: 770; }
[data-testid="stTable"] td { background: rgba(255,255,255,.26); color: var(--ink-soft); font-size: .84rem; }
[data-testid="stTable"] th, [data-testid="stTable"] td { padding: .7rem .85rem; border-color: rgba(111,148,122,.14); }
[data-testid="stVegaLiteChart"], [data-testid="stPlotlyChart"], [data-testid="stPyplot"] {
  overflow: hidden;
  border-radius: 18px;
  background: rgba(255,255,255,.46);
  -webkit-backdrop-filter: var(--g-blur-soft);
  backdrop-filter: var(--g-blur-soft);
  box-shadow: var(--shadow-1), inset 0 1px 0 rgba(255,255,255,.92), 0 0 0 1px rgba(255,255,255,.8);
}

/* ==========================================================================
   10. DETAILS, ACCESSIBILITY, FALLBACKS
   ========================================================================== */
hr { height: 1px; border: 0 !important; background: linear-gradient(90deg, transparent, rgba(92,135,104,.28), transparent); margin: 1.6rem 0 !important; }
:focus-visible { outline: 3px solid rgba(53,150,107,.40); outline-offset: 2px; border-radius: 10px; }
::selection { background: rgba(178,222,190,.72); color: var(--green-deep); }
* { scrollbar-width: thin; scrollbar-color: rgba(70,110,85,.30) transparent; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { border: 3px solid transparent; border-radius: 999px; background: rgba(70,110,85,.30); background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: rgba(70,110,85,.48); background-clip: padding-box; }

/* No backdrop-filter, or user asked for less transparency: switch to more opaque glass */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  :root {
    --g-fill:        linear-gradient(145deg, rgba(250,253,251,.94), rgba(238,246,241,.90));
    --g-fill-strong: linear-gradient(145deg, rgba(252,254,253,.97), rgba(240,248,243,.94));
    --g-fill-soft:   linear-gradient(145deg, rgba(246,251,248,.90), rgba(236,245,240,.86));
  }
}
@media (prefers-reduced-transparency: reduce) {
  :root {
    --g-fill:        linear-gradient(145deg, rgba(250,253,251,.96), rgba(238,246,241,.92));
    --g-fill-strong: linear-gradient(145deg, rgba(252,254,253,.98), rgba(240,248,243,.96));
    --g-fill-soft:   linear-gradient(145deg, rgba(246,251,248,.92), rgba(236,245,240,.90));
  }
  .stApp::before { filter: none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; }
}

/* ==========================================================================
   11. RESPONSIVE
   ========================================================================== */
@media (max-width: 900px) {
  .block-container { padding: 6rem 1.35rem 3rem; }
  .st-key-topbar { top: 8px; width: calc(100vw - 20px) !important; padding: 0 1rem; }
  .st-key-topbar [data-testid="stColumn"]:first-child { margin-right: .35rem; }
  .brand { gap: 8px; font-size: .92rem; }
  .logo { width: 35px; height: 35px; flex-basis: 35px; }
  [data-testid="stPageLink-NavLink"] { padding: .4rem .65rem; font-size: .82rem; }
}
@media (max-width: 650px) {
  .block-container { padding: 5.55rem 1rem 2.5rem; }
  .st-key-topbar { top: 7px; width: calc(100vw - 14px) !important; min-height: 58px; padding: 0 .6rem; border-radius: 19px; }
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
  div.ph { padding: 1.15rem 1.2rem 1.25rem; margin-bottom: 1.25rem; border-radius: 21px; }
  div.ph p { font-size: .9rem; }
  div.sec { margin-top: 1.7rem; }
  .kpis { grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
  .kpi { padding: 15px 13px; border-radius: 18px; }
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
    """Return a frosted-glass Streamlit container. ``key`` must be page-unique."""
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