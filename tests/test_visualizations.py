"""Unit tests for EcoTrack Plotly visualization generator functions."""
from __future__ import annotations

import plotly.graph_objects as go

from visualizations import (
    _extract_category_emissions,
    create_bar_chart,
    create_donut_chart,
    create_projection_chart,
)


def test_extract_category_emissions_standard():
    emissions_dict = {
        "transport": {"total_daily": 5.5},
        "electricity": {"total_daily": 8.0},
        "food": {"total_daily": 4.0},
        "water": {"total_daily": 0.05},
        "waste": {"total_daily": 0.9},
    }
    categories, values = _extract_category_emissions(emissions_dict)
    assert len(categories) == 5
    assert len(values) == 5
    assert values[0] == 5.5
    assert values[1] == 8.0


def test_extract_category_emissions_empty_or_malformed():
    categories, values = _extract_category_emissions({})
    assert len(categories) == 5
    assert all(v == 0.0 for v in values)

    malformed = {
        "transport": "invalid_string",
        "electricity": {"total_daily": None},
    }
    categories, values = _extract_category_emissions(malformed)
    assert len(categories) == 5
    assert all(v == 0.0 for v in values)


def test_create_donut_chart_standard():
    emissions_dict = {
        "transport": {"total_daily": 10.0},
        "electricity": {"total_daily": 5.0},
        "food": {"total_daily": 3.0},
        "water": {"total_daily": 0.01},
        "waste": {"total_daily": 1.0},
    }
    fig = create_donut_chart(emissions_dict)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "pie"
    assert fig.data[0].hole == 0.5


def test_create_donut_chart_all_zeros():
    emissions_dict = {
        "transport": {"total_daily": 0.0},
        "electricity": {"total_daily": 0.0},
        "food": {"total_daily": 0.0},
        "water": {"total_daily": 0.0},
        "waste": {"total_daily": 0.0},
    }
    fig = create_donut_chart(emissions_dict)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    # Fallback placeholder label present
    assert "No Emissions" in fig.data[0].labels


def test_create_bar_chart_standard():
    emissions_dict = {
        "transport": {"total_daily": 12.0},
        "electricity": {"total_daily": 6.0},
        "food": {"total_daily": 4.0},
        "water": {"total_daily": 0.02},
        "waste": {"total_daily": 1.2},
    }
    fig = create_bar_chart(emissions_dict)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"
    assert fig.data[0].orientation == "h"
    assert len(fig.data[0].y) == 5


def test_create_projection_chart_standard():
    monthly_emissions = 200.0
    annual_savings = 360.0  # 30 kg/month savings
    fig = create_projection_chart(monthly_emissions, annual_savings)
    assert isinstance(fig, go.Figure)
    # Expect 3 traces: Baseline, Target, Shaded Difference area
    assert len(fig.data) == 3
    baseline_trace = fig.data[0]
    target_trace = fig.data[1]
    assert len(baseline_trace.x) == 12
    assert len(target_trace.x) == 12
    # Baseline should always be higher than or equal to target
    assert baseline_trace.y[-1] > target_trace.y[-1]
