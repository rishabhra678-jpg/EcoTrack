"""Data visualization module for EcoTrack using Plotly."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import plotly.graph_objects as go

# Canonical palette for category representations
CATEGORY_COLORS: dict[str, str] = {
    "Transport": "#3B82F6",    # Blue
    "Electricity": "#F59E0B",  # Amber/Yellow
    "Food": "#10B981",         # Emerald Green
    "Water": "#06B6D4",        # Cyan
    "Waste": "#EF4444",        # Red
}


def _extract_category_emissions(emissions_dict: Mapping[str, Any]) -> tuple[list[str], list[float]]:
    """Safely extract emission values for categories from the calculation dictionary."""
    categories = ["Transport", "Electricity", "Food", "Water", "Waste"]
    keys = ["transport", "electricity", "food", "water", "waste"]

    values: list[float] = []
    for k in keys:
        component = emissions_dict.get(k, {})
        val = component.get("total_daily", 0.0) if isinstance(component, (dict, Mapping)) else 0.0
        try:
            values.append(max(0.0, float(val)))
        except (ValueError, TypeError):
            values.append(0.0)

    return categories, values


def create_donut_chart(emissions_dict: Mapping[str, Any]) -> go.Figure:
    """Create a Plotly donut chart showing the percentage contribution of each source."""
    categories, values = _extract_category_emissions(emissions_dict)

    # Filter out categories with zero emissions for clean visualization
    filtered_labels: list[str] = []
    filtered_values: list[float] = []
    for label, val in zip(categories, values, strict=False):
        if val > 0:
            filtered_labels.append(label)
            filtered_values.append(val)

    # Fallback if all values are 0
    if not filtered_labels:
        filtered_labels = ["No Emissions"]
        filtered_values = [1.0]
        colors = ["#334155"]
    else:
        colors = [CATEGORY_COLORS.get(label, "#94A3B8") for label in filtered_labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=filtered_labels,
                values=filtered_values,
                hole=0.5,
                marker=dict(colors=colors, line=dict(color="#1E293B", width=2)),
                textinfo="percent+label",
                hoverinfo="label+value+percent",
                hovertemplate="<b>%{label}</b><br>Emissions: %{value:.2f} kg CO₂/day<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Emissions Breakdown by Category",
            font=dict(color="#F8FAFC", size=14),
            x=0.5,
            xanchor="center",
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC", size=12),
        margin=dict(t=40, b=10, l=10, r=10),
        height=320,
    )

    return fig


def create_bar_chart(emissions_dict: Mapping[str, Any]) -> go.Figure:
    """Create a horizontal bar chart comparing daily emissions across categories."""
    categories, values = _extract_category_emissions(emissions_dict)
    colors = [CATEGORY_COLORS.get(cat, "#94A3B8") for cat in categories]

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=categories,
                orientation="h",
                text=[f"{x:.2f} kg" for x in values],
                textposition="auto",
                textfont=dict(color="#F8FAFC", size=11),
                marker=dict(
                    color=colors,
                    line=dict(color="#1E293B", width=1),
                ),
                hovertemplate="<b>%{y}</b><br>Emissions: %{x:.2f} kg CO₂/day<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Daily Emissions by Category",
            font=dict(color="#F8FAFC", size=14),
            x=0.5,
            xanchor="center",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        xaxis=dict(
            title="Emissions (kg CO₂ / day)",
            gridcolor="#334155",
            zerolinecolor="#334155",
            title_font=dict(size=11),
        ),
        yaxis=dict(
            title="",
            autorange="reversed",  # Read top to bottom
        ),
        margin=dict(t=40, b=40, l=10, r=10),
        height=320,
    )

    return fig


def create_projection_chart(monthly_emissions: float | int, annual_savings: float | int) -> go.Figure:
    """Create a 12-month projection comparing baseline vs. target savings."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    m_emissions = max(0.0, float(monthly_emissions))
    a_savings = max(0.0, float(annual_savings))
    monthly_savings = a_savings / 12.0

    baseline_cumulative: list[float] = []
    target_cumulative: list[float] = []

    baseline_sum = 0.0
    target_sum = 0.0

    for _i in range(12):
        baseline_sum += m_emissions
        target_sum += max(0.0, m_emissions - monthly_savings)

        baseline_cumulative.append(baseline_sum)
        target_cumulative.append(target_sum)

    fig = go.Figure()

    # Baseline line (dashed + circle markers)
    fig.add_trace(
        go.Scatter(
            x=months,
            y=baseline_cumulative,
            mode="lines+markers",
            name="Baseline (No Changes)",
            line=dict(color="#EF4444", width=3, dash="dash"),
            marker=dict(size=7, symbol="circle"),
            hovertemplate="Month: %{x}<br>Baseline: %{y:.1f} kg CO₂<extra></extra>",
        )
    )

    # Target line (solid + diamond markers)
    fig.add_trace(
        go.Scatter(
            x=months,
            y=target_cumulative,
            mode="lines+markers",
            name="Target (With Reductions)",
            line=dict(color="#10B981", width=3, dash="solid"),
            marker=dict(size=9, symbol="diamond"),
            hovertemplate="Month: %{x}<br>Target: %{y:.1f} kg CO₂<extra></extra>",
        )
    )

    # Shaded difference area representing carbon saved
    fig.add_trace(
        go.Scatter(
            x=months + months[::-1],
            y=baseline_cumulative + target_cumulative[::-1],
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        xaxis=dict(
            gridcolor="#334155",
            zerolinecolor="#334155",
        ),
        yaxis=dict(
            title="Cumulative Emissions (kg CO₂)",
            gridcolor="#334155",
            zerolinecolor="#334155",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(t=50, b=40, l=10, r=10),
        height=350,
    )

    return fig
