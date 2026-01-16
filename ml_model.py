# ml_model.py - FINAL CORRECTED VERSION
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import streamlit as st

# ==========================================================
# ML MODEL (Baseline Temperature Estimator)
# ==========================================================

@st.cache_resource
def train_heat_predictor():
    """
    Train a small regression model that learns
    how urban form affects surface temperature.

    NOTE:
    This model is intentionally lightweight and
    serves as a baseline estimator — NOT the
    intervention engine.
    """
    X = np.array([
        [0.05, 0.05, 0.90],  # low vegetation, low reflectivity, high density
        [0.10, 0.10, 0.80],
        [0.30, 0.20, 0.60],
        [0.50, 0.30, 0.40],
        [0.70, 0.40, 0.25],
        [0.85, 0.50, 0.15],
    ])
    y = np.array([46, 42, 38, 34, 30, 27])

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    model.fit(X, y)
    return model


# ==========================================================
# INTERVENTION ENGINE (MAIN FIX IS HERE)
# ==========================================================

def apply_intervention_to_dataframe(df, green_increase_pct, refl_increase_pct):
    """
    Apply urban cooling interventions to thermal data.

    FIXED LOGIC:
    - Cooling is applied PER 1% increase (not per 100%)
    - Built-up areas (high NDBI) respond more strongly
    - Results now produce visible, realistic deltas
    """

    df_modified = df.copy()

    # Normalize NDBI to 0–1 range
    ndbi_norm = df['ndbi'] / (df['ndbi'].max() + 1e-6)

    # Cooling coefficients (°C per 1% increase)
    # These are calibrated for visible but realistic city-scale impact
    VEG_COOLING_PER_PCT = 0.04    # trees, parks, green roofs
    REFL_COOLING_PER_PCT = 0.07   # cool roofs, pavements

    # Compute effects
    veg_effect = green_increase_pct * VEG_COOLING_PER_PCT * ndbi_norm
    refl_effect = refl_increase_pct * REFL_COOLING_PER_PCT * ndbi_norm

    # Combine and cap cooling (physics + realism constraint)
    total_reduction = np.minimum(veg_effect + refl_effect, 3.0)

    # Apply cooling
    df_modified['temperature_reduction'] = total_reduction
    df_modified['temperature_c'] = df['temperature_c'] - total_reduction

    return df_modified


# ==========================================================
# SUMMARY METRICS
# ==========================================================

def get_intervention_summary(df_original, df_modified):
    """
    Compute before/after metrics for dashboard display.
    """
    original_mean = df_original['temperature_c'].mean()
    modified_mean = df_modified['temperature_c'].mean()

    return {
        'base_temp': round(original_mean, 2),
        'new_temp': round(modified_mean, 2),
        'reduction': round(original_mean - modified_mean, 2),
        'max_reduction': round(df_modified['temperature_reduction'].max(), 2),
    }


# ==========================================================
# TREE ESTIMATION (POLICY / PLANNING MODULE)
# ==========================================================

def estimate_trees_required(area_km2: float, target_temp_drop_c: float) -> int:
    """
    Estimate number of trees required for city-scale cooling.

    Heuristic:
    ~1000 trees / km² / °C (dense priority zones)
    """
    if target_temp_drop_c <= 0:
        return 0

    TREES_PER_KM2_PER_DEGREE = 1000
    return int(area_km2 * target_temp_drop_c * TREES_PER_KM2_PER_DEGREE)


# ==========================================================
# COOL ROOF ESTIMATION
# ==========================================================

def estimate_paint_layers_and_color(target_temp_drop_c: float) -> tuple:
    """
    Estimate cool-roof paint layers and color type.
    """

    if target_temp_drop_c <= 0:
        return 0, "No coating required"

    COOLING_PER_LAYER = 0.8  # °C per layer
    layers_needed = int(np.ceil(target_temp_drop_c / COOLING_PER_LAYER))
    layers_needed = min(layers_needed, 3)

    color_map = {
        1: "High-Albedo White (95% reflectance, SRI ≈105)",
        2: "Off-White + Primer (90% reflectance, SRI ≈95)",
        3: "Pure White Triple-Coat (98% reflectance, SRI ≈115+)",
    }

    return layers_needed, color_map.get(layers_needed, "Engineering review required")
