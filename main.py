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

    db.addEmojiUsage(guild, channel, user, [em])

@bot.event
async def on_message(msg):


    # for em in bot.emojis:
    #   print(em.guild)
    #   print(em.guild_id)

    if(msg.author.bot):
        return

    if(emojis := extractEmojisFrom(msg.content)):
        guild = msg.guild.id
        channel = msg.channel.id
        user = msg.author.id
        db.addEmojiUsage(msg.guild.id, msg.channel.id, msg.author.id, emojis)

    await bot.process_commands(msg)


def isTarget(text):
    if(text == "global"):
        return True
    if(isChannelTag(text)): #is channel
        return True
    if(isUserTag(text)): #is user
        return True
    return False

def isChannelTag(text):
    return re.search("^<#\d+>$", text)

def isUserTag(text):
    return re.search("^<@!?\d+>$", text)

@bot.command(aliases = ['emoji', 'emojiUse', 'e'])
async def emoji_report(msg, *, args):
    arguments = {'top' : 5, 'bottom' : 5, 'time' : "all"}

    def isArgument(text):
        return text in arguments

    def isValidValueforArgument(value, argument):
        if(argument in ["top", "bottom", "bot"]):
            return value.isnumeric()
        elif(argument == "time"):
            return re.search("^\d+[dwmy]$", value)
        else:
            return False

    bits = args.split()

    selectedArguments = {}
    targets = []

    i = 0
    while(i < len(bits)):
        if(isArgument(bits[i])):
            currentArguments = bits[i]
            i += 1
            if(isValidValueforArgument(bits[i], currentArguments)):
                selectedArguments[currentArguments] = bits[i]
                i += 1
                continue
            else:
                selectedArguments[currentArguments] = arguments[currentArguments]
                continue
        elif(isTarget(bits[i])):
            targets.append(bits[i])
            i += 1
            continue
        i += 1

    print(selectedArguments)
    print(targets)

    # Don't like this. There should be a nicer way to handle default values.
    if(not "time" in selectedArguments.keys()):
        selectedArguments["time"] = arguments["time"]

    for target in targets:
        if("top" in selectedArguments):
            a = db.getTopEmojis(target, selectedArguments["top"], selectedArguments["time"])
            print(a)

@bot.command(aliases = ['updateemojis'])
async def updateEmojis(msg):
    guildID = msg.guild.id
    db.removeEmojisFrom(guildID)

    emojis = [emoji for emoji in bot.emojis if emoji.guild_id == guildID]

    db.addEmojisTo(guildID, emojis)








# default time = all 

# emoji top 5 global bottom time 5d

# !emoji global top  
# !emoji global top 5
# !emoji global bottom 5
# !emoji @antdood top 10 time 5d
# !emoji @antdood top 5
# !emoji #channel top 5
# !emoji #channel top
# !emoji #channel
# !emoji top 5 time 5d global
# - total emojis used
# - total unique emojis



bot.run(TOKEN)
