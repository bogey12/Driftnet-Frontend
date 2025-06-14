import streamlit as st
import numpy as np

"""Generic constraint‐input utilities
This module exposes the same public functions that streamlit_app.py already imports:
    render_power_constraints
    render_land_constraints
    render_climate_constraints
    render_fiber_constraints
    render_future_constraints

Each function renders a block of inputs in native units (number boxes or dropdowns),
translates every input into a 0–100 score, and returns
    {"scores": {metric_key: score, …}, "overall_score": <float>}
The mapping from native value → score is defined in the METRICS dictionary below.
Adjust min/max, default, inverse, or supply a custom lambda in "score" to tune behaviour.
"""

# ─────────────────────────── Metric specification ────────────────────────────
# For number inputs:  supply min / max / default and optionally "inverse=True"
# For categorical inputs: supply a "select" mapping of {label: score}
# Optional "units" (shown as help-text).  Optional custom "score" lambda(value)->0-100.
METRICS = {
    "power": [
        {"key": "cost",       "label": "Cost ($/MWh)",                         "min": 20,  "max": 200,  "default": 70,  "inverse": True,  "units": "$/MWh"},
        {"key": "queue",      "label": "Interconnection Queue (months)",      "min": 0,   "max": 60,   "default": 24,  "inverse": True,  "units": "months"},
        {"key": "territory",  "label": "Service-territory size (mi²)",        "min": 0,   "max": 50_000, "default": 5_000, "inverse": False, "units": "mi²"},
        {"key": "cluster",    "label": "Ongoing Cluster Studies (MW)",       "min": 0,   "max": 10_000, "default": 500, "inverse": False, "units": "MW"},
        {"key": "pipeline",   "label": "New Power Projects (MW)",            "min": 0,   "max": 10_000, "default": 1_000, "inverse": False, "units": "MW"},
        {"key": "reg_change", "label": "Regulatory Climate",                 "select": {"Supportive": 100, "Neutral": 50, "Restrictive": 0}},
        {"key": "lobby",      "label": "Lobbying Effort ($M/y)",             "min": 0,   "max": 50,   "default": 5,   "inverse": False, "units": "Million $"},
        {"key": "hv_dist",    "label": "HV-Line Proximity (km)",             "min": 0,   "max": 100, "default": 25,  "inverse": True,  "units": "km"},
        {"key": "gas_dist",   "label": "Gas-Pipe Proximity (km)",            "min": 0,   "max": 200, "default": 50,  "inverse": True,  "units": "km"},
    ],
    "land": [
        {"key": "parcel", "label": "Parcel size (acres)",              "min": 10,  "max": 5_000, "default": 100, "inverse": False, "units": "acres"},
        {"key": "slope",  "label": "Average slope (%)",               "min": 0,   "max": 15,    "default": 3,   "inverse": True,  "units": "%"},
        {"key": "zoning", "label": "Zoning & land-use",               "select": {"Industrial": 100, "Commercial": 70, "Mixed Use": 40, "Residential": 0}},
    ],
    "climate": [
        {"key": "temp", "label": "Avg. temperature (°F)", "min": 32, "max": 90, "default": 65, "score": lambda v: max(0, 100 - abs(v - 60) * 3), "units": "°F"},
        {"key": "flood", "label": "Flood risk",           "select": {"Very Low": 100, "Low": 80, "Medium": 60, "High": 30, "Very High": 0}},
        {"key": "wildfire", "label": "Wildfire risk",     "select": {"Very Low": 100, "Low": 80, "Medium": 60, "High": 30, "Very High": 0}},
        {"key": "water", "label": "Water availability (kgal/day)", "min": 0, "max": 10_000, "default": 2_000, "inverse": False, "units": "kgal/day"},
    ],
    "fiber": [
        {"key": "fiber_dist", "label": "Fiber backbone distance (km)", "min": 0, "max": 25,  "default": 5,   "inverse": True,  "units": "km"},
        {"key": "subsea",     "label": "Sub-sea cable distance (km)",  "min": 0, "max": 500, "default": 200, "inverse": True,  "units": "km"},
    ],
    "future": [
        {"key": "corridor", "label": "Growth-corridor score",               "min": 0,  "max": 100, "default": 50, "inverse": False},
        {"key": "workload", "label": "Workload/design-trend alignment",     "min": 0,  "max": 100, "default": 50, "inverse": False},
        {"key": "demand",   "label": "Energy-demand growth (%/y)",         "min": 0,  "max": 20,  "default": 5,  "inverse": False, "units": "%"},
    ],
}

# ─────────────────────────── Helper rendering ───────────────────────────────

def _render_table(rows):
    """Render a markdown table for quick reference."""
    header = "| Metric | Granularity | Units |\n|---|---|---|\n"
    st.markdown(header + "\n".join(f"| {m} | {g} | {u} |" for m, g, u in rows))


def _value_to_score(val, spec):
    """Convert raw value to 0-100 score using spec rules."""
    if "score" in spec:
        return np.clip(spec["score"](val), 0, 100)
    min_v, max_v = spec["min"], spec["max"]
    if spec.get("inverse"):
        return np.interp(val, [min_v, max_v], [100, 0])
    return np.interp(val, [min_v, max_v], [0, 100])


def _unit_input(spec, widget_id):
    if "select" in spec:
        choice = st.selectbox(spec["label"], options=list(spec["select"].keys()), key=widget_id)
        return spec["select"][choice]

    step = (spec["max"] - spec["min"]) / 100 or 0.01
    val = st.number_input(
        spec["label"],
        min_value=float(spec["min"]),
        max_value=float(spec["max"]),
        value=float(spec["default"]),
        step=float(step),
        format="%.4f" if isinstance(spec["default"], float) else "%.2f",
        help=spec.get("units", ""),
        key=widget_id
    )
    return _value_to_score(val, spec)


def _render_category(cat_key: str, title: str):
    """Render inputs for a category and return scores."""
    st.markdown(f"### {title}")

    # Build reference table rows
    table_rows = []
    for m in METRICS[cat_key]:
        if "select" in m:
            units = "/".join(m["select"].keys())
            gran = "Categorical"
        else:
            units = m.get("units", "")
            gran = ""
        table_rows.append((m["label"], gran, units))
    # Reference table removed from final UI

    scores = {}
    for m in METRICS[cat_key]:
        scores[m["key"]] = _unit_input(m, f"{cat_key}_{m['key']}")

    overall = float(np.mean(list(scores.values()))) if scores else 0
    st.success(f"Overall {title} Score: **{overall:.1f}/100**")
    return {"scores": scores, "overall_score": overall}

# ─────────────────────────── Public wrappers ────────────────────────────────

def render_power_constraints():
    return _render_category("power", "Power Factors")


def render_land_constraints():
    return _render_category("land", "Land & Site Characteristics")


def render_climate_constraints():
    return _render_category("climate", "Climate & Environmental Risk")


def render_fiber_constraints():
    return _render_category("fiber", "Connectivity Infrastructure")


def render_future_constraints():
    return _render_category("future", "Future Scalability & Demand")

def render_regulatory_constraints():
    """Render regulatory and compliance constraints"""
    st.subheader("Regulatory & Compliance Requirements")
    
    # Initialize scores dictionary
    scores = {}
    
    # 1. Permitting Process
    st.markdown("#### 1️⃣ Permitting Timeline")
    permit_time = st.number_input(
        "Expected permitting timeline (months)",
        min_value=0,
        max_value=48,
        value=12,
        help="Estimated time to obtain all necessary permits"
    )
    permit_score = max(0, 100 - (permit_time * 2))
    scores['permit_score'] = permit_score
    st.markdown(f"Score: {permit_score:.1f}/100")
    
    # 2. Tax Incentives
    st.markdown("#### 2️⃣ Tax Incentives")
    incentives = st.multiselect(
        "Available tax incentives",
        options=[
            "Property tax abatement",
            "Sales tax exemption",
            "Investment tax credits",
            "Job creation credits",
            "Energy efficiency incentives"
        ]
    )
    incentive_score = min(100, len(incentives) * 20)
    scores['incentive_score'] = incentive_score
    st.markdown(f"Score: {incentive_score}/100")
    
    # 3. Environmental Compliance
    st.markdown("#### 3️⃣ Environmental Regulations")
    col1, col2 = st.columns(2)
    
    with col1:
        eia_required = st.checkbox("Environmental Impact Assessment required", value=False)
        emissions_limits = st.checkbox("Strict emissions limits", value=False)
    
    with col2:
        water_restrictions = st.checkbox("Water usage restrictions", value=False)
        noise_regulations = st.checkbox("Noise level restrictions", value=False)
    
    env_restrictions = sum([eia_required, emissions_limits, water_restrictions, noise_regulations])
    env_compliance_score = max(0, 100 - (env_restrictions * 25))
    scores['env_compliance_score'] = env_compliance_score
    st.markdown(f"Score: {env_compliance_score}/100")
    
    # 4. Local Support
    st.markdown("#### 4️⃣ Local Government Support")
    support_level = st.select_slider(
        "Level of local government support",
        options=["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
        value="Neutral"
    )
    
    support_mapping = {
        "Very Negative": 0,
        "Negative": 25,
        "Neutral": 50,
        "Positive": 75,
        "Very Positive": 100
    }
    
    support_score = support_mapping[support_level]
    scores['support_score'] = support_score
    st.markdown(f"Score: {support_score}/100")
    
    # 5. Security Requirements
    st.markdown("#### 5️⃣ Security Requirements")
    security_reqs = st.multiselect(
        "Required security measures",
        options=[
            "24/7 security personnel",
            "Perimeter fencing",
            "Video surveillance",
            "Access control systems",
            "Background checks"
        ]
    )
    security_score = min(100, len(security_reqs) * 20)
    scores['security_score'] = security_score
    st.markdown(f"Score: {security_score}/100")
    
    # 6. Weights
    st.markdown("#### 6️⃣ Weights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        permit_weight = st.slider("Permitting Weight", 0, 100, 20)
        incentive_weight = st.slider("Tax Incentives Weight", 0, 100, 20)
    
    with col2:
        env_weight = st.slider("Environmental Compliance Weight", 0, 100, 20)
        support_weight = st.slider("Local Support Weight", 0, 100, 20)
    
    with col3:
        security_weight = st.slider("Security Requirements Weight", 0, 100, 20)
    
    # Normalize weights
    total_weight = permit_weight + incentive_weight + env_weight + support_weight + security_weight
    if total_weight == 0:
        st.error("❌ Total weight cannot be 0. Please adjust the weights.")
        return None
        
    weights = {
        'permit_score': permit_weight / total_weight,
        'incentive_score': incentive_weight / total_weight,
        'env_compliance_score': env_weight / total_weight,
        'support_score': support_weight / total_weight,
        'security_score': security_weight / total_weight
    }
    
    # Calculate overall score
    overall_score = sum(scores[k] * weights[k] for k in weights.keys())
    
    # Display total weight validation
    st.markdown("---")
    st.markdown(f"**Total Weight**: {total_weight}")
    if total_weight != 100:
        st.warning("⚠️ Weights should sum to 100")
    else:
        st.success("✅ Weights sum to 100")
    
    st.markdown(f"**Overall Regulatory Score**: {overall_score:.1f}/100")
    
    return {
        'scores': scores,
        'weights': weights,
        'overall_score': overall_score
    } 