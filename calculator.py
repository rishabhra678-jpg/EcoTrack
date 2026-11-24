"""Carbon footprint calculation and classification engine for EcoTrack."""
from __future__ import annotations

import functools
import os
from typing import TypedDict

import pandas as pd

# Canonical emission factor defaults (kg CO2 per unit activity)
DEFAULT_FACTORS: dict[str, float] = {
    # Transport (kg CO2 / km)
    "Car": 0.192,
    "Bike": 0.103,
    "Bus": 0.105,
    "Train": 0.041,
    # Home Utilities
    "Grid": 0.82,
    "Electricity": 0.82,  # Alias
    "Tap": 0.0003,
    "Water": 0.0003,  # Alias
    "Trash": 0.57,
    "Waste": 0.57,  # Alias
    # Food (kg CO2 / day)
    "Vegan": 2.0,
    "Vegetarian": 3.0,
    "Mixed Diet": 5.0,
    "Heavy Meat Diet": 7.0,
}


class TransportEmissions(TypedDict):
    car: float
    bike: float
    bus: float
    train: float
    total_daily: float


class SingleComponentEmissions(TypedDict):
    total_daily: float


class TotalsEmissions(TypedDict):
    daily: float
    monthly: float
    annual: float


class FootprintResult(TypedDict):
    transport: TransportEmissions
    electricity: SingleComponentEmissions
    water: SingleComponentEmissions
    food: SingleComponentEmissions
    waste: SingleComponentEmissions
    totals: TotalsEmissions


class FootprintClassification(TypedDict):
    category: str
    badge: str
    color: str
    text_color: str
    description: str


def _coerce_non_negative(val: float | int | str | None, default: float = 0.0) -> float:
    """Safely coerce numerical input to a non-negative float."""
    if val is None:
        return default
    try:
        f_val = float(val)
        return max(0.0, f_val)
    except (ValueError, TypeError):
        return default


@functools.lru_cache(maxsize=1)
def load_emission_factors() -> dict[str, float]:
    """Load emission factors from CSV, caching in memory and falling back to verified defaults."""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "emission_factors.csv")
    factors = DEFAULT_FACTORS.copy()
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                activity = str(row["Activity"]).strip()
                factor = float(row["Factor"])
                factors[activity] = factor
                # Ensure alias compatibility
                if activity == "Grid":
                    factors["Electricity"] = factor
                elif activity == "Tap":
                    factors["Water"] = factor
                elif activity == "Trash":
                    factors["Waste"] = factor
        except Exception:
            pass  # Fall back to default dictionary if CSV parsing fails
    return factors


def calculate_footprint(
    car_km: float | int,
    bike_km: float | int,
    bus_km: float | int,
    train_km: float | int,
    electricity_kwh: float | int,
    water_liters: float | int,
    food_habit: str,
    waste_kg: float | int,
) -> FootprintResult:
    """Calculate carbon footprint for each category and aggregate into daily, monthly, and annual totals (kg CO2).

    Args:
        car_km: Daily car travel distance in kilometers.
        bike_km: Daily bike or e-bike travel in kilometers.
        bus_km: Daily public transit bus travel in kilometers.
        train_km: Daily rail/metro commute in kilometers.
        electricity_kwh: Monthly household electricity usage in kWh.
        water_liters: Personal daily water consumption in liters.
        food_habit: Dietary choice ('Vegan', 'Vegetarian', 'Mixed Diet', 'Heavy Meat Diet').
        waste_kg: Daily solid municipal waste in kilograms.

    Returns:
        Structured footprint dictionary broken down by source with summary totals.
    """
    factors = load_emission_factors()

    # Validate and sanitize inputs
    c_car = _coerce_non_negative(car_km)
    c_bike = _coerce_non_negative(bike_km)
    c_bus = _coerce_non_negative(bus_km)
    c_train = _coerce_non_negative(train_km)
    c_elec = _coerce_non_negative(electricity_kwh)
    c_water = _coerce_non_negative(water_liters)
    c_waste = _coerce_non_negative(waste_kg)
    c_food_habit = str(food_habit).strip() if food_habit else "Mixed Diet"

    # 1. Transport emission (daily in kg CO2/day)
    car_emission = c_car * factors.get("Car", DEFAULT_FACTORS["Car"])
    bike_emission = c_bike * factors.get("Bike", DEFAULT_FACTORS["Bike"])
    bus_emission = c_bus * factors.get("Bus", DEFAULT_FACTORS["Bus"])
    train_emission = c_train * factors.get("Train", DEFAULT_FACTORS["Train"])
    transport_daily = car_emission + bike_emission + bus_emission + train_emission

    # 2. Electricity emission (daily, converted from monthly input: kWh * Factor / 30)
    electricity_daily = (c_elec * factors.get("Grid", factors.get("Electricity", 0.82))) / 30.0

    # 3. Water emission (daily: liters * Factor)
    water_daily = c_water * factors.get("Tap", factors.get("Water", 0.0003))

    # 4. Food emission (daily, based on diet dropdown selection)
    food_daily = factors.get(c_food_habit, DEFAULT_FACTORS.get(c_food_habit, 5.0))

    # 5. Waste emission (daily: kg * Factor)
    waste_daily = c_waste * factors.get("Trash", factors.get("Waste", 0.57))

    # Aggregate totals
    daily_total = transport_daily + electricity_daily + water_daily + food_daily + waste_daily
    monthly_total = daily_total * 30.0
    annual_total = daily_total * 365.0

    return {
        "transport": {
            "car": car_emission,
            "bike": bike_emission,
            "bus": bus_emission,
            "train": train_emission,
            "total_daily": transport_daily,
        },
        "electricity": {
            "total_daily": electricity_daily,
        },
        "water": {
            "total_daily": water_daily,
        },
        "food": {
            "total_daily": food_daily,
        },
        "waste": {
            "total_daily": waste_daily,
        },
        "totals": {
            "daily": daily_total,
            "monthly": monthly_total,
            "annual": annual_total,
        },
    }


def calculate_sustainability_score(annual_footprint: float | int) -> float:
    """Calculate normalized sustainability score: 100 - (annual_footprint / 100), bounded between 0 and 100."""
    footprint = _coerce_non_negative(annual_footprint)
    score = 100.0 - (footprint / 100.0)
    return round(max(0.0, min(100.0, score)), 2)


def classify_footprint(daily_footprint: float | int) -> FootprintClassification:
    """Classify carbon footprint into tiered bands based on daily emissions.

    Bands:
        0 - 10 kg CO2/day   -> Eco Champion (Emerald)
        10 - 20 kg CO2/day  -> Sustainable Citizen (Green)
        20 - 40 kg CO2/day  -> Moderate Impact (Yellow)
        40 - 60 kg CO2/day  -> High Impact (Orange)
        60+ kg CO2/day      -> Critical Impact (Red)
    """
    footprint = _coerce_non_negative(daily_footprint)

    if footprint <= 10.0:
        return {
            "category": "Eco Champion",
            "badge": "🟢 Emerald",
            "color": "#10B981",
            "text_color": "#0F172A",
            "description": "Exemplary lifestyle! Your choices have a very low climate impact. Keep it up!",
        }
    if footprint <= 20.0:
        return {
            "category": "Sustainable Citizen",
            "badge": "🍀 Green",
            "color": "#34D399",
            "text_color": "#0F172A",
            "description": "Good job! You are living in a balanced way, but minor tweaks can make you an Eco Champion.",
        }
    if footprint <= 40.0:
        return {
            "category": "Moderate Impact",
            "badge": "🟡 Yellow",
            "color": "#FBBF24",
            "text_color": "#0F172A",
            "description": "Your carbon footprint is average, but there is substantial room for improvement.",
        }
    if footprint <= 60.0:
        return {
            "category": "High Impact",
            "badge": "🟠 Orange",
            "color": "#EA580C",
            "text_color": "#ffffff",
            "description": "Your lifestyle contributes significantly to carbon emissions. Consider adopting our recommendations.",
        }
    return {
        "category": "Critical Impact",
        "badge": "🔴 Red",
        "color": "#DC2626",
        "text_color": "#ffffff",
        "description": "High footprint warning! Immediate actions are recommended to reduce emissions across energy and transit.",
    }
