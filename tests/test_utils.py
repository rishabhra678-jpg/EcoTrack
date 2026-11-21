"""Tests for EcoTrack utility functions (session state, CSV reports, CSS)."""
import pytest
import pandas as pd
from utils import (
    initialize_session_state,
    log_calculation_history,
    generate_csv_report
)


def test_generate_csv_report_structure():
    inputs = {
        "car": 25.0,
        "bike": 2.0,
        "bus": 0.0,
        "train": 0.0,
        "electricity": 320,
        "water": 150,
        "food": "Mixed Diet",
        "waste": 1.5
    }
    emissions = {
        "transport": {"total_daily": 4.8},
        "electricity": {"total_daily": 8.75},
        "water": {"total_daily": 0.045},
        "food": {"total_daily": 5.0},
        "waste": {"total_daily": 0.855},
        "totals": {
            "daily": 19.45,
            "monthly": 583.5,
            "annual": 7099.25
        }
    }
    score = 71.0
    category = "Sustainable Citizen"

    csv_output = generate_csv_report(inputs, emissions, score, category)
    assert isinstance(csv_output, bytes)
    text = csv_output.decode("utf-8")
    assert "Metric / Activity,Value,Unit" in text
    assert "Car Travel (km/day),25.0,km" in text
    assert "Total Footprint (kg CO2/day),19.450" in text
    assert "Sustainable Citizen" in text
    assert "71.0" in text


def test_session_state_initialization():
    import streamlit as st
    initialize_session_state()
    assert hasattr(st.session_state, "history")
    assert isinstance(st.session_state.history, list)
    assert hasattr(st.session_state, "goals")
    assert isinstance(st.session_state.goals, dict)


def test_log_calculation_history_duplicate_prevention():
    import streamlit as st
    initialize_session_state()
    st.session_state.history = []

    inputs = {"car": 10.0, "electricity": 100, "waste": 1.0, "food": "Vegan"}
    log_calculation_history(inputs, 5.5)
    assert len(st.session_state.history) == 1

    # Second log with identical daily_footprint should be skipped
    log_calculation_history(inputs, 5.5)
    assert len(st.session_state.history) == 1

    # Third log with different footprint should be added
    log_calculation_history(inputs, 6.2)
    assert len(st.session_state.history) == 2
