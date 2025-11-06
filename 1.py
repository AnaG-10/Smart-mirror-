import tkinter as tk
import requests
from datetime import datetime

WEATHER_API = "https://api.open-meteo.com/v1/forecast?latitude=22.57&longitude=88.36&current_weather=true"
NEWS_API = "https://newsdata.io/api/1/news?apikey=pub_12345&country=in&language=en&category=top"  # Replace key
QUOTE_API = "https://api.quotable.io/random"

REFRESH_TIME = 60000  # Refresh every 60 seconds


def get_weather():
    try:
        response = requests.get(WEATHER_API).json()
        temp = response['current_weather']['temperature']
        return f"Weather: {temp}°C"
    except:
        return "Weather: N/A"


def get_news():
    try:
        response = requests.get(NEWS_API).json()
        headline = response['results'][0]['title']
        return f"News: {headline}"
    except:
        return "News: N/A"


def get_quote():
    try:
        response = requests.get(QUOTE_API).json()
        return f"Quote: {response['content']}"
    except:
        return "Quote: N/A"


def update_display():
    now = datetime.now().strftime("%H:%M:%S | %d-%m-%Y")
    time_label.config(text=now)
    weather_label.config(text=get_weather())
    news_label.config(text=get_news())
    quote_label.config(text=get_quote())
    root.after(REFRESH_TIME, update_display)


root = tk.Tk()
root.title("Smart Mirror Simulation")
root.configure(bg="black")

time_label = tk.Label(root, text="", font=("Arial", 24), fg="white", bg="black")
time_label.pack(pady=20)

weather_label = tk.Label(root, text="", font=("Arial", 16), fg="lightblue", bg="black")
weather_label.pack(pady=10)

news_label = tk.Label(root, text="", font=("Arial", 14), fg="lightgreen", bg="black", wraplength=500)
news_label.pack(pady=10)

quote_label = tk.Label(root, text="", font=("Arial", 12), fg="yellow", bg="black", wraplength=500)
quote_label.pack(pady=10)

update_display()
root.mainloop()
