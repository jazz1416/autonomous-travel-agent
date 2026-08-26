# Autonomous-Travel-Agent
---


## Project Introduction
This project aims to create an autonomous travel agent that will take in a user query and generate a specific itinerary, including notes on weather and 
nearby attractions using FastAPI and DSPy. 


## Table of Contents
1. [Project Structure](#project-structure) 
2. [File Breakdown](#file-breakdown)
3. [Technologies Used](#technologies-used)
4. [Future Enhancements](#future-enhancements)


## Project Structure
```
autonomous-travel-agent/
│
├── local_qdrant_storage       # Saved itineraries, embeddings, etc
├── src                 # Agent, database, tool definitions
├── gitgnore                
├── README.md                       # Project documentation
├── app.py                      # Streamlit page creation and customization
├── assertion.log
├── azure_openai_usage.log
├── main.py                      # Backend server setup
├── openai_usage.log
├── requirements.txt           # All required packages with appropriate version numbers
│
```


## File Breakdown

### 1. agent.py
* Creates DSPy agent using DSPy signatures
* Notes when to make API calls
* Notes when to create and use RAG embeddings
* Keeps track of tool usage
* Generates itinary and response to user query

### 2. database.py
* RAG pipeline

### 3. tools.py
* Tool creation for agent
* fetch_current_weather
* search_local_attractions

### 4. app.py 
* Designs streamlit page
* CSS customizations

### 5. main.py
* Back end API manager
* CORS initalizing to secure communication between back and front end systems

---



## Technologies Used


### Programming Language
- **Python 3.12**


### Core Libraries
| Library | Purpose |
|---------|---------|
| `qdrant_client` | Vector search engine |
| `os` | Operating system interactions |
| `dspy` | Agent creation |
| `streamlit` | Front end web page |
| `fastapi` | API building |


### Development Environment
- **Visual Studios Code** — Interactive analysis and experimentation
- **Virtual Environment (venv)** — Dependency isolation


---

## Future Enhancements
Further improving the overall look of the chatbox, increasing the specificity of the itineraries generated, adding an LLM as a judge, and adding in public transit/transportation 
recommendations.








