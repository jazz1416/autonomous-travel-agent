import os
import json
import dspy
from typing import Literal
from dotenv import load_dotenv

# Load the secure environment variables from your local .evn file
load_dotenv()

# =========================================
# 1. Defining Structured DSPy Signatures
# =========================================

class TravelRouterSignature(dspy.Signature):
    """Analyze the user's travel request and select the single most appropriate tool to run."""
    user_query: str = dspy.InputField(dsc = "The message, preference, or question from the traveler")

    required_tool: Literal["WeatherCheck", "LocalAttractions", "GeneralChat"] = dspy.OutputField(
        desc = "The next analytical action step needed. Select GeneralChat if no tools are explicitly required."
    )

    extracted_city: str = dspy.OutputField(
        desc = "The literal name of the target destination city, or 'None' if no city was provided"
    )

class SynthesizeItinerarySignature(dspy.Signature):
    """Combine hyper=local data and real-time tool logs into a fluid, day-by-day travel plan"""
    user_query: str = dspy.InputField(desc = "The original intent and constraints stated by the traveler")
    retrieved_guides: str = dspy.InputField(desc = "Contextual background literature extracted from the local Vector DB")
    api_tool_data: str = dspy.InputField(desc = "Live, structured telemetry payloads fetched dynamically via REST APIs")

    itinerary: str = dspy.OutputField(desc = "A detailed, comprehensive markdown schedule containing explicit structure")

# ==============================================
# 2. The multi-stage DSPy Coordinator Program
# ==============================================

class AutonomousTravelCoordinator(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define internal steps using built-in reasoning layers instead of manual text loops
        self.router = dspy.Predict(TravelRouterSignature)
        self.itinerary_generator = dspy.ChainOfThought(SynthesizeItinerarySignature)

    def forward(self, user_query: str, database_instance=None, tools_instance = None) -> dspy.Prediction:
        # Step 1: Run the declarative classifier to route the query
        routing = self.router(user_query = user_query)

        tool_logs = "No live APIs were queried for this specific task turn"
        guide_context = "No structural background guide matches were pulled"

        # Step 2: Conditionally call live infrastructure or search matching context
        if routing.extracted_city != "None":
            city = routing.extracted_city

        # Pull records from Qdrant vector database if present
        if database_instance:
            # Mock a small mock query vector [0.0]*1536 for RAG demonstration purposes
            dummy_vector = [0.0]*1536
            guide_context_list = database_instance.search_guides(query_vector = dummy_vector, city = city)
            guide_context = "\n--\n".join(guide_context_list) if guide_context_list else guide_context

        # Direct real time functional API routing updates
        if tools_instance:
            if routing.required_tool == "WeatherCheck":
                tool_logs = json.dumps(tools_instance.fetch_current_weather(city))
            elif routing.required_tool == "LocalAttractions":
                tool_logs = json.dumps(tools_instance.search_local_attractions(city))

        # Step 3: Forward execution telemtry directly into the comprehensive synthesis layer
        synthesis = self.itinerary_generator(
            user_query=user_query,
            retrieved_guides=guide_context,  # <--- Fix this typo from "retrieved_gueds" to "retrieved_guides"!
            api_tool_data=tool_logs
        )

        return dspy.Prediction(
            itinerary = synthesis.itinerary,
            executed_tool = routing.required_tool,
            target_city = routing.extracted_city
        )

# ====================================
# 3. Independent Module Test Runner
# ====================================

if __name__ == "__main__":
    # Configure the underlying LLM engine globally via LiteLLM standard
    # If no key is set, it defaults to a mock environment validiation string
    openai_key = os.getenv("OPENAI_API_KEY", "your_key_here")

    if openai_key == "your_key_here" or openai_key == "" or "mock" in openai_key:
        print("⚠️ OPENAI_API_KEY not configured. Running a Local Mock Simulation...")
        
        # We manually simulate what the agent outputs when offline
        print("\n=== [📊 MOCK COMPILATION REPORT TRACE] ===")
        print("Target Destination: Seattle")
        print("Executed Routing Path: WeatherCheck")
        print("\nGenerated Output Preview:")
        print("### 1-Day Seattle Itinerary\n* **Morning:** Enjoy a walk around the Space Needle.\n* **Weather Advisory:** Live telemetry reports 22°C and Partly Cloudy. Perfect for exploring!")

    else:
        lm = dspy.LM("openai/gpt-4o-mini", api_key = openai_key)
        dspy.configure(lm=lm)

        # Initialize and evaluate a quick inference sequence locally via the terminal
        coordinator = AutonomousTravelCoordinator()
        print("Compiling DSPy network program structure...Running forward trace on test sample")

        test_run = coordinator(user_query = "I want to visit Seattle, show me what the weather is")
        print("\n=== [📊 COMPILATION REPORT TRACE] ===")
        print(f"Target Destination: {test_run.target_city}")
        print(f"Executed Routing Path: {test_run.executed_tool}")
        print(f"Generated Output Preview:\n{test_run.itinerary}")


