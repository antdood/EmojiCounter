import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import emoji
import re
from db import db
from discord.utils import get
from discord.ext.commands import CommandNotFound

def extractEmojisFrom(message):
    # First match and remove custom emojis

    customEmojiIDs = []
    indicesToRemove = []

    for match in re.finditer("<a?:\w*:(\d*)>", message):
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

    db.addEmojiUsage(channel, user, [em])

@bot.event
async def on_message(msg):
    if(msg.author.bot):
        return

    if(emojis := extractEmojisFrom(msg.content)):
        guild = msg.guild.id
        channel = msg.channel.id
        user = msg.author.id
        db.addEmojiUsage(msg.channel.id, msg.author.id, emojis)

    await bot.process_commands(msg)


def isTarget(text):
    if(text == "server"):
        return "server"
    if(isChannelTag(text)): #is channel
        return "channel"
    if(isUserTag(text)): #is user
        return "user"
    return None

def isChannelTag(text):
    return re.search("^<#\d+>$", text)

def isUserTag(text):
    return re.search("^<@!?\d+>$", text)

@bot.command(aliases = ['emoji', 'emojiUse', 'e'])
async def emoji_report(msg, *, args = ""):
    



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

bot.run(TOKEN)
