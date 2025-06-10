from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv
from apis.weather import get_weather
from apis.gemini import ask_gemini
from apis.news_api import get_news
from apis.joke_api import get_joke
from apis.facts_api import get_fact
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import datetime

scheduler = AsyncIOScheduler()

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
user_chats = {}

async def haber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_news = get_news()
    prompt = f"Bu haberleri kullanarak kullanıcının anlayacağı şekilde kısa ve akıcı bir haber özeti yap: {raw_news}"
    yanit = ask_gemini(prompt)
    await update.message.reply_text(yanit)

async def saka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_joke = get_joke()
    prompt = f"Bu şakayı daha eğlenceli hale getir: {raw_joke}"
    yanit = ask_gemini(prompt)
    await update.message.reply_text(yanit)

async def bilgi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_fact = get_fact()
    prompt = f"Kullanıcıya anlatmak için bu bilgiyi sohbet tarzında açıkla: {raw_fact}"
    yanit = ask_gemini(prompt)
    await update.message.reply_text(yanit)

async def get_intent_from_gemini(text):
    # Gemini API'ye mesajı gönder, gelen cevaptan niyeti çıkar
    # Örnek olarak:
    if "hava" in text:
        return "hava_durumu"
    elif "haber" in text:
        return "guncel_haber"
    elif "espri" in text:
        return "espri"
    elif "bilgi" in text:
        return "ilginc_bilgi"
    else:
        return "sohbet"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Selam! Ben senin bilge botunum. /hava ve /sohbet komutlarını deneyebilirsin.")

async def hava(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sehir = "Ashgabat"  # default şehir koyabilirsin
    bilgi = get_weather(sehir)
    await update.message.reply_text(bilgi)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mesaj = update.message.text.lower()

    # Kullanıcının önceki mesajları yoksa yeni liste oluştur
    if user_id not in user_chats:
        user_chats[user_id] = []

    # Yeni mesajı listeye ekle
    user_chats[user_id].append(f"Kullanıcı: {mesaj}")

    # Listenin uzunluğunu 4 ile sınırla
    if len(user_chats[user_id]) > 4:
        user_chats[user_id].pop(0)

    # Intent kontrol fonksiyonları (kendin yazacaksın)
    if hava_sorusu_var_mi(mesaj):
        sehir = sehir_cek(mesaj)
        hava = get_weather(sehir)
        user_chats[user_id].append(f"Bot: {hava}")
        prompt = "\n".join(user_chats[user_id]) + "\nBot: Bu bilgiyi konuşma tarzında açıkla."
        yanit = ask_gemini(prompt)

    elif haber_sorusu_var_mi(mesaj):
        haberler = get_news()
        user_chats[user_id].append(f"Bot: {haberler}")
        prompt = "\n".join(user_chats[user_id]) + "\nBot: Haberleri sohbet tarzında açıkla."
        yanit = ask_gemini(prompt)

    elif espri_sorusu_var_mi(mesaj):
        espri = get_joke()
        user_chats[user_id].append(f"Bot: {espri}")
        prompt = "\n".join(user_chats[user_id]) + "\nBot: Bu espriyi sohbet havasında tekrar anlat."
        yanit = ask_gemini(prompt)

    elif bilgi_sorusu_var_mi(mesaj):
        bilgi = get_fact()
        user_chats[user_id].append(f"Bot: {bilgi}")
        prompt = "\n".join(user_chats[user_id]) + "\nBot: Bu bilgiyi sohbet tarzında paylaş."
        yanit = ask_gemini(prompt)

    else:
        prompt = "\n".join(user_chats[user_id]) + "\nBot:"
        yanit = ask_gemini(prompt)

    # Botun cevabını listeye ekle
    user_chats[user_id].append(f"Bot: {yanit}")

    # Yine 4 mesajla sınırla
    if len(user_chats[user_id]) > 4:
        user_chats[user_id].pop(0)

    await update.message.reply_text(yanit)




async def sohbet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🗣️ Lütfen bir şey yaz: /sohbet [mesaj]")
        return

    user_message = " ".join(context.args)
    yanit = ask_gemini(user_message)
    await update.message.reply_text(yanit)

async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = YOUR_TELEGRAM_CHAT_ID
    await context.bot.send_message(chat_id=chat_id, text="Scheduled message!")


async def send_scheduled_messages(app):
    chat_id = YOUR_TELEGRAM_CHAT_ID  # kendi Telegram chat ID'n burada

    # Haber
    raw_news = get_news()
    prompt_news = f"Bugünün önemli haberleri: {raw_news}. Bunu sohbet havasında açıkla."
    yanit_news = ask_gemini(prompt_news)
    await app.bot.send_message(chat_id=chat_id, text=yanit_news)

    # Şaka
    raw_joke = get_joke()
    prompt_joke = f"Bu şakayı eğlenceli şekilde anlat: {raw_joke}"
    yanit_joke = ask_gemini(prompt_joke)
    await app.bot.send_message(chat_id=chat_id, text=yanit_joke)

    # İlginç Bilgi
    raw_fact = get_fact()
    prompt_fact = f"Şimdi de şöyle enteresan bir bilgi var: {raw_fact}"
    yanit_fact = ask_gemini(prompt_fact)
    await app.bot.send_message(chat_id=chat_id, text=yanit_fact)


async def send_good_morning(app, chat_id):
    hava = get_weather()
    mesaj = f"Günaydın! ☀️ Bugün hava durumu şöyle: {hava}"
    await app.bot.send_message(chat_id=chat_id, text=mesaj)

async def send_news(app, chat_id):
    haberler = get_news()
    prompt = f"Güncel haberler: {haberler}"
    yanit = ask_gemini(prompt)
    await app.bot.send_message(chat_id=chat_id, text=yanit)

async def send_fact(app, chat_id):
    bilgi = get_fact()
    yanit = ask_gemini(f"Bu bilgiyi sohbet havasında paylaş: {bilgi}")
    await app.bot.send_message(chat_id=chat_id, text=yanit)

async def send_joke(app, chat_id):
    espri = get_joke()
    yanit = ask_gemini(f"Bu espriyi daha eğlenceli yap: {espri}")
    await app.bot.send_message(chat_id=chat_id, text=yanit)

async def send_evening_weather(app, chat_id):
    hava = get_weather()
    mesaj = f"Akşam hava durumu şöyle: {hava}"
    await app.bot.send_message(chat_id=chat_id, text=mesaj)

async def send_good_night(app, chat_id):
    mesaj = "İyi geceler! 🌙 Yarın görüşmek üzere."
    await app.bot.send_message(chat_id=chat_id, text=mesaj)

async def schedule_jobs(app):
    chat_ids = [7172270461, 1234567890]

    scheduler.add_job(send_good_morning, 'cron', hour=8, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_news, 'cron', hour=10, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_fact, 'cron', hour=12, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_joke, 'cron', hour=14, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_news, 'cron', hour=16, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_evening_weather, 'cron', hour=18, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_joke, 'cron', hour=20, minute=0, args=[app, chat_ids])
    scheduler.add_job(send_good_night, 'cron', hour=22, minute=0, args=[app, chat_ids])

    scheduler.start()







def hava_sorusu_var_mi(mesaj: str):
    anahtar_kelimeler = ["hava", "sıcaklık", "soğuk", "yağmur", "bulut", "güneş"]
    return any(kelime in mesaj.lower() for kelime in anahtar_kelimeler)

def sehir_cek(mesaj: str):
    sehirler = ["Ashgabat", "Istanbul", "Ankara", "London", "New York", "Madrid", "Berlin"]
    for sehir in sehirler:
        if sehir.lower() in mesaj.lower():
            return sehir
    return "Ashgabat"  # default şehir


# Örnek intent fonksiyonları:

def haber_sorusu_var_mi(mesaj):
    return any(kw in mesaj for kw in ["haber", "güncel haber", "son dakika"])

def espri_sorusu_var_mi(mesaj):
    return any(kw in mesaj for kw in ["espri", "şaka", "komik"])

def bilgi_sorusu_var_mi(mesaj):
    return any(kw in mesaj for kw in ["ilginç bilgi", "bilgi", "fakt"])


async def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hava", hava))
    app.add_handler(CommandHandler("sohbet", sohbet))
    app.add_handler(CommandHandler("haber", haber))
    app.add_handler(CommandHandler("saka", saka))
    app.add_handler(CommandHandler("bilgi", bilgi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Railway’de çalışıyor...")

    # Scheduler'ı başlat
    await schedule_jobs(app)

    # polling başlat, kendi içinde idle çalıştırır
    await app.run_polling()


