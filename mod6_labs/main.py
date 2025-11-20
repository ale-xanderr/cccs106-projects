import flet as ft
import httpx
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURATION SECTION ---
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

class Config:
    APP_TITLE = "Weather Pro"
    APP_WIDTH = 400
    APP_HEIGHT = 800

# --- WEATHER SERVICE (API HANDLER) ---
class WeatherService:
    async def get_weather(self, city: str):
        if not API_KEY: raise Exception("API Key missing in .env")
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                raise Exception(resp.json().get("message", "Error fetching weather"))
            return resp.json()

    async def get_forecast(self, city: str):
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200: return None
            return resp.json()

# --- MAIN APP CLASS ---
class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.last_weather_data = None 
        self.setup_page()
        self.build_ui()
        self.current_unit = "metric"

    # ------------------ BASIC UI SETUP ------------------ #
    def setup_page(self):
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
        self.page.run_task(self._auto_fetch_location)

    def get_theme_color(self):
        return ft.Colors.BLUE_900 if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50

    def add_to_history(self, city: str):
        city = city.title()
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10]
        self.update_history_dropdown()

    def build_history_dropdown(self):
        return ft.Dropdown(
            label="Recent Searches",
            options=[],
            on_change=lambda e: self.load_from_history(e.control.value),
            expand=True,
            text_size=12
        )
    
    def update_history_dropdown(self):
        self.history_dropdown.options = [ft.dropdown.Option(c) for c in self.search_history]
        self.page.update()

    def load_from_history(self, city: str):
        if city:
            self.city_input.value = city
            self.page.update()
            self.page.run_task(self.get_weather) 

    # ------------------ THEME TOGGLE ------------------ #
    def toggle_theme(self, e):
        # Switch mode
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE

        # Update colors if weather is showing
        if self.last_weather_data:
            # Re-render the display with the new theme colors
            self.display_weather(self.last_weather_data)
        else:
            # Just update the empty container background
            self.weather_container.bgcolor = self.get_theme_color()
        
        self.page.update()

    # ------------------ UI BUILD ------------------ #
    def build_ui(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        self.title = ft.Text("Weather App", size=28, weight="bold")
        
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE, tooltip="Toggle theme", on_click=self.toggle_theme
        )

        self.unit_button = ft.TextButton(
            text="°C / °F", on_click=self.toggle_units, icon=ft.Icons.DEVICE_THERMOSTAT
        )

        self.city_input = ft.TextField(
            label="Enter city name", hint_text="e.g., London",
            border_radius=10, prefix_icon=ft.Icons.LOCATION_CITY,
            on_submit=self.on_search, expand=True
        )

        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH, on_click=self.on_search,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
        )

        self.weather_container = ft.Container(
            visible=False, bgcolor=self.get_theme_color(),
            border_radius=20, padding=20,
            animate_opacity=300
        )

        self.error_message = ft.Text("", color=ft.Colors.RED, visible=False)

        self.location_button = ft.ElevatedButton(
            "My Location", icon=ft.Icons.MY_LOCATION,
            on_click=lambda e: self.page.run_task(self.get_location_weather),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
        )

        self.loading = ft.ProgressRing(visible=False)
        self.history_dropdown = self.build_history_dropdown()

        self.page.add(
            ft.Column([
                ft.Row([self.title, self.theme_button], alignment="spaceBetween"),
                ft.Divider(height=10, color="transparent"),
                ft.Row([self.city_input, self.search_button]),
                ft.Row([self.location_button, self.history_dropdown], alignment="spaceBetween"),
                ft.Divider(height=10, color="transparent"),
                self.loading,
                self.error_message,
                self.weather_container,
            ], scroll=ft.ScrollMode.HIDDEN)
        )

    # ------------------ MISC ------------------ #
    def convert_temp(self, temp: float, from_unit: str = "metric") -> float:
        if from_unit == self.current_unit: return temp 
        if from_unit == "metric" and self.current_unit == "imperial":
            return (temp * 9/5) + 32
        elif from_unit == "imperial" and self.current_unit == "metric":
            return (temp - 32) * 5/9
        return temp 

    def toggle_units(self, e):
        old_unit = self.current_unit
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        if self.last_weather_data:
             self.display_weather(self.last_weather_data)

    async def _auto_fetch_location(self):
        await self.get_location_weather(auto_fetch=True)

    async def get_location_weather(self, auto_fetch: bool = False):
        if not auto_fetch:
            self.error_message.value = "Locating..."
            self.error_message.visible = True
            self.page.update()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get("city")
                if city:
                    self.city_input.value = city
                    self.page.update()
                    await self.get_weather()
        except Exception as e:
            if not auto_fetch: self.show_error(f"Location error: {str(e)}")

    # ------------------ WEATHER LOGIC ------------------ #
    def on_search(self, e):
        self.page.run_task(self.get_weather)

    async def get_weather(self):
        city = self.city_input.value.strip()
        if not city: return

        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            weather_data = await self.weather_service.get_weather(city)
            forecast_data = await self.weather_service.get_forecast(city)
            
            self.forecast_data = forecast_data 
            self.display_weather(weather_data)
            self.add_to_history(city)

        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()

    def display_weather(self, data: dict):
        self.last_weather_data = data 
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        raw_temp = data.get("main", {}).get("temp", 0)
        raw_feels = data.get("main", {}).get("feels_like", 0)
        raw_min = data.get("main", {}).get("temp_min", 0)
        raw_max = data.get("main", {}).get("temp_max", 0)
        
        temp = self.convert_temp(raw_temp)
        feels_like = self.convert_temp(raw_feels)
        temp_min = self.convert_temp(raw_min)
        temp_max = self.convert_temp(raw_max)

        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        
        self.description = description
        self.icon_code = icon_code
        
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        container_color = self.get_background_for_weather(description, icon_code, is_dark)
        unit_symbol = '°C' if self.current_unit == 'metric' else '°F'
        
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"

        self.weather_container.content = ft.Column([
            self.unit_button,
            ft.Text(f"{city_name}, {country}", size=24, weight="bold", color=text_color),
            ft.Row([
                ft.Image(src=icon_url, width=100, height=100),
                ft.Column([
                    ft.Text(f"{temp:.0f}{unit_symbol}", size=50, weight="bold", color=text_color),
                    ft.Text(description, size=16, italic=True, color=text_color)
                ])
            ], alignment="center"),
            
            ft.Text(f"Feels like {feels_like:.0f}{unit_symbol}", color=text_color),
            ft.Row([
                ft.Text(f"High: {temp_max:.0f}{unit_symbol}", color=text_color),
                ft.Text(f"Low: {temp_min:.0f}{unit_symbol}", color=text_color),
            ], alignment="center", spacing=20),
            
            ft.Divider(color=text_color),
            
            ft.Row([
                self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f"{data['main']['humidity']}%", is_dark),
                self.create_info_card(ft.Icons.AIR, "Wind", f"{data['wind']['speed']} m/s", is_dark),
                self.create_info_card(ft.Icons.CLOUD, "Clouds", f"{data['clouds']['all']}%", is_dark),
            ], alignment="center", spacing=10),
            
            ft.Divider(color=text_color),
            self.build_forecast_view(is_dark, text_color, unit_symbol)
        ], horizontal_alignment="center")
        
        self.weather_container.bgcolor = container_color
        self.weather_container.visible = True
        self.page.update()

    def build_forecast_view(self, is_dark, text_color, unit_symbol):
        if not self.forecast_data: return ft.Container()
        
        cards = []
        daily_list = [x for x in self.forecast_data['list'] if '12:00:00' in x['dt_txt']][:5]
        
        for item in daily_list:
            date_txt = item['dt_txt'].split(" ")[0]
            import datetime
            day_name = datetime.datetime.strptime(date_txt, "%Y-%m-%d").strftime("%a")
            
            f_temp = self.convert_temp(item['main']['temp'])
            f_icon = item['weather'][0]['icon']
            f_url = f"https://openweathermap.org/img/wn/{f_icon}@2x.png"
            
            cards.append(ft.Container(
                padding=10, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK if is_dark else ft.Colors.WHITE),
                border_radius=10,
                content=ft.Column([
                    ft.Text(day_name, size=12, weight="bold", color=text_color),
                    ft.Image(src=f_url, width=40, height=40),
                    ft.Text(f"{f_temp:.0f}{unit_symbol}", size=12, color=text_color)
                ], spacing=2, horizontal_alignment="center")
            ))
            
        return ft.Column([
            ft.Text("5-Day Forecast", weight="bold", color=text_color),
            ft.Row(cards, alignment="center", scroll=ft.ScrollMode.HIDDEN)
        ])

    def create_info_card(self, icon, label, value, is_dark):
        color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        return ft.Container(
            padding=10, bgcolor=ft.Colors.with_opacity(0.1, color), border_radius=10, width=90,
            content=ft.Column([
                ft.Icon(icon, size=20, color=color),
                ft.Text(label, size=10, color=color),
                ft.Text(value, size=12, weight="bold", color=color)
            ], horizontal_alignment="center")
        )

    def get_background_for_weather(self, description: str, icon_code: str, is_dark: bool) -> str:
        desc = description.lower()
        is_night = icon_code.endswith("n")
        
        if "clear" in desc:
            if is_night: return ft.Colors.INDIGO_900 if is_dark else ft.Colors.INDIGO_100
            return ft.Colors.ORANGE_900 if is_dark else ft.Colors.ORANGE_100
        elif "rain" in desc:
            return ft.Colors.BLUE_GREY_900 if is_dark else ft.Colors.BLUE_200
        elif "cloud" in desc:
            return ft.Colors.GREY_800 if is_dark else ft.Colors.GREY_300
        return ft.Colors.BLUE_GREY_900 if is_dark else ft.Colors.BLUE_50

    def show_error(self, message: str):
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()

def main(page: ft.Page):
    WeatherApp(page)

if __name__ == "__main__":
    ft.app(target=main)