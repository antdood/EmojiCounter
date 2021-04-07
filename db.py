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

    def addEmojiUsage(channel, user, emojis):
        c = db.getdb().cursor()

        for emoji in emojis:
            emojiType = 'original'
            if(isinstance(emoji, int) or emoji.isnumeric()):
                emojiType = 'custom'
            c.execute(f"INSERT INTO emoji_usages (channel, user, emoji, type) VALUES ({channel}, {user}, '{emoji}', '{emojiType}')")

        db.getdb().commit()

        return

    def getEmojiUsages(target, timeOffsetString, orientation, count, relevantCustomEmojiIDs):
        c = db.getdb().cursor()

        c.execute("CREATE TEMPORARY TABLE allEmojis (emoji VARCHAR(255), count INT UNSIGNED);")

        for emoji in relevantCustomEmojiIDs:
            c.execute(f"INSERT INTO allEmojis VALUES ({emoji}, 0);")

        orderSort = {
            "top" : "DESC",
            "bottom" : "ASC"
        }

        startTime = 0

        if(timeOffsetString != "all"):
            timeOffset = convertToSeconds(timeOffsetString)
            startTime = int(time.time()) - timeOffset

        # JFC WTF IS THIS QUERY
        query = f"""
        SELECT emoji, sum(count) as count FROM (
            SELECT usedEmojis.emoji, usedEmojis.count FROM (
                SELECT combined.emoji as emoji, count(combined.emoji) as count FROM (
                    SELECT emoji FROM emoji_usages WHERE type = "original" AND {target[0]} = {target[1]} AND UNIX_TIMESTAMP(time) > {startTime}

                    UNION ALL

                    SELECT emoji FROM emoji_usages WHERE type = "custom" AND {target[0]} = {target[1]} AND UNIX_TIMESTAMP(time) > {startTime} AND emoji IN ({",".join(map(str,relevantCustomEmojiIDs))})
                ) AS combined

                GROUP BY emoji
            ) as usedEmojis 
            
            UNION ALL

            SELECT emoji, count FROM allEmojis
        ) 
        x GROUP BY emoji ORDER BY count {orderSort[orientation]} LIMIT {count}
        """

        c.execute(query)

        data = c.fetchall()

        c.execute("DROP TEMPORARY TABLE allEmojis;")

        return data

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

