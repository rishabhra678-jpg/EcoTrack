"""Open-Meteo geocoding and air-quality API client."""
from __future__ import annotations

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
TIMEOUT = 15


class AirQualityError(RuntimeError):
    """Raised when location lookup or air-quality retrieval fails."""


def geocode_city(city: str) -> dict:
    """Return the best matching city with latitude/longitude and country."""
    city = city.strip()
    if not city:
        raise AirQualityError("Enter a city name to search.")

    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": city, "count": 5, "language": "en", "format": "json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
    except requests.RequestException as exc:
        raise AirQualityError("Location search is temporarily unavailable. Please try again.") from exc
    except ValueError as exc:
        raise AirQualityError("The location service returned an invalid response.") from exc

    if not results:
        raise AirQualityError(f"No matching location found for '{city}'.")

    # Prefer an exact case-insensitive city-name match when available.
    match = next(
        (item for item in results if item.get("name", "").casefold() == city.casefold()),
        results[0],
    )
    return {
        "name": match.get("name", city),
        "admin1": match.get("admin1", ""),
        "country": match.get("country", ""),
        "latitude": match["latitude"],
        "longitude": match["longitude"],
        "timezone": match.get("timezone", "auto"),
    }


def fetch_air_quality(latitude: float, longitude: float, timezone: str = "auto") -> dict:
    """Fetch current and hourly pollutant/AQI estimates from Open-Meteo."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "us_aqi,european_aqi,pm10,pm2_5,carbon_monoxide,"
            "nitrogen_dioxide,sulphur_dioxide,ozone"
        ),
        "hourly": "us_aqi,pm10,pm2_5",
        "forecast_days": 2,
        "timezone": timezone or "auto",
    }
    try:
        response = requests.get(AIR_QUALITY_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise AirQualityError("Air-quality data could not be fetched right now. Please retry shortly.") from exc
    except ValueError as exc:
        raise AirQualityError("The air-quality service returned an invalid response.") from exc

    if not payload.get("current"):
        raise AirQualityError("No current air-quality readings are available for this location.")
    return payload
