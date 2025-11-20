import flet as ft
import json
from pathlib import Path
from config import Config
from weather_service import WeatherService, WeatherServiceError

# Validate Config on startup
try:
    Config.validate()
except ValueError as e:
    print(f"CRITICAL ERROR: {e}")

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.service = WeatherService()
        self.search_history = []
        self.last_data = None
        self.current_unit = "metric"
        
        # Setup Page
        self.page.title = Config.APP_TITLE
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.window.center()
        
        self.build_ui()
        # Auto-load history
        self.load_history_file()

    def build_ui(self):
        """Initialize all UI components."""
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        # 1. Header
        self.title = ft.Text("Weather Pro", size=28, weight="bold")
        self.theme_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE, 
            on_click=self.toggle_theme
        )
        
        # 2. Search Area
        self.city_input = ft.TextField(
            label="City Name", 
            hint_text="e.g. Manila",
            prefix_icon=ft.Icons.LOCATION_CITY,
            expand=True,
            border_radius=10,
            on_submit=lambda e: self.page.run_task(self.get_weather)
        )
        
        self.search_btn = ft.IconButton(
            icon=ft.Icons.SEARCH,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
            on_click=lambda e: self.page.run_task(self.get_weather)
        )

        # 3. History Dropdown
        self.history_dd = ft.Dropdown(
            label="Recent Searches",
            options=[],
            on_change=self.history_selected,
            text_size=12
        )

        # 4. Weather Display Container
        self.weather_container = ft.Container(
            visible=False,
            padding=20,
            border_radius=20,
            bgcolor=ft.Colors.BLUE_900 if is_dark else ft.Colors.BLUE_50,
            animate_opacity=300,
        )
        
        self.loading = ft.ProgressRing(visible=False)
        self.error_msg = ft.Text("", color="red", visible=False)
        self.unit_btn = ft.TextButton("°C / °F", on_click=self.toggle_units)

        # Add to Page
        self.page.add(
            ft.Column([
                ft.Row([self.title, self.theme_btn], alignment="spaceBetween"),
                ft.Row([self.city_input, self.search_btn]),
                self.history_dd,
                ft.Divider(height=10, color="transparent"),
                self.loading,
                self.error_msg,
                self.weather_container
            ], scroll=ft.ScrollMode.HIDDEN)
        )

    async def get_weather(self):
        """Async task to fetch data."""
        city = self.city_input.value
        if not city: return
        
        self.loading.visible = True
        self.error_msg.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Use the separate service file
            data = await self.service.get_weather(city)
            forecast = await self.service.get_forecast(city)
            
            self.last_data = {"weather": data, "forecast": forecast}
            self.display_data()
            self.save_history(city)
            
        except WeatherServiceError as e:
            self.error_msg.value = str(e)
            self.error_msg.visible = True
        finally:
            self.loading.visible = False
            self.page.update()

    def display_data(self):
        """Render the UI with current data."""
        if not self.last_data: return
        
        data = self.last_data["weather"]
        forecast = self.last_data["forecast"]
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        txt_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        
        # Extract and Convert
        raw_temp = data['main']['temp']
        temp = self.convert(raw_temp)
        unit = "°F" if self.current_unit == "imperial" else "°C"
        
        # Update Container Content
        self.weather_container.content = ft.Column([
            self.unit_btn,
            ft.Text(f"{data['name']}, {data['sys']['country']}", size=24, weight="bold", color=txt_color),
            ft.Image(src=f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@4x.png", width=100, height=100),
            ft.Text(f"{temp:.0f}{unit}", size=50, weight="bold", color=txt_color),
            ft.Text(data['weather'][0]['description'].title(), italic=True, color=txt_color),
            ft.Divider(),
            # Details Grid
            ft.Row([
                self.detail_card("Humidity", f"{data['main']['humidity']}%", ft.Icons.WATER_DROP),
                self.detail_card("Wind", f"{data['wind']['speed']} m/s", ft.Icons.AIR),
            ], alignment="center", spacing=20),
            ft.Divider(),
            # Forecast
            self.build_forecast(forecast, txt_color, unit)
        ], horizontal_alignment="center")
        
        self.weather_container.bgcolor = ft.Colors.INDIGO_900 if is_dark else ft.Colors.BLUE_50
        self.weather_container.visible = True
        self.page.update()

    def convert(self, temp):
        """Handle Unit Conversion."""
        if self.current_unit == "imperial":
            return (temp * 9/5) + 32
        return temp

    def toggle_units(self, e):
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        self.display_data()

    def toggle_theme(self, e):
        self.page.theme_mode = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        self.theme_btn.icon = ft.Icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        self.display_data()
        self.page.update()

    # --- Helpers ---
    def detail_card(self, label, value, icon):
        return ft.Column([
            ft.Icon(icon, size=20),
            ft.Text(label, size=10),
            ft.Text(value, weight="bold")
        ], horizontal_alignment="center")

    def build_forecast(self, data, color, unit):
        if not data: return ft.Container()
        cards = []
        for item in [x for x in data['list'] if '12:00:00' in x['dt_txt']][:5]:
            t = self.convert(item['main']['temp'])
            day = item['dt_txt'].split(" ")[0]
            cards.append(ft.Container(
                padding=10, bgcolor=ft.colors.with_opacity(0.1, color), border_radius=10,
                content=ft.Column([
                    ft.Text(day[5:], size=10, color=color),
                    ft.Image(src=f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}.png", width=30, height=30),
                    ft.Text(f"{t:.0f}{unit}", size=12, weight="bold", color=color)
                ], horizontal_alignment="center")
            ))
        return ft.Row(cards, scroll=ft.ScrollMode.HIDDEN)

    # --- History Logic ---
    def save_history(self, city):
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.update_history_ui()
            with open("history.json", "w") as f: json.dump(self.search_history, f)

    def load_history_file(self):
        if Path("history.json").exists():
            with open("history.json", "r") as f: self.search_history = json.load(f)
            self.update_history_ui()

    def update_history_ui(self):
        self.history_dd.options = [ft.dropdown.Option(c) for c in self.search_history]
        self.page.update()

    def history_selected(self, e):
        self.city_input.value = e.control.value
        self.page.run_task(self.get_weather)

def main(page: ft.Page):
    WeatherApp(page)

if __name__ == "__main__":
    ft.app(target=main)