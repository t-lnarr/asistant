import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city="Ashgabat"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=tr"
    res = requests.get(url).json()

    if res.get("cod") != 200:
        return "Hava durumu alınamadı."

    desc = res["weather"][0]["description"]
    temp = res["main"]["temp"]
    feels = res["main"]["feels_like"]
    city_name = res["name"]

    return f"🌤 {city_name}: {desc}, {temp}°C (hissedilen: {feels}°C)"
