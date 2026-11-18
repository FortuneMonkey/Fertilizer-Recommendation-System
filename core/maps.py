"""Compartment map: one point per sampled compartment, drawn with pydeck (ships with Streamlit, no API key)."""
from __future__ import annotations

import html
import math

import numpy as np
import pandas as pd
import pydeck as pdk

# Basemaps from CARTO: free, no token needed
BASEMAPS = {"Light": pdk.map_styles.CARTO_LIGHT, "Streets": pdk.map_styles.CARTO_ROAD,
            "Dark": pdk.map_styles.CARTO_DARK}

# label shown -> soil column ("coverage" is the covered flag)
COLOR_BY = {"Sector": "sector", "SMU": "smu", "Soil Family": "soil_family", "Coverage": "covered",
            "pH": "ph", "N (%)": "n_pct", "P avail. (ppm)": "p_avail",
            "K (cmol/kg)": "k", "Ca (cmol/kg)": "ca", "Mg (cmol/kg)": "mg"}
NUMERIC = {"ph", "n_pct", "p_avail", "k", "ca", "mg"}

# Categorical palette tuned to sit with the app's green glass look
PALETTE = [(23, 99, 68), (47, 103, 132), (214, 140, 38), (161, 59, 59), (109, 76, 155),
           (62, 160, 133), (196, 99, 140), (120, 136, 52), (82, 128, 196), (150, 104, 70),
           (93, 160, 196), (176, 120, 196)]
COVERED, NOT_COVERED = (23, 99, 68), (214, 140, 38)
# Sequential ramp, low -> high (pale mint to deep forest)
RAMP = [(230, 244, 205), (172, 222, 160), (102, 189, 128), (44, 143, 102), (12, 82, 58)]
SELECTED, IN_PLAN = (16, 38, 29), (47, 103, 132)


def coordinates(soil: pd.DataFrame) -> pd.DataFrame:
    """lat/lon per row. Fixes rows where the two columns are swapped (|lat| > 90 cannot be a latitude)."""
    lat = pd.to_numeric(soil.get("lat"), errors="coerce")
    lon = pd.to_numeric(soil.get("lon"), errors="coerce")
    swap = (lat.abs() > 90) & (lon.abs() <= 90)
    return pd.DataFrame({"lat": lat.where(~swap, lon), "lon": lon.where(~swap, lat)}, index=soil.index)


def _hex(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _ramp(t: float):
    """Interpolate the sequential ramp at t in [0, 1]."""
    t = min(1.0, max(0.0, t)) * (len(RAMP) - 1)
    i = min(int(t), len(RAMP) - 2)
    f = t - i
    return tuple(round(a + (b - a) * f) for a, b in zip(RAMP[i], RAMP[i + 1]))


def _fmt(value, digits) -> str:
    return "–" if pd.isna(value) else f"{value:.{digits}f}"


def _colors(points: pd.DataFrame, field: str, reference: pd.DataFrame | None = None):
    """RGB per point and the matching legend HTML."""
    if field == "covered":
        rgb = [COVERED if c else NOT_COVERED for c in points["covered"]]
        items = [("Covered", COVERED), ("Not covered", NOT_COVERED)]
        return rgb, _legend_items(items)

    if field in NUMERIC:
        values = points[field].astype(float)
        valid = values.dropna()
        if valid.empty:
            return [(170, 180, 175)] * len(points), '<span class="legend-note">No values</span>'
        # 5th-95th percentile stretch so one outlier does not wash out the colours
        lo, hi = valid.quantile(.05), valid.quantile(.95)
        if hi <= lo:
            lo, hi = valid.min(), valid.max()
        if hi <= lo:
            hi = lo + 1
        rgb = [(170, 180, 175) if pd.isna(v) else _ramp((v - lo) / (hi - lo)) for v in values]
        stops = ", ".join(f"{_hex(c)} {i * 25}%" for i, c in enumerate(RAMP))
        digits = 2 if hi - lo < 5 else 1
        legend = (f'<span class="legend-num">{lo:.{digits}f}</span>'
                  f'<span class="legend-ramp" style="background:linear-gradient(90deg, {stops})"></span>'
                  f'<span class="legend-num">{hi:.{digits}f}</span>')
        return rgb, legend

    labels = points[field].fillna("Unknown").astype(str)
    # colours come from the whole database, so a sector keeps its colour whatever the filter
    universe = (reference if reference is not None else points)[field].fillna("Unknown").astype(str)
    lookup = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(universe.value_counts().index)}
    order = labels.value_counts().index.tolist()          # legend: biggest groups first
    items = [(name, lookup[name]) for name in order]
    return [lookup[name] for name in labels], _legend_items(items, counts=labels.value_counts())


def _legend_items(items, counts=None, limit=10) -> str:
    parts = [f'<span class="legend-item"><span class="dot" style="background:{_hex(rgb)}"></span>'
             f'{html.escape(name)}{f"<em>{counts[name]}</em>" if counts is not None else ""}</span>'
             for name, rgb in items[:limit]]
    if len(items) > limit:
        parts.append(f'<span class="legend-note">+{len(items) - limit} more</span>')
    return "".join(parts)


def _view(points: pd.DataFrame) -> pdk.ViewState:
    """Frame all points, with some padding."""
    if points.empty:
        return pdk.ViewState(latitude=0.3, longitude=101.0, zoom=7)
    lat_span = points["lat"].max() - points["lat"].min()
    lon_span = points["lon"].max() - points["lon"].min()
    # deck.gl Web Mercator: the world is 512 px wide at zoom 0. Fit into ~1000 x 500 px with padding
    # (near the equator a degree of latitude takes about the same pixels as a degree of longitude).
    fit_lon = math.log2(0.80 * 1000 * 360 / (512 * max(lon_span, 0.01)))
    fit_lat = math.log2(0.75 * 500 * 360 / (512 * max(lat_span, 0.01)))
    zoom = min(13.5, fit_lon, fit_lat)
    return pdk.ViewState(latitude=float((points["lat"].max() + points["lat"].min()) / 2),
                         longitude=float((points["lon"].max() + points["lon"].min()) / 2),
                         zoom=zoom, pitch=0, bearing=0)


TOOLTIP = {
    "html": ('<div class="tt-title">{comp_label}</div>'
             '<div class="tt-sub">{sector_t} · SMU {smu_t} · {soil_family_t}</div>'
             '<div class="tt-status" style="color:{status_color}">● {status}</div>'
             '<table class="tt-grid">'
             '<tr><td>pH</td><td>{ph_t}</td><td>N</td><td>{n_t} %</td></tr>'
             '<tr><td>P</td><td>{p_t} ppm</td><td>K</td><td>{k_t}</td></tr>'
             '<tr><td>Ca</td><td>{ca_t}</td><td>Mg</td><td>{mg_t}</td></tr></table>'
             '<div class="tt-foot">Sampled {date_t} · cations in cmol/kg</div>'),
    "style": {"backgroundColor": "rgba(255,255,255,0.92)", "color": "#10261D", "borderRadius": "14px",
              "padding": "12px 14px", "fontFamily": "Inter, system-ui, sans-serif", "fontSize": "12px",
              "boxShadow": "0 18px 40px rgba(24,66,46,.20), inset 0 1px 0 #fff",
              "border": "1px solid rgba(255,255,255,.95)", "backdropFilter": "blur(18px)"},
}


def build(view: pd.DataFrame, color_label: str, basemap: str,
          selected=(), in_plan=(), reference: pd.DataFrame | None = None) -> tuple[pdk.Deck | None, str, int]:
    """Returns (deck, legend_html, number of compartments without coordinates).
    reference: the full soil table, so category colours stay the same when filters change."""
    coords = coordinates(view)
    points = pd.concat([view.drop(columns=["lat", "lon"], errors="ignore"), coords], axis=1).dropna(subset=["lat", "lon"]).reset_index(drop=True)
    missing = len(view) - len(points)
    if points.empty:
        return None, "", missing

    field = COLOR_BY[color_label]
    rgb, legend = _colors(points, field, reference)
    points["fill"] = [[*c, 235] for c in rgb]
    points["glow"] = [[*c, 55] for c in rgb]

    # pre-formatted text for the tooltip
    for col, src in [("sector_t", "sector"), ("smu_t", "smu"), ("soil_family_t", "soil_family")]:
        points[col] = points[src].fillna("–").astype(str)
    points["ph_t"] = [_fmt(v, 1) for v in points["ph"]]
    points["n_t"] = [_fmt(v, 2) for v in points["n_pct"]]
    points["p_t"] = [_fmt(v, 1) for v in points["p_avail"]]
    for col in ["k", "ca", "mg"]:
        points[f"{col}_t"] = [_fmt(v, 3) for v in points[col]]
    points["date_t"] = pd.to_datetime(points["sampling_date"], errors="coerce").dt.strftime("%d %b %Y").fillna("–")
    points["status"] = np.where(points["covered"], "Covered by the trial", "Not covered")
    points["status_color"] = np.where(points["covered"], _hex(COVERED), _hex(NOT_COVERED))

    keep = ["lon", "lat", "fill", "glow", "comp_label", "sector_t", "smu_t", "soil_family_t", "ph_t",
            "n_t", "p_t", "k_t", "ca_t", "mg_t", "date_t", "status", "status_color"]
    data = points[keep]

    layers = [
        # soft halo under every point
        pdk.Layer("ScatterplotLayer", data, id="glow", get_position=["lon", "lat"], get_fill_color="glow",
                  get_radius=420, radius_min_pixels=10, radius_max_pixels=30, pickable=False),
        # the compartments
        pdk.Layer("ScatterplotLayer", data, id="compartments", get_position=["lon", "lat"],
                  get_fill_color="fill", get_line_color=[255, 255, 255, 245], stroked=True, filled=True,
                  get_radius=160, radius_min_pixels=5, radius_max_pixels=16, line_width_min_pixels=1.6,
                  pickable=True, auto_highlight=True, highlight_color=[255, 255, 255, 110]),
    ]
    for ids, ring, layer_id in [(in_plan, IN_PLAN, "in-plan"), (selected, SELECTED, "selected")]:
        ring_data = data[data["comp_label"].isin(list(ids))]
        if not ring_data.empty:
            layers.append(pdk.Layer("ScatterplotLayer", ring_data, id=layer_id, get_position=["lon", "lat"],
                                    filled=False, stroked=True, get_line_color=[*ring, 255],
                                    get_radius=300, radius_min_pixels=10, radius_max_pixels=24,
                                    line_width_min_pixels=2.4, pickable=False))

    deck = pdk.Deck(layers=layers, initial_view_state=_view(points), map_provider="carto",
                    map_style=BASEMAPS[basemap], tooltip=TOOLTIP)
    return deck, legend, missing
