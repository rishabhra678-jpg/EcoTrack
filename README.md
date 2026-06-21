# EcoTrack: Carbon Footprint Awareness Platform 🌿

EcoTrack is a modern, responsive, and data-driven Python Streamlit web application that empowers individuals to calculate, visualize, reduce, and predict their personal carbon footprint based on daily lifestyle choices.

---

## Key Features

1. **Carbon Footprint Calculator**: Computes emissions for transportation, utility electricity, water usage, diet habits, and landfill waste generation.
2. **Interactive Visualizations**: Generates clean, responsive Plotly charts, including:
   - **Donut Chart**: Relative emissions share by source category.
   - **Horizontal Bar Chart**: Comparison of category daily carbon footprint.
   - **12-Month Accumulation Line Chart**: Visualizes progress when carbon reduction goals are met.
3. **AI Predictor (Machine Learning)**: Leverages a `RandomForestRegressor` trained on simulated profiles to project next month's carbon footprint, adjusting for weather seasonality and consumption variance.
4. **Target Goals & Progress Tracking**: Set weekly/monthly reductions in travel, energy, or waste, and watch your carbon offsets, equivalent trees planted, and smartphone charges compute live.
5. **Session History Log**: Stores calculation logs dynamically as you adjust inputs, allowing interactive historical comparison.
6. **Worksheet CSV Export**: Export detailed carbon footprint inputs and calculations in one click.
7. **Educational Science Center**: Detailed scientific references of formulas and factors derived from IPCC & EPA parameters.

---

## Directory Structure

```
EcoTrack/
│
├── .streamlit/
│   └── config.toml          # Custom dark-green CSS colors and configs
│
├── data/
│   └── emission_factors.csv # Data-driven activity emission constants
│
├── models/
│   └── carbon_predictor.pkl # [Auto-generated] Serialized RandomForest model
│
├── assets/
│   └── logo.png             # Application logo
│
├── app.py                   # Main Streamlit layout & UI orchestration
├── calculator.py            # Footprint computation and scoring algorithms
├── recommendations.py       # Recommendation engine with custom HTML cards
├── visualizations.py        # Graph formatting utilizing Plotly
├── predictor.py             # Machine learning training & prediction routines
├── utils.py                 # Styling sheet injections & file export helpers
│
├── requirements.txt         # Project dependencies
├── README.md                # Documentation guide
└── .gitignore               # Ignored cache/pickle definitions
```

---

## Installation & Setup

Ensure you have Python 3.8+ installed on your system.

### 1. Clone the repository and navigate to the project directory:
```bash
cd EcoTrack
```

### 2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit web application:
```bash
streamlit run app.py
```

---

## Emission Factors & Methodology

Emissions are modeled using standard multipliers:
- **Car Travel**: $0.192 \text{ kg CO}_2 / \text{km}$
- **Bike Travel**: $0.103 \text{ kg CO}_2 / \text{km}$
- **Bus Travel**: $0.105 \text{ kg CO}_2 / \text{km}$
- **Train Travel**: $0.041 \text{ kg CO}_2 / \text{km}$
- **Electricity Consumption**: $0.82 \text{ kg CO}_2 / \text{kWh}$ (converted to daily rate)
- **Water Consumption**: $0.0003 \text{ kg CO}_2 / \text{liter}$
- **Waste Landfill**: $0.57 \text{ kg CO}_2 / \text{kg}$
- **Diets**: Vegan ($2.0 \text{ kg/day}$), Vegetarian ($3.0 \text{ kg/day}$), Mixed ($5.0 \text{ kg/day}$), Heavy Meat ($7.0 \text{ kg/day}$).
