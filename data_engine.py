# data_engine.py - COMPLETE VERSION WITH area_km2
import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data
def load_thermal_data():
    """Load pre-generated satellite thermal data from CSV."""
    return pd.read_csv('satellite_thermal_data.csv')

def get_city_data(city_name):
    """Get all pixels for a specific city."""
    df = load_thermal_data()
    return df[df['city'] == city_name].copy()

def get_baseline_stats(city_name):
    """
    Get comprehensive baseline statistics for a city.
    
    Returns:
        Dict with: mean_temp, max_temp, hotspot_pct, urban_density, area_km2
    """
    df = get_city_data(city_name)
    
    mean_temp = df['temperature_c'].mean()
    max_temp = df['temperature_c'].max()
    
    # "Hotspot" = pixels in top 25% by temperature
    hotspot_threshold = df['temperature_c'].quantile(0.75)
    hotspot_pct = 100 * (df['temperature_c'] >= hotspot_threshold).sum() / len(df)
    
    # Urban density = mean NDBI
    urban_density = df['ndbi'].mean()
    
    # NEW: Calculate area in km²
    # Assumption: Each pixel = 100m × 100m = 0.01 km²
    # (Landsat 8 Level 2 resolution is ~100m per pixel)
    pixel_area_km2 = 0.01  # 100m × 100m = 10,000 m² = 0.01 km²
    num_pixels = len(df)
    area_km2 = num_pixels * pixel_area_km2
    
    return {
        'mean_temp': mean_temp,
        'max_temp': max_temp,
        'hotspot_pct': hotspot_pct,
        'urban_density': urban_density,
        'area_km2': area_km2,  # NEW: Total area covered
    }


# ============ OPTIONAL: ADDITIONAL UTILITY FUNCTIONS ============

def get_pixel_statistics(city_name):
    """
    Get detailed pixel-level statistics for a city.
    Useful for advanced analysis and visualizations.
    """
    df = get_city_data(city_name)
    
    return {
        'total_pixels': len(df),
        'temp_min': df['temperature_c'].min(),
        'temp_max': df['temperature_c'].max(),
        'temp_mean': df['temperature_c'].mean(),
        'temp_std': df['temperature_c'].std(),
        'temp_median': df['temperature_c'].median(),
        'ndbi_min': df['ndbi'].min(),
        'ndbi_max': df['ndbi'].max(),
        'ndbi_mean': df['ndbi'].mean(),
    }


def get_city_list():
    """Get list of all available cities in the dataset."""
    df = load_thermal_data()
    return sorted(df['city'].unique().tolist())


def filter_by_temperature_range(city_name, min_temp_c, max_temp_c):
    """
    Filter city data by temperature range.
    Useful for identifying specific hotspots or cool zones.
    
    Args:
        city_name: City to filter
        min_temp_c: Minimum temperature threshold
        max_temp_c: Maximum temperature threshold
    
    Returns:
        DataFrame with filtered pixels
    """
    df = get_city_data(city_name)
    return df[(df['temperature_c'] >= min_temp_c) & (df['temperature_c'] <= max_temp_c)].copy()


def get_hottest_zones(city_name, percentile=95):
    """
    Identify hottest zones in a city.
    
    Args:
        city_name: City to analyze
        percentile: Temperature percentile threshold (default 95th percentile)
    
    Returns:
        DataFrame with pixels above the percentile threshold
    """
    df = get_city_data(city_name)
    threshold = df['temperature_c'].quantile(percentile / 100)
    return df[df['temperature_c'] >= threshold].copy()


def get_coolest_zones(city_name, percentile=5):
    """
    Identify coolest zones in a city.
    Useful for understanding natural cooling patterns.
    
    Args:
        city_name: City to analyze
        percentile: Temperature percentile threshold (default 5th percentile)
    
    Returns:
        DataFrame with pixels below the percentile threshold
    """
    df = get_city_data(city_name)
    threshold = df['temperature_c'].quantile(percentile / 100)
    return df[df['temperature_c'] <= threshold].copy()


def get_urban_density_zones(city_name, ndbi_threshold=0.3):
    """
    Identify high-density urban zones.
    NDBI (Normalized Difference Built-up Index) > 0.3 = strong urban signals.
    
    Args:
        city_name: City to analyze
        ndbi_threshold: NDBI threshold for urban classification
    
    Returns:
        DataFrame with high urban density pixels
    """
    df = get_city_data(city_name)
    return df[df['ndbi'] >= ndbi_threshold].copy()


def calculate_intervention_impact(df_original, df_modified):
    """
    Calculate detailed intervention impact statistics.
    
    Args:
        df_original: Original (baseline) dataframe
        df_modified: Modified (after intervention) dataframe
    
    Returns:
        Dict with impact metrics
    """
    if 'temperature_reduction' not in df_modified.columns:
        return None
    
    return {
        'pixels_with_cooling': (df_modified['temperature_reduction'] > 0).sum(),
        'avg_cooling': df_modified['temperature_reduction'].mean(),
        'max_cooling': df_modified['temperature_reduction'].max(),
        'min_cooling': df_modified['temperature_reduction'].min(),
        'std_cooling': df_modified['temperature_reduction'].std(),
        'total_cooling_potential': df_modified['temperature_reduction'].sum(),
        'baseline_avg_temp': df_original['temperature_c'].mean(),
        'modified_avg_temp': df_modified['temperature_c'].mean(),
        'overall_reduction': df_original['temperature_c'].mean() - df_modified['temperature_c'].mean(),
    }
