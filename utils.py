import streamlit as st
import pandas as pd
from datetime import datetime

def inject_custom_css():
    """
    Injects custom CSS to style Streamlit components, offering a sleek, premium,
    eco-themed Dark Mode experience with glassmorphism, gradients, and micro-animations.
    """
    css = """
    <style>
        /* Modern font load */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Gradient titles */
        .main-title {
            background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            text-align: left;
            animation: fadeIn 1s ease-in-out;
        }
        
        .subtitle {
            color: #CBD5E1;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-weight: 400;
            line-height: 1.5;
        }
        
        /* Glassmorphism Metric Cards */
        .metric-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .metric-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            min-width: 200px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.1);
        }
        
        .metric-label {
            color: #CBD5E1;
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .metric-value {
            color: #F8FAFC;
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .metric-sub {
            color: #10B981;
            font-size: 0.85rem;
            margin-top: 5px;
            font-weight: 600;
        }

        /* Dynamic Badge Container */
        .badge-box {
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            animation: pulse 2.5s infinite;
        }

        /* Slide-in Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        /* High-contrast accessible focus states (WCAG 2.4.7 & 2.4.11) */
        *:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, [tabindex]:focus-visible {
            outline: 3px solid #10B981 !important;
            outline-offset: 3px !important;
            box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.35) !important;
        }

        /* Respect user preference for reduced motion (WCAG 2.3.3) */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.001ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.001ms !important;
            }
            .badge-box, .main-title {
                animation: none !important;
            }
        }

        /* Responsive touch targets and mobile layout (WCAG 2.5.5 & 2.5.8) */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2.1rem !important;
            }
            .metric-container {
                flex-direction: column !important;
                gap: 12px !important;
            }
            .metric-card {
                min-width: 100% !important;
                padding: 16px !important;
            }
            .stButton>button {
                width: 100% !important;
            }
        }

        /* Screen-reader only utility */
        .sr-only {
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            padding: 0 !important;
            margin: -1px !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
            white-space: nowrap !important;
            border: 0 !important;
        }

        /* Form slider tweaks for eco look */
        .stSlider > div [data-baseweb="slider"] {
            background-color: #1E293B;
        }
        
        /* Expander headers */
        .streamlit-expanderHeader {
            background-color: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
            margin-bottom: 5px !important;
        }

        /* Tabs custom design */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(15, 23, 42, 0.5);
            padding: 6px;
            border-radius: 12px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 8px;
            color: #94A3B8;
            font-weight: 500;
            padding: 0 16px;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #10B981;
            background-color: rgba(16, 185, 129, 0.05);
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(16, 185, 129, 0.1) !important;
            color: #10B981 !important;
            font-weight: 700 !important;
        }
        
        /* Rounded buttons */
        .stButton>button {
            border-radius: 8px;
            background-color: #10B981;
            color: white;
            font-weight: 600;
            border: none;
            padding: 8px 24px;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #059669;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            transform: scale(1.02);
            color: white;
        }
        
        .stButton>button:active {
            transform: scale(0.98);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def generate_csv_report(inputs, emissions, score, category):
    """
    Builds a DataFrame and compiles a downloadable CSV report of the user's carbon footprint.
    """
    report_data = {
        "Metric / Activity": [
            "Car Travel (km/day)",
            "Bike Travel (km/day)",
            "Bus Travel (km/day)",
            "Train Travel (km/day)",
            "Electricity Consumption (kWh/month)",
            "Water Usage (liters/day)",
            "Food Habit / Diet",
            "Waste Generation (kg/day)",
            "Transport Emissions (kg CO2/day)",
            "Electricity Emissions (kg CO2/day)",
            "Water Emissions (kg CO2/day)",
            "Food Emissions (kg CO2/day)",
            "Waste Emissions (kg CO2/day)",
            "Total Footprint (kg CO2/day)",
            "Total Footprint (kg CO2/month)",
            "Total Footprint (kg CO2/year)",
            "Sustainability Score",
            "Environmental Category"
        ],
        "Value": [
            inputs["car"],
            inputs["bike"],
            inputs["bus"],
            inputs["train"],
            inputs["electricity"],
            inputs["water"],
            inputs["food"],
            inputs["waste"],
            f"{emissions['transport']['total_daily']:.3f}",
            f"{emissions['electricity']['total_daily']:.3f}",
            f"{emissions['water']['total_daily']:.3f}",
            f"{emissions['food']['total_daily']:.3f}",
            f"{emissions['waste']['total_daily']:.3f}",
            f"{emissions['totals']['daily']:.3f}",
            f"{emissions['totals']['monthly']:.3f}",
            f"{emissions['totals']['annual']:.3f}",
            f"{score:.1f}",
            category
        ],
        "Unit": [
            "km", "km", "km", "km", "kWh", "liters", "text", "kg",
            "kg CO2/day", "kg CO2/day", "kg CO2/day", "kg CO2/day", "kg CO2/day",
            "kg CO2/day", "kg CO2/month", "kg CO2/year", "out of 100", "category text"
        ]
    }
    
    df = pd.DataFrame(report_data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv

def initialize_session_state():
    """
    Initializes tracking variables, history logs, and goal benchmarks in Streamlit session state.
    """
    if "history" not in st.session_state:
        st.session_state.history = []
        
    if "goals" not in st.session_state:
        st.session_state.goals = {
            "car_reduction": 0.0,
            "electricity_reduction": 0.0,
            "waste_reduction": 0.0,
            "meat_free_days": 0
        }

def log_calculation_history(inputs, daily_footprint):
    """
    Logs the current footprint metrics into the history log with a timestamp.
    Limits history to the 20 most recent entries.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Check if we should log (avoid duplicate adjacent logging on page refresh)
    if st.session_state.history:
        last_log = st.session_state.history[-1]
        # Skip logging if same footprint and within a short timeframe
        if abs(last_log["daily_footprint"] - daily_footprint) < 0.001:
            return
            
    log_entry = {
        "timestamp": timestamp,
        "car": inputs["car"],
        "electricity": inputs["electricity"],
        "waste": inputs["waste"],
        "food": inputs["food"],
        "daily_footprint": daily_footprint
    }
    
    st.session_state.history.append(log_entry)
    # Cap history at last 20 calculations
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)
