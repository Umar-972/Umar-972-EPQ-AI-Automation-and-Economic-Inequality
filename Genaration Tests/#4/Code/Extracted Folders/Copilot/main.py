
import threading
import requests
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import uvicorn
from backend import app

THEMES = {
    'Blue': ('blue','dark'),
    'Green': ('green','dark'),
    'System': ('blue','system')
}

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Modern Weather App')
        self.attributes('-fullscreen', True)

        ctk.CTkLabel(self,text='Weather Dashboard',font=('Segoe UI',32,'bold')).pack(pady=10)

        top=ctk.CTkFrame(self)
        top.pack(fill='x',padx=20,pady=10)

        self.city=ctk.CTkEntry(top,width=250,placeholder_text='Enter city')
        self.city.pack(side='left',padx=10,pady=10)

        ctk.CTkButton(top,text='Search',command=self.search).pack(side='left',padx=10)

        self.theme=ctk.CTkOptionMenu(top,values=list(THEMES.keys()),command=self.change_theme)
        self.theme.pack(side='left',padx=10)

        self.info=ctk.CTkLabel(self,text='Search for a city')
        self.info.pack(pady=10)

        self.graph_frame=ctk.CTkFrame(self)
        self.graph_frame.pack(fill='both',expand=True,padx=20,pady=20)

        ctk.CTkButton(self,text='Exit',command=self.destroy).pack(pady=10)

    def change_theme(self,choice):
        color, mode = THEMES[choice]
        ctk.set_default_color_theme(color)
        ctk.set_appearance_mode(mode)

    def search(self):
        city=self.city.get().strip()
        if not city:
            return

        r=requests.get('http://127.0.0.1:8000/weather',params={'city':city},timeout=15)
        data=r.json()

        if 'error' in data:
            self.info.configure(text=data['error'])
            return

        current=data['weather']['current']
        self.info.configure(
            text=f"{data['city']}, {data['country']} | Temp {current['temperature_2m']}°C | Wind {current['wind_speed_10m']} km/h | {datetime.now():%Y-%m-%d %H:%M}"
        )

        hourly=data['weather']['hourly']
        temps=hourly['temperature_2m'][:24]

        for w in self.graph_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(range(len(temps)), temps)
        ax.set_title('24 Hour Temperature Forecast')
        ax.set_ylabel('°C')
        ax.grid(True)

        canvas=FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)


def start_api():
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')

if __name__=='__main__':
    threading.Thread(target=start_api, daemon=True).start()
    ctk.set_appearance_mode('dark')
    weather=WeatherApp()
    weather.mainloop()
