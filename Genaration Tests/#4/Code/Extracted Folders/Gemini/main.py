import sys
import threading
import requests
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configure CustomTkinter default settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Open-Meteo Weather App")
        
        # Force Fullscreen on open
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))

        self.backend_url = "http://127.0.0.1:8000/weather"
        
        # Color theme configurations for Matplotlib matching
        self.theme_colors = {
            "Dark": {"bg": "#2b2b2b", "fg": "#ffffff", "line": "#1f538d", "grid": "#444444"},
            "Light": {"bg": "#dbdbdb", "fg": "#000000", "line": "#3b8ed0", "grid": "#cccccc"},
            "System": {"bg": "#2b2b2b", "fg": "#ffffff", "line": "#1f538d", "grid": "#444444"}
        }

        self.setup_ui()

    def setup_ui(self):
        # Header / Control Bar Frame
        self.top_frame = ctk.CTkFrame(self, corner_radius=10)
        self.top_frame.pack(fill="x", padx=20, pady=20)

        # Search Box
        self.city_entry = ctk.CTkEntry(
            self.top_frame, placeholder_text="Enter City Name (e.g. London, Tokyo)...", width=300, font=("Helvetica", 14)
        )
        self.city_entry.pack(side="left", padx=15, pady=15)
        self.city_entry.bind("<Return>", lambda event: self.fetch_weather())

        # Search Button
        self.search_btn = ctk.CTkButton(
            self.top_frame, text="Search Weather", command=self.fetch_weather, font=("Helvetica", 14, "bold")
        )
        self.search_btn.pack(side="left", padx=10, pady=15)

        # Preset Theme Switcher
        self.theme_label = ctk.CTkLabel(self.top_frame, text="Theme:", font=("Helvetica", 14))
        self.theme_label.pack(side="left", padx=(30, 5))

        self.theme_option = ctk.CTkOptionMenu(
            self.top_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            font=("Helvetica", 13)
        )
        self.theme_option.pack(side="left", padx=5)

        # Close App Button
        self.close_btn = ctk.CTkButton(
            self.top_frame, text="Exit Fullscreen / Quit", fg_color="transparent", border_width=1, command=self.destroy
        )
        self.close_btn.pack(side="right", padx=15)

        # Content Dashboard Frame
        self.dashboard = ctk.CTkFrame(self, corner_radius=15)
        self.dashboard.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # City & Temperature Summary Label
        self.info_label = ctk.CTkLabel(
            self.dashboard,
            text="Search for a city to display weather metrics.",
            font=("Helvetica", 22, "bold")
        )
        self.info_label.pack(anchor="w", padx=30, pady=(25, 5))

        # Detailed Metrics Label
        self.details_label = ctk.CTkLabel(
            self.dashboard,
            text="",
            font=("Helvetica", 14),
            justify="left"
        )
        self.details_label.pack(anchor="w", padx=30, pady=(0, 15))

        # Matplotlib Container Frame
        self.chart_frame = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Matplotlib Figure Initialization
        self.fig, self.ax = plt.subplots(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.update_chart_style("Dark")

    def change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        self.update_chart_style(new_theme)

    def update_chart_style(self, theme: str):
        colors = self.theme_colors.get(theme, self.theme_colors["Dark"])
        self.fig.patch.set_facecolor(colors["bg"])
        self.ax.set_facecolor(colors["bg"])
        self.ax.tick_params(colors=colors["fg"], labelsize=10)
        self.ax.spines['bottom'].set_color(colors["fg"])
        self.ax.spines['top'].set_color(colors["fg"])
        self.ax.spines['left'].set_color(colors["fg"])
        self.ax.spines['right'].set_color(colors["fg"])
        self.ax.xaxis.label.set_color(colors["fg"])
        self.ax.yaxis.label.set_color(colors["fg"])
        self.ax.title.set_color(colors["fg"])
        self.canvas.draw()

    def fetch_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            self.info_label.configure(text="Please enter a valid city name.")
            return

        self.info_label.configure(text=f"Loading weather for '{city}'...")
        # Asynchronous fetch using threading to avoid locking GUI
        threading.Thread(target=self._async_fetch, args=(city,), daemon=True).start()

    def _async_fetch(self, city: str):
        try:
            response = requests.get(self.backend_url, params={"city": city}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.after(0, self._render_weather, data)
            elif response.status_code == 404:
                self.after(0, lambda: self.info_label.configure(text=f"City '{city}' not found."))
            else:
                self.after(0, lambda: self.info_label.configure(text="Failed to retrieve weather data."))
        except Exception as e:
            self.after(0, lambda: self.info_label.configure(text="Error: Is backend.py running on port 8000?"))

    def _render_weather(self, data: dict):
        city = data["city"]
        temp = data["current_temperature"]
        wind = data["windspeed"]
        times = data["hourly_times"]
        temps = data["hourly_temps"]

        self.info_label.configure(text=f"{city}: {temp} °C")
        self.details_label.configure(text=f"Wind Speed: {wind} km/h  |  Forecast Horizon: 24 Hours")

        # Plot 24-hour temperature trend line chart
        self.ax.clear()
        current_theme = self.theme_option.get()
        colors = self.theme_colors.get(current_theme, self.theme_colors["Dark"])

        self.ax.plot(times, temps, marker='o', color=colors["line"], linewidth=2.5, markersize=4)
        self.ax.set_title("24-Hour Temperature Forecast (°C)", fontsize=12, pad=10)
        self.ax.set_xlabel("Time (Local)", fontsize=10)
        self.ax.set_ylabel("Temperature (°C)", fontsize=10)
        self.ax.grid(True, linestyle="--", alpha=0.5, color=colors["grid"])
        self.ax.tick_params(axis='x', rotation=45)

        self.fig.tight_layout()
        self.update_chart_style(current_theme)

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()