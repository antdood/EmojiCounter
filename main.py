import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import emoji
import re
from db import db
from discord.utils import get

def extractEmojisFrom(message):
	# First match and remove custom emojis

	customEmojiIDs = []
	indicesToRemove = []

	for match in re.finditer("<:\w*:(\d*)>", message):
		indicesToRemove.append((match.start(), match.end()))
		customEmojiIDs.append(match.group(1))

	for indexPair in reversed(indicesToRemove):
		message = message[:indexPair[0]] + message[indexPair[1]:]

	message = emoji.demojize(message)


	baseEmojis =  re.findall(":\w+:", message)

	return baseEmojis + customEmojiIDs

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

	em = payload.emoji.id or emoji.demojize(str(payload.emoji))

	db.add_emoji_usage(guild, channel, user, [em])

@bot.event
async def on_message(msg):
	if(msg.author.bot):
		return

	if(emojis := extractEmojisFrom(msg.content)):
		guild = msg.guild.id
		channel = msg.channel.id
		user = msg.author.id
		db.add_emoji_usage(msg.guild.id, msg.channel.id, msg.author.id, emojis)


# @bot.commands(aliases = ['emoji'])
# async def emoji_report

# default time = all 

# !emoji global top  
# !emoji global top 5
# !emoji global bottom 5
# !emoji @antdood top 10 time 5d
# !emoji @antdood top 5
# !emoji #channel top 5
# !emoji #channel top
# !emoji #channel
# - total emojis used
# - total unique emojis



bot.run(TOKEN)
