"""EcoTrack: Personal Carbon Footprint Awareness and Urban Air Quality Platform."""
from __future__ import annotations

import inspect
import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image


# Compatibility helpers for Streamlit container stretching across versions
def _render_plotly_chart(fig: go.Figure, **kwargs: Any) -> Any:
    sig = inspect.signature(st.plotly_chart)
    if "width" in sig.parameters:
        return st.plotly_chart(fig, width="stretch", **kwargs)
    return st.plotly_chart(fig, use_container_width=True, **kwargs)


def _render_button(label: str, **kwargs: Any) -> bool:
    sig = inspect.signature(st.button)
    if "width" in sig.parameters:
        return bool(st.button(label, width="stretch", **kwargs))
    return bool(st.button(label, use_container_width=True, **kwargs))


def _render_image(image: Any, **kwargs: Any) -> Any:
    sig = inspect.signature(st.image)
    if "width" in sig.parameters:
        return st.image(image, width="stretch", **kwargs)
    return st.image(image, use_container_width=True, **kwargs)


def _render_dataframe(data: Any, **kwargs: Any) -> Any:
    sig = inspect.signature(st.dataframe)
    if "width" in sig.parameters:
        return st.dataframe(data, width="stretch", **kwargs)
    return st.dataframe(data, use_container_width=True, **kwargs)


# Set Streamlit Page Configuration at the very top
st.set_page_config(
    page_title="EcoTrack: Carbon Footprint Awareness Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Local module imports
from air_quality.analysis import aqi_category, build_air_quality_insight
from air_quality.api import AirQualityError, GeocodedLocation, fetch_air_quality, geocode_city
from air_quality.assistant import answer_air_quality_question
from calculator import (
    DEFAULT_FACTORS,
    calculate_footprint,
    calculate_sustainability_score,
    classify_footprint,
)
from predictor import predict_next_month
from recommendations import generate_recommendations, render_recommendation_card
from utils import (
    generate_csv_report,
    initialize_session_state,
    inject_custom_css,
    log_calculation_history,
)
from visualizations import create_bar_chart, create_donut_chart, create_projection_chart

# Initialize session state logs & CSS styles
initialize_session_state()
inject_custom_css()

# Sidebar Layout - Input Fields
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #10B981; margin-bottom: 5px;'>🌱 EcoTrack</h2>
        <p style='color: #CBD5E1; font-size: 0.9rem;'>Adjust your daily activities below</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Expanders in Sidebar for neat organization
with st.sidebar.expander("🚗 Transportation", expanded=True):
    car = st.slider(
        "Daily Car Travel (km)",
        min_value=0.0,
        max_value=200.0,
        value=25.0,
        step=1.0,
        help="Estimated daily distance traveled by personal automobile in kilometers.",
    )
    bike = st.slider(
        "Daily Bike Travel (km)",
        min_value=0.0,
        max_value=50.0,
        value=2.0,
        step=1.0,
        help="Estimated daily distance traveled by bicycle or e-bike in kilometers.",
    )
    bus = st.slider(
        "Daily Bus Travel (km)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
        help="Estimated daily distance commuted via local transit or bus in kilometers.",
    )
    train = st.slider(
        "Daily Train Travel (km)",
        min_value=0.0,
        max_value=200.0,
        value=0.0,
        step=1.0,
        help="Estimated daily distance traveled via commuter rail or metro in kilometers.",
    )

with st.sidebar.expander("💡 Home Utilities", expanded=True):
    electricity = st.slider(
        "Monthly Electricity (kWh)",
        min_value=0,
        max_value=1200,
        value=320,
        step=10,
        help="Average monthly household electricity usage from your utility bill in kilowatt-hours (kWh).",
    )
    water = st.slider(
        "Daily Water Usage (liters)",
        min_value=0,
        max_value=600,
        value=150,
        step=10,
        help="Estimated personal daily water usage in liters (bathing, cleaning, cooking).",
    )

with st.sidebar.expander("🥗 Diet & Waste Habits", expanded=True):
    food = st.selectbox(
        "Primary Diet / Food Habit",
        options=["Vegan", "Vegetarian", "Mixed Diet", "Heavy Meat Diet"],
        index=2,
        help="Select the dietary profile that most closely reflects your daily meals.",
    )
    waste = st.slider(
        "Daily Waste Generated (kg)",
        min_value=0.0,
        max_value=10.0,
        value=1.5,
        step=0.1,
        help="Estimated municipal solid waste/trash generated per person per day in kilograms.",
    )

# Group user inputs together
user_inputs: dict[str, Any] = {
    "car": car,
    "bike": bike,
    "bus": bus,
    "train": train,
    "electricity": electricity,
    "water": water,
    "food": food,
    "waste": waste,
}

# Run Calculator
emissions = calculate_footprint(
    car_km=car,
    bike_km=bike,
    bus_km=bus,
    train_km=train,
    electricity_kwh=electricity,
    water_liters=water,
    food_habit=food,
    waste_kg=waste,
)

# Extract calculations
daily_total = emissions["totals"]["daily"]
monthly_total = emissions["totals"]["monthly"]
annual_total = emissions["totals"]["annual"]

# Calculate sustainability score and classify
sustainability_score = calculate_sustainability_score(annual_total)
classification = classify_footprint(daily_total)

# Log calculations to history
log_calculation_history(user_inputs, daily_total)

# Header Section with App Logo
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
col_logo, col_title = st.columns([1, 9])
with col_logo:
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            _render_image(img)
            st.markdown("<span class='sr-only'>EcoTrack Platform Logo</span>", unsafe_allow_html=True)
        except Exception:
            st.markdown("<div role='img' aria-label='EcoTrack Seedling Logo' style='font-size: 3rem;'>🌱</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div role='img' aria-label='EcoTrack Seedling Logo' style='font-size: 3rem;'>🌱</div>", unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 class='main-title'>EcoTrack</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Carbon Footprint Awareness & Reduction Platform</p>", unsafe_allow_html=True)

# Main Application Tabs
tab_dash, tab_ai, tab_goals, tab_history, tab_air, tab_learn = st.tabs([
    "📊 Personal Dashboard",
    "🤖 AI Predictor",
    "🎯 Reduction Goals",
    "⏳ Session History",
    "🌫️ Urban Air Quality",
    "📖 Learn More",
])

# ----------------- TAB 1: DASHBOARD -----------------
with tab_dash:
    # 1. Classification Badge
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 20px;'>
            <span style='font-size: 1.1rem; color: #94A3B8;'>Climate Footprint Status:</span>
            <div class='badge-box' style='background-color: {classification["color"]}; color: {classification["text_color"]};'>
                {classification["badge"]} - {classification["category"]}
            </div>
        </div>
        <p style='color: #E2E8F0; font-size: 1rem; margin-top: -15px; margin-bottom: 25px; max-width: 800px; font-weight: 300; line-height: 1.5;'>
            {classification["description"]}
        </p>
        """,
        unsafe_allow_html=True,
    )

    # 2. Glassmorphism metrics row
    score_label = (
        "Excellent"
        if sustainability_score >= 80
        else "Good"
        if sustainability_score >= 60
        else "Moderate"
        if sustainability_score >= 40
        else "Needs Work"
    )
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-label">Daily Carbon Footprint</div>
                <div class="metric-value">{daily_total:.2f} kg</div>
                <div class="metric-sub">CO₂ / day</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Monthly Projected</div>
                <div class="metric-value">{monthly_total:.1f} kg</div>
                <div class="metric-sub">CO₂ / month</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Annual Projected</div>
                <div class="metric-value">{annual_total / 1000.0:.2f} tons</div>
                <div class="metric-sub">CO₂ / year</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sustainability Score</div>
                <div class="metric-value">{sustainability_score:.1f} / 100</div>
                <div class="metric-sub" style="color: #60A5FA;">Status: {score_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Visualization columns
    col_donut, col_bar = st.columns(2)
    with col_donut:
        st.markdown("<h3 style='color: #F8FAFC; font-size: 1.25rem; font-weight:600;'>Emissions Breakdown</h3>", unsafe_allow_html=True)
        donut_fig = create_donut_chart(emissions)
        _render_plotly_chart(donut_fig)

    with col_bar:
        st.markdown("<h3 style='color: #F8FAFC; font-size: 1.25rem; font-weight:600;'>Category Comparison</h3>", unsafe_allow_html=True)
        bar_fig = create_bar_chart(emissions)
        _render_plotly_chart(bar_fig)

    # Accessible tabular representation for emissions breakdown
    with st.expander("📊 View Emissions Breakdown Data Table (Accessible)", expanded=False):
        emissions_table = [
            {
                "Source": "Transportation",
                "Daily (kg CO₂)": emissions["transport"]["total_daily"],
                "Monthly (kg CO₂)": emissions["transport"]["total_daily"] * 30.0,
                "Share (%)": (emissions["transport"]["total_daily"] / daily_total * 100.0) if daily_total > 0 else 0.0,
            },
            {
                "Source": "Home Electricity",
                "Daily (kg CO₂)": emissions["electricity"]["total_daily"],
                "Monthly (kg CO₂)": emissions["electricity"]["total_daily"] * 30.0,
                "Share (%)": (emissions["electricity"]["total_daily"] / daily_total * 100.0) if daily_total > 0 else 0.0,
            },
            {
                "Source": "Diet / Food",
                "Daily (kg CO₂)": emissions["food"]["total_daily"],
                "Monthly (kg CO₂)": emissions["food"]["total_daily"] * 30.0,
                "Share (%)": (emissions["food"]["total_daily"] / daily_total * 100.0) if daily_total > 0 else 0.0,
            },
            {
                "Source": "Water Usage",
                "Daily (kg CO₂)": emissions["water"]["total_daily"],
                "Monthly (kg CO₂)": emissions["water"]["total_daily"] * 30.0,
                "Share (%)": (emissions["water"]["total_daily"] / daily_total * 100.0) if daily_total > 0 else 0.0,
            },
            {
                "Source": "Waste Disposal",
                "Daily (kg CO₂)": emissions["waste"]["total_daily"],
                "Monthly (kg CO₂)": emissions["waste"]["total_daily"] * 30.0,
                "Share (%)": (emissions["waste"]["total_daily"] / daily_total * 100.0) if daily_total > 0 else 0.0,
            },
        ]
        emissions_df = pd.DataFrame(emissions_table)
        _render_dataframe(emissions_df.style.format({
            "Daily (kg CO₂)": "{:.2f}",
            "Monthly (kg CO₂)": "{:.1f}",
            "Share (%)": "{:.1f}%",
        }))

    # 4. Recommendation Cards
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #10B981; margin-bottom: 15px;'>🌱 Personalized Recommendations for Carbon Reduction</h3>", unsafe_allow_html=True)

    recs = generate_recommendations(
        car_km=car,
        bike_km=bike,
        bus_km=bus,
        train_km=train,
        electricity_kwh=electricity,
        water_liters=water,
        food_habit=food,
        waste_kg=waste,
    )

    for r in recs:
        st.markdown(render_recommendation_card(r), unsafe_allow_html=True)

# ----------------- TAB 2: AI PREDICTOR -----------------
with tab_ai:
    st.markdown("### 🤖 Next-Month Carbon Prediction Engine")
    st.write(
        """
        Using a machine learning **Random Forest Regressor** trained on synthetic lifestyle profiles,
        EcoTrack simulates next month's footprint. The model factors in potential **seasonal variations**
        (e.g., HVAC electricity loads) and random lifestyle changes to project your future impact.
        """
    )

    if st.button("Run AI Prediction Model", help="Run the Random Forest Regressor to simulate next month's footprint."):
        with st.spinner("Analyzing current lifestyle and loading AI model..."):
            predicted_footprint = predict_next_month(
                car_km=car,
                bike_km=bike,
                bus_km=bus,
                train_km=train,
                electricity_kwh=electricity,
                water_liters=water,
                food_habit=food,
                waste_kg=waste,
            )

        difference = predicted_footprint - monthly_total
        pct_change = (difference / monthly_total) * 100 if monthly_total > 0 else 0.0

        # Display Prediction Card
        card_bg = "rgba(16, 185, 129, 0.15)" if difference <= 0 else "rgba(239, 68, 68, 0.15)"
        border_col = "#10B981" if difference <= 0 else "#EF4444"
        arrow = "⬇️" if difference <= 0 else "⬆️"
        status_text = "decrease" if difference <= 0 else "increase"

        st.markdown(
            f"""
            <div style="background-color: {card_bg}; border: 1px solid {border_col}; border-radius: 12px; padding: 25px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
                <h4 style="margin: 0 0 15px 0; color: #F8FAFC; font-weight: 600;">Prediction Output: Next Month's Projected Emissions</h4>
                <div style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC; margin-bottom: 10px;">
                    {predicted_footprint:.1f} kg CO₂ / month
                </div>
                <p style="margin: 0; color: #CBD5E1; line-height: 1.5; font-size: 1rem;">
                    {arrow} Your monthly footprint is predicted to <strong>{status_text} by {abs(pct_change):.1f}%</strong>
                    ({abs(difference):.1f} kg CO₂) compared to this month ({monthly_total:.1f} kg CO₂), due to seasonal weather
                    fluctuations and simulated consumption variability.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------- TAB 3: REDUCTION GOALS -----------------
with tab_goals:
    st.markdown("### 🎯 Carbon Reduction Commitments")
    st.write(
        """
        Commit to reducing your daily resource usage. See how these lifestyle tweaks translate into annual carbon offsets
        and check your progress line against the baseline forecast.
        """
    )

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Set Weekly/Monthly Targets")
        car_red = st.slider(
            "Reduce Car Travel by (km / week)",
            min_value=0,
            max_value=500,
            value=50,
            step=5,
            help="Target reduction in weekly car driving distance in kilometers.",
        )
        elec_red = st.slider(
            "Reduce Electricity by (kWh / month)",
            min_value=0,
            max_value=300,
            value=40,
            step=5,
            help="Target reduction in monthly electricity usage in kilowatt-hours.",
        )
        waste_red = st.slider(
            "Reduce Daily Waste by (kg / day)",
            min_value=0.0,
            max_value=5.0,
            value=0.5,
            step=0.1,
            help="Target reduction in daily waste generation in kilograms.",
        )
        diet_shift = st.slider(
            "Go Plant-Based / Meat-Free (days / week)",
            min_value=0,
            max_value=7,
            value=2,
            step=1,
            help="Number of days per week replacing meat meals with plant-based options.",
        )

        # Calculate goal offsets using verified factors
        car_factor = DEFAULT_FACTORS.get("Car", 0.192)
        grid_factor = DEFAULT_FACTORS.get("Grid", 0.82)
        waste_factor = DEFAULT_FACTORS.get("Trash", 0.57)

        car_savings = car_red * 52.0 * car_factor
        elec_savings = elec_red * 12.0 * grid_factor
        waste_savings = waste_red * 365.0 * waste_factor
        # Diet savings: shifting from heavy meat (7 kg/day) to vegan (2 kg/day) = 5.0 kg/day saved
        diet_savings = diet_shift * 52.0 * 5.0

        total_annual_savings = car_savings + elec_savings + waste_savings + diet_savings
        pct_footprint_reduced = (total_annual_savings / annual_total) * 100.0 if annual_total > 0 else 0.0

    with col_g2:
        st.markdown("#### Annual Environmental Savings")
        st.markdown(
            f"""
            <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 5px solid #3B82F6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <div style="font-size: 0.85rem; text-transform: uppercase; color: #94A3B8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 5px;">Total Carbon Offset</div>
                <div style="font-size: 2rem; font-weight: 700; color: #3B82F6;">{total_annual_savings:.1f} kg CO₂ / year</div>
                <div style="font-size: 0.95rem; color: #10B981; font-weight: 500; margin-top: 5px;">
                    Offsetting <strong>{pct_footprint_reduced:.1f}%</strong> of your annual footprint!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Equivalence metrics
        trees_planted = total_annual_savings / 22.0  # 1 mature tree absorbs ~22kg CO2/year
        smartphone_charges = total_annual_savings / 0.008  # 1 smartphone charge is ~8g CO2

        st.markdown(
            f"""
            <div style="display: flex; gap: 15px; margin-top: 10px;">
                <div style="background-color: rgba(30,41,59,0.5); padding: 15px; border-radius: 8px; flex: 1; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 1.5rem; margin-bottom: 5px;">🌲</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">{trees_planted:.1f}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Trees Planted Equiv.</div>
                </div>
                <div style="background-color: rgba(30,41,59,0.5); padding: 15px; border-radius: 8px; flex: 1; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 1.5rem; margin-bottom: 5px;">📱</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">{smartphone_charges:,.0f}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Smartphone Charges</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 📅 12-Month Cumulative Projection Analysis", unsafe_allow_html=True)
    projection_fig = create_projection_chart(monthly_total, total_annual_savings)
    _render_plotly_chart(projection_fig)

    with st.expander("📊 View 12-Month Projection Data Table (Accessible)", expanded=False):
        months_arr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        m_savings = total_annual_savings / 12.0
        proj_rows = []
        b_acc = 0.0
        t_acc = 0.0
        for m_name in months_arr:
            b_acc += monthly_total
            t_acc += max(0.0, monthly_total - m_savings)
            proj_rows.append({
                "Month": m_name,
                "Baseline Cumulative (kg CO₂)": b_acc,
                "Target Cumulative (kg CO₂)": t_acc,
                "Cumulative Savings (kg CO₂)": b_acc - t_acc,
            })
        proj_df = pd.DataFrame(proj_rows)
        _render_dataframe(proj_df.style.format({
            "Baseline Cumulative (kg CO₂)": "{:.1f}",
            "Target Cumulative (kg CO₂)": "{:.1f}",
            "Cumulative Savings (kg CO₂)": "{:.1f}",
        }))

# ----------------- TAB 4: HISTORY & EXPORTS -----------------
with tab_history:
    st.markdown("### ⏳ Session Log & Report Export")
    st.write(
        """
        Track how adjustments to sliders alter your footprint. Download your carbon calculator worksheet
        as a standard CSV file for record-keeping.
        """
    )

    # 1. Download CSV Button
    csv_data = generate_csv_report(user_inputs, emissions, sustainability_score, classification["category"])

    st.download_button(
        label="Download Footprint Report (CSV)",
        data=csv_data,
        file_name="EcoTrack_Carbon_Report.csv",
        mime="text/csv",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. History table
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        # Clean columns for display
        display_df = history_df.rename(columns={
            "timestamp": "Timestamp",
            "car": "Car (km/day)",
            "electricity": "Electricity (kWh/mo)",
            "waste": "Waste (kg/day)",
            "food": "Diet Type",
            "daily_footprint": "Footprint (kg CO₂/day)",
        })

        st.markdown("#### Saved Activity Log")
        _render_dataframe(display_df.style.format({
            "Car (km/day)": "{:.1f}",
            "Electricity (kWh/mo)": "{:.0f}",
            "Waste (kg/day)": "{:.1f}",
            "Footprint (kg CO₂/day)": "{:.2f}",
        }))

        # 3. History trend chart
        if len(st.session_state.history) > 1:
            st.markdown("#### Footprint Progress Trend")
            trend_fig = go.Figure(
                data=[
                    go.Scatter(
                        x=history_df["timestamp"],
                        y=history_df["daily_footprint"],
                        mode="lines+markers",
                        line=dict(color="#10B981", width=3),
                        marker=dict(size=8, color="#059669"),
                    )
                ]
            )
            trend_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                xaxis=dict(
                    title="Time of Calculation",
                    gridcolor="#334155",
                    zerolinecolor="#334155",
                ),
                yaxis=dict(
                    title="Daily Footprint (kg CO₂)",
                    gridcolor="#334155",
                    zerolinecolor="#334155",
                ),
                margin=dict(t=10, b=40, l=10, r=10),
                height=250,
            )
            _render_plotly_chart(trend_fig)
    else:
        st.info("No calculations logged yet. Adjust sidebar sliders to record values.")

# ----------------- TAB 5: URBAN AIR QUALITY -----------------
with tab_air:
    st.markdown("### 🌫️ Urban Air Quality Assistant")
    st.write(
        "Explore current modelled air-quality estimates, pollutant levels and the near-term trend "
        "for a city. Data is provided by Open-Meteo and is not a substitute for an official local monitoring station."
    )

    @st.cache_data(ttl=900, show_spinner=False)
    def load_city_air_quality(city_name: str) -> tuple[GeocodedLocation, dict[str, Any]]:
        loc = geocode_city(city_name)
        payload = fetch_air_quality(
            loc["latitude"], loc["longitude"], loc.get("timezone", "auto")
        )
        return loc, payload

    city_col, refresh_col = st.columns([4, 1])
    with city_col:
        city_name = st.text_input(
            "Search city",
            value=st.session_state.get("air_quality_city", "Bhopal"),
            placeholder="Enter a city, e.g. Bhopal",
            key="air_quality_city_input",
            help="Search for global modeled air quality forecasts by city name.",
        )
    with refresh_col:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        refresh_air = _render_button("Refresh data", help="Re-fetch the latest air-quality readings for this location.")

    if refresh_air:
        load_city_air_quality.clear()

    if city_name.strip():
        try:
            with st.spinner("Fetching the latest available air-quality estimates..."):
                location, air_payload = load_city_air_quality(city_name.strip())
            current = air_payload["current"]
            category = aqi_category(current.get("us_aqi"))

            st.markdown(
                f"**{location['name']}**"
                + (f", {location['admin1']}" if location.get("admin1") else "")
                + (f", {location['country']}" if location.get("country") else "")
            )
            st.caption(
                f"Updated: {current.get('time', 'Not provided')} · "
                "Source: Open-Meteo modelled air-quality data · AQI scale: US EPA"
            )

            def _fmt_metric_int(val: Any) -> str:
                if val is None:
                    return "N/A"
                try:
                    return str(round(float(val)))
                except (ValueError, TypeError):
                    return "N/A"

            def _fmt_metric_float(val: Any, unit: str = "") -> str:
                if val is None:
                    return "N/A"
                try:
                    return f"{float(val):.1f} {unit}".strip()
                except (ValueError, TypeError):
                    return "N/A"

            metric_cols = st.columns(4)
            metric_cols[0].metric("US AQI estimate", _fmt_metric_int(current.get("us_aqi")))
            metric_cols[1].metric("PM2.5", _fmt_metric_float(current.get("pm2_5"), "µg/m³"))
            metric_cols[2].metric("PM10", _fmt_metric_float(current.get("pm10"), "µg/m³"))
            metric_cols[3].metric("European AQI", _fmt_metric_int(current.get("european_aqi")))

            st.markdown(
                f"<div style='border-left: 5px solid {category['color']}; padding: 12px 16px; "
                f"background: rgba(100,116,139,0.12); border-radius: 8px; margin: 12px 0;'>"
                f"<strong>{category['label']}</strong><br>{category['advice']}</div>",
                unsafe_allow_html=True,
            )

            pollutant_labels = {
                "pm2_5": "PM2.5",
                "pm10": "PM10",
                "nitrogen_dioxide": "NO₂",
                "sulphur_dioxide": "SO₂",
                "ozone": "O₃",
                "carbon_monoxide": "CO",
            }
            pollutant_values = []
            for key, label in pollutant_labels.items():
                value = current.get(key)
                if value is not None:
                    try:
                        pollutant_values.append({"Pollutant": label, "Concentration (µg/m³)": float(value)})
                    except (ValueError, TypeError):
                        pass

            left, right = st.columns([1, 1])
            with left:
                st.markdown("#### Pollutant readings")
                if pollutant_values:
                    pollutant_df = pd.DataFrame(pollutant_values)
                    fig_pollutants = go.Figure(
                        go.Bar(
                            x=pollutant_df["Pollutant"],
                            y=pollutant_df["Concentration (µg/m³)"],
                            marker_color="#10B981",
                        )
                    )
                    fig_pollutants.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#F8FAFC",
                        yaxis_title="µg/m³",
                        margin=dict(t=15, b=15, l=10, r=10),
                        height=300,
                    )
                    _render_plotly_chart(fig_pollutants)
                    with st.expander("📊 View Pollutant Concentrations Table (Accessible)", expanded=False):
                        _render_dataframe(pollutant_df.style.format({"Concentration (µg/m³)": "{:.1f}"}))
                else:
                    st.info("No pollutant concentration readings were returned.")

            with right:
                st.markdown("#### City location")
                if hasattr(go, "Scattermap"):
                    map_fig = go.Figure(
                        go.Scattermap(
                            lat=[location["latitude"]],
                            lon=[location["longitude"]],
                            mode="markers",
                            marker=dict(size=18, color="#10B981"),
                            text=[location["name"]],
                            hoverinfo="text",
                        )
                    )
                    map_fig.update_layout(
                        map=dict(
                            style="open-street-map",
                            center=dict(lat=location["latitude"], lon=location["longitude"]),
                            zoom=9,
                        ),
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=300,
                    )
                else:
                    map_fig = go.Figure(
                        go.Scattermapbox(
                            lat=[location["latitude"]],
                            lon=[location["longitude"]],
                            mode="markers",
                            marker=dict(size=18, color="#10B981"),
                            text=[location["name"]],
                            hoverinfo="text",
                        )
                    )
                    map_fig.update_layout(
                        mapbox=dict(
                            style="open-street-map",
                            center=dict(lat=location["latitude"], lon=location["longitude"]),
                            zoom=9,
                        ),
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=300,
                    )
                _render_plotly_chart(map_fig)
                st.caption(
                    f"📍 Coordinates: {location['latitude']:.4f}° N, {location['longitude']:.4f}° E · Timezone: {location.get('timezone', 'auto')}"
                )

            hourly = air_payload.get("hourly", {})
            if hourly.get("time") and hourly.get("us_aqi"):
                times = hourly["time"]
                aqis = hourly["us_aqi"]
                min_len = min(len(times), len(aqis))
                if min_len > 0:
                    st.markdown("#### AQI trend · next available forecast hours")
                    trend_df = (
                        pd.DataFrame({
                            "Time": pd.to_datetime(times[:min_len]),
                            "US AQI": aqis[:min_len],
                        })
                        .dropna()
                        .head(24)
                    )
                    if not trend_df.empty:
                        trend_fig = go.Figure(
                            go.Scatter(
                                x=trend_df["Time"],
                                y=trend_df["US AQI"],
                                mode="lines+markers",
                                line=dict(color="#10B981", width=3),
                            )
                        )
                        trend_fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#F8FAFC",
                            yaxis_title="US AQI",
                            margin=dict(t=15, b=15, l=10, r=10),
                            height=280,
                        )
                        _render_plotly_chart(trend_fig)
                        with st.expander("📊 View Hourly AQI Forecast Table (Accessible)", expanded=False):
                            _render_dataframe(trend_df.style.format({"US AQI": "{:.0f}"}))

            st.markdown("#### Ask EcoTrack about this city's air")
            question = st.text_input(
                "Your question",
                placeholder="Is it a good time to go running?",
                key="air_quality_question",
                help="Ask questions about outdoor activities, masks, sensitive groups, or air quality.",
            )
            if st.button(
                "Ask EcoTrack AI",
                key="ask_air_quality",
                help="Get a grounded response based on the latest air quality readings.",
            ):
                st.markdown(answer_air_quality_question(question, current))

            with st.expander("How to interpret this data"):
                st.markdown(build_air_quality_insight(current))
                st.caption(
                    "Open-Meteo's US AQI and European AQI are different scales. "
                    "This release does not calculate CPCB India AQI. For official Indian AQI advisories, "
                    "consult CPCB monitoring and guidance."
                )

        except AirQualityError as exc:
            st.error(str(exc))
        except (KeyError, TypeError, ValueError):
            st.error("The air-quality response was incomplete or could not be displayed. Please refresh and try again.")
    else:
        st.info("Enter a city name to view its air-quality estimates.")

# ----------------- TAB 6: LEARN MORE -----------------
with tab_learn:
    st.markdown("### 📖 Science & Educational Reference")
    st.markdown(
        """
        #### What is a Carbon Footprint?
        A carbon footprint represents the total greenhouse gas (GHG) emissions caused directly and indirectly by an individual,
        organization, event, or product. It is expressed in carbon dioxide equivalents ($CO_2e$) to standardize the warming impacts
        of various gases like methane ($CH_4$) and nitrous oxide ($N_2O$).

        #### Calculation Methodologies
        EcoTrack calculates footprints by multiplying activity rates by verified emission factors:

        $$\\text{Emission} = \\text{Activity Quantity} \\times \\text{Emission Factor}$$

        Our database references parameters from environmental bodies:
        * **Transit**: Standard vehicle emission factors represent EPA averages for internal combustion vehicles. Active transit (like biking) reflects minimal indirect caloric food chain emissions.
        * **Electricity**: Uses regional grid carbon intensity averages ($0.82 \\text{ kg CO}_2/\\text{kWh}$), which accounts for natural gas, coal, and renewables in the local utility mix.
        * **Food**: Emits carbon based on food supply chain studies (IPCC, Poore & Nemecek 2018). Animal agriculture contributes methane ($CH_4$) from enteric fermentation and land deforestation, giving heavy meat diets high factors ($7 \\text{ kg CO}_2/\\text{day}$), whereas plant diets remain low ($2 \\text{ kg CO}_2/\\text{day}$).
        * **Waste**: Accounts for landfills where anaerobically digested waste leaks methane ($0.57 \\text{ kg CO}_2/\\text{kg}$).

        #### Quick Habits for Immediate Reduction
        1. **Turn down the thermostat**: Lowering heating by 1-2°C saves 5% of energy.
        2. **Drive smoothly**: Sudden acceleration decreases fuel efficiency by up to 30%.
        3. **Air dry clothes**: Tumble dryers are energy intensive. Air drying offsets 90 kg of carbon annually.
        4. **Compost kitchen waste**: Prevents organic materials from turning into landfill methane.
        """
    )
