import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# File path for the model
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "carbon_predictor.pkl")

# Food encoding map
FOOD_MAP = {
    "Vegan": 0,
    "Vegetarian": 1,
    "Mixed Diet": 2,
    "Heavy Meat Diet": 3
}

def generate_synthetic_data(num_samples=1000):
    """
    Generates a synthetic dataset of lifestyles and predicts next month's footprint
    with some seasonal/random variations to train a machine learning model.
    """
    np.random.seed(42)
    
    # Generate realistic features
    car_km = np.random.uniform(0, 80, num_samples)
    bike_km = np.random.uniform(0, 20, num_samples)
    bus_km = np.random.uniform(0, 40, num_samples)
    train_km = np.random.uniform(0, 60, num_samples)
    electricity_kwh = np.random.uniform(50, 600, num_samples)
    water_liters = np.random.uniform(30, 400, num_samples)
    food_encoded = np.random.choice([0, 1, 2, 3], num_samples) # 0: Vegan, 1: Veg, 2: Mixed, 3: Heavy Meat
    waste_kg = np.random.uniform(0.1, 4.0, num_samples)
    
    # Map food back to values for emission calculations
    food_factors = {0: 2.0, 1: 3.0, 2: 5.0, 3: 7.0}
    
    # Target calculation (current monthly baseline + next month changes)
    target_next_month = []
    
    for i in range(num_samples):
        # Current daily footprint
        transport = (car_km[i] * 0.192) + (bike_km[i] * 0.103) + (bus_km[i] * 0.105) + (train_km[i] * 0.041)
        electricity = (electricity_kwh[i] * 0.82) / 30.0
        water = water_liters[i] * 0.0003
        food = food_factors[food_encoded[i]]
        waste = waste_kg[i] * 0.57
        
        daily_total = transport + electricity + water + food + waste
        current_monthly = daily_total * 30.0
        
        # Simulate next month's carbon footprint:
        # 1. Seasonal variation (e.g. heating/cooling uses +/- 10% electricity)
        # 2. Random variation in travel/activities (+/- 5%)
        seasonal_factor = np.random.normal(0, 0.08)
        random_factor = np.random.normal(0, 0.04)
        
        # Calculate next month's carbon footprint
        next_month = current_monthly * (1.0 + seasonal_factor + random_factor)
        target_next_month.append(max(5.0, next_month)) # Ensure positive footprint
        
    # Create DataFrame
    data = pd.DataFrame({
        "car_km": car_km,
        "bike_km": bike_km,
        "bus_km": bus_km,
        "train_km": train_km,
        "electricity_kwh": electricity_kwh,
        "water_liters": water_liters,
        "food_encoded": food_encoded,
        "waste_kg": waste_kg,
        "target": target_next_month
    })
    
    return data

def train_and_save_model():
    """
    Trains the RandomForestRegressor and serializes it to models/carbon_predictor.pkl.
    """
    # Generate data
    df = generate_synthetic_data(1000)
    
    X = df.drop(columns=["target"])
    y = df["target"]
    
    # Train Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)
    
    # Ensure directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
        
    return model

def predict_next_month(car_km, bike_km, bus_km, train_km, electricity_kwh, water_liters, food_habit, waste_kg):
    """
    Loads the trained model and predicts next month's carbon footprint (in kg CO2)
    based on the current lifestyle input.
    """
    # Ensure model is trained and saved
    if not os.path.exists(MODEL_PATH):
        model = train_and_save_model()
    else:
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
        except Exception:
            # Re-train if load fails
            model = train_and_save_model()
            
    # Encode food habit
    food_encoded = FOOD_MAP.get(food_habit, 2) # Default to Mixed Diet (2) if not matched
    
    # Create feature dataframe
    features = pd.DataFrame([{
        "car_km": car_km,
        "bike_km": bike_km,
        "bus_km": bus_km,
        "train_km": train_km,
        "electricity_kwh": electricity_kwh,
        "water_liters": water_liters,
        "food_encoded": food_encoded,
        "waste_kg": waste_kg
    }])
    
    # Predict
    predicted_footprint = model.predict(features)[0]
    return predicted_footprint
