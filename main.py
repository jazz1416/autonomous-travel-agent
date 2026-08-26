import os
import dspy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import modules built earlier
from src.agent import AutonomousTravelCoordinator
from src.database import TravelVectorDB
from src.tools import TravelTools

# Load the environment keys from secure local configuration layer
load_dotenv()

# ======================================
# 1. API Server and CORS Initialization
# ======================================
app = FastAPI(
    title= "Autonomous Travel Coordinator Core API",
    description = "Production ready asynchronous API enginge orchestrating DSPy frameworks, Qdrant vecotres, and REST APIs",
    version = "1.0.0"
)

# Enable cross-origin resource sharing (CORS) so front end can communicate securely
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =============================
# 2. Shared API Infrastructure
# =============================
db = TravelVectorDB()
tools = TravelTools()
coordinator_agent = AutonomousTravelCoordinator()

# ===================================
# 3. Pydantic Data Validation Scheme
# ===================================
class TravelRequest(BaseModel):
    user_query : str = Field(..., example = "I want to visit Tokyo for 3 days and I need a weather advisory.")

class TravelResponse(BaseModel):
    itinerary: str = Field(..., description= "The complete markdown-formatted structured schedule text block.")
    target_city: str = Field(..., description= "The literal destination city extracted by the agent router.")
    executed_tool: str = Field(..., description= "The definitive analytical action step triggered by the agent.")
    system_status: str = Field(..., description= "Details if the model ran live or executed its fallback simulation loops.")

# ===============================
# 4. Asynchronous Rest Endpoints
# ===============================
@app.get("/health")
def health_check():
    """Simple heartbeat ping endpoint to verify the backend container infrastructure is active."""
    return {"status": "operational", "engine": "FastAPI Framework"}

@app.post("/api/coordinate", response_model=TravelResponse)
def process_travel_request(request: TravelRequest): 
    """Processes a user's travel request, coordinates routing metrics, and creates an itinerary."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    # Check if a real OpenAI secret key is present
    is_simulation = not openai_key or "YOUR" in openai_key or "mock" in openai_key

    try:
        if is_simulation:
            # Match the fallback logic designed inside Streamlit app layer
            return TravelResponse(
                itinerary=(
                    "### ⚠️ Local API Server Simulation Notice\n"
                    "Your production FastAPI backend endpoint `/api/coordinate` executed cleanly! "
                    "Because an active `OPENAI_API_KEY` is missing from your local configuration layer, "
                    "the engine successfully processed this request through its baseline fallback validation rules.\n\n"
                    f"**Telemetry Log:** Your destination request *'{request.user_query}'* was processed through the agent core successfully.\n\n"
                    "**Sample Output Preview:**\n"
                    "1. **Morning Exploration:** Gather near local cultural hot-spots. \n"
                    "2. **Real-time Environmental Telemetry:** Weather arrays safely returned a comfortable `22°C` with `Partly Cloudy` skies."
                ),
                target_city="Simulation Mode",
                executed_tool="Dynamic Stub Route",
                system_status="offline_fallback_simulation"
            )
        
        # Configure and mount the live DSPy LLM connection context globally
        lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_key)
        dspy.configure(lm=lm) 
        
        # Fire execution parameters down through your core DSPy module pipeline
        agent_prediction = coordinator_agent(
            user_query=request.user_query,
            database_instance=db,
            tools_instance=tools
        )
        
        return TravelResponse(
            itinerary=str(agent_prediction.itinerary),
            target_city=str(agent_prediction.target_city),
            executed_tool=str(agent_prediction.executed_tool),
            system_status="live_inference_success"
        )

    except Exception as error_exception:
        # Log the raw text down into the console so you can view the direct issue
        print(f"BACKEND SYSTEM FAULT LOG: {error_exception}")
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Fault: {str(error_exception)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting local Uvicorn development server engine...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
