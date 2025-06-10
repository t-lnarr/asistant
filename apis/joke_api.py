import requests

def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?type=single"
    res = requests.get(url)
    data = res.json()
    return data.get("joke", "Bir şaka bulamadım, üzgünüm!")
