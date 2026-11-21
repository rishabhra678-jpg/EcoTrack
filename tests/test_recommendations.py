"""Tests for EcoTrack personalized recommendation generation."""
import pytest
from recommendations import generate_recommendations, render_recommendation_card


def test_generate_recommendations_high_car():
    recs = generate_recommendations(
        car_km=40.0,
        bike_km=0.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=200,
        water_liters=100,
        food_habit="Mixed Diet",
        waste_kg=1.0
    )
    categories = [r["category"] for r in recs]
    assert "Transit" in categories
    transit_rec = next(r for r in recs if r["category"] == "Transit")
    assert transit_rec["savings"] > 0
    assert "Public Transportation" in transit_rec["title"]


def test_generate_recommendations_low_car():
    recs = generate_recommendations(
        car_km=10.0,
        bike_km=5.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=200,
        water_liters=100,
        food_habit="Mixed Diet",
        waste_kg=1.0
    )
    transit_rec = next(r for r in recs if r["category"] == "Transit")
    assert "Active Commuting" in transit_rec["title"]


def test_generate_recommendations_zero_car():
    recs = generate_recommendations(
        car_km=0.0,
        bike_km=10.0,
        bus_km=10.0,
        train_km=10.0,
        electricity_kwh=200,
        water_liters=100,
        food_habit="Vegetarian",
        waste_kg=1.0
    )
    # When car_km is 0, no car-replacement recommendation is added
    assert not any(r["title"] == "Use Public Transportation" for r in recs)


def test_generate_recommendations_high_electricity():
    recs = generate_recommendations(
        car_km=0.0,
        bike_km=0.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=500,
        water_liters=100,
        food_habit="Vegetarian",
        waste_kg=1.0
    )
    energy_rec = next(r for r in recs if r["category"] == "Energy")
    assert energy_rec["type"] == "danger"
    assert energy_rec["savings"] > 0


def test_generate_recommendations_diet_variants():
    # Heavy Meat Diet
    recs_meat = generate_recommendations(0, 0, 0, 0, 100, 100, "Heavy Meat Diet", 1.0)
    diet_meat = next(r for r in recs_meat if r["category"] == "Diet")
    assert "Meatless" in diet_meat["title"]
    assert diet_meat["savings"] > 0

    # Vegan Diet
    recs_vegan = generate_recommendations(0, 0, 0, 0, 100, 100, "Vegan", 1.0)
    diet_vegan = next(r for r in recs_vegan if r["category"] == "Diet")
    assert diet_vegan["type"] == "success"
    assert diet_vegan["savings"] == 0.0


def test_render_recommendation_card_contains_accessibility_attributes():
    sample_rec = {
        "category": "Transit",
        "title": "Use Public Transportation",
        "description": "Switching your commute 2 days a week saves fuel.",
        "savings": 150.5,
        "type": "warning",
        "icon": "🚌"
    }
    html = render_recommendation_card(sample_rec)
    assert 'role="region"' in html
    assert 'aria-label=' in html
    assert 'Transit' in html
    assert '150.5' in html
    assert '🚌' in html
