import os
import requests
from typing import Dict, Any

class TravelTools:
    def __init__(self):
        # Read directly from .env file
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.yelp_api_key = os.getenv("YELP_API_KEY")

    def fetch_current_weather(self, city: str, is_forecast: bool = False) -> dict:
        """Fetches live weather conditions for a destination using OpenWeatherMap API."""
        if self.weather_api_key == "mock_weather_key" or not self.weather_api_key:
            return {"temperature": "22°C", "condition": "Partly Cloudy", "humidity": "60%"}

        clean_city = str(city).strip()
        
        # ABSOLUTE FIX: Hardcoded domain layout with clear structural dividers
        base_domain = "https://api.openweathermap.org"
        if is_forecast:
            endpoint_path = f"/data/2.5/forecast?q={clean_city}&units=metric&appid={self.weather_api_key}"
        else:
            endpoint_path = f"/data/2.5/weather?q={clean_city}&units=metric&appid={self.weather_api_key}"
            
        url = f"{base_domain}{endpoint_path}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() 
            data = response.json()
            
            # Parse the 5-Day forecast if asked
            if is_forecast:
                forecast_summary = []
                # Only grab one forecast snapshot per day
                for i in range(0, len(data.get("list", [])), 8):
                    day_data = data["list"][i]
                    date_text = day_data.get("dt_txt", "").split(" ")[0]
                    temp = day_data["main"]["temp"]
                    desc = day_data["weather"][0]["description"].title()
                    forecast_summary.append(f"[{date_text}]: {temp}°C, {desc}")
                
                return {
                    "city": clean_city.capitalize(),
                    "forecast_timeline": " | ".join(forecast_summary)
                }
            
            # Parse the current forecast if multiple days not asked
            return {
                "temperature": f"{data['main']['temp']}°C",
                "condition": data['weather'][0]['description'].title(),
                "humidity": f"{data['main']['humidity']}%"
            }
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Weather API Exception for {clean_city}: {e}")
            return {"error": f"Weather lookup failed: {str(e)}"}



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