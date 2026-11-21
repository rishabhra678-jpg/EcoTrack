"""Tests for Open-Meteo API client, analysis, and assistant modules."""
import pytest
from unittest.mock import patch, MagicMock
import requests

from air_quality.api import (
    geocode_city,
    fetch_air_quality,
    AirQualityError
)
from air_quality.analysis import (
    aqi_category,
    build_air_quality_insight
)
from air_quality.assistant import answer_air_quality_question


# ---------------- API Tests ----------------

def test_geocode_city_empty_input_raises():
    with pytest.raises(AirQualityError, match="Enter a city name"):
        geocode_city("")
    with pytest.raises(AirQualityError, match="Enter a city name"):
        geocode_city("   ")


@patch("requests.get")
def test_geocode_city_success_mocked(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "results": [
            {
                "name": "Bhopal",
                "admin1": "Madhya Pradesh",
                "country": "India",
                "latitude": 23.25,
                "longitude": 77.40,
                "timezone": "Asia/Kolkata"
            }
        ]
    }
    mock_get.return_value = mock_resp

    loc = geocode_city("Bhopal")
    assert loc["name"] == "Bhopal"
    assert loc["latitude"] == 23.25
    assert loc["longitude"] == 77.40
    assert loc["country"] == "India"


@patch("requests.get")
def test_geocode_city_no_results_raises(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"results": []}
    mock_get.return_value = mock_resp

    with pytest.raises(AirQualityError, match="No matching location found"):
        geocode_city("AtlantisUnreachable")


@patch("requests.get")
def test_geocode_city_network_error_raises(mock_get):
    mock_get.side_effect = requests.RequestException("DNS lookup failure")

    with pytest.raises(AirQualityError, match="Location search is temporarily unavailable"):
        geocode_city("Paris")


@patch("requests.get")
def test_fetch_air_quality_success_mocked(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "current": {
            "time": "2026-11-20T06:00",
            "us_aqi": 82,
            "pm2_5": 27.5,
            "pm10": 48.0,
            "european_aqi": 42
        },
        "hourly": {
            "time": ["2026-11-20T06:00", "2026-11-20T07:00"],
            "us_aqi": [82, 85]
        }
    }
    mock_get.return_value = mock_resp

    payload = fetch_air_quality(23.25, 77.40)
    assert "current" in payload
    assert payload["current"]["us_aqi"] == 82


def test_fetch_air_quality_invalid_coordinates():
    with pytest.raises(AirQualityError, match="Invalid coordinates"):
        fetch_air_quality("not-a-lat", "not-a-lon")


@patch("requests.get")
def test_fetch_air_quality_missing_current_raises(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"hourly": {}}
    mock_get.return_value = mock_resp

    with pytest.raises(AirQualityError, match="No current air-quality readings"):
        fetch_air_quality(10.0, 20.0)


# ---------------- Analysis Tests ----------------

def test_aqi_category_levels():
    # None or invalid input
    assert aqi_category(None)["label"] == "Unavailable"
    assert aqi_category("invalid_value")["label"] == "Unavailable"

    # Good: 0-50
    assert aqi_category(0)["label"] == "Good"
    assert aqi_category(50)["label"] == "Good"

    # Moderate: 51-100
    assert aqi_category(51)["label"] == "Moderate"
    assert aqi_category(100)["label"] == "Moderate"

    # Unhealthy for Sensitive Groups: 101-150
    assert aqi_category(101)["label"] == "Unhealthy for Sensitive Groups"
    assert aqi_category(150)["label"] == "Unhealthy for Sensitive Groups"

    # Unhealthy: 151-200
    assert aqi_category(151)["label"] == "Unhealthy"
    assert aqi_category(200)["label"] == "Unhealthy"

    # Very Unhealthy: 201-300
    assert aqi_category(201)["label"] == "Very Unhealthy"
    assert aqi_category(300)["label"] == "Very Unhealthy"

    # Hazardous: 301+
    assert aqi_category(301)["label"] == "Hazardous"
    assert aqi_category(500)["label"] == "Hazardous"


def test_build_air_quality_insight_complete():
    current_data = {
        "us_aqi": 75,
        "pm2_5": 24.5,
        "pm10": 42.1
    }
    insight = build_air_quality_insight(current_data)
    assert "Moderate" in insight
    assert "75" in insight
    assert "24.5" in insight
    assert "42.1" in insight
    assert "CPCB" in insight


def test_build_air_quality_insight_empty_and_none():
    insight_empty = build_air_quality_insight({})
    assert "Unavailable" in insight_empty

    insight_none = build_air_quality_insight(None)
    assert "Unavailable" in insight_none


# ---------------- Assistant Tests ----------------

def test_answer_air_quality_question_empty_prompt():
    ans = answer_air_quality_question("", {"us_aqi": 60})
    assert "Ask me about" in ans


def test_answer_air_quality_question_exercise():
    current = {"us_aqi": 80, "pm2_5": 25.0}
    ans = answer_air_quality_question("Can I go for a run outside?", current)
    assert "Activity guidance:" in ans


def test_answer_air_quality_question_mask():
    current = {"us_aqi": 165, "pm2_5": 65.0}
    ans = answer_air_quality_question("Should I wear an N95 mask?", current)
    assert "mask" in ans.casefold()
    assert "165" in ans


def test_answer_air_quality_question_pm_specific():
    current = {"us_aqi": 90, "pm2_5": 31.4, "pm10": 58.2}
    ans_pm25 = answer_air_quality_question("What is the PM2.5 level?", current)
    assert "31.4" in ans_pm25

    ans_pm10 = answer_air_quality_question("What about PM10 dust?", current)
    assert "58.2" in ans_pm10


def test_answer_air_quality_question_sensitive_groups():
    current = {"us_aqi": 110}
    ans = answer_air_quality_question("Is it safe for children with asthma?", current)
    assert "Sensitive groups advisory" in ans
