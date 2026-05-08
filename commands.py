import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

# =====================================
# CONFIG
# =====================================

TOKEN = os.environ.get("DISCORD_TOKEN")

TIMEZONE = pytz.timezone("Asia/Kolkata")

FOREX_FACTORY_XML = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.xml"
)

# =====================================
# BOT SETUP
# =====================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

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

                        try:

    dt_string = f"{date} {event_time}"

    ff_time = datetime.strptime(
        dt_string,
        "%m-%d-%Y %I:%M%p"
    )

    ff_time = pytz.utc.localize(ff_time)

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
        "%I:%M %p IST"
    )

except:

    formatted_time = event_time

events.append({
    "title": title,
    "date": date,
    "time": formatted_time
})

            except:
                pass

        return events

    except Exception as e:

        print("XML Error:", e)

        return []

# =====================================
# READY EVENT
# =====================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Logged in as {bot.user}")

# =====================================
# /news_today
# =====================================

@bot.tree.command(
    name="news_today",
    description="Today's high impact USD news"
)
async def news_today(
    interaction: discord.Interaction
):

    events = get_events()

    today = datetime.now(
        TIMEZONE
    ).strftime("%m-%d-%Y")

    today_events = []

    for e in events:

        if e["date"] == today:

            today_events.append(e)

    if not today_events:

        await interaction.response.send_message(
            "✅ No major USD news today."
        )

        return

    msg = "📅 Today's High Impact USD News\n\n"

    for e in today_events:

        msg += (
            f"🇺🇸 {e['title']}\n"
            f"🕒 {e['time']}\n\n"
        )

    await interaction.response.send_message(
        msg
    )

# =====================================
# /nextnews
# =====================================

@bot.tree.command(
    name="nextnews",
    description="Next high impact USD event"
)
async def nextnews(
    interaction: discord.Interaction
):

    events = get_events()

    if not events:

        await interaction.response.send_message(
            "No events found."
        )

        return

    e = events[0]

    msg = (
        f"🚨 Next High Impact USD Event\n\n"
        f"🇺🇸 {e['title']}\n"
        f"📅 {e['date']}\n"
        f"🕒 {e['time']}\n\n"
        f"Affects:\n"
        f"• XAUUSD\n"
        f"• NASDAQ"
    )

    await interaction.response.send_message(
        msg
    )

# =====================================
# /countdown
# =====================================

@bot.tree.command(
    name="countdown",
    description="Countdown to next USD news"
)
async def countdown(
    interaction: discord.Interaction
):

    events = get_events()

    if not events:

        await interaction.response.send_message(
            "No events found."
        )

        return

    e = events[0]

    msg = (
        f"⏳ Countdown To Next News\n\n"
        f"🇺🇸 {e['title']}\n"
        f"📅 {e['date']}\n"
        f"🕒 {e['time']}"
    )

    await interaction.response.send_message(
        msg
    )

# =====================================
# /gold_bias
# =====================================

@bot.tree.command(
    name="gold_bias",
    description="XAUUSD market bias"
)
async def gold_bias(
    interaction: discord.Interaction
):

    msg = (
        "🟡 XAUUSD Bias: Neutral/Bullish\n\n"
        "Reason:\n"
        "• USD high impact news nearby\n"
        "• Volatility expected\n"
        "• Trade with reduced risk"
    )

    await interaction.response.send_message(
        msg
    )

# =====================================
# /risk
# =====================================

@bot.tree.command(
    name="risk",
    description="Risk management reminder"
)
async def risk(
    interaction: discord.Interaction
):

    msg = (
        "⚠️ Risk Management Checklist\n\n"
        "• Risk 0.5%–1%\n"
        "• Reduce size before news\n"
        "• Avoid revenge trading\n"
        "• Protect funded account"
    )

    await interaction.response.send_message(
        msg
    )

# =====================================
# /session
# =====================================

@bot.tree.command(
    name="session",
    description="Current trading session"
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

# =====================================
# START BOT
# =====================================

bot.run(TOKEN)
