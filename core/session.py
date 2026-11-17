"""The plan being worked on, kept in the browser session."""
import hashlib

import pandas as pd
import streamlit as st

import config

PLAN_COLUMNS = ["Comp ID", "Soil", "Clone", "MAI target (T/ha)", "Spacing", "Remove"]
KEY_COLUMNS = ["Comp ID", "Clone", "MAI target (T/ha)", "Spacing"]


def empty_plan():
    return pd.DataFrame({"Comp ID": pd.Series(dtype="object"), "Soil": pd.Series(dtype="object"),
                         "Clone": pd.Series(dtype="object"), "MAI target (T/ha)": pd.Series(dtype="float"),
                         "Spacing": pd.Series(dtype="object"), "Remove": pd.Series(dtype="bool")})


def init():
    st.session_state.setdefault("plan", empty_plan())
    st.session_state.setdefault("results", None)       # {"calculated", "skipped", "inputs_key"}
    st.session_state.setdefault("plan_meta", None)     # {"name", "created_at"} of an opened saved plan
    st.session_state.setdefault("editor_version", 0)


def signature(df):
    """Plain-text version of a table, so two tables can be compared safely."""
    return df.astype(object).where(df.notna(), "").astype(str).values.tolist()


def inputs_key(plan):
    return hashlib.md5(str(signature(plan[KEY_COLUMNS])).encode()).hexdigest()


def reset_editor():
    st.session_state.editor_version += 1


def add_compartments(soil, labels):
    """Add compartments (by Comp ID) to the plan; ones already in it are skipped."""
    init()
    plan = st.session_state.plan
    rows = soil[soil["comp_label"].isin(list(labels)) & ~soil["comp_label"].isin(plan["Comp ID"])]
    new = pd.DataFrame({
        "Comp ID": rows["comp_label"].values,
        "Soil": (rows["smu"].astype(str) + " · " + rows["soil_family"].astype(str)).values,
        "Clone": pd.Series([None] * len(rows), dtype="object"),
        "MAI target (T/ha)": float(config.DEFAULT_MAI_TARGET),
        "Spacing": pd.Series([None] * len(rows), dtype="object"),
        "Remove": False})
    st.session_state.plan = pd.concat([plan, new], ignore_index=True)
    reset_editor()


def open_plan(saved):
    """Load a saved plan (inputs and its results) into the session."""
    plan = saved["inputs"].copy()
    plan["Remove"] = False
    plan["MAI target (T/ha)"] = pd.to_numeric(plan["MAI target (T/ha)"], errors="coerce")
    st.session_state.plan = plan[PLAN_COLUMNS]
    st.session_state.results = {"calculated": saved["calculated"], "skipped": saved["skipped"],
                                "inputs_key": inputs_key(st.session_state.plan)}
    st.session_state.plan_meta = {"name": saved["name"], "created_at": saved["created_at"]}
    reset_editor()
