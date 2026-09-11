import streamlit as str_layout
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. Web Page Layout and Styling
# ==========================================
str_layout.set_page_config(
    page_title="Autonomous Travel Coordinator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# str_layout.title("✈️ Autonomous Travel Coordinator")
# str_layout.caption("Enterprise MLOps Frontend UI communicating with an asynchronous FastAPI Backend Engine")

# # Initialize session history state variables if they are missing
# if "chat_history" not in str_layout.session_state:
#     str_layout.session_state.chat_history = []

str_layout.markdown("""
    <style>
    /* Main Background and Fonts */
    .stApp{
    background: linear-gradient(to left, #e0f7fa, #b3e5fc);
    }
    /* Custom Colorful Header Banner */
    .header-banner{
        background: linear-gradient(to right, #e8f5e9, #e2f5e5);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 4px 15 px rgba(0,0,0,0.1);
    }
    /* Metrics Box Custom Styling */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 12px;
        padding: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #FF4B4B;
    }
    
    /* Chat bubbles text enhancement */
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Render the colorful Header Banner
str_layout.markdown("""
    <div class="header-banner">
        <h1 style='margin:0; font-family:sans-serif; font-size:2.8rem;color: #FFD700;'>🌍 AI Travel Coordinator</h1>
        <p style='margin:5px 0 0 0; font-size:1.1rem; opacity:0.9; color: #FFD700'>Your Next Adventure, Orchestrated by Multi-Agent MLOps Networks</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session history state variables if they are missing
if "chat_history" not in str_layout.session_state:
    str_layout.session_state.chat_history = []

# ==========================================
# 2. Analytical Monitor Sidebar
# ==========================================
with str_layout.sidebar:
    str_layout.markdown("### 🗺️ Trip Control Center")

    str_layout.divider()
    str_layout.markdown("### 📊 Active Telemetry")
    
    # Render colorful analytical tracking widgets
    active_city_widget = str_layout.empty()
    active_routing_widget = str_layout.empty()
    system_status_widget = str_layout.empty()
    
    active_city_widget.metric(label="📍 Target Destination", value="Idle")
    active_routing_widget.metric(label="⚡ Orchestration Path", value="Idle")
    system_status_widget.metric(label="🟢 Pipeline Status", value="Waiting")
    
    str_layout.divider()
    str_layout.markdown("### 🎛️ Hyperparameters")
    st_model = str_layout.selectbox("🤖 Brain Model", ["gpt-4o-mini", "gpt-4o", "claude-3-5-sonnet"])
    st_temp = str_layout.slider("🔥 Creativity Level", 0.0, 1.0, 0.4)

# ==========================================
# 3. Interactive Chat Engine Terminal
# ==========================================
# Display historic text blocks sequentially across page cycles
for interaction in str_layout.session_state.chat_history:
    with str_layout.chat_message(interaction["speaker"]):
        str_layout.markdown(interaction["text"])

# Catch explicit user text submissions
if user_prompt := str_layout.chat_input("Where are you planning to travel next?"):
    
    # Instantly append and print out user query to layout
    str_layout.chat_message("user").markdown(user_prompt)
    str_layout.session_state.chat_history.append({"speaker": "user", "text": user_prompt})
    
    # Trigger background processing layout bubble
    with str_layout.chat_message("assistant"):
        with str_layout.spinner("Communicating with production FastAPI backend server..."):
            
            try:
                # Fire a real REST API POST request to your FastAPI backend on port 8000
                backend_url = "http://localhost:8000/api/coordinate"
                payload = {"user_query": user_prompt}

                
                response = requests.post(backend_url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                response_text = data["itinerary"]
                
                # Refresh sidebar widgets instantly with bright new logs
                active_city_widget.metric(label="📍 Target Destination", value=data["target_city"].capitalize())
                active_routing_widget.metric(label="⚡ Orchestration Path", value=data["executed_tool"])
                system_status_widget.metric(label="🟢 Pipeline Status", value="Success")
                
                # 🚀 NEW VISUAL ACCENT: Highlight standalone weather reports uniquely
                if data["executed_tool"] == "WeatherCheck":
                    str_layout.toast("🌤️ Live Weather Metrics Synchronized!", icon="🌤️")

                
            except Exception as system_fault:
                print(f"Frontend Connection Error: {system_fault}")
                response_text = (
                    "### ⚠️ Connection Fault\n"
                    "The frontend UI could not talk to your FastAPI backend server.\n\n"
                    "**How to fix this right now:**\n"
                    "Make sure your backend server is actively running in your other terminal tab! "
                    "Run `uvicorn main:app --reload` on port 8000 so the frontend has an API to talk to."
                )
                system_status_widget.metric(label="Backend Pipeline Status", value="API Offline")

            # Output response to user dashboard
            str_layout.markdown(response_text)
            str_layout.session_state.chat_history.append({"speaker": "assistant", "text": response_text})
