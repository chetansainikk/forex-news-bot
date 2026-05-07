import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

# =========================
# CONFIG
# =========================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501994314086223924/MB-Tp5cFqSoXSBM9yf9T39oYtOCoAKtkjivfyFJd1joU-ZsfFwoyD4Myrg-AYfcR8u87"

TIMEZONE = pytz.timezone("Asia/Kolkata")

# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex News Bot Running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# =========================
# SEND MESSAGE
# =========================

def send_message(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# =========================
# GET FOREX FACTORY NEWS
# =========================

def get_news():

    url = "https://www.forexfactory.com/calendar"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text("\n")

    keywords = [
        "CPI",
        "FOMC",
        "NFP",
        "Powell",
        "Interest Rate"
    ]

    results = []

    for line in text.split("\n"):

        clean = line.strip()

        for key in keywords:

            if key.lower() in clean.lower():

                if clean not in results:
                    results.append(clean)

    return results[:10]

# =========================
# WEEKLY NEWS
# =========================

def weekly_news():

    news = get_news()

    if not news:
        return

    msg = "📅 **HIGH IMPACT NEWS THIS WEEK**\n\n"

    for item in news:
        msg += f"• {item}\n"

    send_message(msg)

# =========================
# REMINDER
# =========================

def reminder():

    send_message(
        "🚨 **HIGH IMPACT NEWS IN 15 MINUTES**\n\nReduce risk on XAUUSD / GER40"
    )

# =========================
# SCHEDULES
# =========================

schedule.every().sunday.at("18:00").do(weekly_news)

schedule.every().day.at("17:45").do(reminder)

# =========================
# MAIN LOOP
# =========================

def run_bot():

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":

    send_message("✅ TEST MESSAGE FROM FOREX BOT")

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    run_bot()
