import flet as ft
import json
import httpx
import datetime
from pathlib import Path
from config import Config
from weather_service import WeatherService

# Validate Config on startup
try:
    Config.validate()
except ValueError as e:
    print(f"CRITICAL ERROR: {e}")

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        
        # Feature: Search History
        self.search_history = []
        
        # Feature: Metric/Imperial Toggle
        self.last_weather_data = None 
        self.current_unit = "metric"
        self.forecast_data = None

        self.setup_page()
        self.build_ui()
        
        # Feature: User Location Preload
        self.page.run_task(self._auto_fetch_location)

    # ------------------ BASIC UI SETUP ------------------ #
    def setup_page(self):
        self.page.title = Config.APP_TITLE
        # Feature: Theme Toggle
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT + 100 # Increased height for chart
        self.page.window.resizable = True # Allow resizing for chart visibility
        self.page.window.center()

    def get_theme_color(self):
        """Returns a fallback color based on theme if weather data isn't loaded."""
        return ft.Colors.BLUE_900 if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50

    # ------------------ FEATURE: SEARCH HISTORY ------------------ #
    def add_to_history(self, city: str):
        city = city.title()
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10] # Limit to 10
        self.update_history_dropdown()
        self.save_history_to_file()

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
            
    def save_history_to_file(self):
        try:
            with open("history.json", "w") as f:
                json.dump(self.search_history, f)
        except: pass

    def load_history_from_file(self):
        if Path("history.json").exists():
            try:
                with open("history.json", "r") as f:
                    self.search_history = json.load(f)
                self.update_history_dropdown()
            except: pass

    # ------------------ FEATURE: THEME TOGGLE ------------------ #
    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE

        if self.last_weather_data:
            self.display_weather(self.last_weather_data)
        else:
            self.weather_container.bgcolor = self.get_theme_color()
        
        self.page.update()

    # ------------------ UI BUILD ------------------ #
    def build_ui(self):
        self.title = ft.Text("Weather Weather Lang", size=28, weight=ft.FontWeight.BOLD)
        
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

        # Feature: Dynamic Background
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
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([self.city_input, self.search_button]),
                ft.Row([self.location_button, self.history_dropdown], alignment="spaceBetween"),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.loading,
                self.error_message,
                self.weather_container,
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )
        
        self.load_history_from_file()

    # ------------------ FEATURE: METRIC/IMPERIAL TOGGLE ------------------ #
    def convert_temp(self, temp: float, from_unit: str = "metric") -> float:
        if from_unit == self.current_unit: return temp 
        if from_unit == "metric" and self.current_unit == "imperial":
            return (temp * 9/5) + 32
        elif from_unit == "imperial" and self.current_unit == "metric":
            return (temp - 32) * 5/9
        return temp 

    def toggle_units(self, e):
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        if self.last_weather_data:
             self.display_weather(self.last_weather_data)

    # ------------------ FEATURE: USER LOCATION ------------------ #
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
        
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        container_color = self.get_background_for_weather(description, icon_code, is_dark)
        
        unit_symbol = '°C' if self.current_unit == 'metric' else '°F'
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"

        self.weather_container.content = ft.Column([
            self.unit_button,
            ft.Text(f"{city_name}, {country}", size=24, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Row([
                ft.Image(src=icon_url, width=100, height=100),
                ft.Column([
                    ft.Text(f"{temp:.0f}{unit_symbol}", size=50, weight=ft.FontWeight.BOLD, color=text_color),
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
            
            # NEW: Hourly Trend Chart
            self.build_hourly_chart(is_dark, text_color, unit_symbol),
            
            ft.Divider(color=text_color),
            self.build_forecast_view(is_dark, text_color, unit_symbol)
        ], horizontal_alignment="center")
        
        self.weather_container.bgcolor = container_color
        self.weather_container.visible = True
        self.page.update()

    # ------------------ FEATURE: CHARTS & GRAPHS (NEW) ------------------ #
    def build_hourly_chart(self, is_dark, text_color, unit_symbol):
        """
        Creates a LineChart showing the temperature trend for the next 24 hours (8 intervals).
        Includes interactive tooltips and transparent styling.
        """
        if not self.forecast_data: return ft.Container()

        # 1. Extract next 8 intervals (approx 24 hours)
        # OpenWeatherMap free API gives 3-hour intervals
        hourly_data = self.forecast_data['list'][:8]
        
        data_points = []
        x_labels = []
        
        min_temp = 1000
        max_temp = -1000

        for i, item in enumerate(hourly_data):
            # Process Time
            dt_txt = item['dt_txt']
            dt_obj = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            time_label = dt_obj.strftime("%H:%M") # e.g., 15:00
            
            # Process Temp
            raw_val = item['main']['temp']
            val = self.convert_temp(raw_val)
            
            if val < min_temp: min_temp = val
            if val > max_temp: max_temp = val
            
            # Create Data Point with Tooltip
            data_points.append(
                ft.LineChartDataPoint(
                    i, val,
                    tooltip=f"{time_label}\n{val:.1f}{unit_symbol}",
                    point=True
                )
            )
            
            # Create X-Axis Label (only show every 2nd label to avoid clutter)
            if i % 2 == 0:
                x_labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(time_label, size=10, weight=ft.FontWeight.BOLD, color=text_color)
                    )
                )

        # 2. Define Chart Styling
        chart_color = ft.Colors.ORANGE_ACCENT if is_dark else ft.Colors.BLUE_ACCENT
        grid_color = ft.Colors.with_opacity(0.2, text_color)
        
        # Add padding to Y axis so the line doesn't touch the top/bottom
        min_y = min_temp - 2
        max_y = max_temp + 2
        
        # 3. Construct the LineChart
        chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=3,
                    color=chart_color,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.1, chart_color),
                )
            ],
            border=ft.border.all(0, ft.Colors.TRANSPARENT),
            horizontal_grid_lines=ft.ChartGridLines(interval=5, color=grid_color, width=1),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=grid_color, width=1),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text(f"Temp ({unit_symbol})", size=10, color=text_color),
                title_size=20,
                show_labels=True,
                labels_interval=5 # Adjust based on your temp range preference
            ),
            bottom_axis=ft.ChartAxis(
                labels=x_labels,
                labels_size=20,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
            min_y=min_y,
            max_y=max_y,
            expand=True,
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("24-Hour Temperature Trend", size=14, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Container(
                    content=chart,
                    height=200, # Fixed height for the chart
                    padding=ft.padding.only(right=20, left=10)
                )
            ]),
            padding=ft.padding.symmetric(vertical=10)
        )

    # ------------------ EXISTING FORECAST VIEW ------------------ #
    def build_forecast_view(self, is_dark, text_color, unit_symbol):
        if not self.forecast_data: return ft.Container()
        
        cards = []
        # Filter for roughly "noon" forecasts for the daily summary
        daily_list = [x for x in self.forecast_data['list'] if '12:00:00' in x['dt_txt']][:5]
        
        for item in daily_list:
            date_txt = item['dt_txt'].split(" ")[0]
            day_name = datetime.datetime.strptime(date_txt, "%Y-%m-%d").strftime("%a")
            
            f_temp = self.convert_temp(item['main']['temp'])
            f_icon = item['weather'][0]['icon']
            f_url = f"https://openweathermap.org/img/wn/{f_icon}@2x.png"
            
            cards.append(ft.Container(
                padding=10, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK if is_dark else ft.Colors.WHITE),
                border_radius=10,
                content=ft.Column([
                    ft.Text(day_name, size=12, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Image(src=f_url, width=40, height=40),
                    ft.Text(f"{f_temp:.0f}{unit_symbol}", size=12, color=text_color)
                ], spacing=2, horizontal_alignment="center")
            ))
            
        return ft.Column([
            ft.Text("5-Day Forecast", weight=ft.FontWeight.BOLD, color=text_color),
            ft.Row(cards, alignment="center", scroll=ft.ScrollMode.HIDDEN)
        ])

    def create_info_card(self, icon, label, value, is_dark):
        color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        return ft.Container(
            padding=10, bgcolor=ft.Colors.with_opacity(0.1, color), border_radius=10, width=90,
            content=ft.Column([
                ft.Icon(icon, size=20, color=color),
                ft.Text(label, size=10, color=color),
                ft.Text(value, size=12, weight=ft.FontWeight.BOLD, color=color)
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