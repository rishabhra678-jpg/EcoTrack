"""Tests for EcoTrack carbon prediction engine (RandomForestRegressor)."""
import os
import pytest
import pandas as pd
from predictor import (
    generate_synthetic_data,
    train_and_save_model,
    predict_next_month,
    MODEL_PATH,
    FOOD_MAP
)


def test_generate_synthetic_data_structure():
    df = generate_synthetic_data(num_samples=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    expected_cols = [
        "car_km", "bike_km", "bus_km", "train_km",
        "electricity_kwh", "water_liters", "food_encoded", "waste_kg", "target"
    ]
    for col in expected_cols:
        assert col in df.columns
    # Check all targets are non-negative
    assert (df["target"] > 0).all()


def test_food_map_encoding():
    assert FOOD_MAP["Vegan"] == 0
    assert FOOD_MAP["Vegetarian"] == 1
    assert FOOD_MAP["Mixed Diet"] == 2
    assert FOOD_MAP["Heavy Meat Diet"] == 3


def test_predict_next_month_reasonable_range():
    prediction = predict_next_month(
        car_km=25.0,
        bike_km=2.0,
        bus_km=0.0,
        train_km=0.0,
        electricity_kwh=320,
        water_liters=150,
        food_habit="Mixed Diet",
        waste_kg=1.5
    )
    assert isinstance(prediction, (float, int))
    # A typical monthly footprint should fall between 50 and 2000 kg CO2/month
    assert 50.0 <= prediction <= 2000.0


def test_predict_next_month_with_unknown_diet_falls_back():
    # Unknown diet should gracefully default to Mixed Diet (code 2) without raising KeyError
    prediction = predict_next_month(
        car_km=20.0,
        bike_km=5.0,
        bus_km=10.0,
        train_km=15.0,
        electricity_kwh=200,
        water_liters=100,
        food_habit="UnknownFadDiet",
        waste_kg=1.0
    )
    assert prediction > 0


def test_train_and_save_model_creates_file():
    model = train_and_save_model()
    assert model is not None
    assert os.path.exists(MODEL_PATH)
    assert os.path.getsize(MODEL_PATH) > 1000
