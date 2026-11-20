"""Generative AI service module for EcoTrack using Google Gemini API."""
from __future__ import annotations

import os
from typing import Any
import streamlit as st

_CLIENT_CACHE: dict[str, Any] = {}


def get_api_key(explicit_key: str | None = None) -> str | None:
    """Retrieve Gemini API key from explicit argument, Streamlit secrets, or environment."""
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    # Check Streamlit secrets
    try:
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                return str(st.secrets["GEMINI_API_KEY"]).strip()
            if "GOOGLE_API_KEY" in st.secrets and st.secrets["GOOGLE_API_KEY"]:
                return str(st.secrets["GOOGLE_API_KEY"]).strip()
    except Exception:
        pass

    # Check environment variables
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    return None


def get_genai_client(api_key: str | None = None) -> Any | None:
    """Instantiate and cache a google.genai Client."""
    key = get_api_key(api_key)
    if not key:
        return None

    if key in _CLIENT_CACHE:
        return _CLIENT_CACHE[key]

    try:
        from google import genai
        client = genai.Client(api_key=key)
        _CLIENT_CACHE[key] = client
        return client
    except Exception:
        return None


def ask_gemini_air_quality(
    question: str,
    city_name: str,
    current: dict,
    category: dict | None = None,
    api_key: str | None = None,
    model: str = "gemini-2.5-flash",
) -> str | None:
    """Answer air-quality queries using Gemini grounded on live Open-Meteo readings."""
    client = get_genai_client(api_key)
    if not client:
        return None

    aqi = current.get("us_aqi")
    category_label = category.get("label", "Unavailable") if category else "Unavailable"
    category_advice = category.get("advice", "") if category else ""
    pm25 = current.get("pm2_5")
    pm10 = current.get("pm10")
    no2 = current.get("nitrogen_dioxide")
    so2 = current.get("sulphur_dioxide")
    o3 = current.get("ozone")
    co = current.get("carbon_monoxide")
    european_aqi = current.get("european_aqi")
    time_str = current.get("time", "Current")

    prompt = f"""You are EcoTrack AI, an intelligent, empathetic urban air-quality and climate assistant.
You provide clear, practical health, outdoor exercise, and environmental advice grounded strictly in real-time air quality data.

Location: {city_name}
Timestamp: {time_str}
Live Air Quality Readings:
- US AQI: {aqi if aqi is not None else 'N/A'} (Category: {category_label})
- Health Advisory: {category_advice}
- PM2.5: {pm25 if pm25 is not None else 'N/A'} µg/m³
- PM10: {pm10 if pm10 is not None else 'N/A'} µg/m³
- Nitrogen Dioxide (NO₂): {no2 if no2 is not None else 'N/A'} µg/m³
- Sulphur Dioxide (SO₂): {so2 if so2 is not None else 'N/A'} µg/m³
- Ozone (O₃): {o3 if o3 is not None else 'N/A'} µg/m³
- Carbon Monoxide (CO): {co if co is not None else 'N/A'} µg/m³
- European AQI: {european_aqi if european_aqi is not None else 'N/A'}

User's Question: "{question}"

Instructions:
1. Ground your answer directly in the numbers and category above.
2. If the user asks about outdoor workouts (running, cycling, walking), specify intensity recommendations based on the AQI category.
3. If the user asks about masks or sensitive groups (children, elderly, asthma), provide evidence-based guidance (e.g. N95 masks when AQI > 100).
4. Keep the tone helpful, concise, and structured with bold highlights and bullet points where helpful.
5. Remind the user that this is an automated informational estimate, not official medical advice.
"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception:
        # Fallback to gemini-1.5-flash if gemini-2.5-flash is unavailable
        if model != "gemini-1.5-flash":
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                )
                return response.text
            except Exception:
                pass
        return None


def generate_ecocoach_plan(
    user_inputs: dict,
    emissions: dict,
    sustainability_score: float,
    classification: dict,
    api_key: str | None = None,
    model: str = "gemini-2.5-flash",
) -> str | None:
    """Generate a personalized carbon reduction plan using Gemini."""
    client = get_genai_client(api_key)
    if not client:
        return None

    daily_total = emissions.get("totals", {}).get("daily", 0.0)
    monthly_total = emissions.get("totals", {}).get("monthly", 0.0)
    annual_total = emissions.get("totals", {}).get("annual", 0.0)

    car_km = user_inputs.get("car", 0)
    bike_km = user_inputs.get("bike", 0)
    bus_km = user_inputs.get("bus", 0)
    train_km = user_inputs.get("train", 0)
    electricity = user_inputs.get("electricity", 0)
    water = user_inputs.get("water", 0)
    food = user_inputs.get("food", "Mixed Diet")
    waste = user_inputs.get("waste", 0)

    prompt = f"""You are EcoCoach, EcoTrack's personalized generative climate advisor.
Your job is to analyze the user's lifestyle inputs and emissions profile to provide an inspiring, highly customized, actionable 30-day Carbon Reduction Action Plan.

User Lifestyle & Activity Profile:
- Car Travel: {car_km} km/day
- Bike Travel: {bike_km} km/day
- Bus Travel: {bus_km} km/day
- Train Travel: {train_km} km/day
- Home Electricity: {electricity} kWh/month
- Daily Water Consumption: {water} liters/day
- Dietary Habit: {food}
- Waste Generation: {waste} kg/day

Calculated Impact:
- Daily Carbon Footprint: {daily_total:.2f} kg CO₂/day
- Monthly Footprint: {monthly_total:.1f} kg CO₂/month
- Annual Projected Footprint: {annual_total/1000.0:.2f} tonnes CO₂/year
- Sustainability Score: {sustainability_score:.1f} / 100
- Climate Footprint Status: {classification.get('category', 'Moderate Impact')} ({classification.get('badge', '')})

Instructions:
1. Start with an encouraging assessment of their biggest emission drivers and strengths.
2. Provide 3 "Quick Wins" (zero-cost changes they can make today).
3. Outline a "30-Day Step-by-Step Reduction Roadmap" covering transit, home energy, and diet.
4. Estimate how much carbon and money they could save annually if they follow the roadmap.
5. Use clean GitHub markdown with emojis, bullet points, and bold text. Keep it concise, practical, and highly motivating.
"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception:
        if model != "gemini-1.5-flash":
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                )
                return response.text
            except Exception:
                pass
        return None
