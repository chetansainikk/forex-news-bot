import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread

# ======================================
# CONFIG
# ======================================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501994314086223924/MB-Tp5cFqSoXSBM9yf9T39oYtOCoAKtkjivfyFJd1joU-ZsfFwoyD4Myrg-AYfcR8u87"

TIMEZONE = pytz.timezone("Asia/Kolkata")

sent_alerts = set()

# ======================================
# FLASK SERVER
# ======================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Factory Pro Bot Running"


def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ======================================
# DISCORD EMBED MESSAGE
# ======================================


def send_embed(title, description, color=16711680):

    data = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }

    try:

        r = requests.post(
            DISCORD_WEBHOOK,
            json=data,
            timeout=10
        )

        print("Discord:", r.status_code)

    except Exception as e:

        print("Discord Error:", e)

# ======================================
# FOREX FACTORY SCRAPER
# ======================================


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

        soup = BeautifulSoup(response.text, "lxml")

        rows = soup.find_all("tr")

        events = []

        current_date = ""

        for row in rows:

            text = row.get_text(" ", strip=True)

            if not text:
                continue

            # Only important USD news
            important_keywords = [
                "USD",
                "Non-Farm Payrolls",
                "CPI",
                "FOMC",
                "Powell",
                "Interest Rate"
            ]

            if any(k.lower() in text.lower() for k in important_keywords):

                # Try to detect time
                detected_time = None

                possible_times = [
                    "6:00pm",
                    "6:30pm",
                    "7:00pm",
                    "8:00pm",
                    "11:30pm"
                ]

                lower_text = text.lower()

                for t in possible_times:
                    if t in lower_text:
                        detected_time = t
                        break

                events.append({
                    "text": text,
                    "time": detected_time
                })

        return events[:15]

    except Exception as e:

        print("Scrape Error:", e)

        return []

# ======================================
# WEEKLY NEWS SUMMARY
# ======================================


def weekly_news():

    news = scrape_forex_factory()

    if not news:

        send_embed(
            "⚠️ Forex Factory Error",
            "Could not fetch weekly news"
        )

        return

    desc = "💰 Affects: XAUUSD & NASDAQ\n\n"

    for event in news:

        desc += f"• {event['text']}\n\n"

    send_embed(
        "📅 HIGH IMPACT USD NEWS THIS WEEK",
        desc,
        16753920
    )

# ======================================
# EVENT ALERTS
# ======================================


def check_news_alerts():

    news = scrape_forex_factory()

    now = datetime.now(TIMEZONE)

    current_time = now.strftime("%I:%M%p").lower()

    for event in news:

        event_time = event["time"]

        if not event_time:
            continue

        try:

            event_dt = datetime.strptime(
                event_time,
                "%I:%M%p"
            )

            reminder_dt = event_dt - timedelta(minutes=15)

            reminder_time = reminder_dt.strftime(
                "%I:%M%p"
            ).lower()

            unique_id = f"{event['text']}_{reminder_time}"

            if (
                current_time == reminder_time and
                unique_id not in sent_alerts
            ):

                desc = (
                    f"🚨 {event['text']}\n\n"
                    f"⚠️ High volatility expected\n\n"
                    f"Most affected:\n"
                    f"• XAUUSD\n"
                    f"• NASDAQ\n\n"
                    f"Consider reducing risk before release"
                )

                send_embed(
                    "🚨 NEWS IN 15 MINUTES",
                    desc,
                    16711680
                )

                sent_alerts.add(unique_id)

        except Exception as e:

            print("Alert Error:", e)

# ======================================
# SCHEDULES
# ======================================

schedule.every().sunday.at("18:00").do(weekly_news)

schedule.every(1).minutes.do(check_news_alerts)

# ======================================
# MAIN LOOP
# ======================================


def run_bot():

    send_embed(
        "🧪 PRO BOT TEST",
        "If you see this embed, the pro bot works correctly.",
    65280
    )

    while True:

        schedule.run_pending()

        time.sleep(30)

# ======================================
# START
# ======================================

if __name__ == "__main__":

    flask_thread = Thread(target=run_flask)

    flask_thread.start()

    run_bot()
