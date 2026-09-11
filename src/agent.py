import os
import json
import dspy
from typing import Literal
from dotenv import load_dotenv

# Load the secure environment variables from local .evn file
load_dotenv()

# =========================================
#  1. Define Structured DSPy Signatures
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
    """Combine hyper-local data and real-time tool logs into a fluid, day-by-day travel plan"""
    user_query: str = dspy.InputField(desc = "The original intent and constraints stated by the traveler")
    retrieved_guides: str = dspy.InputField(desc = "Contextual background literature extracted from the local Vector DB")
    api_tool_data: str = dspy.InputField(desc = "Live, structured telemetry payloads fetched dynamically via REST APIs")

    itinerary: str = dspy.OutputField(desc = "A detailed, comprehensive markdown schedule containing explicit structure, " \
                                        "summarized reviews for attractions, recommended time spent" \
                                        "links for attractions mentioned, precise names for locations")

class GetWeather(dspy.Signature):
    """Get the current or future weather for specified city in Fahrenheit by default, or other unit if specified."""
    user_query: str = dspy.InputField(desc = "The location and time frame that the traveler is wanting to know the weather for")
    api_tool_data: str = dspy.InputField(desc = "Live, raw weather telemetry question or data criteria")
    weather_report: str = dspy.OutputField(desc = "A beautifully formatted, concise markdown weather advisory. Do NOT include a travel itinerary unless specifically requested")

# ==============================================
# 2. Travel Coordinator Definition
# ==============================================

class AutonomousTravelCoordinator(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define internal steps using built-in reasoning layers instead of manual text loops
        self.router = dspy.Predict(TravelRouterSignature)
        self.itinerary_generator = dspy.ChainOfThought(SynthesizeItinerarySignature)
        self.weather = dspy.ChainOfThought(GetWeather)

    def forward(self, user_query: str, database_instance=None, tools_instance = None) -> dspy.Prediction:
        # Run declarative classifier to route the query
        routing = self.router(user_query = user_query)

        tool_logs = "No live APIs were queried for this specific task turn"
        guide_context = "No structural background guide matches were pulled"

        # Call live infrastructure or search matching context only if city specified
        if routing.extracted_city != "None":
            city = routing.extracted_city
            
            # Pull records from our Qdrant vector database if present
            if database_instance:
                try:
                    # 1. Generate a real embedding vector using the standardized OpenAI interface mapping
                    openai_key = os.getenv("OPENAI_API_KEY", "")
                    
                    # We initialize a direct client connection loop for vector extraction
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_key)
                    
                    response = client.embeddings.create(
                        input=[user_query],
                        model="text-embedding-3-small"
                    )
                    real_query_vector = response.data[0].embedding
                    
                    # 2. Pass the real mathematical vector into your search function
                    guide_context_list = database_instance.search_guides(
                        query_vector=real_query_vector, 
                        city=city
                    )
                    guide_context = "\n---\n".join(guide_context_list) if guide_context_list else guide_context
                
                except Exception as embedding_fault:
                    print(f"⚠️ RAG Embedding generation bypassed: {embedding_fault}")
                    # Safe fallback: if embedding fails, fall back to empty vector tracking
                    dummy_vector = [0.0] * 1536
                    guide_context_list = database_instance.search_guides(query_vector=dummy_vector, city=city)
                    guide_context = "\n---\n".join(guide_context_list) if guide_context_list else guide_context



        # Direct real time functional API routing updates
        if tools_instance:
            if routing.required_tool == "WeatherCheck":
                # Check if the user query is asking for multiple days, a future forecast, or a timeline
                query_lower = user_query.lower()
                needs_forecast = any(word in query_lower for word in ["days", "forecast", "future", "week", "tomorrow", "weekend"])
                    
                # Pass the boolean indicator directly down to your upgraded tool method
                tool_logs = json.dumps(tools_instance.fetch_current_weather(city, is_forecast=needs_forecast))
            elif routing.required_tool == "LocalAttractions":
                tool_logs = json.dumps(tools_instance.search_local_attractions(city))

        if routing.required_tool == "WeatherCheck":
            synthesis = self.weather(
                user_query = user_query,
                api_tool_data = tool_logs
            )
            final_text = synthesis.weather_report
        else:
            synthesis = self.itinerary_generator(
                        user_query=user_query,
                        retrieved_guides=guide_context, 
                        api_tool_data=tool_logs
            )
            final_text = synthesis.itinerary

        # Forward execution into synthesis layer
        

        return dspy.Prediction(
            itinerary = final_text,
            executed_tool = routing.required_tool,
            target_city = routing.extracted_city
        )

# ====================================
# 3. Independent Test Runner
# ====================================

if __name__ == "__main__":
    # Configure LLMs
    openai_key = os.getenv("OPENAI_API_KEY")

    lm = dspy.LM("openai/gpt-4o-mini", api_key = openai_key)
    dspy.configure(lm=lm)

    # Initialize and evaluate locally via the terminal
    coordinator = AutonomousTravelCoordinator()
    print("Compiling DSPy network program structure...Running forward trace on test sample")

    test_run = coordinator(user_query = "I want to visit Seattle, show me what the weather is")
    print("\n=== [📊 COMPILATION REPORT TRACE] ===")
    print(f"Target Destination: {test_run.target_city}")
    print(f"Executed Routing Path: {test_run.executed_tool}")
    print(f"Generated Output Preview:\n{test_run.itinerary}")


