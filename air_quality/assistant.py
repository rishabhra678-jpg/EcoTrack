"""Grounded response helper for the first EcoTrack air-quality release."""
from .analysis import build_air_quality_insight


def answer_air_quality_question(question: str, current: dict) -> str:
    """Answer common air-quality questions using only the latest API readings."""
    prompt = (question or "").strip().casefold()
    if not prompt:
        return "Ask me about the current air quality, pollution levels, or outdoor activities."

    summary = build_air_quality_insight(current)
    if any(word in prompt for word in ("run", "running", "jog", "cycle", "cycling", "exercise", "outdoor", "walk")):
        return (
            summary
            + "\n\n**Activity guidance:** Base outdoor exercise on the AQI category above. "
            "If the estimate is elevated, reduce intensity or duration, choose an indoor option, "
            "and follow local health advisories."
        )
    if any(word in prompt for word in ("pm2.5", "pm 2.5", "fine particle")):
        value = current.get("pm2_5")
        detail = f"The latest PM2.5 estimate is {float(value):.1f} µg/m³." if value is not None else "A PM2.5 reading is not available."
        return detail + "\n\n" + summary
    if any(word in prompt for word in ("pm10", "dust", "particle")):
        value = current.get("pm10")
        detail = f"The latest PM10 estimate is {float(value):.1f} µg/m³." if value is not None else "A PM10 reading is not available."
        return detail + "\n\n" + summary
    return summary
