import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Settings
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    # App Settings
    APP_TITLE = "Weather Weather Lang"
    APP_WIDTH = 400
    APP_HEIGHT = 800
    
    @classmethod
    def validate(cls):
        """Ensure API key is present."""
        if not cls.API_KEY:
            raise ValueError("Missing API Key! Check your .env file.")