"""Tests for EcoTrack carbon footprint calculator logic."""
import pytest
from calculator import (
    load_emission_factors,
    calculate_footprint,
    calculate_sustainability_score,
    classify_footprint,
    DEFAULT_FACTORS
)


def test_load_emission_factors_returns_dict():
    factors = load_emission_factors()
    assert isinstance(factors, dict)
    assert "Car" in factors
    assert "Electricity" in factors or "Grid" in factors
    assert factors["Car"] == pytest.approx(0.192, rel=1e-2)


def test_calculate_footprint_standard_values():
    result = calculate_footprint(
        car_km=25.0,
        bike_km=2.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=320,
        water_liters=150,
        food_habit="Mixed Diet",
        waste_kg=1.5
    )
    assert "transport" in result
    assert "electricity" in result
    assert "water" in result
    assert "food" in result
    assert "waste" in result
    assert "totals" in result

    totals = result["totals"]
    assert totals["daily"] > 0
    assert totals["monthly"] == pytest.approx(totals["daily"] * 30.0)
    assert totals["annual"] == pytest.approx(totals["daily"] * 365.0)


def test_calculate_footprint_zero_values():
    result = calculate_footprint(
        car_km=0.0,
        bike_km=0.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=0,
        water_liters=0,
        food_habit="Vegan",
        waste_kg=0.0
    )
    # Vegan diet has minimum daily emission factor
    totals = result["totals"]
    assert totals["daily"] >= 0
    assert result["transport"]["total_daily"] == 0.0
    assert result["electricity"]["total_daily"] == 0.0
    assert result["water"]["total_daily"] == 0.0
    assert result["waste"]["total_daily"] == 0.0


def test_calculate_footprint_all_diets():
    diets = ["Vegan", "Vegetarian", "Mixed Diet", "Heavy Meat Diet"]
    emissions_list = []
    for d in diets:
        res = calculate_footprint(10, 0, 0, 0, 100, 50, d, 1.0)
        emissions_list.append(res["food"]["total_daily"])

    # Verify monotonic increase: Vegan < Vegetarian < Mixed < Heavy Meat
    assert emissions_list[0] <= emissions_list[1] <= emissions_list[2] <= emissions_list[3]


def test_calculate_sustainability_score_bounds():
    # Very small annual footprint should give near 100
    assert calculate_sustainability_score(0.0) == 100.0
    assert calculate_sustainability_score(500.0) == 95.0
    # Very large footprint should not drop below 0
    assert calculate_sustainability_score(50000.0) == 0.0
    # Boundary tests
    score_mid = calculate_sustainability_score(5000.0)
    assert 0.0 <= score_mid <= 100.0


def test_classify_footprint_all_tiers():
    # 0-10 -> Eco Champion
    c1 = classify_footprint(5.0)
    assert c1["category"] == "Eco Champion"
    assert "color" in c1 and "badge" in c1 and "text_color" in c1

    # 10.01 - 20 -> Sustainable Citizen
    c2 = classify_footprint(15.0)
    assert c2["category"] == "Sustainable Citizen"

    # 20.01 - 40 -> Moderate Impact
    c3 = classify_footprint(30.0)
    assert c3["category"] == "Moderate Impact"

    # 40.01 - 60 -> High Impact
    c4 = classify_footprint(50.0)
    assert c4["category"] == "High Impact"

    # 60+ -> Critical Impact
    c5 = classify_footprint(80.0)
    assert c5["category"] == "Critical Impact"


def test_classify_footprint_edge_thresholds():
    assert classify_footprint(10.0)["category"] == "Eco Champion"
    assert classify_footprint(10.001)["category"] == "Sustainable Citizen"
    assert classify_footprint(20.0)["category"] == "Sustainable Citizen"
    assert classify_footprint(20.001)["category"] == "Moderate Impact"
    assert classify_footprint(40.0)["category"] == "Moderate Impact"
    assert classify_footprint(40.001)["category"] == "High Impact"
    assert classify_footprint(60.0)["category"] == "High Impact"
    assert classify_footprint(60.001)["category"] == "Critical Impact"
