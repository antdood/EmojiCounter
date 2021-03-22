import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import emoji
import re
from db import db

def extractEmojisFrom(message):
	message = emoji.demojize(message)
	return re.findall(":\w+:", message)

load_dotenv()

TOKEN = os.getenv("discord_token")

bot = commands.Bot(command_prefix="!", help_command=None)

@bot.event
async def on_ready():
    print("Logged in.")
    db()

@bot.event
async def on_raw_reaction_add(payload):
	guild = payload.guild_id
	channel = payload.channel_id
	user = payload.user_id
	em = emoji.demojize(str(payload.emoji))

	db.add_emoji_usage(guild, channel, user, [em])

@bot.event
async def on_message(msg):
	if(emojis := extractEmojisFrom(msg.content)):
		guild = msg.guild.id
		channel = msg.channel.id
		user = msg.author.id
		db.add_emoji_usage(msg.guild.id, msg.channel.id, msg.author.id, emojis)

bot.run(TOKEN)
