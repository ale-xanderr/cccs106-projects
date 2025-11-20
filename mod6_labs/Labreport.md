Flet Weather Application - Module 6 

---
Student Information
---
A modern, cross-platform weather application built with Python and Flet. This app provides real-time weather data, dynamic environmental visualizations, and a responsive Material Design interface.

(Dynamic background changing based on "Clear Night" condition)

Features

Real-time Weather: Fetches current temperature, humidity, and wind speed via OpenWeatherMap API.

Dynamic Backgrounds: The app interface changes color and gradient based on the weather conditions (e.g., Indigo for clear nights, Grey for cloudy, Orange for sunset).

Geolocation: Automatically detects your location on startup to show local weather instantly.

City Search: Search for any city globally with error handling for invalid names.

Unit Conversion: Toggle between Metric (°C) and Imperial (°F) units.

Dark/Light Mode: Fully supported theme toggling with system preference detection.

Search History: Saves your last 5 searched locations for quick access.

Tech Stack

Language: Python 3.x

Framework: Flet (Flutter for Python)

API: OpenWeatherMap

Assets: Material Icons

Installation

Clone the repository

git clone [https://github.com/yourusername/weather-app-flet.git](https://github.com/yourusername/weather-app-flet.git)
cd weather-app-flet


Create a virtual environment (Optional but recommended)

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


Install dependencies

pip install flet requests


Set up API Key

Get a free API key from OpenWeatherMap.

Open main.py (or your config file) and replace the placeholder with your key:

API_KEY = "YOUR_OPENWEATHER_API_KEY"


Usage

Run the application as a desktop app:

flet run main.py


To run it as a web app in your browser:

flet run main.py --web


Key Implementation Details

State Management: Uses client_storage to persist user preferences (Theme, Search History) across sessions.

Async Handling: Geolocation and API requests are handled asynchronously to prevent UI freezing.

UI Design: Utilizes "Glassmorphism" effects (semi-transparent containers) to ensure text remains readable against the dynamic, high-contrast weather backgrounds.
