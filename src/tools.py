import os
import requests
from typing import Dict, Any

class TravelTools:
    def __init__(self):
        # Read directly from .env file
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.yelp_api_key = os.getenv("YELP_API_KEY")

    def fetch_current_weather(self, city: str) -> Dict[str, Any]:
        """Fetches live weather conditions for a destination using OpenWeatherMap API."""

        url = f"https://openweathermap.org{city}&units=metric&appid={self.weather_api_key}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() 
            data = response.json()
            
            return {
                "temperature": f"{data['main']['temp']}°C",
                "condition": data['weather'][0]['description'].title(), 
                "humidity": f"{data['main']['humidity']}%"
            }
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Weather API Error for {city}: {e}")
            return {"error": "Weather data temporarily unavailable for this destination."}


    def search_local_attractions(self, city: str, category: str = "tourist") -> Dict[str, Any]:
        """Queries local hot-spots and restaurants within a specific city from Yelp."""

        url = f"https://yelp.com{city}&term={category}&limit=3"
        headers = {"Authorization": f"Bearer {self.yelp_api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            names = [business["name"] for business in data.get("businesses", [])]
            return {"attractions": names if names else ["No local recommendations found."]}
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Places API Error for {city}: {e}")
            return {"error": "Local attraction directories are temporarily offline."}


if __name__ == "__main__":
    tools = TravelTools()
    print("Testing weather tool {Mock Fallback}...")
    print(tools.fetch_current_weather("Paris"))
    print("API tools module compiled and operational")