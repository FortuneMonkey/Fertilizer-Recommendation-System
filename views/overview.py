"""Overview: numbers at a glance, where to start, saved plans."""
import streamlit as st

import config
import nav
from core import data, plans, session, ui


def render():
    ctx = data.get_context()
    session.init()
    soil = ctx.soil
    saved = plans.list_plans()
    total, covered = len(soil), int(soil["covered"].sum())

    ui.page_header("Overview", "Soil database, plans and fertilizer doses in one place.")
    ui.kpi_grid([
        ui.kpi("Compartments", f"{total:,}", f"In the soil database · updated {ctx.soil_updated}", tone="plain"),
        ui.kpi("Covered soil", f"{covered:,}", f"{covered / total:.0%} of the database can be calculated", share=covered / total),
        ui.kpi("Other soils", f"{total - covered:,}", "Shown in the database, not calculated", tone="amber"),
        ui.kpi("Saved plans", f"{len(saved)}", f"Latest: {saved.iloc[0]['created_at']}" if len(saved) else "None saved yet", tone="plain"),
    ])

    ui.section("How it works")
    steps = [("1", "Choose compartments", "Filter the soil database and tick the compartments you want to plan.",
              "Open the database", "database"),
             ("2", "Enter the site details", "Pick the clone, MAI target and spacing for each compartment.",
              "Open recommendations", "recommendations"),
             ("3", "Get the doses", "See g/tree for every product, check how it was calculated and download it.",
              "Open recommendations", "recommendations")]
    for column, (number, title, text, label, target) in zip(st.columns(3), steps):
        with column, ui.card(f"step-{number}"):
            ui.card_text(title, text, badge=number)
            if st.button(label, key=f"step_{number}"):
                st.switch_page(nav.PAGES[target])

    ui.section("Soil database")
    with ui.card("database"):
        info, action = st.columns([5, 1.2], vertical_alignment="center")
        with info:
            st.markdown(f'<div class="item-t">{total:,} compartments · updated {ctx.soil_updated}</div>'
                        f'<div class="mono" style="margin:4px 0 8px">{config.SOIL_DB_PATH}</div>'
                        '<div class="item-m">' + ui.chip(f"Covered: {ctx.covered_text}") + "</div>", unsafe_allow_html=True)
        if action.button("Reload data", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    ui.section("Saved plans")
    if saved.empty:
        with ui.card("no-plans"):
            ui.empty_state("No saved plans yet", "Build a plan in Recommendations and save it to find it here.")
    for _, plan in saved.head(10).iterrows():
        with ui.card(f"plan-{plan['id']}"):
            info, open_col, delete_col = st.columns([6, 1, 1], vertical_alignment="center")
            info.markdown(f'<div class="item-t">{plan["name"]}</div><div class="item-m">'
                          + ui.chip(f'{plan["n_compartments"]} compartments', "") + ui.chip(plan["created_at"], "muted")
                          + "</div>", unsafe_allow_html=True)
            if open_col.button("Open", key=f"open_{plan['id']}", type="primary", width="stretch"):
                session.open_plan(plans.load_plan(int(plan["id"])))
                st.switch_page(nav.PAGES["recommendations"])
            with delete_col.popover("Delete", width="stretch"):
                st.write("Delete this saved plan?")
                if st.button("Yes, delete", key=f"delete_{plan['id']}", type="primary"):
                    plans.delete_plan(int(plan["id"]))
                    st.rerun()
