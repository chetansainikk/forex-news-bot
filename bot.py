import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread

# ====================================
# CONFIG
# ====================================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501994314086223924/MB-Tp5cFqSoXSBM9yf9T39oYtOCoAKtkjivfyFJd1joU-ZsfFwoyD4Myrg-AYfcR8u87"

TIMEZONE = pytz.timezone("Asia/Kolkata")

sent_alerts = set()

# ====================================
# FLASK
# ====================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Factory News Bot Running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ====================================
# DISCORD MESSAGE
# ====================================

def send_message(msg):

    try:

        r = requests.post(
            DISCORD_WEBHOOK,
            json={"content": msg}
        )

        print("Discord:", r.status_code)

    except Exception as e:

        print("Discord Error:", e)

# ====================================
# FOREX FACTORY SCRAPER
# ====================================

def scrape_forex_factory():

    try:

        url = "https://www.forexfactory.com/calendar"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        rows = soup.find_all("tr")

        events = []

        for row in rows:

            text = row.get_text(" ", strip=True)

            if not text:
                continue

            important = [
                "USD",
                "Non-Farm",
                "CPI",
                "FOMC",
                "Powell",
                "Interest Rate"
            ]

            if any(k.lower() in text.lower() for k in important):

                events.append(text)

        return list(set(events))[:15]

    except Exception as e:

        print("Scraping Error:", e)

        return []

# ====================================
# WEEKLY NEWS
# ====================================

def send_weekly_news():

    news = scrape_forex_factory()

    if not news:

        send_message("⚠️ Could not fetch Forex Factory news")

        return

    msg = (
        "📅 **HIGH IMPACT USD NEWS THIS WEEK**\n\n"
        "💰 Affects: XAUUSD & NASDAQ\n\n"
    )

    for event in news:

        msg += f"• {event}\n\n"

    send_message(msg)

# ====================================
# 15 MINUTE ALERT SYSTEM
# ====================================

def check_news_alerts():

    now = datetime.now(TIMEZONE)

    current_time = now.strftime("%H:%M")

    important_times = [
        "18:15",
        "18:45",
        "19:15",
        "20:15",
        "21:15",
        "22:15",
        "23:15"
    ]

    for t in important_times:

        if current_time == t:

            if t in sent_alerts:
                continue

            send_message(
                "🚨 **HIGH IMPACT USD NEWS IN 15 MINUTES**\n\n"
                "⚠️ Reduce risk on XAUUSD & NASDAQ\n"
                "📉 Expect volatility spikes"
            )

            sent_alerts.add(t)

# ====================================
# SCHEDULES
# ====================================

schedule.every().sunday.at("18:00").do(send_weekly_news)

schedule.every(1).minutes.do(check_news_alerts)

# ====================================
# MAIN LOOP
# ====================================

def run_bot():

    send_message(
        "✅ Forex Factory XAUUSD/NASDAQ Bot LIVE"
    )

    while True:

        schedule.run_pending()

        time.sleep(30)

# ====================================
# START
# ====================================

if __name__ == "__main__":

    flask_thread = Thread(target=run_flask)

    flask_thread.start()

    run_bot()
