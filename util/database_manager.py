import sqlite3

from util.config_manager import Config

"""
This class manages a database used for storing bot information.

Functionality includes seting up an empty database, if one is not present, and returning a connection to said database.
"""
class Database:
    """
    Returns a connection to the specified database in the config.json file.

    @return A sqlite3 connection to the database or None if a connection was unable to be made.
    """
    @staticmethod
    def get_connection():
        try:
            # Get the bot database name from the config file.
            config = Config.get_config()
            bot_database_name = str(config["bot_database_name"])

            # If the bot database name in the config is not suffixed with '.db' we will add it.
            if not (bot_database_name.endswith(".db")):
                bot_database_name += ".db"
            
            # Attempt to open a connect to a bot database with the name provided in the config file.
            con = sqlite3.connect(f"file:{bot_database_name}?mode=rw", uri=True)
            return con
        except:
            # Return none since we were unable to open a connection.
            return None
    
    """
    Attempts to read from the database specified in the config.json file, and creates an empty one if it is not present.
    """
    @staticmethod
    def setup_bot_database():
        # Get a connection with the bot database.
        print("Attempting to read in specified bot database file...")
        con = Database.get_connection()

        # If a connection is made with the bot database we will have a connection object that is not equal to None.
        if (con is not None):
            # If we are successfully able to open a connect with the bot database we will close the connection and print a message saying so.
            print("Successfully read specified bot database file.\n")
            con.close()
        # Since the bot database with the given name doesn't exist, we will create one and setup it up for our needs.
        else:
            # Print a message saying that we were unable to connect to the bot database.
            print("Unable to read specified bot database file. Writing a default one to the current directory.\n")
            
            # Get the bot database name from the config file.
            config = Config.get_config()
            bot_database_name = str(config["bot_database_name"])

            # If the bot database name in the config is not suffixed with '.db' we will add it.
            if not (bot_database_name.endswith(".db")):
                bot_database_name += ".db"

            # Create a new bot database by creating a connection.
            con = sqlite3.connect(bot_database_name)

            # Create a table to contain the database information.
            cur = con.cursor()
            cur.execute("CREATE TABLE tags(name, content, authorID, guildID, date, amountUsed)")
            cur.execute("CREATE TABLE timezones(timezone, userID, guildID)")
            con.commit()

            # Close the database connection now that we are done with it.
            con.close()