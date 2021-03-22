import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import emoji
import re

def containsEmoji(message):
	message = emoji.demojize(message)
	return re.findall(":\w+:", message)

load_dotenv()

TOKEN = os.getenv("discord_token")

bot = commands.Bot(command_prefix="!", help_command=None)

@bot.event
async def on_ready():
    print("Logged in.")

@bot.event
async def on_raw_reaction_add(payload):
	print(emoji.demojize(str(payload.emoji)))

@bot.event
async def on_message(msg):
	print(msg.content)
	print(containsEmoji(msg.content))

bot.run(TOKEN)