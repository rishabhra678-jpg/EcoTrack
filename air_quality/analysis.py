"""Interpret Open-Meteo AQI estimates and generate practical guidance."""
from __future__ import annotations


def aqi_category(aqi):
    """Return US EPA AQI category metadata; input must be the US AQI field."""
    if aqi is None:
        return {"label": "Unavailable", "color": "#64748B", "advice": "No AQI estimate is available."}
    try:
        value = float(aqi)
    except (ValueError, TypeError):
        return {"label": "Unavailable", "color": "#64748B", "advice": "No AQI estimate is available."}

    if value <= 50:
        return {"label": "Good", "color": "#16A34A", "advice": "Air quality is generally satisfactory."}
    if value <= 100:
        return {"label": "Moderate", "color": "#CA8A04", "advice": "Most people can continue normal activities; unusually sensitive people may notice effects."}
    if value <= 150:
        return {"label": "Unhealthy for Sensitive Groups", "color": "#EA580C", "advice": "Sensitive groups should reduce prolonged or heavy outdoor exertion."}
    if value <= 200:
        return {"label": "Unhealthy", "color": "#DC2626", "advice": "Everyone should consider reducing prolonged or heavy outdoor exertion."}
    if value <= 300:
        return {"label": "Very Unhealthy", "color": "#7C3AED", "advice": "Avoid prolonged outdoor exertion; sensitive groups should avoid outdoor activity."}
    return {"label": "Hazardous", "color": "#7F1D1D", "advice": "Avoid outdoor exertion and follow local public-health guidance."}


def build_air_quality_insight(current: dict) -> str:
    """Create a transparent, rule-based summary grounded in returned readings."""
    if not isinstance(current, dict):
        current = {}

    aqi = current.get("us_aqi")
    category = aqi_category(aqi)
    lines = [f"**Current estimate: {category['label']}**"]
    if aqi is not None:
        try:
            lines.append(f"Open-Meteo US AQI estimate: **{round(float(aqi))}**.")
        except (ValueError, TypeError):
            pass
    lines.append(category["advice"])

    pm25 = current.get("pm2_5")
    pm10 = current.get("pm10")
    if pm25 is not None:
        try:
            lines.append(f"PM2.5: **{float(pm25):.1f} µg/m³**.")
        except (ValueError, TypeError):
            pass
    if pm10 is not None:
        try:
            lines.append(f"PM10: **{float(pm10):.1f} µg/m³**.")
        except (ValueError, TypeError):
            pass
    lines.append(
        "This is an automated informational estimate, not a medical diagnosis. "
        "The displayed US AQI is not the CPCB India AQI; use local CPCB advisories for official Indian AQI guidance."
    )
    return "\n\n".join(lines)
