import geocoder
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config
from util.database_manager import Database

import interactions
from interactions import Extension, InteractionContext, OptionType

"""
A class representing an extension of the bot. This extention contains the functionality for the timezone slash commands provided by the bot.
"""
class TimezonesExtension(Extension):
    """
    Timezone Set Command.
    Registers the timezone for a user in the current server.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param name The name of the nearest large city.
    """
    @interactions.slash_command(
        name="server",
        group_name="timezone",
        dm_permission=False,
        sub_cmd_name="set",
        sub_cmd_description="Registers the timezone for a user in the current server"
    )
    @interactions.slash_option(
        name="city",
        description="The name of the nearest large city",
        required=True,
        opt_type=OptionType.STRING
    )
    @interactions.auto_defer()
    async def timezone_set(self, context: InteractionContext, city: str):
        # Gets the GeoName API username from the config.
        api_username = Config.get_config()["geoname_api_username"]
        
        # Creates an object to store our GeoName API response in.
        geonameCity = ""

        try:
            # Attempt to query the GeoName API with the given city name and API username.
            geonameCity = geocoder.geonames(location=city, key=api_username, fuzzy=0, isNameRequired=True, featureClass="P", cities="cities15000")
        except:
            # If an invalid API username was provided a message will be sent to the user who invoked this command.
            await context.send("Invalid GeoNames API username provided in config! This command will not work until the issue is resolved.")
            return

        # Check if the the city name provided by the user resulted in an actual place.
        if (geonameCity.geonames_id is None):
            # If no places were found with the given city name we will tell the user who invoked this command.
            await context.send("City name not recognized!")
            return
        
        # Get the timezone of the resulting location by querying the GeoName API.
        geonameTimezone = geocoder.geonames(geonameCity.geonames_id, method="details", key=api_username).timeZoneId

        # Get a connection to the bot database.
        con = Database.get_connection()
        
        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Query the databse for any rows with the current userID and guildID.
            params = (str(context.author_id), str(context.guild_id),)
            res = cur.execute(f"SELECT userID, guildID FROM timezones WHERE userID = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()
            
            # Build a new list of parameters for the upcoming database query.
            params = (geonameTimezone, str(context.author_id), str(context.guild_id),)

            # Check if this user already has a timezone set for this server.
            if (fetch is None):
                # If the user does not have their timezone set for this server, we will add it to the database.
                cur.execute("INSERT INTO timezones VALUES (?, ?, ?)", params)
                await context.send("City found! Registered your timezone for this server.")
            else:
                # If the user already has their timezone set for this server, we will update their timezone.
                cur.execute(f"UPDATE timezones SET timezone = ? WHERE userID = ? AND guildID = ?", params)
                await context.send("City found! Updated your timezone for this server.")
            
            # Commit the changes to the database.
            con.commit()

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")
    
    """
    Timezone Get Command.
    Displays the registered timezone for a user in the current server.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @timezone_set.subcommand(
        sub_cmd_name="get",
        sub_cmd_description="Displays the registered timezone for a user in the current server"
    )
    async def timezone_get(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()
        
        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Query the databse for any rows with the current userID and guildID.
            params = (str(context.author_id), str(context.guild_id),)
            res = cur.execute(f"SELECT timezone FROM timezones WHERE userID = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if this user has a timezone set for this server.
            if (fetch is None):
                # If the user has not set their timezone for this server we will send them a message telling them so.
                await context.send("You have not registered your timezone in this server!")
            else:
                # Respond with the timezone the user has set for this server and their current time.
                timezone = fetch[0]
                currentTime = datetime.now(tz=ZoneInfo(timezone[0])).strftime("%H:%M")
                await context.send(f"Your timezone is: `{timezone}`\nThe current time is: `{currentTime}`")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")
    
    """
    Timezone Remove Command.
    Removes the registered timezone for a user in the current server.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @timezone_set.subcommand(
        sub_cmd_name="remove",
        sub_cmd_description="Removes the registered timezone for a user in the current server"
    )
    async def timezone_remove(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()
        
        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Query the databse for any rows with the current userID and guildID.
            params = (str(context.author_id), str(context.guild_id),)
            res = cur.execute(f"SELECT timezone FROM timezones WHERE userID = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if this user has a timezone set for this server.
            if (fetch is None):
                # If the user has not set their timezone for this server we will send them a message telling them so.
                await context.send("You have not registered your timezone in this server!")
            else:
                # Delete the user's timezone for this server from the database.
                cur.execute(f"DELETE FROM timezones WHERE userID = ? AND guildID = ?", params)
                con.commit()

                # Respond to the user and tell them that their timezone has been removed.
                await context.send(f"Your timezone has been removed from this server.")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")
    
    """
    Timezone List Command.
    Lists the time for all users with registered timezones in the current server.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @timezone_set.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="Lists the time for all users with registered timezones in the current server"
    )
    async def timezone_list(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()
        
        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Query the databse for any rows with the current guildID.
            params = (str(context.guild_id),)
            res = cur.execute(f"SELECT timezone, userID FROM timezones WHERE guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchall()

            # Checks if the results list is empty.
            if (not fetch):
                # If the list is empty we will send a message, to the user who invoked this command, saying so.
                await context.send("No users have registered there timezone yet!")
                return
            
            # Create a dictionary to store the users with registered timezones.
            user_dict = {}

            # Loop through all the users with registered timezones in this server.
            for timezone in fetch:
                # Get the current time and username for all people with registered timezones.
                time = datetime.now(tz=ZoneInfo(timezone[0])).strftime("%H:%M")
                user_name = context.client.get_user(timezone[1]).display_name

                # Put the users in a dictionary.
                if (time in user_dict):
                    user_dict[time].append(user_name)
                else:
                    user_dict[time] = [user_name]
            
            # Get all the times from the user dictionary.
            timezone_list = list(user_dict.keys())

            # Sort the times.
            sorted_timezone_list = sorted(timezone_list, key=lambda x: float(f"{x[0:2]}{float(x[3:4])/60.0 * 100.0}"))
            
            # Sort the users using the sorted times.
            sorted_user_dict = {k: user_dict[k] for k in sorted_timezone_list if k in user_dict}

            # Start building a list to send in the message.
            message = "Registered timezones for this server:\n```\n"
            
            # Add every time to the list and list every user with that time alongside it.
            for time_display, name_list in sorted_user_dict.items():
                message = f"{message}{time_display} - [{', '.join(name_list)}]\n"
            message = message + "```"

            # Send the list to the user who invoked this command.
            await context.send(message)

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")