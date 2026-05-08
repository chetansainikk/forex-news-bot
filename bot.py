import os
import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

# =====================================
# CONFIG
# =====================================

DISCORD_WEBHOOK = os.environ.get(
    "DISCORD_WEBHOOK"
)

FOREX_FACTORY_XML = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.xml"
)

TIMEZONE = pytz.timezone("Asia/Kolkata")

sent_alerts = set()

# =====================================
# FLASK KEEPALIVE
# =====================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Forex Factory XML Bot Running"

def run_flask():

    app.run(
        host='0.0.0.0',
        port=10000
    )

# =====================================
# DISCORD EMBED
# =====================================

def send_embed(
    title,
    description,
    color=16711680
):

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

# =====================================
# GET EVENTS FROM XML
# =====================================

def get_events():

    try:

        response = requests.get(
            FOREX_FACTORY_XML,
            timeout=15
        )

        root = ET.fromstring(
            response.content
        )

        events = []

        important_titles = [
            "Non-Farm",
            "CPI",
            "FOMC",
            "Powell",
            "Interest Rate",
            "PPI",
            "Core Retail Sales",
            "Retail Sales"
        ]

        for item in root.findall("event"):

            try:

                country = (
                    item.find("country").text
                )

                impact = (
                    item.find("impact").text
                )

                title = (
                    item.find("title").text
                )

                date = (
                    item.find("date").text
                )

                event_time = (
                    item.find("time").text
                )

                if (
                    country == "USD"
                    and impact == "High"
                ):

                    if any(
                        k.lower() in title.lower()
                        for k in important_titles
                    ):

                        events.append({
                            "title": title,
                            "date": date,
                            "time": event_time
                        })

            except:
                pass

        return events

    except Exception as e:

        print("XML Error:", e)

        return []

# =====================================
# WEEKLY SUMMARY
# =====================================

def weekly_summary():

    events = get_events()

    if not events:

        send_embed(
            "⚠️ Forex Factory Error",
            "Could not fetch weekly events"
        )

        return

    desc = (
        "💰 Affects: XAUUSD & NASDAQ\n\n"
    )

    for e in events:

        desc += (
            f"🇺🇸 {e['title']}\n"
            f"📅 {e['date']}\n"
            f"🕒 {e['time']}\n\n"
        )

    send_embed(
        "📅 HIGH IMPACT USD NEWS THIS WEEK",
        desc,
        16753920
    )

# =====================================
# 15-MINUTE ALERTS
# =====================================

def check_alerts():

    now = datetime.now(TIMEZONE)

    current = now.strftime(
        "%Y-%m-%d %H:%M"
    )

    events = get_events()

    for e in events:

        try:

            dt_string = (
                f"{e['date']} "
                f"{e['time']}"
            )

            event_dt = datetime.strptime(
                dt_string,
                "%m-%d-%Y %I:%M%p"
            )

            event_dt = TIMEZONE.localize(
                event_dt
            )

            reminder = (
                event_dt -
                timedelta(minutes=15)
            ).strftime("%Y-%m-%d %H:%M")

            unique_id = (
                f"{e['title']}_{reminder}"
            )

            if (
                current == reminder
                and unique_id not in sent_alerts
            ):

                desc = (
                    f"🇺🇸 {e['title']}\n\n"
                    f"⚠️ High volatility expected\n\n"
                    f"Most affected:\n"
                    f"• XAUUSD\n"
                    f"• NASDAQ\n\n"
                    f"Consider reducing risk "
                    f"before release."
                )

                send_embed(
                    "🚨 NEWS IN 15 MINUTES",
                    desc,
                    16711680
                )

                sent_alerts.add(unique_id)

        except Exception as ex:

            print("Alert Error:", ex)

# =====================================
# DAILY CLEANUP
# =====================================

def reset_alerts():

    global sent_alerts

    sent_alerts = set()

    print("Alerts reset")

# =====================================
# SCHEDULES
# =====================================

schedule.every().sunday.at(
    "18:00"
).do(weekly_summary)

schedule.every(1).minutes.do(
    check_alerts
)

schedule.every().day.at(
    "00:05"
).do(reset_alerts)

# =====================================
# MAIN LOOP
# =====================================

def run_bot():

    send_embed(
        "✅ Forex Factory XML Bot LIVE",
        "XAUUSD & NASDAQ alerts activated",
        65280
    )

    while True:

        schedule.run_pending()

        time.sleep(30)

# =====================================
# START
# =====================================

if __name__ == "__main__":

    flask_thread = Thread(
        target=run_flask
    )

    flask_thread.start()

    run_bot()
