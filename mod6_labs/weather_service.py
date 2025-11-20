import httpx
from config import Config

class WeatherService:
    async def get_weather(self, city: str):
        if not Config.API_KEY: 
            raise Exception("API Key missing in .env")
            
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": Config.API_KEY, "units": "metric"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                raise Exception(resp.json().get("message", "Error fetching weather"))
            return resp.json()

    async def get_forecast(self, city: str):
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": city, "appid": Config.API_KEY, "units": "metric"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200: 
                return None
            return resp.json()