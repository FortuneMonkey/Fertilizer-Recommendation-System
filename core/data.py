"""Loads (and caches) the rules workbook and the soil database."""
import os
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import streamlit as st

import config
from core import engine


@dataclass
class Context:
    rules: dict
    soil: pd.DataFrame          # soil database + a 'covered' flag per compartment
    soil_updated: str
    clone_ids: list
    spacing_labels: list
    covered_text: str


@st.cache_data(show_spinner="Loading rules ...")
def _load_rules(path, modified):
    return engine.load_rules(path)


@st.cache_data(show_spinner="Loading soil database ...")
def _load_soil(path, sheet, modified):
    cfg = {"SOIL_DB_PATH": path, "SOIL_DB_SHEET": sheet, "SOIL_COLUMNS": engine.CONFIG["SOIL_COLUMNS"]}
    return engine.load_soil_database(cfg)


def get_context():
    """Everything the pages need. Shows a clear message (and stops) if a file is missing."""
    for label, path in [("Rules file", config.RULES_PATH), ("Soil database", config.SOIL_DB_PATH)]:
        if not os.path.exists(path):
            st.error(f"{label} not found: {path}\n\nCheck the path in config.py.")
            st.stop()
    try:
        rules = _load_rules(config.RULES_PATH, os.path.getmtime(config.RULES_PATH))
        soil = _load_soil(config.SOIL_DB_PATH, config.SOIL_DB_SHEET, os.path.getmtime(config.SOIL_DB_PATH))
    except Exception as error:
        st.error(f"Could not read the rules or the soil database:\n\n{error}")
        st.stop()
    if rules["spacing"].empty:
        st.error("The rules workbook has no 'Spacing' sheet (BRI x IRI choices). Use the latest Fertilizer_Rules.xlsx.")
        st.stop()

    soil = soil.copy()
    soil["covered"] = engine.is_covered(soil, rules)
    pairs = sorted(rules["eligible"]) if rules["eligible"] else []
    covered_text = " or ".join(f"SMU {smu} with Soil Family {family}" for smu, family in pairs) or "all soils"
    updated = datetime.fromtimestamp(os.path.getmtime(config.SOIL_DB_PATH)).strftime("%d %b %Y, %H:%M")
    return Context(rules=rules, soil=soil, soil_updated=updated,
                   clone_ids=rules["clones"]["Clone ID"].astype(str).tolist(),
                   spacing_labels=rules["spacing"].index.tolist(), covered_text=covered_text)
