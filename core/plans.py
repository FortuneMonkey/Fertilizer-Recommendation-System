"""Saved plans, kept in a small SQLite file (inputs + the results as they were calculated)."""
import io
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pandas as pd

import config


def _connect():
    path = Path(config.PLANS_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at TEXT NOT NULL,
        n_compartments INTEGER NOT NULL, inputs_json TEXT NOT NULL,
        results_json TEXT NOT NULL, skipped_json TEXT NOT NULL)""")
    return con


def _dump(df):
    return df.to_json(orient="split", date_format="iso")


def _load(text):
    return pd.read_json(io.StringIO(text), orient="split")


def save_plan(name, inputs, calculated, skipped):
    created = datetime.now().strftime("%Y-%m-%d %H:%M")
    with closing(_connect()) as con, con:
        cursor = con.execute(
            "INSERT INTO plans (name, created_at, n_compartments, inputs_json, results_json, skipped_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, created, len(inputs), _dump(inputs), _dump(calculated), _dump(skipped)))
        return cursor.lastrowid, created


def list_plans():
    with closing(_connect()) as con:
        return pd.read_sql_query(
            "SELECT id, name, created_at, n_compartments FROM plans ORDER BY id DESC", con)


def load_plan(plan_id):
    with closing(_connect()) as con:
        row = con.execute("SELECT name, created_at, inputs_json, results_json, skipped_json "
                          "FROM plans WHERE id = ?", (plan_id,)).fetchone()
    name, created, inputs, results, skipped = row
    return {"name": name, "created_at": created, "inputs": _load(inputs),
            "calculated": _load(results), "skipped": _load(skipped)}


def delete_plan(plan_id):
    with closing(_connect()) as con, con:
        con.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
