import discord
from discord import app_commands
from discord.ext import commands
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import os

# ==================================================
# CONFIG
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

TIMEZONE = pytz.timezone("Asia/Kolkata")

XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

# ==================================================
# BOT SETUP
# ==================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==================================================
# FETCH EVENTS
# ==================================================

def get_events():

    response = requests.get(XML_URL)

    root = ET.fromstring(response.content)

    events = []

    for item in root.findall("event"):

        currency = item.find("country").text
        impact = item.find("impact").text
        title = item.find("title").text
        date = item.find("date").text
        event_time = item.find("time").text

        if (
            currency == "USD"
            and impact == "High"
        ):

            try:

                dt_string = f"{date} {event_time}"

                ff_time = datetime.strptime(
                    dt_string,
                    "%m-%d-%Y %I:%M%p"
                )

                ff_timezone = pytz.timezone(
                    "Etc/GMT-4"
                )

                ff_time = ff_timezone.localize(
                    ff_time
                )

                ist_time = ff_time.astimezone(
                    TIMEZONE
                )

                formatted_time = ist_time.strftime(
                    "%d %b • %I:%M %p IST"
                )

            except:

                formatted_time = event_time

            events.append({
                "title": title,
                "time": formatted_time,
                "datetime": ist_time
            })

    events.sort(
        key=lambda x: x["datetime"]
    )

    return events

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

    now = datetime.now(TIMEZONE)

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

    now = datetime.now(TIMEZONE)

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

    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    msg = (
        f"⏳ **Countdown To News**\n\n"
        f"🇺🇸 {e['title']}\n"
        f"🕒 {e['time']}\n\n"
        f"⏱ {hours}h {minutes}m remaining"
    )

    await interaction.followup.send(msg)

# ==================================================
# RUN BOT
# ==================================================

bot.run(BOT_TOKEN)
