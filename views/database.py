"""Database: browse the soil database and pick compartments for a plan."""
import io

import numpy as np
import pandas as pd
import streamlit as st

import nav
from core import data, session, ui

COVERED, ALL = "Covered soil only", "All soils"


def _excel(table):
    buffer = io.BytesIO()
    table.to_excel(buffer, index=False, sheet_name="Soil database")
    return buffer.getvalue()


def render():
    ctx = data.get_context()
    session.init()
    soil = ctx.soil

    ui.page_header("Database", "The soil database behind the recommendation, one row per compartment.")

    with ui.card("filters"):
        scope = st.segmented_control("Show", [COVERED, ALL], default=COVERED, key="db_scope") or COVERED
        pool = soil[soil["covered"]] if scope == COVERED else soil
        search, sector, smu, family = st.columns([2, 1.5, 1.5, 1.5])
        query = search.text_input("Search Comp ID", placeholder="e.g. BASI081")
        sectors = sector.multiselect("Sector", sorted(pool["sector"].dropna().astype(str).unique()))
        smus = smu.multiselect("SMU", sorted(pool["smu"].dropna().astype(str).unique()))
        families = family.multiselect("Soil Family", sorted(pool["soil_family"].dropna().astype(str).unique()))

    view = pool
    if query.strip():
        view = view[view["comp_label"].str.contains(query.strip(), case=False, regex=False)]
    if sectors:
        view = view[view["sector"].astype(str).isin(sectors)]
    if smus:
        view = view[view["smu"].astype(str).isin(smus)]
    if families:
        view = view[view["soil_family"].astype(str).isin(families)]
    view = view.reset_index(drop=True)

    table = pd.DataFrame({
        "Comp ID": view["comp_label"], "Sector": view["sector"], "SMU": view["smu"],
        "Soil Family": view["soil_family"], "Sampled": pd.to_datetime(view["sampling_date"], errors="coerce"),
        "pH": view["ph"], "N (%)": view["n_pct"], "P avail. (ppm)": view["p_avail"],
        "K (cmol/kg)": view["k"], "Ca (cmol/kg)": view["ca"], "Mg (cmol/kg)": view["mg"]})
    if scope == ALL:
        table.insert(1, "Status", np.where(view["covered"], "Covered", "Not covered"))

    number = st.column_config.NumberColumn
    settings = {"Sampled": st.column_config.DateColumn("Sampled", format="YYYY-MM-DD"),
                "pH": number("pH", format="%.1f"), "N (%)": number("N (%)", format="%.2f"),
                "P avail. (ppm)": number("P avail. (ppm)", format="%.1f"),
                "K (cmol/kg)": number("K (cmol/kg)", format="%.2f"),
                "Ca (cmol/kg)": number("Ca (cmol/kg)", format="%.2f"),
                "Mg (cmol/kg)": number("Mg (cmol/kg)", format="%.2f")}
    options = dict(hide_index=True, width="stretch", height=min(38 * len(table) + 40, 560), column_config=settings)

    selectable = scope == COVERED
    st.markdown("<div style='height:.9rem'></div>", unsafe_allow_html=True)
    bar = st.container()
    if selectable:
        event = st.dataframe(table, on_select="rerun", selection_mode="multi-row", key="db_table", **options)
        picked = list(event.selection.rows)
    else:
        st.dataframe(table, **options)
        picked = []

    with bar:
        summary, add_selected, add_all, download = st.columns([3, 1.7, 1.5, 1.3], vertical_alignment="center")
        summary.markdown(ui.chip(f"{len(table):,} compartments shown", "muted")
                         + (ui.chip(f"{len(picked)} selected", "") if selectable else ui.chip("View only", "warn")),
                         unsafe_allow_html=True)
        if selectable:
            if add_selected.button(f"Add selected to plan ({len(picked)})", type="primary", disabled=not picked, width="stretch"):
                session.add_compartments(soil, table.loc[picked, "Comp ID"])
                st.switch_page(nav.PAGES["recommendations"])
            if add_all.button(f"Add all {len(table):,} shown", disabled=table.empty, width="stretch"):
                session.add_compartments(soil, table["Comp ID"])
                st.switch_page(nav.PAGES["recommendations"])
        download.download_button("Download Excel", _excel(table), file_name="Soil_database.xlsx",
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    if not selectable:
        st.info(f"Compartments in other soils cannot be added to a plan: the trial covers {ctx.covered_text}.")
