import discord
from discord.ext import commands
from discord import app_commands

import requests
import xml.etree.ElementTree as ET

from datetime import datetime
import pytz
import os

# ==================================================
# CONFIG
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

TIMEZONE = pytz.timezone("Asia/Kolkata")

# ==================================================
# BOT SETUP
# ==================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==================================================
# GET EVENTS
# ==================================================

def get_events():

    try:

        response = requests.get(
            XML_URL,
            timeout=10
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        events = []

        for item in root.findall("event"):

            try:

                currency = item.find("currency").text
                impact = item.find("impact").text
                title = item.find("title").text
                date = item.find("date").text
                event_time = item.find("time").text

                # ONLY USD HIGH IMPACT
                if currency == "USD" and impact == "High":

                    dt_string = f"{date} {event_time}"

                    ff_time = datetime.strptime(
                        dt_string,
                        "%m-%d-%Y %I:%M%p"
                    )

                    # ForexFactory XML times are UTC
                    ff_time = pytz.utc.localize(
                        ff_time
                    )

                    ist_time = ff_time.astimezone(
                        TIMEZONE
                    )

                    formatted_time = ist_time.strftime(
                        "%d %b • %I:%M %p IST"
                    )

                    events.append({
                        "title": title,
                        "time": formatted_time,
                        "datetime": ist_time
                    })

            except Exception as e:

                print("EVENT ERROR:", e)

                continue

        events.sort(
            key=lambda x: x["datetime"]
        )

        return events

    except Exception as e:

        print("XML ERROR:", e)

        return []

# ==================================================
# READY
# ==================================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Logged in as {bot.user}")

# ==================================================
# /news_today
# ==================================================

@bot.tree.command(
    name="news_today",
    description="Shows upcoming high impact USD news"
)
async def news_today(
    interaction: discord.Interaction
):

    await interaction.response.defer()

    events = get_events()

    if not events:

        await interaction.followup.send(
            "❌ No major USD news found."
        )

        return

    msg = "📅 **Upcoming High Impact USD News**\n\n"

    for e in events[:5]:

        msg += (
            f"🇺🇸 {e['title']}\n"
            f"🕒 {e['time']}\n\n"
        )

    await interaction.followup.send(msg)

# ==================================================
# /nextnews
# ==================================================

@bot.tree.command(
    name="nextnews",
    description="Shows next upcoming news event"
)
async def nextnews(
    interaction: discord.Interaction
):

    await interaction.response.defer()

    events = get_events()

    now = datetime.now(
        TIMEZONE
    )

    future_events = [
        e for e in events
        if e["datetime"] > now
    ]

    if not future_events:

        await interaction.followup.send(
            "❌ No upcoming news found."
        )

        return

    e = future_events[0]

    msg = (
        f"🚨 **Next High Impact USD News**\n\n"
        f"🇺🇸 {e['title']}\n"
        f"🕒 {e['time']}"
    )

    await interaction.followup.send(msg)

# ==================================================
# /countdown
# ==================================================

@bot.tree.command(
    name="countdown",
    description="Countdown to next high impact news"
)
async def countdown(
    interaction: discord.Interaction
):

    await interaction.response.defer()

    events = get_events()

    now = datetime.now(
        TIMEZONE
    )

    future_events = [
        e for e in events
        if e["datetime"] > now
    ]

    if not future_events:

        await interaction.followup.send(
            "❌ No upcoming news."
        )

        return

    e = future_events[0]

    diff = e["datetime"] - now

    total_seconds = int(
        diff.total_seconds()
    )

    hours = total_seconds // 3600
    minutes = (
        total_seconds % 3600
    ) // 60

    msg = (
        f"⏳ **Countdown To News**\n\n"
        f"🇺🇸 {e['title']}\n"
        f"🕒 {e['time']}\n\n"
        f"⏱ {hours}h {minutes}m remaining"
    )

    await interaction.followup.send(msg)

# ==================================================
# /gold_bias
# ==================================================

@bot.tree.command(
    name="gold_bias",
    description="Current XAUUSD bias"
)
async def gold_bias(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "🟡 XAUUSD Bias\n\n"
        "High impact USD news nearby.\n"
        "Expect volatility in Gold & NASDAQ."
    )

# ==================================================
# /risk
# ==================================================

@bot.tree.command(
    name="risk",
    description="Risk management reminder"
)
async def risk(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "⚠️ Risk Management\n\n"
        "• Risk 0.5%–1%\n"
        "• Reduce lot size near news\n"
        "• Protect funded account"
    )

# ==================================================
# /session
# ==================================================

@bot.tree.command(
    name="session",
    description="Current market session"
)
async def session(
    interaction: discord.Interaction
):

    now = datetime.now(
        TIMEZONE
    )

    hour = now.hour

    if 5 <= hour < 13:

        current = "Asian Session"

    elif 13 <= hour < 17:

        current = "London Session"

    elif 17 <= hour < 23:

        current = "New York Session"

    else:

        current = "Low Liquidity"

    await interaction.response.send_message(
        f"🌍 Current Session:\n\n{current}"
    )

# ==================================================
# RUN
# ==================================================

bot.run(BOT_TOKEN)
