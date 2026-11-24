"""Machine learning carbon prediction module for EcoTrack using Random Forest."""
from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from calculator import DEFAULT_FACTORS

# Model file storage location
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "carbon_predictor.pkl")

# Categorical diet encoding map
FOOD_MAP: dict[str, int] = {
    "Vegan": 0,
    "Vegetarian": 1,
    "Mixed Diet": 2,
    "Heavy Meat Diet": 3,
}

_REVERSE_FOOD_FACTORS: dict[int, float] = {
    0: DEFAULT_FACTORS.get("Vegan", 2.0),
    1: DEFAULT_FACTORS.get("Vegetarian", 3.0),
    2: DEFAULT_FACTORS.get("Mixed Diet", 5.0),
    3: DEFAULT_FACTORS.get("Heavy Meat Diet", 7.0),
}

# In-memory model cache to avoid repeated disk unpickling
_CACHED_MODEL: Any | None = None


def _coerce_non_negative(val: float | int | str | None, default: float = 0.0) -> float:
    """Coerce numerical values to non-negative floats."""
    if val is None:
        return default
    try:
        return max(0.0, float(val))
    except (ValueError, TypeError):
        return default


def generate_synthetic_data(num_samples: int = 1000) -> pd.DataFrame:
    """Generate a synthetic dataset of lifestyles and simulated next-month footprints.

    Incorporates realistic consumption bounds along with simulated seasonal variance
    (e.g., HVAC heating/cooling) and stochastic monthly habits to train the regressor.
    """
    np.random.seed(42)

    # Generate synthetic activity features within realistic bounds
    car_km = np.random.uniform(0, 80, num_samples)
    bike_km = np.random.uniform(0, 20, num_samples)
    bus_km = np.random.uniform(0, 40, num_samples)
    train_km = np.random.uniform(0, 60, num_samples)
    electricity_kwh = np.random.uniform(50, 600, num_samples)
    water_liters = np.random.uniform(30, 400, num_samples)
    food_encoded = np.random.choice([0, 1, 2, 3], num_samples)
    waste_kg = np.random.uniform(0.1, 4.0, num_samples)

    target_next_month: list[float] = []

    car_factor = DEFAULT_FACTORS.get("Car", 0.192)
    bike_factor = DEFAULT_FACTORS.get("Bike", 0.103)
    bus_factor = DEFAULT_FACTORS.get("Bus", 0.105)
    train_factor = DEFAULT_FACTORS.get("Train", 0.041)
    grid_factor = DEFAULT_FACTORS.get("Grid", 0.82)
    tap_factor = DEFAULT_FACTORS.get("Tap", 0.0003)
    waste_factor = DEFAULT_FACTORS.get("Trash", 0.57)

    for i in range(num_samples):
        # Baseline daily emissions calculation
        transport = (
            (car_km[i] * car_factor)
            + (bike_km[i] * bike_factor)
            + (bus_km[i] * bus_factor)
            + (train_km[i] * train_factor)
        )
        electricity = (electricity_kwh[i] * grid_factor) / 30.0
        water = water_liters[i] * tap_factor
        food = _REVERSE_FOOD_FACTORS.get(int(food_encoded[i]), 5.0)
        waste = waste_kg[i] * waste_factor

        daily_total = transport + electricity + water + food + waste
        current_monthly = daily_total * 30.0

        # Simulate seasonal variation (±8%) and stochastic activity variation (±4%)
        seasonal_factor = np.random.normal(0, 0.08)
        random_factor = np.random.normal(0, 0.04)

        next_month = current_monthly * (1.0 + seasonal_factor + random_factor)
        target_next_month.append(max(5.0, float(next_month)))

    return pd.DataFrame({
        "car_km": car_km,
        "bike_km": bike_km,
        "bus_km": bus_km,
        "train_km": train_km,
        "electricity_kwh": electricity_kwh,
        "water_liters": water_liters,
        "food_encoded": food_encoded,
        "waste_kg": waste_kg,
        "target": target_next_month,
    })


def train_and_save_model() -> RandomForestRegressor:
    """Train the RandomForestRegressor on synthetic lifestyle data and serialize to disk."""
    global _CACHED_MODEL
    df = generate_synthetic_data(1000)

    X = df.drop(columns=["target"])
    y = df["target"]

    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    _CACHED_MODEL = model
    return model


def _get_model() -> Any:
    """Retrieve the model from memory cache or load from disk, training if missing."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    if not os.path.exists(MODEL_PATH):
        return train_and_save_model()

    try:
        with open(MODEL_PATH, "rb") as f:
            _CACHED_MODEL = pickle.load(f)
        return _CACHED_MODEL
    except Exception:
        return train_and_save_model()


def predict_next_month(
    car_km: float | int,
    bike_km: float | int,
    bus_km: float | int,
    train_km: float | int,
    electricity_kwh: float | int,
    water_liters: float | int,
    food_habit: str,
    waste_kg: float | int,
) -> float:
    """Predict next month's carbon footprint (in kg CO2) based on current inputs and learned variations."""
    model = _get_model()

    # Sanitize and validate inputs
    c_car = _coerce_non_negative(car_km)
    c_bike = _coerce_non_negative(bike_km)
    c_bus = _coerce_non_negative(bus_km)
    c_train = _coerce_non_negative(train_km)
    c_elec = _coerce_non_negative(electricity_kwh)
    c_water = _coerce_non_negative(water_liters)
    c_waste = _coerce_non_negative(waste_kg)

    clean_diet = str(food_habit).strip() if food_habit else "Mixed Diet"
    food_encoded = FOOD_MAP.get(clean_diet, 2)  # Default to Mixed Diet (2) if unrecognized

    features = pd.DataFrame([{
        "car_km": c_car,
        "bike_km": c_bike,
        "bus_km": c_bus,
        "train_km": c_train,
        "electricity_kwh": c_elec,
        "water_liters": c_water,
        "food_encoded": food_encoded,
        "waste_kg": c_waste,
    }])

    prediction = float(model.predict(features)[0])
    return round(prediction, 2)
