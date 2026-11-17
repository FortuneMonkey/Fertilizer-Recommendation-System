"""
Fertilizer Recommendation Calculator
====================================

Reproduces the calculation of Fertilizer_Calculation.xlsx (column I onward)
for every compartment, using:

  * the CLEAN soil database      (output of the data quality check)
  * the SITE INPUT file          (typed by the user: clone, MAI target, BRI, IRI ...)
  * Fertilizer_Rules.xlsx        (every constant, factor, grade, dose rule and the
                                  clone requirement table -- nothing is hardcoded here)

Calculation (per nutrient N, P, K, Ca, Mg)
  1. Soil supply        = soil ppm x soil_mass_factor            (kg/ha)
  2. Site potential     = soil supply + harvest residue - stem loss
  3. Gap                = clone requirement - site potential
  4. Gap + sustainability = gap x sustainability_factor
  5. Nutritional balance  = (4) - SOP regime
  6. After recovery     = balance / (recovery % / 100)
  7. Product kg/ha      = (6) x conversion factor / (grade % / 100)
  8. g/tree             = product kg/ha x 1000 / trees per ha
  9. Recommended g/tree = dose rule (zero dose / minimum / round up): defaults on 'Dose Rules',
                          overridden per clone on 'Dose Rules by Clone'

Only soils covered by the trial are calculated: the SMU + Soil Family pairs listed on the
'Eligible Soils' sheet of Fertilizer_Rules.xlsx (currently SMU B with Soil Family KDT-FL).

Output workbook
  * "Recommendation"  -- compartments that were calculated
  * "Not Calculated"  -- compartments that could not be calculated, with the reason
"""

import math
import os

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION -- edit these paths / column names as needed
# ============================================================

CONFIG = {
    # ---- files ----
    "RULES_PATH":       r"C:\Users\saputra\Projects\fertilization\rules\Fertilizer_Rules.xlsx",
    "SOIL_DB_PATH":     r"C:\Users\saputra\Projects\fertilization\output\correct_data.xlsx",
    "SOIL_DB_SHEET":    0,                      # sheet name, or 0 = first sheet
    "SITE_INPUT_PATH":  r"C:\Users\saputra\Projects\fertilization\input\Site_Input.xlsx",
    "SITE_INPUT_SHEET": 0,
    "OUTPUT_PATH":      r"C:\Users\saputra\Projects\fertilization\output\Fertilizer_Recommendation.xlsx",

    # ---- column names in the SITE INPUT file (left = meaning, right = your header) ----
    "SITE_COLUMNS": {
        "comp_id":    "Comp ID",
        "clone_id":   "Clone ID",
        "mai_target": "MAI Target 5y (T/ha)",
        "bri":        "BRI",
        "iri":        "IRI",
    },

    # ---- column names in the CLEAN SOIL DATABASE ----
    "SOIL_COLUMNS": {
        "comp_id":        "compartment_code",
        "smu":            "SMU",
        "soil_family":    "Soil Family",
        "sampling_date":  "dt_sample_collected",
        "ph":             "ph",
        "organic_matter": "soil_organic_matter",
        "n_pct":          "N (%)",
        "al":             "al",
        "cec":            "ctc",
        "k":              "k_soil",
        "na":             "Na",
        "ca":             "ca_soil",
        "mg":             "mg_soil",
        "p_avail":        "p_available",
        "sector":         "Sector",
    },
}

# These soil values feed the calculation: a compartment without them is NOT calculated.
REQUIRED_SOIL_FIELDS = ["n_pct", "p_avail", "k", "ca", "mg"]
# These site values feed the calculation.
REQUIRED_SITE_FIELDS = ["comp_id", "clone_id", "bri", "iri"]

NUTRIENTS = ["N", "P", "K", "Ca", "Mg"]          # fixed structure of the calculation

# Physical unit conversions (not agronomic rules, so not in Fertilizer_Rules.xlsx)
PERCENT_TO_PPM = 10_000        # 1 % = 10,000 mg/kg
CMOL_TO_PPM_BASE = 10          # cmol(+)/kg x 10 x (atomic weight / valence) = mg/kg
M2_PER_HA = 10_000
G_PER_KG = 1_000

REQUIRED_CONSTANTS = ["soil_mass_factor", "sustainability_factor",
                      "requirement_mai_target", "om_to_corg_divisor"]


# ============================================================
# Helpers
# ============================================================

def normalize_key(series):
    """Compartment codes: ignore case and stray spaces."""
    return series.astype(str).str.strip().str.upper()


def normalize_clone(series):
    """Clone IDs: ignore case and ALL spaces ('CEP 0074' == 'CEP0074')."""
    return series.astype(str).str.replace(r"\s+", "", regex=True).str.upper()


def excel_ceiling(value, significance):
    """Excel CEILING for positive numbers (with a tiny tolerance for float noise)."""
    return math.ceil(round(value / significance, 9)) * significance


def read_sheet(path, sheet, required_columns, label):
    df = pd.read_excel(path, sheet_name=sheet)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"{label}: column(s) {missing} not found. "
                         f"Columns found: {list(df.columns)}")
    return df


# ============================================================
# STEP 1 -- Load and validate the rules workbook
# ============================================================

def load_rules(path):
    print("Loading rules from:", path)

    constants_df = read_sheet(path, "Constants", ["Parameter", "Value"], "Constants sheet")
    constants_df = constants_df.dropna(subset=["Parameter"])
    constants = dict(zip(constants_df["Parameter"].astype(str).str.strip(),
                         pd.to_numeric(constants_df["Value"], errors="coerce")))
    for key in REQUIRED_CONSTANTS:
        if key not in constants or pd.isna(constants[key]):
            raise ValueError(f"Constants sheet: '{key}' is missing or not a number.")

    nut_cols = ["Nutrient", "Atomic Weight", "Valence", "Harvest Residue (kg/ha)",
                "Stem Loss (kg/ha)", "SOP Regime (kg/ha)", "Recovery (%)"]
    nutrients = read_sheet(path, "Nutrients", nut_cols, "Nutrients sheet").dropna(subset=["Nutrient"])
    nutrients["Nutrient"] = nutrients["Nutrient"].astype(str).str.strip()
    nutrients = nutrients.set_index("Nutrient")
    missing = [n for n in NUTRIENTS if n not in nutrients.index]
    if missing:
        raise ValueError(f"Nutrients sheet: nutrient(s) {missing} missing.")
    for n in NUTRIENTS:
        for col in ["Harvest Residue (kg/ha)", "Stem Loss (kg/ha)", "SOP Regime (kg/ha)", "Recovery (%)"]:
            if pd.isna(pd.to_numeric(nutrients.at[n, col], errors="coerce")):
                raise ValueError(f"Nutrients sheet: '{col}' for {n} is missing or not a number.")
        if float(nutrients.at[n, "Recovery (%)"]) <= 0:
            raise ValueError(f"Nutrients sheet: Recovery (%) for {n} must be above 0.")
    for n in ["K", "Ca", "Mg"]:
        for col in ["Atomic Weight", "Valence"]:
            if pd.isna(pd.to_numeric(nutrients.at[n, col], errors="coerce")):
                raise ValueError(f"Nutrients sheet: '{col}' for {n} is required (used for cmol/kg -> ppm).")

    prod_cols = ["Source Product", "Nutrient", "Grade (%)", "Conversion Factor", "Output Product"]
    products = read_sheet(path, "Products", prod_cols, "Products sheet").dropna(subset=["Source Product"])
    products["Nutrient"] = products["Nutrient"].astype(str).str.strip()
    products["Output Product"] = products["Output Product"].astype(str).str.strip()
    bad = products[~products["Nutrient"].isin(NUTRIENTS)]
    if not bad.empty:
        raise ValueError(f"Products sheet: unknown nutrient for {bad['Source Product'].tolist()}")
    for col in ["Grade (%)", "Conversion Factor"]:
        products[col] = pd.to_numeric(products[col], errors="coerce")
        if (products[col].isna() | (products[col] <= 0)).any():
            raise ValueError(f"Products sheet: '{col}' must be a number above 0 for every product.")

    dose_cols = ["Output Product", "Zero Dose (g/tree)", "Min Dose (g/tree)", "Round Up To (g/tree)"]
    dose = read_sheet(path, "Dose Rules", dose_cols, "Dose Rules sheet").dropna(subset=["Output Product"])
    dose["Output Product"] = dose["Output Product"].astype(str).str.strip()
    for col in dose_cols[1:]:
        dose[col] = pd.to_numeric(dose[col], errors="coerce")
    dose = dose.set_index("Output Product")
    no_rule = sorted(set(products["Output Product"]) - set(dose.index))
    if no_rule:
        raise ValueError(f"Dose Rules sheet: no rule for output product(s) {no_rule}")

    # clone-specific dose rules (optional sheet): override the defaults for that clone + product
    dose_fields = ["Zero Dose (g/tree)", "Min Dose (g/tree)", "Round Up To (g/tree)"]
    if "Dose Rules by Clone" in pd.ExcelFile(path).sheet_names:
        by_clone = read_sheet(path, "Dose Rules by Clone", ["Clone ID", "Output Product"] + dose_fields,
                              "Dose Rules by Clone sheet").dropna(subset=["Clone ID", "Output Product"])
    else:
        print("  NOTE: no 'Dose Rules by Clone' sheet -> default dose rules used for every clone")
        by_clone = pd.DataFrame(columns=["Clone ID", "Output Product"] + dose_fields)
    by_clone["_key"] = normalize_clone(by_clone["Clone ID"])
    by_clone["Output Product"] = by_clone["Output Product"].astype(str).str.strip()
    for col in dose_fields:
        by_clone[col] = pd.to_numeric(by_clone[col], errors="coerce").astype(float)
    unknown_prod = sorted(set(by_clone["Output Product"]) - set(dose.index))
    if unknown_prod:
        raise ValueError(f"Dose Rules by Clone sheet: unknown output product(s) {unknown_prod}")
    if by_clone.duplicated(["_key", "Output Product"]).any():
        raise ValueError("Dose Rules by Clone sheet: a clone + product is listed more than once.")

    # soils covered by the trial (optional sheet): SMU + Soil Family pairs
    if "Eligible Soils" in pd.ExcelFile(path).sheet_names:
        el = read_sheet(path, "Eligible Soils", ["SMU", "Soil Family"], "Eligible Soils sheet").dropna(how="all")
        el = el.dropna(subset=["SMU", "Soil Family"])
        if el.empty:
            raise ValueError("Eligible Soils sheet has no rows. Add the covered SMU + Soil Family pairs, "
                             "or delete the sheet to calculate every soil.")
        eligible = set(zip(normalize_key(el["SMU"]), normalize_key(el["Soil Family"])))
    else:
        print("  NOTE: no 'Eligible Soils' sheet -> every SMU / Soil Family is calculated")
        eligible = None

    clone_cols = ["Clone ID"] + [f"{n} (kg/ha)" for n in NUTRIENTS]
    clones = read_sheet(path, "Clone Requirement", clone_cols, "Clone Requirement sheet").dropna(subset=["Clone ID"])
    clones["_key"] = normalize_clone(clones["Clone ID"])
    for col in clone_cols[1:]:
        clones[col] = pd.to_numeric(clones[col], errors="coerce")
    if clones["_key"].duplicated().any():
        dup = clones.loc[clones["_key"].duplicated(keep=False), "Clone ID"].tolist()
        raise ValueError(f"Clone Requirement sheet: clone(s) listed more than once: {dup}")
    incomplete = clones[clones[clone_cols[1:]].isna().any(axis=1)]["Clone ID"].tolist()
    if incomplete:
        raise ValueError(f"Clone Requirement sheet: missing/non-numeric requirement for {incomplete}")
    clones = clones.set_index("_key")

    # spacing presets (optional sheet): label -> BRI / IRI in metres (used by the dashboard)
    if "Spacing" in pd.ExcelFile(path).sheet_names:
        spacing = read_sheet(path, "Spacing", ["Spacing", "BRI (m)", "IRI (m)"], "Spacing sheet").dropna(subset=["Spacing"])
        spacing["Spacing"] = spacing["Spacing"].astype(str).str.strip()
        for col in ["BRI (m)", "IRI (m)"]:
            spacing[col] = pd.to_numeric(spacing[col], errors="coerce")
        if (spacing[["BRI (m)", "IRI (m)"]].isna().any(axis=1) | (spacing[["BRI (m)", "IRI (m)"]] <= 0).any(axis=1)).any():
            raise ValueError("Spacing sheet: BRI and IRI must be numbers above 0.")
        spacing = spacing.set_index("Spacing")
    else:
        spacing = pd.DataFrame(columns=["BRI (m)", "IRI (m)"])

    print(f"  -> {len(products)} products, {len(clones)} clones loaded")
    return {"spacing": spacing, "constants": constants, "nutrients": nutrients, "products": products,
            "dose": dose, "dose_by_clone": by_clone, "clones": clones, "eligible": eligible}


# ============================================================
# STEP 2 -- Load site input + soil database and join them
# ============================================================

def load_site_input(cfg):
    cols = cfg["SITE_COLUMNS"]
    needed = [cols[f] for f in REQUIRED_SITE_FIELDS]
    df = read_sheet(cfg["SITE_INPUT_PATH"], cfg["SITE_INPUT_SHEET"], needed, "Site input")
    df = df.dropna(subset=[cols["comp_id"]]).copy()
    for f in ["mai_target", "bri", "iri"]:
        if cols[f] in df.columns:
            df[cols[f]] = pd.to_numeric(df[cols[f]], errors="coerce")
    df["_key"] = normalize_key(df[cols["comp_id"]])
    print(f"  -> {len(df)} compartments in site input")
    return df


def load_soil_database(cfg):
    cols = cfg["SOIL_COLUMNS"]
    needed = [cols[f] for f in ["comp_id"] + REQUIRED_SOIL_FIELDS]
    df = read_sheet(cfg["SOIL_DB_PATH"], cfg["SOIL_DB_SHEET"], needed, "Soil database")
    df = df.dropna(subset=[cols["comp_id"]]).copy()

    # optional (display-only) columns: warn and leave empty if they are absent
    optional_missing = [cols[f] for f in cols if cols[f] not in df.columns]
    if optional_missing:
        print(f"  WARNING: soil database has no column(s) {optional_missing} -> shown empty")

    soil = pd.DataFrame({"_key": normalize_key(df[cols["comp_id"]])})
    for field, col in cols.items():
        if field == "comp_id":
            continue
        soil[field] = df[col].values if col in df.columns else np.nan
    for field in ["ph", "organic_matter", "n_pct", "al", "cec", "k", "na", "ca", "mg", "p_avail"]:
        soil[field] = pd.to_numeric(soil[field], errors="coerce")

    soil["comp_label"] = df[cols["comp_id"]].astype(str).str.strip().values   # code as written in the database

    if soil["_key"].duplicated().any():
        n = soil["_key"].duplicated().sum()
        print(f"  WARNING: {n} duplicate compartment code(s) in the soil database -> first row kept")
        soil = soil.drop_duplicates("_key")
    print(f"  -> {len(soil)} compartments in soil database")
    return soil


def is_covered(soil, rules):
    """True for compartments whose SMU + Soil Family pair is covered by the trial."""
    if rules["eligible"] is None:
        return pd.Series(True, index=soil.index)
    pairs = zip(normalize_key(soil["smu"]), normalize_key(soil["soil_family"]))
    listed = pd.Series([p in rules["eligible"] for p in pairs], index=soil.index)
    return listed & soil["smu"].notna() & soil["soil_family"].notna()


# ============================================================
# STEP 3 -- Decide which compartments can be calculated
# ============================================================

def find_problems(df, rules, site_cols):
    """Returns a Series with the reason a row cannot be calculated ('' = OK)."""
    # Plain Python lists/strings on purpose: mixing pandas 'object' and 'str' text
    # columns breaks on newer pandas versions.
    found = {i: [] for i in df.index}

    def add(mask, text):
        texts = text if isinstance(text, pd.Series) else pd.Series(text, index=df.index)
        for i in df.index[mask.to_numpy(dtype=bool)]:
            found[i].append(str(texts[i]))

    add(~df["_in_soil"], "compartment not found in soil database")

    for field in REQUIRED_SOIL_FIELDS:
        add(df["_in_soil"] & df[field].isna(), f"missing soil value: {field}")

    # soil covered by the trial? (SMU + Soil Family must be a listed pair)
    if rules["eligible"] is not None:
        soil_missing = df["_in_soil"] & (df["smu"].isna() | df["soil_family"].isna())
        add(soil_missing, "SMU / Soil Family missing")
        pairs = list(zip(normalize_key(df["smu"]), normalize_key(df["soil_family"])))
        covered = pd.Series([p in rules["eligible"] for p in pairs], index=df.index)
        add(df["_in_soil"] & ~soil_missing & ~covered,
            "soil not covered by the trial (SMU " + df["smu"].astype(str) + " / " + df["soil_family"].astype(str) + ")")

    clone_keys = normalize_clone(df[site_cols["clone_id"]])
    unknown = ~clone_keys.isin(rules["clones"].index)
    add(unknown, "clone not in 'Clone Requirement' sheet")

    for f in ["bri", "iri"]:
        col = site_cols[f]
        add(df[col].isna() | (df[col] <= 0), f"invalid {col}")
    return pd.Series({i: "; ".join(parts) for i, parts in found.items()}, index=df.index, dtype=object)


# ============================================================
# STEP 4 -- The calculation
# ============================================================

def apply_dose_rule(values, zero_dose, min_dose, round_to):
    """values and the three rule arguments are Series with the same index (rules can differ per row)."""
    out = []
    for v, zero, minimum, step in zip(values, zero_dose, min_dose, round_to):
        if v <= 0:
            out.append(v if pd.isna(zero) else zero)
        elif pd.notna(minimum) and v < minimum:
            out.append(minimum)
        elif pd.notna(step) and step > 0:
            out.append(excel_ceiling(v, step))
        else:
            out.append(v)
    return pd.Series(out, index=values.index, dtype=float)


def calculate(df, rules, site_cols):
    c, nut, prod, dose, clones = (rules["constants"], rules["nutrients"], rules["products"],
                                  rules["dose"], rules["clones"])
    out = pd.DataFrame(index=df.index)

    trees_ha = M2_PER_HA / (df[site_cols["bri"]] * df[site_cols["iri"]])
    out["Tree/ha"] = trees_ha

    # ---- soil display columns (Excel P:AG) ----
    ppm = {
        "N": df["n_pct"] * PERCENT_TO_PPM,
        "P": df["p_avail"],
    }
    cmol = {"K": df["k"], "Ca": df["ca"], "Mg": df["mg"]}
    for n, series in cmol.items():
        aw, val = float(nut.at[n, "Atomic Weight"]), float(nut.at[n, "Valence"])
        ppm[n] = series * CMOL_TO_PPM_BASE * (aw / val)

    corg = df["organic_matter"] / c["om_to_corg_divisor"]
    cec = df["cec"].where(df["cec"] > 0)
    soil_cols = {
        "SMU": df["smu"], "Soil Family": df["soil_family"],
        "Soil Sampling Date": df["sampling_date"], "pH-H2O": df["ph"],
        "C-Org (%)": corg, "N (%)": df["n_pct"], "C/N Ratio": corg / df["n_pct"],
        "Al3+ (cmol/kg)": df["al"], "CEC Soil (cmol/kg)": df["cec"],
        "exch-K (cmol/kg)": df["k"], "exch-Na (cmol/kg)": df["na"],
        "exch-Ca (cmol/kg)": df["ca"], "exch-Mg (cmol/kg)": df["mg"],
        "Avail-P (ppm)": df["p_avail"],
        "BS (%)": (df["k"] + df["na"] + df["ca"] + df["mg"]) * 100 / cec,
        "exch-K (ppm)": ppm["K"], "exch-Ca (ppm)": ppm["Ca"], "exch-Mg (ppm)": ppm["Mg"],
    }
    for name, series in soil_cols.items():
        out[name] = series

    # ---- nutrient balance (kg/ha), one block per step ----
    clone_keys = normalize_clone(df[site_cols["clone_id"]])
    blocks = {}
    for n in NUTRIENTS:
        supply = ppm[n] * c["soil_mass_factor"]
        residue = float(nut.at[n, "Harvest Residue (kg/ha)"])
        stem = float(nut.at[n, "Stem Loss (kg/ha)"])
        sop = float(nut.at[n, "SOP Regime (kg/ha)"])
        recovery = float(nut.at[n, "Recovery (%)"]) / 100
        requirement = clone_keys.map(clones[f"{n} (kg/ha)"]).astype(float)

        potential = supply + residue - stem
        gap = requirement - potential
        gap_sust = gap * c["sustainability_factor"]
        balance = gap_sust - sop
        after_recovery = balance / recovery
        blocks[n] = {
            "Soil Supply": supply, "Harvest Residue Left": pd.Series(residue, index=df.index),
            "Stem Extraction Loss": pd.Series(stem, index=df.index),
            "Site Potential Capacity": potential, "Requirement by Target MAI": requirement,
            "Gap (Requirement - Potential)": gap, "Gap + Sustainability": gap_sust,
            "SOP Regime": pd.Series(sop, index=df.index), "Nutritional Balance": balance,
            "After Plant Recovery": after_recovery,
        }
    group_order = list(blocks["N"].keys())
    for group in group_order:
        for n in NUTRIENTS:
            out[f"{group} - {n} (kg/ha)"] = blocks[n][group]

    # ---- fertilizer amounts per source product (kg/ha) ----
    amount = {}
    for _, p in prod.iterrows():
        amount[p["Source Product"]] = (blocks[p["Nutrient"]]["After Plant Recovery"]
                                       * p["Conversion Factor"] / (p["Grade (%)"] / 100))
        out[f"Fertilizer Amount - {p['Source Product']} (kg/ha)"] = amount[p["Source Product"]]

    # ---- g/tree per output product, then dose rule ----
    output_products = list(dict.fromkeys(prod["Output Product"]))      # keep sheet order
    calculated, recommended = {}, {}
    for op in output_products:
        sources = prod.loc[prod["Output Product"] == op, "Source Product"].tolist()
        kg_ha = pd.concat([amount[s] for s in sources], axis=1).max(axis=1)
        calculated[op] = kg_ha * G_PER_KG / trees_ha
        # default rule for the product, overridden per row where the clone has its own rule
        overrides = rules["dose_by_clone"]
        overrides = overrides[overrides["Output Product"] == op].set_index("_key")
        row_rules = []
        for field in ["Zero Dose (g/tree)", "Min Dose (g/tree)", "Round Up To (g/tree)"]:
            default = pd.Series(float(dose.at[op, field]), index=df.index)
            clone_value = clone_keys.map(overrides[field]).astype(float)
            row_rules.append(clone_value.fillna(default))
        recommended[op] = apply_dose_rule(calculated[op], *row_rules)
    for op in output_products:
        out[f"Calculated {op} (g/tree)"] = calculated[op]
    for op in output_products:
        out[f"Recommended {op} (g/tree)"] = recommended[op]

    # ---- notes ----
    notes = pd.Series("", index=df.index, dtype=object)
    mai = df[site_cols["mai_target"]] if site_cols["mai_target"] in df.columns else pd.Series(np.nan, index=df.index)
    differs = mai.notna() & (mai != c["requirement_mai_target"])
    notes[differs] = [f"MAI target {value:g} differs from the requirement table (MAI {c['requirement_mai_target']:g}); "
                      "the doses are not adjusted" for value in mai[differs]]
    out["Notes"] = notes
    return out


# ============================================================
# STEP 5 -- Write the output workbook
# ============================================================

def write_workbook(target, calculated_df, not_calculated_df):
    """target: a file path or a binary buffer."""
    with pd.ExcelWriter(target, engine="openpyxl", datetime_format="yyyy-mm-dd") as writer:
        calculated_df.to_excel(writer, sheet_name="Recommendation", index=False)
        not_calculated_df.to_excel(writer, sheet_name="Not Calculated", index=False)

        from openpyxl.styles import Alignment, Font, PatternFill
        head_font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
        head_fill = PatternFill("solid", start_color="305496")
        for ws in writer.book.worksheets:
            for cell in ws[1]:
                cell.font, cell.fill = head_font, head_fill
                cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            ws.row_dimensions[1].height = 45
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = 16
            ws.freeze_panes = "A2"

        ws = writer.book["Recommendation"]
        for cell in ws[1]:
            name = str(cell.value)
            fmt = None
            if name.startswith("Recommended "):
                fmt = "#,##0"
            elif "(kg/ha)" in name or name.startswith("Calculated ") or name in ("Tree/ha", "BS (%)"):
                fmt = "#,##0.00"
            if fmt:
                for row in ws.iter_rows(min_row=2, min_col=cell.column, max_col=cell.column):
                    row[0].number_format = fmt


def write_output(path, calculated_df, not_calculated_df):
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    write_workbook(path, calculated_df, not_calculated_df)
    print("Saved output to:", path)


def to_excel_bytes(calculated_df, not_calculated_df):
    import io
    buffer = io.BytesIO()
    write_workbook(buffer, calculated_df, not_calculated_df)
    return buffer.getvalue()


def build_recommendation(site, soil, rules, site_cols):
    """site: one row per compartment (columns named as in site_cols; extra columns are
    carried to the output). Returns (calculated_df, not_calculated_df)."""
    site = site.copy()
    for f in ["mai_target", "bri", "iri"]:
        if site_cols[f] in site.columns:
            site[site_cols[f]] = pd.to_numeric(site[site_cols[f]], errors="coerce")
    site["_key"] = normalize_key(site[site_cols["comp_id"]])

    merged = site.merge(soil, on="_key", how="left", indicator=True)
    merged["_in_soil"] = merged["_merge"] == "both"

    reasons = find_problems(merged, rules, site_cols)
    ok = reasons == ""

    # passthrough = site columns that are not one of the mapped site fields
    mapped = set(site_cols.values())
    passthrough = [c for c in site.columns if c not in mapped and c != "_key"]
    site_out_cols = [site_cols[f] for f in site_cols if site_cols[f] in site.columns]

    calc = calculate(merged[ok], rules, site_cols)
    calculated_df = pd.concat([merged.loc[ok, passthrough + site_out_cols], calc], axis=1)
    not_calculated_df = merged.loc[~ok, passthrough + site_out_cols].copy()
    not_calculated_df["Reason"] = reasons[~ok]
    return calculated_df, not_calculated_df


# ============================================================
# MAIN
# ============================================================

def main():
    cfg = CONFIG
    site_cols = cfg["SITE_COLUMNS"]

    rules = load_rules(cfg["RULES_PATH"])

    print("Loading site input from:", cfg["SITE_INPUT_PATH"])
    site = load_site_input(cfg)
    print("Loading soil database from:", cfg["SOIL_DB_PATH"])
    soil = load_soil_database(cfg)

    calculated_df, not_calculated_df = build_recommendation(site, soil, rules, site_cols)
    calc = calculated_df

    print()
    print(f"Calculated:     {len(calculated_df)} compartment(s)")
    print(f"Not calculated: {len(not_calculated_df)} compartment(s)")
    if len(not_calculated_df):
        print(not_calculated_df["Reason"].value_counts().to_string())
    noted = (calc["Notes"] != "").sum()
    if noted:
        print(f"Note: {noted} compartment(s) have a MAI target different from the requirement table.")

    write_output(cfg["OUTPUT_PATH"], calculated_df, not_calculated_df)


if __name__ == "__main__":
    main()
