def generate_recommendations(car_km, bike_km, bus_km, train_km, electricity_kwh, water_liters, food_habit, waste_kg):
    """
    Generates dynamic lifestyle recommendations based on user inputs.
    Returns a list of dictionaries containing recommendation details, potential annual savings, and colors.
    """
    recommendations = []
    
    # 1. Transportation Recommendation
    if car_km > 20:
        # Saving formula: replacement of 2 days/week of car travel with public transit (Bus)
        # Car emissions for 2 days/week: car_km * 2 * 52 * 0.192
        # Bus emissions for same: car_km * 2 * 52 * 0.105
        car_savings = car_km * 2 * 52 * (0.192 - 0.105)
        recommendations.append({
            "category": "Transit",
            "title": "Use Public Transportation",
            "description": f"By switching your daily car commute of {car_km:.1f} km to bus or train just 2 days a week, you'll reduce traffic congestion and save fuel.",
            "savings": car_savings,
            "type": "warning", # orange/yellow card
            "icon": "🚌"
        })
    elif car_km > 0 and car_km <= 20:
        # Suggest carpooling or cycling more
        car_savings = car_km * 1 * 52 * (0.192 - 0.103) # Replace 1 day of car with bike
        recommendations.append({
            "category": "Transit",
            "title": "Try Active Commuting",
            "description": "Consider biking or walking for short trips instead of driving. It's great for your health and has zero emissions.",
            "savings": car_savings,
            "type": "info",
            "icon": "🚲"
        })
        
    # 2. Electricity Recommendation
    if electricity_kwh > 300:
        # Saving formula: assume 15% reduction in electricity through energy-efficient measures
        electricity_savings = electricity_kwh * 0.15 * 12 * 0.82
        recommendations.append({
            "category": "Energy",
            "title": "Switch to energy-efficient appliances & LED lighting",
            "description": "Lighting and older appliances consume a large share of home power. Switching to LEDs and Energy Star appliances can save up to 15% on your monthly bill.",
            "savings": electricity_savings,
            "type": "danger", # red card
            "icon": "💡"
        })
    else:
        # Suggest vampire power cut
        electricity_savings = 10 * 12 * 0.82 # 10 kWh saved per month by unplugging devices
        recommendations.append({
            "category": "Energy",
            "title": "Unplug 'Vampire' Electronics",
            "description": "Electronics in standby mode still draw power. Plug them into smart power strips that shut down when not in use.",
            "savings": electricity_savings,
            "type": "info",
            "icon": "🔌"
        })

    # 3. Food Habits Recommendation
    if food_habit == "Heavy Meat Diet":
        # Saving formula: Go from heavy meat (7 kg/day) to vegetarian (3 kg/day) 1 day per week
        food_savings = (7 - 3) * 52
        recommendations.append({
            "category": "Diet",
            "title": "Reduce Meat Consumption (Meatless Mondays)",
            "description": "Animal agriculture is carbon-intensive. Reducing meat consumption by just 1 day per week (going vegetarian/vegan) significantly cuts food-related emissions.",
            "savings": food_savings,
            "type": "warning",
            "icon": "🥗"
        })
    elif food_habit == "Mixed Diet":
        # Go from mixed diet (5 kg/day) to vegan (2 kg/day) 1 day per week
        food_savings = (5 - 2) * 52
        recommendations.append({
            "category": "Diet",
            "title": "Incorporate More Plant-Based Meals",
            "description": "Increasing the share of whole grains, vegetables, and legumes in your diet reduces emissions, saves water, and improves wellness.",
            "savings": food_savings,
            "type": "info",
            "icon": "🌽"
        })
    elif food_habit in ["Vegetarian", "Vegan"]:
        recommendations.append({
            "category": "Diet",
            "title": "Sustain Your Plant-Based Journey!",
            "description": "Your diet choices prevent major greenhouse emissions and conserve forest land. Share your recipes to inspire others!",
            "savings": 0.0,
            "type": "success", # green card
            "icon": "🌱"
        })

    # 4. Waste Recommendation
    if waste_kg > 2.0:
        # Saving formula: Recyle/compost 40% of the waste
        waste_savings = waste_kg * 0.40 * 365 * 0.57
        recommendations.append({
            "category": "Waste",
            "title": "Practice Recycling and Composting",
            "description": f"Organic waste in landfills decomposes anaerobically, creating methane. Composting your organic waste and recycling plastics/paper can cut your landfill footprint by 40%.",
            "savings": waste_savings,
            "type": "danger",
            "icon": "♻️"
        })
    else:
        # General reduction suggestion
        waste_savings = waste_kg * 0.10 * 365 * 0.57
        recommendations.append({
            "category": "Waste",
            "title": "Reduce Single-Use Packaging",
            "description": "Try buying in bulk, carrying reusable bags, and refilling bottles to avoid synthetic packaging waste entirely.",
            "savings": waste_savings,
            "type": "info",
            "icon": "🛍️"
        })

    # 5. Water Recommendation
    if water_liters > 200:
        # Saving formula: save 20% water by low-flow and shorter showers
        water_savings = water_liters * 0.20 * 365 * 0.0003
        recommendations.append({
            "category": "Water",
            "title": "Optimize Water Usage",
            "description": "Install low-flow showerheads and aerators on faucets, and take shorter showers. Pumping and heating water uses significant energy.",
            "savings": water_savings,
            "type": "warning",
            "icon": "💧"
        })
        
    return recommendations

def render_recommendation_card(rec):
    """
    Returns an HTML representation of a recommendation card with modern responsive styling.
    """
    card_colors = {
        "success": {
            "border": "#10B981",
            "bg": "rgba(16, 185, 129, 0.1)",
            "badge": "#059669",
            "text": "#F8FAFC"
        },
        "info": {
            "border": "#3B82F6",
            "bg": "rgba(59, 130, 246, 0.1)",
            "badge": "#2563EB",
            "text": "#F8FAFC"
        },
        "warning": {
            "border": "#F59E0B",
            "bg": "rgba(245, 158, 11, 0.1)",
            "badge": "#D97706",
            "text": "#F8FAFC"
        },
        "danger": {
            "border": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.1)",
            "badge": "#DC2626",
            "text": "#F8FAFC"
        }
    }
    
    theme = card_colors.get(rec["type"], card_colors["info"])
    savings_badge = ""
    if rec["savings"] > 0:
        savings_badge = f'<span style="background-color: {theme["badge"]}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-left: 10px;">-{rec["savings"]:.1f} kg CO₂/yr</span>'
        
    html = f"""
    <div style="border-left: 5px solid {theme["border"]}; background-color: {theme["bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); transition: transform 0.2s ease-in-out;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 10px;">{rec["icon"]}</span>
                <strong style="color: {theme["text"]}; font-size: 1.05rem;">{rec["title"]}</strong>
            </div>
            <div>
                <span style="background-color: #334155; color: #E2E8F0; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; text-transform: uppercase;">{rec["category"]}</span>
                {savings_badge}
            </div>
        </div>
        <p style="color: #94A3B8; font-size: 0.9rem; margin: 0; line-height: 1.4;">{rec["description"]}</p>
    </div>
    """
    return html
