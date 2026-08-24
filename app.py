import streamlit as str_layout
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🎨 1. WEB PAGE LAYOUT & STYLING
# ==========================================
str_layout.set_page_config(
    page_title="Autonomous Travel Coordinator",
    page_icon="✈️",
    layout="wide"
)

str_layout.title("✈️ Autonomous Travel Coordinator")
str_layout.caption("Enterprise MLOps Frontend UI communicating with an asynchronous FastAPI Backend Engine")

# Initialize session history state variables if they are missing
if "chat_history" not in str_layout.session_state:
    str_layout.session_state.chat_history = []

# ==========================================
# 📊 2. THE ANALYTICAL MONITOR SIDEBAR
# ==========================================
with str_layout.sidebar:
    str_layout.header("⚙️ Core Orchestration Telemetry")
    str_layout.info("Visualizing live data tracking variables parsed straight from the backend REST API.")
    
    active_city_widget = str_layout.empty()
    active_routing_widget = str_layout.empty()
    system_status_widget = str_layout.empty()
    
    active_city_widget.metric(label="Target Focus City", value="Idle")
    active_routing_widget.metric(label="Orchestration Routing Path", value="Idle")
    system_status_widget.metric(label="Backend Pipeline Status", value="Waiting")

# ==========================================
# 💬 3. INTERACTIVE CHAT ENGINE TERMINAL
# ==========================================
# Display historic text blocks sequentially across page cycles
for interaction in str_layout.session_state.chat_history:
    with str_layout.chat_message(interaction["speaker"]):
        str_layout.markdown(interaction["text"])

# Catch explicit user text submissions
if user_prompt := str_layout.chat_input("Where are you planning to travel next?"):
    
    # 1. Instantly append and print out user query to layout
    str_layout.chat_message("user").markdown(user_prompt)
    str_layout.session_state.chat_history.append({"speaker": "user", "text": user_prompt})
    
    # 2. Trigger background processing layout bubble
    with str_layout.chat_message("assistant"):
        with str_layout.spinner("Communicating with production FastAPI backend server..."):
            
            try:
                # 3. Fire a real REST API POST request to your FastAPI backend on port 8000
                backend_url = "http://localhost:8000/api/coordinate"  # Used localhost to bypass Windows filters
                payload = {"user_query": user_prompt}

                
                response = requests.post(backend_url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                response_text = data["itinerary"]
                
                # 4. Refresh sidebar dashboard parameters with live metrics straight from the API
                active_city_widget.metric(label="Target Focus City", value=data["target_city"].capitalize())
                active_routing_widget.metric(label="Orchestration Routing Path", value=data["executed_tool"])
                system_status_widget.metric(label="Backend Pipeline Status", value=data["system_status"])
                
            except Exception as system_fault:
                print(f"🚨 FRONTEND CONNECTION ERROR: {system_fault}")
                response_text = (
                    "### ⚠️ Connection Fault\n"
                    "The frontend UI could not talk to your FastAPI backend server.\n\n"
                    "**How to fix this right now:**\n"
                    "Make sure your backend server is actively running in your other terminal tab! "
                    "Run `uvicorn main:app --reload` on port 8000 so the frontend has an API to talk to."
                )
                system_status_widget.metric(label="Backend Pipeline Status", value="API Offline")

            # 5. Output response to user dashboard
            str_layout.markdown(response_text)
            str_layout.session_state.chat_history.append({"speaker": "assistant", "text": response_text})
