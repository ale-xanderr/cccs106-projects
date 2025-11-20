import httpx
from config import Config

class WeatherServiceError(Exception):
    """Custom exception for weather service errors."""
    pass

class WeatherService:
    async def get_weather(self, city: str):
        """Fetch current weather data."""
        if not city: 
            raise WeatherServiceError("City name cannot be empty")
            
        url = f"{Config.BASE_URL}/weather"
        params = {"q": city, "appid": Config.API_KEY, "units": "metric"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 404:
                    raise WeatherServiceError("City not found")
                elif response.status_code != 200:
                    raise WeatherServiceError(f"API Error: {response.status_code}")
                    
                return response.json()
        except httpx.RequestError:
            raise WeatherServiceError("Network error. Check connection.")
            
    async def get_forecast(self, city: str):
        """Fetch 5-day forecast data."""
        url = f"{Config.BASE_URL}/forecast"
        params = {"q": city, "appid": Config.API_KEY, "units": "metric"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                return None
        except:
            return None