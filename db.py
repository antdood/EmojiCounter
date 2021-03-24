from dotenv import load_dotenv
import os
import MySQLdb
import re
import time



load_dotenv()

class db:
    """Highly customized db class for the purposes of this bot. Loads of very specific helper functions to wrap the mess of db handling away."""

    _instance = None

    def __init__(self):

        try:                                                                                                                 
            host = os.getenv("db_host")
            user = os.getenv("db_user")
            pw = os.getenv("db_password")
            dbname = os.getenv("db")
            dbconn = MySQLdb.connect(host, user, pw, dbname)
            dbconn.ping(True)
            print("Database connection established.")
        except:
            print("Failed to connect to database. Aborting.")
            exit()

        db._instance = dbconn

        return

    @staticmethod
    def getdb():
        if(db._instance == None):
            db()

        return db._instance

    def addEmojiUsage(server, channel, user, emojis):
        c = db.getdb().cursor()

        for emoji in emojis:
            emojiType = 'original'
            if(isinstance(emoji, int) or emoji.isnumeric()):
                emojiType = 'custom'
            c.execute(f"INSERT INTO emoji_usages (server, channel, user, emoji, type) VALUES ({server}, {channel}, {user}, '{emoji}', '{emojiType}')")

        db.getdb().commit()

        return

    def removeEmojisFrom(guildID):
        c = db.getdb().cursor()

        c.execute(f"DELETE FROM emojis WHERE guild = {guildID}")

        db.getdb().commit()

    def addEmojisTo(guildID, emojis):
        c = db.getdb().cursor()

        for emoji in emojis:
            c.execute(f"INSERT INTO emojis VALUES({guildID}, {emoji.id})")

        db.getdb().commit()

    def getEmojisUses(target, number, timeOffsetString, orientation):
        c = db.getdb().cursor()

        c.execute(db.buildEmojiUsesQuery(target, number, timeOffsetString, orientation))

        return c.fetchall()

    def buildEmojiUsesQuery(target, number, timeOffsetString, orientation):
        
        orderSort = {
            "top" : "DESC",
            "bottom" : "ASC"
        }

        query = ""

        if(target[0] == "server"):
            query += "SELECT emojiID, count(emoji) FROM emoji_usages RIGHT JOIN emojis ON emoji_usages.emoji = emojis.emojiID WHERE 1=1 "
        else:
            query += "SELECT emoji, count(emoji) FROM emoji_usages WHERE 1=1 "
            clean = re.findall("\d+", target[1])[0] # How is there no easier way to get the first regex match. I must be missing something
            query += f"AND {target[0]} = {clean} "

        if(timeOffsetString != "all"):
            timeOffset = convertToSeconds(timeOffsetString)
            query += f"AND UNIX_TIMESTAMP(time) > {time.time() - timeOffset} "

        query += f"GROUP BY emoji ORDER BY count(emoji) {orderSort[orientation]} LIMIT {number};"

        return query


# !emoji @antdood time all 
# 1. :heart: 63 times
# 2. :sweat_smile: 50 times
# ...
# fuck 0 uses

# !emoji #channel 
# 1. :heart: 63 times
# 2. :sweat_smile: 50 times
# ...
# fuck 0 uses

# !emoji global
# Your guild emoji usages :
# 1. :heart: 63 times
# 2. :sweat_smile: 50 times
# ...
# include 0 uses
        


# Helper function, if more comes, move to different file
def convertToSeconds(string):
    amount = string[:-1]
    interval = string[-1:]

    # Google's numbers ¯\_(ツ)_/¯
    intervalSeconds = {
        "d" : 86400,
        "w" : 604800,
        "m" : 2628000,
        "y" : 31540000
    }

    return int(amount) * intervalSeconds[interval]
