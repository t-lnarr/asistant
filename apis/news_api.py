import requests
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Ortam değişkeninden API anahtarını al
NEWS_API_KEY = os.getenv("GNEWS_API_KEY")

def get_news():
    if not NEWS_API_KEY:
        return "API anahtarı bulunamadı! Lütfen .env dosyasını kontrol edin."

    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&language=en&country=tr, us"
    response = requests.get(url)

    if response.status_code != 200:
        return "Haberler alınırken bir hata oluştu."

    data = response.json()
    articles = data.get("results", [])

    if not articles:
        return "Şu anda haber bulunmamaktadır."

    news_list = [article.get('title', 'Başlık yok') for article in articles[:5]]
    return "\n".join(news_list)
