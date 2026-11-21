import os
import pandas as pd

# Default emission factors (fallbacks if CSV is missing)
DEFAULT_FACTORS = {
    "Car": 0.192,
    "Bike": 0.103,
    "Bus": 0.105,
    "Train": 0.041,
    "Electricity": 0.82,
    "Water": 0.0003,
    "Waste": 0.57,
    "Vegan": 2.0,
    "Vegetarian": 3.0,
    "Mixed Diet": 5.0,
    "Heavy Meat Diet": 7.0
}

def load_emission_factors():
    """Loads emission factors from CSV, falling back to defaults if not found."""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "emission_factors.csv")
    factors = DEFAULT_FACTORS.copy()
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                activity = row["Activity"]
                factor = float(row["Factor"])
                factors[activity] = factor
        except Exception:
            pass  # Fall back to default dictionary if CSV parsing fails
    return factors

def calculate_footprint(car_km, bike_km, bus_km, train_km, electricity_kwh, water_liters, food_habit, waste_kg):
    """
    Calculates carbon footprint for different components and returns daily, monthly, and annual totals (kg CO2).
    """
    factors = load_emission_factors()
    
    # 1. Transport emission (daily in kg CO2/day)
    car_emission = car_km * factors.get("Car", 0.192)
    bike_emission = bike_km * factors.get("Bike", 0.103)
    bus_emission = bus_km * factors.get("Bus", 0.105)
    train_emission = train_km * factors.get("Train", 0.041)
    transport_daily = car_emission + bike_emission + bus_emission + train_emission
    
    # 2. Electricity emission (daily, converted from monthly input: kWh * Factor / 30)
    electricity_daily = (electricity_kwh * factors.get("Grid", 0.82)) / 30.0
    
    # 3. Water emission (daily: liters * Factor)
    water_daily = water_liters * factors.get("Tap", 0.0003)
    
    # 4. Food emission (daily, based on diet dropdown selection)
    food_factor_key = food_habit  # Should match activity names in CSV e.g., 'Vegan', 'Vegetarian', 'Mixed Diet', 'Heavy Meat Diet'
    food_daily = factors.get(food_factor_key, 5.0)
    
    # 5. Waste emission (daily: kg * Factor)
    waste_daily = waste_kg * factors.get("Trash", 0.57)
    
    # Calculate daily total
    daily_total = transport_daily + electricity_daily + water_daily + food_daily + waste_daily
    
    # Extrapolate
    monthly_total = daily_total * 30.0
    annual_total = daily_total * 365.0
    
    return {
        "transport": {
            "car": car_emission,
            "bike": bike_emission,
            "bus": bus_emission,
            "train": train_emission,
            "total_daily": transport_daily
        },
        "electricity": {
            "total_daily": electricity_daily
        },
        "water": {
            "total_daily": water_daily
        },
        "food": {
            "total_daily": food_daily
        },
        "waste": {
            "total_daily": waste_daily
        },
        "totals": {
            "daily": daily_total,
            "monthly": monthly_total,
            "annual": annual_total
        }
    }

def calculate_sustainability_score(annual_footprint):
    """
    Calculates sustainability score: 100 - (annual_footprint / 100), bounded between 0 and 100.
    """
    score = 100.0 - (annual_footprint / 100.0)
    return max(0.0, min(100.0, score))

def classify_footprint(daily_footprint):
    """
    Classifies carbon footprint based on daily emissions.
    0-10      -> Eco Champion
    10-20     -> Sustainable Citizen
    20-40     -> Moderate Impact
    40-60     -> High Impact
    60+       -> Critical Impact
    """
    if daily_footprint <= 10.0:
        return {
            "category": "Eco Champion",
            "badge": "🟢 Emerald",
            "color": "#10B981",
            "text_color": "#0F172A",
            "description": "Exemplary lifestyle! Your choices have a very low climate impact. Keep it up!"
        }
    elif daily_footprint <= 20.0:
        return {
            "category": "Sustainable Citizen",
            "badge": "🍀 Green",
            "color": "#34D399",
            "text_color": "#0F172A",
            "description": "Good job! You are living in a balanced way, but minor tweaks can make you an Eco Champion."
        }
    elif daily_footprint <= 40.0:
        return {
            "category": "Moderate Impact",
            "badge": "🟡 Yellow",
            "color": "#FBBF24",
            "text_color": "#0F172A",
            "description": "Your carbon footprint is average, but there is substantial room for improvement."
        }
    elif daily_footprint <= 60.0:
        return {
            "category": "High Impact",
            "badge": "🟠 Orange",
            "color": "#EA580C",
            "text_color": "#ffffff",
            "description": "Your lifestyle contributes significantly to carbon emissions. Consider adopting our recommendations."
        }
    else:
        return {
            "category": "Critical Impact",
            "badge": "🔴 Red",
            "color": "#DC2626",
            "text_color": "#ffffff",
            "description": "High footprint warning! Immediate actions are recommended to reduce emissions across energy and transit."
        }
