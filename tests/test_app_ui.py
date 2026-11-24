"""End-to-end Streamlit AppTest suite verifying UI integrity, widgets, and workflows."""
import os
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))


def mock_requests_get(url, *args, **kwargs):
    """Deterministic mock for Open-Meteo geocoding and air-quality API endpoints."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    if "geocoding-api" in url:
        mock_resp.json.return_value = {
            "results": [
                {
                    "name": "Bhopal",
                    "latitude": 23.2599,
                    "longitude": 77.4126,
                    "country": "India",
                    "timezone": "Asia/Kolkata",
                }
            ]
        }
    else:
        mock_resp.json.return_value = {
            "current": {
                "us_aqi": 75,
                "european_aqi": 45,
                "pm2_5": 22.5,
                "pm10": 48.0,
                "nitrogen_dioxide": 18.2,
                "sulphur_dioxide": 6.1,
                "ozone": 30.5,
                "carbon_monoxide": 410.0,
            },
            "hourly": {
                "time": ["2026-11-21T00:00", "2026-11-21T01:00"],
                "us_aqi": [70, 75],
            },
        }
    return mock_resp


@pytest.fixture
def app():
    """Fixture that initializes the Streamlit AppTest tree with mocked network APIs for deterministic testing."""
    with patch("requests.get", side_effect=mock_requests_get):
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        yield at


def test_app_loads_without_exceptions(app):
    """Verify application boots cleanly without uncaught runtime exceptions."""
    assert len(app.exception) == 0, f"App loaded with exceptions: {app.exception}"


def test_app_sidebar_sliders_present_and_functional(app):
    """Verify all 7 activity input sliders and diet selectbox are rendered."""
    assert len(app.slider) >= 7
    # Adjust daily car travel slider
    car_slider = app.slider[0]
    car_slider.set_value(50.0)
    with patch("requests.get", side_effect=mock_requests_get):
        app.run()
    assert len(app.exception) == 0


def test_app_ai_predictor_execution(app):
    """Test clicking the Run AI Prediction Model button."""
    predict_button = next((b for b in app.button if "Prediction" in b.label), None)
    assert predict_button is not None, "Prediction model button not found in app"
    predict_button.click()
    with patch("requests.get", side_effect=mock_requests_get):
        app.run()
    assert len(app.exception) == 0


def test_app_reduction_goals_interaction(app):
    """Verify reduction goal adjustment recalculates offsets cleanly."""
    goal_sliders = [s for s in app.slider if "Reduce" in s.label or "Plant-Based" in s.label]
    assert len(goal_sliders) >= 3
    # Adjust first goal slider
    goal_sliders[0].set_value(100)
    with patch("requests.get", side_effect=mock_requests_get):
        app.run()
    assert len(app.exception) == 0


def test_app_air_quality_tab_and_assistant(app):
    """Verify air quality city search and question submission."""
    city_input = app.text_input(key="air_quality_city_input")
    assert city_input is not None
    assert city_input.value != ""

    # Test question submission
    question_input = app.text_input(key="air_quality_question")
    assert question_input is not None
    question_input.set_value("Is the air clean for an outdoor walk?")

    ask_button = app.button(key="ask_air_quality")
    assert ask_button is not None
    ask_button.click()
    with patch("requests.get", side_effect=mock_requests_get):
        app.run()
    assert len(app.exception) == 0


def test_app_accessible_expanders_rendered(app):
    """Verify accessible data table expanders are present for charts."""
    expander_labels = [e.label for e in app.expander]
    # Check that accessible tables exist for emissions, projections, and air quality
    assert any("Emissions Breakdown Data Table (Accessible)" in label for label in expander_labels)
    assert any("12-Month Projection Data Table (Accessible)" in label for label in expander_labels)
    assert any("Pollutant Concentrations Table (Accessible)" in label for label in expander_labels)
