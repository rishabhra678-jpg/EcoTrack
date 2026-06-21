import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Standard color scheme for categories
CATEGORY_COLORS = {
    "Transport": "#3B82F6",    # Blue
    "Electricity": "#F59E0B",  # Amber/Yellow
    "Food": "#10B981",         # Emerald Green
    "Water": "#06B6D4",        # Cyan
    "Waste": "#EF4444"         # Red
}

def create_donut_chart(emissions_dict):
    """
    Creates a Plotly donut chart showing the percentage contribution of each source.
    """
    labels = ["Transport", "Electricity", "Food", "Water", "Waste"]
    values = [
        emissions_dict["transport"]["total_daily"],
        emissions_dict["electricity"]["total_daily"],
        emissions_dict["food"]["total_daily"],
        emissions_dict["water"]["total_daily"],
        emissions_dict["waste"]["total_daily"]
    ]
    
    # Filter out sources with 0 emissions to keep the chart clean
    filtered_labels = []
    filtered_values = []
    for label, val in zip(labels, values):
        if val > 0:
            filtered_labels.append(label)
            filtered_values.append(val)
            
    colors = [CATEGORY_COLORS[label] for label in filtered_labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels,
        values=filtered_values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='#1E293B', width=2)),
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Emissions: %{value:.2f} kg CO₂/day<br>Share: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F8FAFC', size=12),
        margin=dict(t=10, b=10, l=10, r=10),
        height=320
    )
    
    return fig

def create_bar_chart(emissions_dict):
    """
    Creates a horizontal bar chart comparing emissions from different sources.
    """
    categories = ["Transport", "Electricity", "Food", "Water", "Waste"]
    values = [
        emissions_dict["transport"]["total_daily"],
        emissions_dict["electricity"]["total_daily"],
        emissions_dict["food"]["total_daily"],
        emissions_dict["water"]["total_daily"],
        emissions_dict["waste"]["total_daily"]
    ]
    
    colors = [CATEGORY_COLORS[cat] for cat in categories]
    
    fig = go.Figure(data=[go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#1E293B', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Emissions: %{x:.2f} kg CO₂/day<extra></extra>'
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F8FAFC'),
        xaxis=dict(
            title="Emissions (kg CO₂ / day)",
            gridcolor='#334155',
            zerolinecolor='#334155',
            title_font=dict(size=11)
        ),
        yaxis=dict(
            title="",
            autorange="reversed" # Read top to bottom
        ),
        margin=dict(t=10, b=40, l=10, r=10),
        height=320
    )
    
    return fig

def create_projection_chart(monthly_emissions, annual_savings):
    """
    Creates a line chart projecting cumulative emissions over 12 months.
    Compares the baseline (no change) vs. target (adopting recommendations).
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    monthly_savings = annual_savings / 12.0
    
    baseline_cumulative = []
    target_cumulative = []
    
    baseline_sum = 0
    target_sum = 0
    
    for i in range(12):
        baseline_sum += monthly_emissions
        # Target sum accumulates monthly footprint minus potential savings (non-negative)
        target_sum += max(0.0, monthly_emissions - monthly_savings)
        
        baseline_cumulative.append(baseline_sum)
        target_cumulative.append(target_sum)
        
    fig = go.Figure()
    
    # Baseline line
    fig.add_trace(go.Scatter(
        x=months,
        y=baseline_cumulative,
        mode='lines+markers',
        name='Baseline (No Changes)',
        line=dict(color='#EF4444', width=3, dash='dash'),
        marker=dict(size=6),
        hovertemplate='Month: %{x}<br>Baseline: %{y:.1f} kg CO₂<extra></extra>'
    ))
    
    # Target line (savings applied)
    fig.add_trace(go.Scatter(
        x=months,
        y=target_cumulative,
        mode='lines+markers',
        name='Target (With Reductions)',
        line=dict(color='#10B981', width=4),
        marker=dict(size=8),
        hovertemplate='Month: %{x}<br>Target: %{y:.1f} kg CO₂<extra></extra>'
    ))
    
    # Shade the difference area representing carbon saved
    fig.add_trace(go.Scatter(
        x=months + months[::-1],
        y=baseline_cumulative + target_cumulative[::-1],
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F8FAFC'),
        xaxis=dict(
            gridcolor='#334155',
            zerolinecolor='#334155'
        ),
        yaxis=dict(
            title="Cumulative Emissions (kg CO₂)",
            gridcolor='#334155',
            zerolinecolor='#334155'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, b=40, l=10, r=10),
        height=350
    )
    
    return fig
