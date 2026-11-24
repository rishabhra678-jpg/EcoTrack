"""Actionable carbon reduction recommendation engine and card renderer for EcoTrack."""
from __future__ import annotations

from typing import Any, Literal, TypedDict

from calculator import DEFAULT_FACTORS


class Recommendation(TypedDict):
    category: str
    title: str
    description: str
    savings: float
    type: Literal["success", "info", "warning", "danger"]
    icon: str


def _coerce_non_negative(val: float | int | str | None, default: float = 0.0) -> float:
    """Coerce numerical values to non-negative floats."""
    if val is None:
        return default
    try:
        return max(0.0, float(val))
    except (ValueError, TypeError):
        return default


def generate_recommendations(
    car_km: float | int,
    bike_km: float | int,
    bus_km: float | int,
    train_km: float | int,
    electricity_kwh: float | int,
    water_liters: float | int,
    food_habit: str,
    waste_kg: float | int,
) -> list[Recommendation]:
    """Generate dynamic, tailored lifestyle recommendations and estimated annual carbon savings.

    Args:
        car_km: Daily car travel in km.
        bike_km: Daily bike travel in km.
        bus_km: Daily bus travel in km.
        train_km: Daily train travel in km.
        electricity_kwh: Monthly electricity consumption in kWh.
        water_liters: Daily water usage in liters.
        food_habit: Current primary diet selection.
        waste_kg: Daily waste generated in kg.

    Returns:
        List of recommendation dictionaries detailing category, advice, savings, and card theme.
    """
    c_car = _coerce_non_negative(car_km)
    c_elec = _coerce_non_negative(electricity_kwh)
    c_water = _coerce_non_negative(water_liters)
    c_waste = _coerce_non_negative(waste_kg)
    diet = str(food_habit).strip() if food_habit else "Mixed Diet"

    recommendations: list[Recommendation] = []

    car_factor = DEFAULT_FACTORS.get("Car", 0.192)
    bike_factor = DEFAULT_FACTORS.get("Bike", 0.103)
    bus_factor = DEFAULT_FACTORS.get("Bus", 0.105)
    grid_factor = DEFAULT_FACTORS.get("Grid", 0.82)
    tap_factor = DEFAULT_FACTORS.get("Tap", 0.0003)
    waste_factor = DEFAULT_FACTORS.get("Trash", 0.57)

    # 1. Transportation Recommendation
    if c_car > 20.0:
        # Saving formula: replacing 2 days/week of car travel with bus
        car_savings = c_car * 2.0 * 52.0 * (car_factor - bus_factor)
        recommendations.append({
            "category": "Transit",
            "title": "Use Public Transportation",
            "description": (
                f"By switching your daily car commute of {c_car:.1f} km to bus or train just 2 days a week, "
                "you'll reduce traffic congestion and save fuel."
            ),
            "savings": car_savings,
            "type": "warning",
            "icon": "🚌",
        })
    elif 0.0 < c_car <= 20.0:
        # Replace 1 day of car driving with active transit (bicycle)
        car_savings = c_car * 1.0 * 52.0 * (car_factor - bike_factor)
        recommendations.append({
            "category": "Transit",
            "title": "Try Active Commuting",
            "description": (
                "Consider biking or walking for short trips instead of driving. "
                "It's great for your health and has zero emissions."
            ),
            "savings": car_savings,
            "type": "info",
            "icon": "🚲",
        })

    # 2. Electricity Recommendation
    if c_elec > 300.0:
        # 15% reduction in electricity through energy-efficient measures
        electricity_savings = c_elec * 0.15 * 12.0 * grid_factor
        recommendations.append({
            "category": "Energy",
            "title": "Switch to energy-efficient appliances & LED lighting",
            "description": (
                "Lighting and older appliances consume a large share of home power. "
                "Switching to LEDs and Energy Star appliances can save up to 15% on your monthly bill."
            ),
            "savings": electricity_savings,
            "type": "danger",
            "icon": "💡",
        })
    else:
        # Vampire power cut (~10 kWh/month)
        electricity_savings = 10.0 * 12.0 * grid_factor
        recommendations.append({
            "category": "Energy",
            "title": "Unplug 'Vampire' Electronics",
            "description": (
                "Electronics in standby mode still draw power. "
                "Plug them into smart power strips that shut down when not in use."
            ),
            "savings": electricity_savings,
            "type": "info",
            "icon": "🔌",
        })

    # 3. Food Habits Recommendation
    if diet == "Heavy Meat Diet":
        # Shift 1 day/week from heavy meat (7 kg/day) to vegetarian (3 kg/day)
        food_savings = (DEFAULT_FACTORS.get("Heavy Meat Diet", 7.0) - DEFAULT_FACTORS.get("Vegetarian", 3.0)) * 52.0
        recommendations.append({
            "category": "Diet",
            "title": "Reduce Meat Consumption (Meatless Mondays)",
            "description": (
                "Animal agriculture is carbon-intensive. Reducing meat consumption by just 1 day per week "
                "(going vegetarian/vegan) significantly cuts food-related emissions."
            ),
            "savings": food_savings,
            "type": "warning",
            "icon": "🥗",
        })
    elif diet == "Mixed Diet":
        # Shift 1 day/week from mixed diet (5 kg/day) to vegan (2 kg/day)
        food_savings = (DEFAULT_FACTORS.get("Mixed Diet", 5.0) - DEFAULT_FACTORS.get("Vegan", 2.0)) * 52.0
        recommendations.append({
            "category": "Diet",
            "title": "Incorporate More Plant-Based Meals",
            "description": (
                "Increasing the share of whole grains, vegetables, and legumes in your diet reduces emissions, "
                "saves water, and improves wellness."
            ),
            "savings": food_savings,
            "type": "info",
            "icon": "🌽",
        })
    elif diet in ("Vegetarian", "Vegan"):
        recommendations.append({
            "category": "Diet",
            "title": "Sustain Your Plant-Based Journey!",
            "description": (
                "Your diet choices prevent major greenhouse emissions and conserve forest land. "
                "Share your recipes to inspire others!"
            ),
            "savings": 0.0,
            "type": "success",
            "icon": "🌱",
        })

    # 4. Waste Recommendation
    if c_waste > 2.0:
        # Recycle or compost 40% of solid waste
        waste_savings = c_waste * 0.40 * 365.0 * waste_factor
        recommendations.append({
            "category": "Waste",
            "title": "Practice Recycling and Composting",
            "description": (
                "Organic waste in landfills decomposes anaerobically, creating methane. "
                "Composting your organic waste and recycling plastics/paper can cut your landfill footprint by 40%."
            ),
            "savings": waste_savings,
            "type": "danger",
            "icon": "♻️",
        })
    else:
        # General packaging reduction (10%)
        waste_savings = c_waste * 0.10 * 365.0 * waste_factor
        recommendations.append({
            "category": "Waste",
            "title": "Reduce Single-Use Packaging",
            "description": (
                "Try buying in bulk, carrying reusable bags, and refilling bottles to avoid synthetic packaging waste entirely."
            ),
            "savings": waste_savings,
            "type": "info",
            "icon": "🛍️",
        })

    # 5. Water Recommendation
    if c_water > 200.0:
        # 20% water saving through aerators and shorter showers
        water_savings = c_water * 0.20 * 365.0 * tap_factor
        recommendations.append({
            "category": "Water",
            "title": "Optimize Water Usage",
            "description": (
                "Install low-flow showerheads and aerators on faucets, and take shorter showers. "
                "Pumping and heating water uses significant energy."
            ),
            "savings": water_savings,
            "type": "warning",
            "icon": "💧",
        })

    return recommendations


def render_recommendation_card(rec: Recommendation | dict[str, Any]) -> str:
    """Return an accessible, WCAG 2.2 AA compliant HTML card component for a recommendation."""
    card_colors = {
        "success": {
            "border": "#10B981",
            "bg": "rgba(16, 185, 129, 0.12)",
            "badge": "#059669",
            "text": "#F8FAFC",
        },
        "info": {
            "border": "#3B82F6",
            "bg": "rgba(59, 130, 246, 0.12)",
            "badge": "#2563EB",
            "text": "#F8FAFC",
        },
        "warning": {
            "border": "#F59E0B",
            "bg": "rgba(245, 158, 11, 0.12)",
            "badge": "#B45309",
            "text": "#F8FAFC",
        },
        "danger": {
            "border": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.12)",
            "badge": "#DC2626",
            "text": "#F8FAFC",
        },
    }

    theme = card_colors.get(rec["type"], card_colors["info"])
    savings_badge = ""
    if rec["savings"] > 0:
        savings_badge = (
            f'<span style="background-color: {theme["badge"]}; color: white; padding: 2px 8px; '
            f'border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-left: 10px;" '
            f'aria-label="Estimated annual savings: {rec["savings"]:.1f} kilograms of CO2">'
            f'-{rec["savings"]:.1f} kg CO₂/yr</span>'
        )

    return f"""
    <div role="region" aria-label="{rec['category']} recommendation: {rec['title']}" style="border-left: 5px solid {theme["border"]}; background-color: {theme["bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); transition: transform 0.2s ease-in-out;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 10px;" aria-hidden="true">{rec["icon"]}</span>
                <strong style="color: {theme["text"]}; font-size: 1.05rem;">{rec["title"]}</strong>
            </div>
            <div>
                {savings_badge}
            </div>
        </div>
        <p style="color: #CBD5E1; font-size: 0.95rem; margin: 0; line-height: 1.5;">{rec["description"]}</p>
    </div>
    """
