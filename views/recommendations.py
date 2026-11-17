"""Recommendations: site details for the plan, the calculation and the doses."""
from datetime import date

import pandas as pd
import streamlit as st

import config
import nav
from core import data, engine, plans, session, ui

SITE = engine.CONFIG["SITE_COLUMNS"]
EXCEL_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# (label shown, column group in the engine output) for the step-by-step view
BALANCE_STEPS = [
    ("Soil supply", "Soil Supply"), ("+ Harvest residue left", "Harvest Residue Left"),
    ("− Stem loss", "Stem Extraction Loss"), ("= Site potential", "Site Potential Capacity"),
    ("Clone requirement", "Requirement by Target MAI"), ("Gap (requirement − potential)", "Gap (Requirement - Potential)"),
    ("Gap + sustainability margin", "Gap + Sustainability"), ("− Standard regime (SOP)", "SOP Regime"),
    ("= Nutritional balance", "Nutritional Balance"), ("After plant recovery", "After Plant Recovery")]


def _empty_state():
    with ui.card("empty-plan"):
        ui.empty_state("No compartments in your plan yet",
                       "Choose compartments in the Database, or open a saved plan from the Overview.")
        _, centre, _ = st.columns([2, 1.2, 2])
        if centre.button("Open the database", type="primary", width="stretch"):
            st.switch_page(nav.PAGES["database"])


def _apply_to_all(ctx):
    with ui.card("apply-all"):
        st.markdown('<div class="item-t" style="margin-bottom:.4rem">Fill in every compartment at once</div>', unsafe_allow_html=True)
        clone, mai, spacing, apply = st.columns([2, 1.2, 1.6, 1.2], vertical_alignment="bottom")
        clone_all = clone.selectbox("Clone", ctx.clone_ids, index=None, placeholder="Choose clone", key="all_clone")
        mai_all = mai.number_input("MAI target (T/ha)", min_value=1.0, max_value=200.0,
                                   value=float(config.DEFAULT_MAI_TARGET), step=1.0, key="all_mai")
        spacing_all = spacing.selectbox("Spacing (BRI × IRI)", ctx.spacing_labels, index=None,
                                        placeholder="Choose spacing", key="all_spacing")
        if apply.button("Apply to all", width="stretch"):
            plan = st.session_state.plan.copy()
            if clone_all:
                plan["Clone"] = clone_all
            if spacing_all:
                plan["Spacing"] = spacing_all
            plan["MAI target (T/ha)"] = float(mai_all)
            st.session_state.plan = plan
            session.reset_editor()
            st.rerun()


def _plan_editor(ctx):
    plan = st.session_state.plan
    column = st.column_config
    edited = st.data_editor(
        plan, key=f"plan_editor_{st.session_state.editor_version}", hide_index=True, width="stretch",
        num_rows="fixed", disabled=["Comp ID", "Soil"],
        column_order=["Comp ID", "Soil", "Clone", "MAI target (T/ha)", "Spacing", "Remove"],
        column_config={
            "Clone": column.SelectboxColumn("Clone", options=ctx.clone_ids, required=False, width="medium"),
            "MAI target (T/ha)": column.NumberColumn("MAI target (T/ha)", min_value=1, max_value=200, step=1, format="%g"),
            "Spacing": column.SelectboxColumn("Spacing (BRI × IRI)", options=ctx.spacing_labels, required=False, width="medium"),
            "Remove": column.CheckboxColumn("Remove", width="small")})
    # keep every edit in the session, so nothing is lost when the user visits another page
    if session.signature(edited.reset_index(drop=True)) != session.signature(plan.reset_index(drop=True)):
        st.session_state.plan = edited.reset_index(drop=True)
        session.reset_editor()
        st.rerun()
    return edited


def _calculate(ctx, edited):
    missing = edited["Clone"].isna() | edited["Spacing"].isna()
    if missing.any():
        st.error(f"Choose a clone and a spacing for every compartment ({int(missing.sum())} still missing).")
        return
    spacing = ctx.rules["spacing"]
    site = pd.DataFrame({
        "Spacing": edited["Spacing"].values, SITE["comp_id"]: edited["Comp ID"].values,
        SITE["clone_id"]: edited["Clone"].values, SITE["mai_target"]: edited["MAI target (T/ha)"].values,
        SITE["bri"]: edited["Spacing"].map(spacing["BRI (m)"]).values,
        SITE["iri"]: edited["Spacing"].map(spacing["IRI (m)"]).values})
    calculated, skipped = engine.build_recommendation(site, ctx.soil, ctx.rules, SITE)
    st.session_state.results = {"calculated": calculated, "skipped": skipped,
                                "inputs_key": session.inputs_key(st.session_state.plan)}
    st.session_state.plan_meta = None
    st.rerun()


def _detail(ctx, calculated):
    ui.section("How a result was calculated")
    picker, _ = st.columns([1, 3])
    chosen = picker.selectbox("Compartment", calculated[SITE["comp_id"]].tolist(), key="detail_comp")
    row = calculated[calculated[SITE["comp_id"]] == chosen].iloc[0]
    st.markdown(ui.chip(f"Clone {row[SITE['clone_id']]}") + ui.chip(f"Spacing {row['Spacing']}", "muted")
                + ui.chip(f"{row['Tree/ha']:,.0f} trees per hectare", "muted"), unsafe_allow_html=True)
    names = list(dict.fromkeys(ctx.rules["products"]["Output Product"]))
    ui.tiles([(p, row[f"Recommended {p} (g/tree)"]) for p in names])
    balance_tab, product_tab = st.tabs(["Nutrient balance (kg/ha)", "Fertilizer products"])
    with balance_tab:
        balance = pd.DataFrame({n: [row[f"{group} - {n} (kg/ha)"] for _, group in BALANCE_STEPS]
                                for n in engine.NUTRIENTS}, index=[label for label, _ in BALANCE_STEPS])
        st.dataframe(balance, width="stretch", column_config={
            n: st.column_config.NumberColumn(n, format="%.1f") for n in engine.NUTRIENTS})
    with product_tab:
        sources, doses = st.columns(2)
        products = ctx.rules["products"]
        sources.dataframe(pd.DataFrame({
            "Product": products["Source Product"].values, "Nutrient": products["Nutrient"].values,
            "Needed (kg/ha)": [row[f"Fertilizer Amount - {p} (kg/ha)"] for p in products["Source Product"]]}),
            hide_index=True, width="stretch",
            column_config={"Needed (kg/ha)": st.column_config.NumberColumn(format="%.1f")})
        names = list(dict.fromkeys(products["Output Product"]))
        doses.dataframe(pd.DataFrame({
            "Product": names, "Calculated (g/tree)": [row[f"Calculated {p} (g/tree)"] for p in names],
            "Recommended (g/tree)": [row[f"Recommended {p} (g/tree)"] for p in names]}),
            hide_index=True, width="stretch", column_config={
                "Calculated (g/tree)": st.column_config.NumberColumn(format="%.1f"),
                "Recommended (g/tree)": st.column_config.NumberColumn(format="%d")})
        st.caption("Dolomite uses the higher of the CaO and MgO amounts. Recommended = after the minimum dose and rounding rules.")


def _results(ctx, plan):
    ui.section("Doses", number=2, note="grams per tree")
    results = st.session_state.results
    if results is None:
        with ui.card("no-doses"):
            ui.empty_state("No doses yet", "Fill in the site details above and press Calculate.")
        return
    if results["inputs_key"] != session.inputs_key(plan):
        st.warning("The site details changed after the last calculation. Press Calculate to update the doses.")
    calculated, skipped = results["calculated"], results["skipped"]

    st.markdown(ui.chip(f"{len(calculated)} calculated") + (ui.chip(f"{len(skipped)} not calculated", "warn") if len(skipped) else ""),
                unsafe_allow_html=True)

    if not calculated.empty:
        products = list(dict.fromkeys(ctx.rules["products"]["Output Product"]))
        dose_columns = {f"Recommended {p} (g/tree)": f"{p} (g/tree)" for p in products}
        table = calculated[[SITE["comp_id"], SITE["clone_id"], "Spacing", "Tree/ha", *dose_columns]].rename(columns=dose_columns)
        st.dataframe(table, hide_index=True, width="stretch", column_config={
            "Tree/ha": st.column_config.NumberColumn("Trees/ha", format="%d"),
            **{name: st.column_config.NumberColumn(name, format="%d") for name in dose_columns.values()}})
        for _, row in calculated[calculated["Notes"].fillna("") != ""].iterrows():
            st.markdown(ui.chip(row[SITE["comp_id"]], "warn") + row["Notes"], unsafe_allow_html=True)

    if not skipped.empty:
        with st.expander(f"{len(skipped)} compartment(s) not calculated", expanded=True):
            st.dataframe(skipped[[SITE["comp_id"], "Reason"]], hide_index=True, width="stretch")
    if not calculated.empty:
        _detail(ctx, calculated)

    ui.section("Save or download")
    name_col, save_col, _, download_col = st.columns([3, 1.2, 1, 1.6], vertical_alignment="bottom")
    name = name_col.text_input("Plan name", placeholder="e.g. RKT 2028 · Sector BAS", key="plan_name")
    if save_col.button("Save plan", disabled=not name.strip() or results["inputs_key"] != session.inputs_key(plan)):
        _, created = plans.save_plan(name.strip(), plan.drop(columns=["Remove"]).reset_index(drop=True),
                                     calculated, skipped)
        st.success(f"Saved “{name.strip()}” ({created}). Find it on the Overview.")
    download_col.download_button("Download Excel", engine.to_excel_bytes(calculated, skipped),
                                 file_name=f"Fertilizer_Recommendation_{date.today():%Y-%m-%d}.xlsx", mime=EXCEL_TYPE)


def render():
    ctx = data.get_context()
    session.init()
    ui.page_header("Recommendations", "Choose the clone and spacing for each compartment, then calculate the doses.")

    if st.session_state.plan.empty:
        _empty_state()
        return
    meta = st.session_state.plan_meta
    if meta:
        st.info(f"Opened the saved plan “{meta['name']}” (saved {meta['created_at']}). "
                "The doses shown are as saved; press Calculate to use the current rules.")

    ui.section("Site details", number=1, note=f"{len(st.session_state.plan)} compartments in the plan")
    _apply_to_all(ctx)
    edited = _plan_editor(ctx)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    calculate, remove, _ = st.columns([1.3, 1.6, 5])
    do_calculate = calculate.button("Calculate", type="primary", width="stretch")
    if remove.button("Remove ticked", disabled=not edited["Remove"].any(), width="stretch"):
        kept = edited[~edited["Remove"]].reset_index(drop=True)
        st.session_state.plan = kept
        if kept.empty:
            st.session_state.results = None
        session.reset_editor()
        st.rerun()
    if do_calculate:
        _calculate(ctx, edited)

    _results(ctx, st.session_state.plan)
