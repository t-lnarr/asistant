import requests

def get_fact():
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    res = requests.get(url)
    data = res.json()
    return data.get("text", "Şu an enteresan bilgi yok.")
