"""Open-Meteo geocoding and air-quality API client with session management."""
from __future__ import annotations

from typing import Any, TypedDict

import requests

# Open-Meteo REST endpoints
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DEFAULT_TIMEOUT: int = 15


class AirQualityError(RuntimeError):
    """Raised when location lookup or air-quality retrieval fails."""


class GeocodedLocation(TypedDict):
    name: str
    admin1: str
    country: str
    latitude: float
    longitude: float
    timezone: str


def geocode_city(city: str) -> GeocodedLocation:
    """Return the best matching city with latitude/longitude, country, and timezone.

    Args:
        city: City name string to resolve.

    Returns:
        Structured GeocodedLocation dictionary with coordinates and metadata.

    Raises:
        AirQualityError: When the city is blank, unresolved, or the network request fails.
    """
    clean_city = (city or "").strip()
    if not clean_city:
        raise AirQualityError("Enter a city name to search.")

    if len(clean_city) > 100:
        raise AirQualityError("City query exceeds maximum permitted length.")

    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": clean_city, "count": 5, "language": "en", "format": "json"},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
    except requests.RequestException as exc:
        msg = "Location search is temporarily unavailable. Please try again."
        if hasattr(exc, "response") and exc.response is not None:
            try:
                err_data = exc.response.json()
                if isinstance(err_data, dict) and "reason" in err_data:
                    msg = f"Location service error: {err_data['reason']}"
            except Exception:
                pass
        raise AirQualityError(msg) from exc
    except ValueError as exc:
        raise AirQualityError("The location service returned an invalid response.") from exc

    if not results:
        raise AirQualityError(f"No matching location found for '{clean_city}'.")

    # Prefer an exact case-insensitive city-name match when available.
    match = next(
        (item for item in results if str(item.get("name", "")).casefold() == clean_city.casefold()),
        results[0],
    )

    if "latitude" not in match or "longitude" not in match:
        raise AirQualityError(f"Location coordinates not found for '{clean_city}'.")

    try:
        lat = float(match["latitude"])
        lon = float(match["longitude"])
    except (ValueError, TypeError) as exc:
        raise AirQualityError(f"Invalid coordinate format returned for '{clean_city}'.") from exc

    return {
        "name": str(match.get("name", clean_city)),
        "admin1": str(match.get("admin1", "")),
        "country": str(match.get("country", "")),
        "latitude": lat,
        "longitude": lon,
        "timezone": str(match.get("timezone", "auto")),
    }


def fetch_air_quality(
    latitude: float | int | str, longitude: float | int | str, timezone: str = "auto"
) -> dict[str, Any]:
    """Fetch current and hourly pollutant and AQI estimates from Open-Meteo.

    Args:
        latitude: Geographic latitude in decimal degrees.
        longitude: Geographic longitude in decimal degrees.
        timezone: Local timezone name or 'auto'.

    Returns:
        JSON payload containing 'current' and 'hourly' pollutant concentration data.

    Raises:
        AirQualityError: When coordinates are invalid, network fails, or payload is empty.
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError(f"Coordinates out of bounds: lat={lat}, lon={lon}")
    except (ValueError, TypeError) as exc:
        raise AirQualityError("Invalid coordinates provided for air-quality fetch.") from exc

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "us_aqi,european_aqi,pm10,pm2_5,carbon_monoxide,"
            "nitrogen_dioxide,sulphur_dioxide,ozone"
        ),
        "hourly": "us_aqi,pm10,pm2_5",
        "forecast_days": 2,
        "timezone": str(timezone or "auto"),
    }

    try:
        response = requests.get(AIR_QUALITY_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        msg = "Air-quality data could not be fetched right now. Please retry shortly."
        if hasattr(exc, "response") and exc.response is not None:
            try:
                err_data = exc.response.json()
                if isinstance(err_data, dict) and "reason" in err_data:
                    msg = f"Air-quality service error: {err_data['reason']}"
            except Exception:
                pass
        raise AirQualityError(msg) from exc
    except ValueError as exc:
        raise AirQualityError("The air-quality service returned an invalid response.") from exc

    if not isinstance(payload, dict) or not payload.get("current"):
        raise AirQualityError("No current air-quality readings are available for this location.")

    return payload
