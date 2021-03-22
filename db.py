from dotenv import load_dotenv
import os
import MySQLdb

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

    def add_emoji_usage(server, channel, user, emojis):
    	c = db.getdb().cursor()

    	for emoji in emojis:
    		c.execute(f"INSERT INTO emoji_usages (server, channel, user, emoji) VALUES ({server}, {channel}, {user}, '{emoji}')")

    	db.getdb().commit()

    	return