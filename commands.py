import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import pytz

TOKEN = "PASTE_YOUR_DISCORD_BOT_TOKEN"

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

TIMEZONE = pytz.timezone("Asia/Kolkata")

# ======================================
# READY EVENT
# ======================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Logged in as {bot.user}")

# ======================================
# /news_today
# ======================================

@bot.tree.command(name="news_today", description="Today's high impact USD news")
async def news_today(interaction: discord.Interaction):

    msg = (
        "📅 Today's High Impact USD News

"
        "🇺🇸 CPI m/m — 6:00 PM IST
"
        "🇺🇸 FOMC — 11:30 PM IST
"
        "🇺🇸 Powell Speaks — 8:00 PM IST"
    )

    await interaction.response.send_message(msg)

# ======================================
# /nextnews
# ======================================

@bot.tree.command(name="nextnews", description="Next major USD event")
async def nextnews(interaction: discord.Interaction):

    msg = (
        "🚨 Next High Impact Event

"
        "🇺🇸 Non-Farm Payrolls
"
        "🕒 Friday 6:00 PM IST

"
        "Affected:
"
        "• XAUUSD
"
        "• NASDAQ"
    )

    await interaction.response.send_message(msg)

# ======================================
# /countdown
# ======================================

@bot.tree.command(name="countdown", description="Countdown to next USD news")
async def countdown(interaction: discord.Interaction):

    now = datetime.now(TIMEZONE)

    target = now.replace(hour=18, minute=0, second=0)

    if now > target:
        await interaction.response.send_message(
            "No major news today"
        )
        return

    remaining = target - now

    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    msg = (
        f"⏳ Next USD News In:

"
        f"{hours}h {minutes}m {seconds}s"
    )

    await interaction.response.send_message(msg)

# ======================================
# /gold_bias
# ======================================

@bot.tree.command(name="gold_bias", description="XAUUSD market bias")
async def gold_bias(interaction: discord.Interaction):

    msg = (
        "🟡 XAUUSD Bias: Bullish

"
        "Reason:
"
        "• DXY weak
"
        "• Bonds soft
"
        "• Risk sentiment positive
"
        "• USD news approaching"
    )

    await interaction.response.send_message(msg)

# ======================================
# /risk
# ======================================

@bot.tree.command(name="risk", description="Risk management reminder")
async def risk(interaction: discord.Interaction):

    msg = (
        "⚠️ Risk Management Checklist

"
        "• Risk 0.5%–1% max
"
        "• Avoid revenge trades
"
        "• Reduce size before news
"
        "• Respect daily drawdown"
    )

    await interaction.response.send_message(msg)

# ======================================
# /session
# ======================================

@bot.tree.command(name="session", description="Current trading session")
async def session(interaction: discord.Interaction):

    now = datetime.now(TIMEZONE)

    hour = now.hour

    if 5 <= hour < 13:
        current = "Asian Session"
    elif 13 <= hour < 17:
        current = "London Session"
    elif 17 <= hour < 23:
        current = "New York Session"
    else:
        current = "Low Liquidity Hours"

    msg = f"🌍 Current Session:

{current}"

    await interaction.response.send_message(msg)

# ======================================
# RUN BOT
# ======================================

bot.run(TOKEN)
