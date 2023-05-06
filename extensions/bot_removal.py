import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config
from util.database_manager import Database

from interactions import listen, Extension
from interactions.api.events import GuildLeft, MemberRemove, MemberAdd

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

            # Check the config to see if the keep_server_tags_separate flag is set to true.
            if (Config.get_config()["keep_server_tags_separate"]):
                # If the flag is set to true we will delete all tags from this server.
                cur.execute(f"DELETE FROM tags WHERE guildID = ?", (str(event.guild.id),))
            
            # Delete all timezone registrations from this server.
            cur.execute(f"DELETE FROM timezones WHERE guildID = ?", (str(event.guild.id),))

            # Commit the changes to the database.
            con.commit()

            # Close the connection to the database now that we are done accessing it.
            con.close()
    
    @listen(MemberRemove)
    async def on_member_remove(self, event: MemberRemove):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()

            # Check the config to see if the keep_server_tags_separate flag is set to true.
            if (Config.get_config()["keep_server_tags_separate"]):
                # If the flag is set to true we will delete, all tags created by this user from this server.
                cur.execute(f"DELETE FROM tags WHERE authorID = ? AND guildID = ?", (str(event.member.id), str(event.guild.id),))
            else:
                # If the flag is set to false we will check if this user is in any other servers the bot has access to.
                if (event.bot.get_user(event.member.id) is None):
                    # If the user isn't in any servers the bot has access to, we will delete all the tags created by this user.
                    cur.execute(f"DELETE FROM tags WHERE authorID = ?", (str(event.member.id),))
            
            # Delete all timezone registrations for this user from this server.
            cur.execute(f"DELETE FROM timezones WHERE userID = ? AND guildID = ?", (str(event.member.id), str(event.guild.id),))

            # Commit the changes to the database.
            con.commit()

            # Close the connection to the database now that we are done accessing it.
            con.close()