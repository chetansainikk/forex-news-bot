import os
import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread
import xml.etree.ElementTree as ET

# ==================================================
# CONFIG
# ==================================================

DISCORD_WEBHOOK = os.getenv(
    "DISCORD_WEBHOOK"
)

FOREX_FACTORY_XML = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.xml"
)

TIMEZONE = pytz.timezone(
    "Asia/Kolkata"
)

FF_TIMEZONE = pytz.timezone(
    "America/New_York"
)

sent_alerts = set()

# ==================================================
# FLASK KEEPALIVE
# ==================================================

app = Flask(__name__)

@app.route("/")
def home():

    return "Forex Factory News Bot Running"

def run_flask():

    app.run(
        host="0.0.0.0",
        port=10000
    )

# ==================================================
# DISCORD EMBED
# ==================================================

def send_embed(
    title,
    description,
    color
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

        print(
            "Discord:",
            r.status_code
        )

    except Exception as e:

        print(
            "Discord Error:",
            e
        )

# ==================================================
# GET EVENTS
# ==================================================

def get_events():

    try:

        response = requests.get(
            FOREX_FACTORY_XML,
            timeout=10
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        events = []

        for item in root.findall("event"):

            try:

                currency = ""

                if item.find("currency") is not None:

                    currency = (
                        item.find("currency").text
                    )

                elif item.find("country") is not None:

                    currency = (
                        item.find("country").text
                    )

                impact = (
                    item.find("impact").text
                    or ""
                )

                title = (
                    item.find("title").text
                    or ""
                )

                date = (
                    item.find("date").text
                    or ""
                )

                event_time = (
                    item.find("time").text
                    or ""
                )

                # ONLY USD NEWS
                if currency == "USD":

                    # RED + ORANGE
                    if (
                        "High" in impact
                        or "Medium" in impact
                    ):

                        dt_string = (
                            f"{date} {event_time}"
                        )

                        ff_time = datetime.strptime(
                            dt_string,
                            "%m-%d-%Y %I:%M%p"
                        )

                        ff_time = FF_TIMEZONE.localize(
                            ff_time
                        )

                        ist_time = (
                            ff_time.astimezone(
                                TIMEZONE
                            )
                        )

                        formatted_time = (
                            ist_time.strftime(
                                "%A • %I:%M %p IST"
                            )
                        )

                        if "High" in impact:

                            folder = "🔴 RED"

                            color = 16711680

                        else:

                            folder = "🟠 ORANGE"

                            color = 16753920

                        events.append({
                            "title": title,
                            "time": formatted_time,
                            "datetime": ist_time,
                            "folder": folder,
                            "color": color
                        })

            except Exception as e:

                print(
                    "EVENT ERROR:",
                    e
                )

        events.sort(
            key=lambda x: x["datetime"]
        )

        return events

    except Exception as e:

        print(
            "XML ERROR:",
            e
        )

        return []

# ==================================================
# WEEKLY SUMMARY
# ==================================================

def weekly_summary():

    events = get_events()

    if not events:

        return

    desc = (
        "💰 Affects XAUUSD & NASDAQ\n\n"
    )

    for e in events:

        desc += (
            f"{e['folder']} "
            f"{e['title']}\n"
            f"🕒 {e['time']}\n\n"
        )

    send_embed(
        "📅 WEEKLY FOREX FACTORY NEWS",
        desc,
        16753920
    )

# ==================================================
# 15 MINUTE ALERTS
# ==================================================

def check_alerts():

    now = datetime.now(
        TIMEZONE
    )

    events = get_events()

    for e in events:

        reminder = (
            e["datetime"] -
            timedelta(minutes=15)
        )

        key = (
            f"{e['title']}_{reminder}"
        )

        if (
            now >= reminder
            and key not in sent_alerts
        ):

            desc = (
                f"{e['folder']} "
                f"{e['title']}\n\n"
                f"🕒 {e['time']}\n\n"
                f"⚠️ VOLATILITY WARNING\n"
                f"• XAUUSD\n"
                f"• NASDAQ\n"
                f"• USD Pairs"
            )

            send_embed(
                "🚨 NEWS IN 15 MINUTES",
                desc,
                e["color"]
            )

            sent_alerts.add(key)

# ==================================================
# RESET ALERTS DAILY
# ==================================================

def reset_alerts():

    global sent_alerts

    sent_alerts = set()

    print("Alerts reset")

# ==================================================
# SCHEDULES
# ==================================================

# WEEKLY NEWS
schedule.every().sunday.at(
    "17:00"
).do(weekly_summary)

# CHECK ALERTS
schedule.every(1).minutes.do(
    check_alerts
)

# RESET DAILY
schedule.every().day.at(
    "00:05"
).do(reset_alerts)

# ==================================================
# MAIN LOOP
# ==================================================

def run_bot():

    send_embed(
        "✅ FOREX FACTORY BOT LIVE",
        "Red + Orange Folder Alerts Activated",
        65280
    )

    while True:

        schedule.run_pending()

        time.sleep(30)

# ==================================================
# START
# ==================================================

if __name__ == "__main__":

    flask_thread = Thread(
        target=run_flask
    )

    flask_thread.start()

    run_bot()
