# queue_capacity_map.py
import ast, io, re, requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import Optional, List, Set

# ======= caching loaders =======
@st.cache_data(show_spinner=False)
def load_projects(path: str) -> pd.DataFrame:
    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    raise ValueError("Use .parquet, .csv, or .xlsx")

@st.cache_data(show_spinner=False)
def load_county_crosswalk() -> pd.DataFrame:
    """Return columns: fips, state_clean, county_clean, name, state"""
    UA = {"User-Agent": "interconnection-fyi/1.0"}
    # 1) try GitHub (handle messy encodings)
    gh_url = "https://raw.githubusercontent.com/kjhealy/fips-codes/master/county_fips_master.csv"
    try:
        r = requests.get(gh_url, headers=UA, timeout=30)
        r.raise_for_status()
        content = r.content
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(io.BytesIO(content), dtype={"fips": str}, encoding=enc)
                df["county_clean"] = (
                    df["name"].str.lower()
                    .str.replace(" county", "", regex=False)
                    .str.replace(" parish", "", regex=False)
                    .str.replace(" borough", "", regex=False)
                    .str.replace(" census area", "", regex=False)
                    .str.replace(" city and borough", "", regex=False)
                    .str.replace(" municipality", "", regex=False)
                    .str.strip()
                )
                df["state_clean"] = df["state_abbr"].str.upper()
                out = df[["fips", "state_clean", "county_clean", "name", "state"]].drop_duplicates()
                out["fips"] = out["fips"].str.zfill(5)
                return out
            except UnicodeDecodeError:
                continue
    except Exception:
        pass
    # 2) fallback: Census
    census_url = "https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt"
    r = requests.get(census_url, headers=UA, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(
        io.BytesIO(r.content),
        header=None,
        names=["state_abbr", "state_fips", "county_fips", "name", "classfp"],
        dtype=str,
        sep=",",
        encoding="latin-1",
        engine="python",
    )
    df["fips"] = df["state_fips"].str.zfill(2) + df["county_fips"].str.zfill(3)
    STATE_NAMES = {
        "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut",
        "DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
        "IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts",
        "MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
        "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
        "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota",
        "TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
        "WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico","AS":"American Samoa","GU":"Guam","VI":"Virgin Islands","MP":"Northern Mariana Islands"
    }
    df["state_clean"] = df["state_abbr"].str.upper()
    df["state"] = df["state_abbr"].map(STATE_NAMES).fillna(df["state_abbr"])
    df["county_clean"] = (
        df["name"].str.lower()
        .str.replace(" county", "", regex=False)
        .str.replace(" parish", "", regex=False)
        .str.replace(" borough", "", regex=False)
        .str.replace(" census area", "", regex=False)
        .str.replace(" city and borough", "", regex=False)
        .str.replace(" municipality", "", regex=False)
        .str.strip()
    )
    out = df[["fips", "state_clean", "county_clean", "name", "state"]].drop_duplicates()
    out["fips"] = out["fips"].str.zfill(5)
    return out

@st.cache_data(show_spinner=False)
def load_counties_geojson():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    return requests.get(url, timeout=30).json()

# ======= transforms =======
def _parse_gen_types(val):
    if pd.isna(val):
        return []
    if isinstance(val, list):
        return val
    s = str(val).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = ast.literal_eval(s)
            return [str(x) for x in parsed]
        except Exception:
            pass
    return [x.strip() for x in re.split(r"[;,/]| and ", s) if x.strip()]

def _capacity_from_row(row, method="midpoint"):
    for key in ["Capacity (MW)", "Capacity MW", "Nameplate Capacity (MW)"]:
        if key in row and pd.notna(row[key]):
            try:
                return float(row[key])
            except Exception:
                pass
    s = None
    for key in ["Capacity Range (MW)", "Capacity range (MW)"]:
        if key in row and pd.notna(row[key]):
            s = str(row[key]); break
    if s:
        m = re.search(r"([0-9]*\.?[0-9]+)\s*[-–]\s*([0-9]*\.?[0-9]+)", s)
        if m:
            lo, hi = float(m.group(1)), float(m.group(2))
            return {"lower": lo, "midpoint": (lo + hi) / 2.0, "upper": hi}[method]
        try:
            return float(re.sub(r"[^\d.]", "", s))
        except Exception:
            return np.nan
    return np.nan

def _normalize_county(name: str) -> str:
    if pd.isna(name):
        return ""
    s = str(name).lower()
    s = re.sub(r"\b(county|parish|borough|census area|municipality|city and borough|city|municipio)\b", "", s)
    s = re.sub(r"[-–]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _tidy_projects(df: pd.DataFrame, method: str, link_col: Optional[str]) -> pd.DataFrame:
    gen_col = "Canonical Generation Types" if "Canonical Generation Types" in df.columns else \
              "Generation Type(s)" if "Generation Type(s)" in df.columns else None
    if gen_col is None:
        return pd.DataFrame(columns=["Queue ID","Project Name","gen_type","capacity_mw","county_clean","state_clean"])

    g = df.copy()
    if "Status" in g.columns:
        g = g[g["Status"].astype(str).str.lower() == "active"]
    if g.empty:
        return g

    g["gen_type"] = g[gen_col].apply(_parse_gen_types)
    g = g.explode("gen_type")
    g["gen_type"] = g["gen_type"].fillna("Unknown")

    g["capacity_mw"] = g.apply(lambda r: _capacity_from_row(r, method), axis=1)
    g = g[pd.notna(g["capacity_mw"]) & (g["capacity_mw"] > 0)]

    g["county_clean"] = g.get("County", "").apply(_normalize_county)
    state_series = g.get("State")
    if state_series is None:
        return pd.DataFrame(columns=["Queue ID","Project Name","gen_type","capacity_mw","county_clean","state_clean"])
    g["state_clean"] = state_series.astype(str).str.upper().str.strip()

    cols = ["Queue ID","Project Name","gen_type","capacity_mw","county_clean","state_clean"]
    if link_col and link_col in g.columns:
        cols.append(link_col)
    return g[cols]

# ======= public renderer =======
def render_capacity_map_tab(
    data_path: str,
    default_gen_types: Optional[List[str]] = None,
    exclude_states: Set[str] = frozenset({"AK"}),  # or just Set[str] = {"AK"}
    link_col: Optional[str] = "source_url",
):
    st.markdown("This map sums **active** queue capacity (MW) per county for selected generation types.")

    cap_method = st.radio(
        "When only a capacity range is available, use:",
        ["midpoint", "lower", "upper"],
        index=0, horizontal=True
    )

    df_raw  = load_projects(data_path)
    df_tidy = _tidy_projects(df_raw, cap_method, link_col)

    if df_tidy.empty:
        st.warning("No active projects with capacity found.")
        return

    all_types = sorted(df_tidy["gen_type"].dropna().unique())
    default = default_gen_types or (["Solar"] if "Solar" in all_types else all_types)
    sel_types = st.multiselect("Generation types to include", all_types, default=default)

    df_sel = df_tidy[df_tidy["gen_type"].isin(sel_types)]
    if df_sel.empty:
        st.info("No rows after filtering.")
        return

    # roll up
    agg = df_sel.groupby(["state_clean","county_clean","gen_type"], as_index=False)["capacity_mw"].sum()
    rollup = agg.groupby(["state_clean","county_clean"], as_index=False)["capacity_mw"] \
                .sum().rename(columns={"capacity_mw":"capacity_total_mw"})

    xwalk = load_county_crosswalk()
    merged = rollup.merge(xwalk, how="left", on=["state_clean","county_clean"])
    merged_ok = merged.dropna(subset=["fips"]).copy()
    merged_ok["fips"] = merged_ok["fips"].str.zfill(5)

    # CONUS filtering
    xwalk_conus  = xwalk[~xwalk["state_clean"].isin(exclude_states)].copy()
    merged_conus = merged_ok[~merged_ok["state_clean"].isin(exclude_states)].copy()
    xwalk_conus["fips"] = xwalk_conus["fips"].str.zfill(5)

    geojson = load_counties_geojson()

    fig = go.Figure()
    # base grey
    fig.add_choropleth(
        geojson=geojson,
        locations=xwalk_conus["fips"],
        z=[0]*len(xwalk_conus),
        colorscale=[[0, "#E0E0E0"], [1, "#E0E0E0"]],
        showscale=False,
        marker_line_width=0.2,
        marker_line_color="white",
        hovertext=xwalk_conus["name"] + ", " + xwalk_conus["state"] + "<br>Capacity: Unknown",
        hoverinfo="text",
    )
    # overlay data
    fig.add_choropleth(
        geojson=geojson,
        locations=merged_conus["fips"],
        z=merged_conus["capacity_total_mw"],
        colorscale="Viridis",
        zmin=0,
        colorbar_title="MW",
        marker_line_width=0.2,
        marker_line_color="white",
        hovertext=(
            merged_conus["name"] + ", " + merged_conus["state"] +
            "<br>Total MW: " + merged_conus["capacity_total_mw"].map(lambda v: f"{v:,.1f}")
        ),
        hoverinfo="text",
    )

    fig.update_geos(scope="usa", fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("See aggregated table / download"):
        tbl = merged_conus[["state","name","capacity_total_mw"]].rename(
            columns={"state":"State","name":"County","capacity_total_mw":"Total MW"}
        ).sort_values("Total MW", ascending=False)
        st.dataframe(tbl, use_container_width=True)
        st.download_button(
            "Download county totals (CSV)",
            data=tbl.to_csv(index=False).encode("utf-8"),
            file_name="county_totals_active_mw.csv",
            mime="text/csv",
        )