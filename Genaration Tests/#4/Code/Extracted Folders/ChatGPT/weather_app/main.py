"""
Modern desktop Weather app.

Run:
    python main.py

The application starts the local FastAPI server on localhost, opens a
fullscreen CustomTkinter GUI, and shuts the server down when the GUI exits.
"""

from __future__ import annotations

import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import customtkinter as ctk
import httpx
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


APP_DIR = Path(__file__).resolve().parent
API_BASE = "http://127.0.0.1:8000"
THEMES = {
    "Midnight": {
        "bg": "#0B1020",
        "panel": "#131B2E",
        "panel2": "#1B2640",
        "text": "#F4F7FB",
        "muted": "#AAB6CC",
        "accent": "#62B0FF",
        "accent_hover": "#3E98F0",
        "border": "#273654",
    },
    "Ocean": {
        "bg": "#071A24",
        "panel": "#0D2A38",
        "panel2": "#12394A",
        "text": "#F0FBFF",
        "muted": "#9CC2CF",
        "accent": "#55D6BE",
        "accent_hover": "#36BCA5",
        "border": "#1E5264",
    },
    "Sunset": {
        "bg": "#21131A",
        "panel": "#331C24",
        "panel2": "#47252E",
        "text": "#FFF6EF",
        "muted": "#D6B5A5",
        "accent": "#FF9A62",
        "accent_hover": "#F17B3C",
        "border": "#663542",
    },
    "Forest": {
        "bg": "#0D1A14",
        "panel": "#15271E",
        "panel2": "#1C3528",
        "text": "#F1FAF3",
        "muted": "#A8C1AF",
        "accent": "#80D49B",
        "accent_hover": "#61BF7F",
        "border": "#2C4B39",
    },
}

WEATHER_LABELS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm + hail",
    99: "Thunderstorm + heavy hail",
}

WEATHER_SYMBOLS = {
    0: "☀", 1: "🌤", 2: "⛅", 3: "☁", 45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧", 56: "🌧", 57: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧", 66: "🌧", 67: "🌧",
    71: "🌨", 73: "🌨", 75: "❄", 77: "❄",
    80: "🌦", 81: "🌧", 82: "⛈", 85: "🌨", 86: "❄",
    95: "⛈", 96: "⛈", 99: "⛈",
}


class WeatherApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.theme_name = "Midnight"
        self.theme = THEMES[self.theme_name]
        self.weather_data: dict[str, Any] | None = None
        self.api_process: subprocess.Popen[str] | None = None
        self.http_client = httpx.Client(timeout=10.0)
        self.search_lock = threading.Lock()

        self.title("Modern Weather")
        self.configure(fg_color=self.theme["bg"])
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _event: self.toggle_fullscreen())
        self.bind("<Return>", lambda _event: self.search_city())

        self._build_ui()
        self._apply_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.search_entry.focus_set()
        self.after(250, self.search_city)

    def _build_ui(self) -> None:
        self.header = ctk.CTkFrame(self, corner_radius=0)
        self.header.pack(fill="x", padx=0, pady=0)

        self.brand = ctk.CTkLabel(
            self.header, text="WEATHER", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.brand.pack(side="left", padx=28, pady=22)

        self.theme_menu = ctk.CTkOptionMenu(
            self.header,
            values=list(THEMES.keys()),
            command=self.change_theme,
            width=150,
            height=36,
        )
        self.theme_menu.set(self.theme_name)
        self.theme_menu.pack(side="right", padx=(8, 28), pady=20)

        self.fullscreen_button = ctk.CTkButton(
            self.header, text="Exit Fullscreen", width=130,
            command=self.toggle_fullscreen
        )
        self.fullscreen_button.pack(side="right", padx=8, pady=20)

        self.search_entry = ctk.CTkEntry(
            self.header,
            placeholder_text="Search for a city…",
            width=300,
            height=38,
            font=ctk.CTkFont(size=14),
        )
        self.search_entry.pack(side="right", padx=8, pady=20)

        self.search_button = ctk.CTkButton(
            self.header, text="Search", width=90, height=38,
            command=self.search_city
        )
        self.search_button.pack(side="right", padx=8, pady=20)

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=22, pady=22)

        self.hero = ctk.CTkFrame(self.content, corner_radius=18)
        self.hero.pack(fill="x", padx=20, pady=(20, 12))

        self.location_label = ctk.CTkLabel(
            self.hero, text="Loading weather…",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.location_label.pack(anchor="w", padx=28, pady=(24, 2))

        self.updated_label = ctk.CTkLabel(self.hero, text="", font=ctk.CTkFont(size=13))
        self.updated_label.pack(anchor="w", padx=30, pady=(0, 18))

        self.hero_grid = ctk.CTkFrame(self.hero, fg_color="transparent")
        self.hero_grid.pack(fill="x", padx=24, pady=(0, 26))

        self.condition_icon = ctk.CTkLabel(
            self.hero_grid, text="☀", font=ctk.CTkFont(size=76)
        )
        self.condition_icon.grid(row=0, column=0, rowspan=2, padx=(0, 28), sticky="w")

        self.temperature_label = ctk.CTkLabel(
            self.hero_grid, text="--°", font=ctk.CTkFont(size=64, weight="bold")
        )
        self.temperature_label.grid(row=0, column=1, sticky="w")

        self.condition_label = ctk.CTkLabel(
            self.hero_grid, text="Waiting for data",
            font=ctk.CTkFont(size=20)
        )
        self.condition_label.grid(row=1, column=1, sticky="w")

        self.metrics_frame = ctk.CTkFrame(self.hero_grid, fg_color="transparent")
        self.metrics_frame.grid(row=0, column=2, rowspan=2, padx=70, sticky="e")
        self.metrics_labels: dict[str, ctk.CTkLabel] = {}
        for row, (key, title) in enumerate([
            ("feels", "Feels like"),
            ("humidity", "Humidity"),
            ("wind", "Wind"),
            ("rain", "Precipitation"),
        ]):
            title_label = ctk.CTkLabel(
                self.metrics_frame, text=title.upper(),
                font=ctk.CTkFont(size=11, weight="bold")
            )
            title_label.grid(row=row, column=0, padx=10, pady=4, sticky="w")
            value = ctk.CTkLabel(
                self.metrics_frame, text="—",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            value.grid(row=row, column=1, padx=10, pady=4, sticky="e")
            self.metrics_labels[key] = value

        self.lower = ctk.CTkFrame(self.content, fg_color="transparent")
        self.lower.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.chart_card = ctk.CTkFrame(self.lower, corner_radius=18)
        self.chart_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.chart_title = ctk.CTkLabel(
            self.chart_card, text="7-Day Temperature Forecast",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.chart_title.pack(anchor="w", padx=22, pady=(18, 5))

        self.figure = Figure(figsize=(8, 3.8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.chart_card)
        self.figure_canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.daily_card = ctk.CTkFrame(self.lower, corner_radius=18, width=430)
        self.daily_card.pack(side="right", fill="y", padx=(10, 0))
        self.daily_card.pack_propagate(False)

        self.daily_title = ctk.CTkLabel(
            self.daily_card, text="Daily Outlook",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.daily_title.pack(anchor="w", padx=22, pady=(18, 8))

        self.daily_rows: list[ctk.CTkFrame] = []

        self.status_label = ctk.CTkLabel(
            self, text="Ready", anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(fill="x", padx=28, pady=(0, 10))

    def _apply_theme(self) -> None:
        t = self.theme
        self.configure(fg_color=t["bg"])
        self.header.configure(fg_color=t["panel"])
        self.content.configure(fg_color=t["bg"])
        self.hero.configure(fg_color=t["panel"])
        self.lower.configure(fg_color=t["bg"])
        self.chart_card.configure(fg_color=t["panel"])
        self.daily_card.configure(fg_color=t["panel"])

        for label in [
            self.brand, self.location_label, self.updated_label,
            self.condition_icon, self.temperature_label, self.condition_label,
            self.chart_title, self.daily_title, self.status_label
        ]:
            label.configure(text_color=t["text"])
        self.updated_label.configure(text_color=t["muted"])
        self.status_label.configure(text_color=t["muted"])

        for value in self.metrics_labels.values():
            value.configure(text_color=t["text"])

        self.search_entry.configure(
            fg_color=t["panel2"], border_color=t["border"],
            text_color=t["text"], placeholder_text_color=t["muted"]
        )
        self.search_button.configure(
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color=t["bg"]
        )
        self.fullscreen_button.configure(
            fg_color=t["panel2"], hover_color=t["border"], text_color=t["text"]
        )
        self.theme_menu.configure(
            fg_color=t["panel2"], button_color=t["accent"],
            button_hover_color=t["accent_hover"], text_color=t["text"]
        )
        self._draw_chart()

    def change_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self._apply_theme()
        if self.weather_data:
            self._render_daily(self.weather_data)

    def toggle_fullscreen(self) -> None:
        current = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not current)
        self.fullscreen_button.configure(
            text="Exit Fullscreen" if not current else "Fullscreen"
        )

    def search_city(self) -> None:
        city = self.search_entry.get().strip()
        if not city:
            return
        if self.search_lock.locked():
            return

        self.status_label.configure(text=f"Searching for {city}…")
        self.search_button.configure(state="disabled")
        threading.Thread(target=self._fetch_weather, args=(city,), daemon=True).start()

    def _fetch_weather(self, city: str) -> None:
        with self.search_lock:
            try:
                response = self.http_client.get(
                    f"{API_BASE}/weather", params={"city": city}
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.json().get("detail", "Weather request failed.")
                self.after(0, lambda: self._show_error(str(detail)))
                return
            except Exception as exc:
                self.after(0, lambda: self._show_error(
                    f"Could not connect to the local weather service: {exc}"
                ))
                return

        self.after(0, lambda: self._render_weather(data))

    def _show_error(self, message: str) -> None:
        self.status_label.configure(text=message)
        self.search_button.configure(state="normal")

    def _render_weather(self, data: dict[str, Any]) -> None:
        self.weather_data = data
        location = data["location"]
        current = data["current"]

        place = location["name"]
        region = location.get("admin1")
        country = location.get("country")
        subtitle = ", ".join(x for x in [region, country] if x)

        self.location_label.configure(
            text=f"{place}{', ' + subtitle if subtitle else ''}"
        )
        self.updated_label.configure(
            text=f"Updated {datetime.now().strftime('%d %b %Y, %H:%M')}  •  "
                 f"{location.get('timezone', 'local time')}"
        )

        code = int(current.get("weather_code", 0))
        self.condition_icon.configure(text=WEATHER_SYMBOLS.get(code, "☀"))
        self.temperature_label.configure(
            text=f"{current.get('temperature_2m', '--'):.0f}°"
        )
        self.condition_label.configure(text=WEATHER_LABELS.get(code, "Unknown"))

        self.metrics_labels["feels"].configure(
            text=f"{current.get('apparent_temperature', '—')}°C"
        )
        self.metrics_labels["humidity"].configure(
            text=f"{current.get('relative_humidity_2m', '—')}%"
        )
        self.metrics_labels["wind"].configure(
            text=f"{current.get('wind_speed_10m', '—')} km/h"
        )
        self.metrics_labels["rain"].configure(
            text=f"{current.get('precipitation', '—')} mm"
        )

        self._render_daily(data)
        self._draw_chart()
        self.status_label.configure(text="Weather loaded.")
        self.search_button.configure(state="normal")

    def _render_daily(self, data: dict[str, Any]) -> None:
        for row in self.daily_rows:
            row.destroy()
        self.daily_rows.clear()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        codes = daily.get("weather_code", [])
        highs = daily.get("temperature_2m_max", [])
        lows = daily.get("temperature_2m_min", [])
        rain = daily.get("precipitation_probability_max", [])

        for i in range(min(7, len(dates))):
            row = ctk.CTkFrame(
                self.daily_card, corner_radius=12, fg_color=self.theme["panel2"]
            )
            row.pack(fill="x", padx=16, pady=4)
            self.daily_rows.append(row)

            try:
                day = datetime.fromisoformat(dates[i]).strftime("%a")
            except ValueError:
                day = dates[i]

            ctk.CTkLabel(
                row, text=day, width=55,
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(side="left", padx=10, pady=10)

            ctk.CTkLabel(
                row, text=WEATHER_SYMBOLS.get(int(codes[i]), "•"),
                font=ctk.CTkFont(size=20)
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row, text=f"{highs[i]:.0f}° / {lows[i]:.0f}°",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row, text=f"{rain[i]}%",
                text_color=self.theme["muted"],
                font=ctk.CTkFont(size=12)
            ).pack(side="right", padx=12)

    def _draw_chart(self) -> None:
        self.ax.clear()
        self.ax.set_facecolor(self.theme["panel"])
        self.figure.patch.set_facecolor(self.theme["panel"])

        if not self.weather_data:
            self.ax.text(
                0.5, 0.5, "Search for a city to see the forecast",
                ha="center", va="center",
                transform=self.ax.transAxes,
                color=self.theme["muted"], fontsize=12
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.figure_canvas.draw_idle()
            return

        daily = self.weather_data["daily"]
        dates = [datetime.fromisoformat(x) for x in daily["time"]]
        highs = daily["temperature_2m_max"]
        lows = daily["temperature_2m_min"]

        self.ax.plot(dates, highs, marker="o", linewidth=2.5, label="High")
        self.ax.plot(dates, lows, marker="o", linewidth=2.5, label="Low")
        self.ax.fill_between(dates, lows, highs, alpha=0.10)

        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%a"))
        self.ax.grid(alpha=0.15)
        self.ax.tick_params(axis="both", colors=self.theme["muted"], labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.legend(
            frameon=False, labelcolor=self.theme["text"],
            loc="upper left", ncols=2
        )
        self.ax.set_ylabel("°C", color=self.theme["muted"])
        self.figure.tight_layout(pad=1.2)
        self.figure_canvas.draw_idle()

    def on_close(self) -> None:
        try:
            self.http_client.close()
        except Exception:
            pass

        if self.api_process and self.api_process.poll() is None:
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.api_process.kill()

        self.destroy()


def start_backend() -> subprocess.Popen[str]:
    # Running uvicorn as a child process isolates the FastAPI event loop from
    # Tk's main loop and keeps the GUI responsive.
    command = [
        sys.executable, "-m", "uvicorn",
        "backend:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "warning",
    ]
    return subprocess.Popen(
        command, cwd=str(APP_DIR), stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, text=True
    )


def wait_for_backend(process: subprocess.Popen[str]) -> None:
    deadline = time.time() + 8
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("FastAPI backend exited before starting.")
        try:
            with httpx.Client(timeout=0.4) as client:
                if client.get(f"{API_BASE}/health").status_code == 200:
                    return
        except Exception:
            time.sleep(0.15)
    raise RuntimeError("Timed out while starting the FastAPI backend.")


def main() -> None:
    backend_process = start_backend()
    try:
        wait_for_backend(backend_process)
        app = WeatherApp()
        app.api_process = backend_process
        app.mainloop()
    except Exception:
        if backend_process.poll() is None:
            backend_process.terminate()
        raise


if __name__ == "__main__":
    main()
