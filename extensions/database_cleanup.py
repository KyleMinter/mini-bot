import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config
from util.database_manager import Database

from interactions import listen, Extension, Client
from interactions.api.events import GuildLeft, MemberRemove

"""
A class representing an extension of the bot.
This extention contains the functionality for the removing server specific information from the database.
"""
class DatabaseCleanupExtension(Extension):
    """
    GuildLeft event listener.
    This is a callback function that is called when a GuildLeft event is triggered.
    This function will delete server specific information from the bot database when the bot user is removed from a server.

    @param event The event context.
    """
    @listen(GuildLeft)
    async def on_guild_left(self, event: GuildLeft):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()

            # Delete all tags from this server.
            cur.execute(f"DELETE FROM tags WHERE guildID = ?", (str(event.guild.id),))
            
            # Delete all timezone registrations from this server.
            cur.execute(f"DELETE FROM timezones WHERE guildID = ?", (str(event.guild.id),))

            # Commit the changes to the database.
            con.commit()

            # Close the connection to the database now that we are done accessing it.
            con.close()
    
    """
    MemberRemove event listener.
    This is a callback function that is called when a MemberRemove event is triggered.
    This function will delete user specific information from the bot database when the user is removed from a server.

    @param event The event context.
    """
    @listen(MemberRemove)
    async def on_member_remove(self, event: MemberRemove):
        # Checks if the "clean_user_data" flag is enabled in the config.
        if (Config.get_config["clean_user_data"]):
            # Get a connection to the bot database.
            con = Database.get_connection()

            # Check if the connection is valid.
            if (con is not None):
                # Create a cursor to query the database.
                cur = con.cursor()

                # Delete all tags created by this user from this server.
                cur.execute(f"DELETE FROM tags WHERE authorID = ? AND guildID = ?", (str(event.member.id), str(event.guild.id),))
                
                # Delete all timezone registrations for this user from this server.
                cur.execute(f"DELETE FROM timezones WHERE userID = ? AND guildID = ?", (str(event.member.id), str(event.guild.id),))

                # Commit the changes to the database.
                con.commit()

                # Close the connection to the database now that we are done accessing it.
                con.close()

    """
    Deletes server and user specific information from the bot database for servers and users that are unavailable to the bot.
    This function is called when the On Ready event is triggered to ensure that no uneccesary data wasn't left unremoved during the bot's downtime.
    """
    @staticmethod
    def on_ready_cleanup(client: Client):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Make sure the temporary tables we are going to create, don't already exist.
            cur.execute("DROP TABLE IF EXISTS guilds")
            cur.execute("DROP TABLE IF EXISTS users")

            # Create two temporary tables in the database to store the guild IDs and user IDs for all the servers the bot is currently in.
            cur.execute("CREATE TABLE guilds(guildID)")
            cur.execute("CREATE TABLE users(userID, guildID)")
            
            # Get a list of guilds the bot is in.
            guilds = client.guilds

            # Loop over the list of guilds.
            for guild in guilds:
                # Insert the guild ID for this guild into the temporary table.
                cur.execute("INSERT INTO guilds VALUES (?)", (str(guild.id),))

                # Check if the "clean_user_data" flag is enabled in the config.
                if (Config.get_config()["clean_user_data"]):
                    # Get a list of users in this server.
                    users = guild.members

                    # Loop over the list of users.
                    for user in users:
                        # For each user in a guild we will insert the user IDs into the temporary table.
                        cur.execute("INSERT INTO users VALUES (?, ?)", (str(user.id), str(guild.id),))
                    
                    # If the flag is enabled we will delete all tags and timezone registrations from users not available to the bot.
                    cur.execute("DELETE FROM tags WHERE authorID NOT IN (SELECT u.userID FROM users u WHERE guildID = ?)", (str(guild.id),))
                    cur.execute("DELETE FROM timezones WHERE userID NOT IN (SELECT u.userID FROM users u WHERE guildID = ?)", (str(guild.id),))

                    # Clear the temporary table.
                    cur.execute("DELETE FROM users")

            # Delete all tags from the database that don't have an author ID or guild ID present in the temporary table.
            cur.execute("DELETE FROM tags WHERE guildID NOT IN (SELECT g.guildID FROM guilds g)")

            # Delete all timezone registrations from the database that don't have a userID or guild ID present in the temporary table.
            cur.execute("DELETE FROM timezones WHERE guildID NOT IN (SELECT g.guildID FROM guilds g)")

            # Delete the temporary tables.
            cur.execute("DROP TABLE guilds")
            cur.execute("DROP TABLE users")
            
            # Commit the changes to the database.
            con.commit()

            # Close the connection to the database now that we are done accessing it.
            con.close()