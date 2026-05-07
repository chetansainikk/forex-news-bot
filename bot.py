import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread

# =========================
# CONFIG
# =========================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501994314086223924/MB-Tp5cFqSoXSBM9yf9T39oYtOCoAKtkjivfyFJd1joU-ZsfFwoyD4Myrg-AYfcR8u87"

TIMEZONE = pytz.timezone("Asia/Kolkata")

sent_events = set()

# =========================
# FLASK
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Factory Bot Running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# =========================
# SEND DISCORD MESSAGE
# =========================

def send_message(message):

    requests.post(
        DISCORD_WEBHOOK,
        json={"content": message}
    )

# =========================
# SCRAPE FOREX FACTORY
# =========================

def scrape_news():

    url = "https://www.forexfactory.com/calendar"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    events = []

    rows = soup.find_all("tr")

    current_date = ""

    for row in rows:

        text = row.get_text(" ", strip=True)

        if not text:
            continue

        # ONLY HIGH IMPACT USD NEWS
        important_keywords = [
            "USD",
            "CPI",
            "FOMC",
            "NFP",
            "Powell",
            "Interest Rate"
        ]

        if any(k.lower() in text.lower() for k in important_keywords):

            events.append(text)

    return events[:15]

# =========================
# WEEKLY NEWS
# =========================

def weekly_news():

    news = scrape_news()

    if not news:
        return

    msg = "📅 **HIGH IMPACT NEWS THIS WEEK**\n\n"

    for event in news:
        msg += f"• {event}\n\n"

    send_message(msg)

# =========================
# CHECK UPCOMING EVENTS
# =========================

def check_upcoming_news():

    news = scrape_news()

    now = datetime.now(TIMEZONE)

    current_time = now.strftime("%H:%M")

    for event in news:

        if event in sent_events:
            continue

        # VERY BASIC TIME CHECK
        possible_times = [
            "18:00",
            "18:30",
            "19:00",
            "20:00",
            "21:00",
            "22:00",
            "23:00"
        ]

        for t in possible_times:

            try:

                event_time = datetime.strptime(t, "%H:%M")

                reminder_time = (
                    event_time - timedelta(minutes=15)
                ).strftime("%H:%M")

                if current_time == reminder_time:

                    send_message(
                        f"🚨 **HIGH IMPACT NEWS IN 15 MINUTES**\n\n{event}"
                    )

                    sent_events.add(event)

            except:
                pass

# =========================
# SCHEDULES
# =========================

schedule.every().sunday.at("18:00").do(weekly_news)

schedule.every(1).minutes.do(check_upcoming_news)

# =========================
# MAIN LOOP
# =========================

def run_bot():

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    run_bot()
