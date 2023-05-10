import os
import sys
from datetime import date

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config
from util.database_manager import Database

from interactions import Extension, InteractionContext, OptionType, Embed, slash_command, slash_option
from interactions.ext.paginators import Paginator

"""
A class representing an extension of the bot. This extention contains the functionality for the tag slash commands provided by the bot.
"""
class TagExtension(Extension):
    """
    Tag Get Command.
    Displays the specified tag's content to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param name The tag's name.
    """
    @slash_command(
        name="tag_get",
        description="Displays the specified tag's content",
        dm_permission=False
    )
    @slash_option(
        name="name",
        description="The tag's name",
        required=True,
        opt_type=OptionType.STRING
    )
    async def tag_get(self, context: InteractionContext, name: str):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Check if any tags with the same name and guildID exists in the database.
            params = (name, str(context.guild_id),)
            res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE name = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is an existing tag in the database.
            if (fetch is None):
                # If the the specified tag is not in the database we will respond to the user who invoked this command and tell them so.
                await context.send(f"No tags with name '{name}' found!")
            else:
                # Update the amountUsed counter for the tag.
                used_counter = fetch[2]
                used_counter += 1

                # Only updates the tag if they share the same name and guildID.
                params = (used_counter, name, str(context.guild_id),)
                cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ? AND guildID = ?", params)
                
                # Commit the changes to the database.
                con.commit()

                # Respond to the user who invoked this command with the content of the tag.
                content = fetch[1]
                await context.send(f"{content}")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")

    """
    Tag Add Command.
    Creates a tag with a given name and content and responds the user who invoked this command accordingly.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param name The name of the tag.
    @param content The content of the tag.
    """
    @slash_command(
        name="tag_add",
        description="Creates a tag with a given name and content",
        dm_permission=False
    )
    @slash_option(
        name="name",
        description="The name of the tag",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="content",
        description="The content of the tag",
        required=True,
        opt_type=OptionType.STRING
    )
    async def tag_add(self, context: InteractionContext, name: str, content: str):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Check if any tags with the same name and guildID already exists in the database.
            params = (name, str(context.guild_id),)
            res = cur.execute(f"SELECT name FROM tags WHERE name = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is a conflicting tag already in the database.
            if (fetch is None):
                # Gets the current date and stores it as a string with a month abbreviation, day, and year format {Jan-01-2000}.
                currentDate = date.today().strftime("%b-%d-%Y")

                # If there are no conflicting tags with the same name and guildID we will add the new tag to the database.
                params = (name, content, str(context.author_id), str(context.guild_id), currentDate,)
                cur.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, 0)", params)
                con.commit()

                # Respond to the user who invoked this command.
                await context.send(f"Created tag: '{name}'")
            else:
                # Respond to the user who invoked this command and tell them that a conflicting tag already exists.
                await context.send("Tag with that name already exists!")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")

    """
    Tag Delete Command.
    Deletes the specified tag from the bot database and repsonds to the user who invoked this command accordingly.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param name The tag's name.
    """
    @slash_command(
        name="tag_delete",
        description="Deletes the specified tag",
        dm_permission=False
    )
    @slash_option(
        name="name",
        description="The tag's name",
        required=True,
        opt_type=OptionType.STRING
    )
    async def tag_delete(self, context: InteractionContext, name: str):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()

            # Gets the config file.
            config = Config.get_config()

            # Check if any tags with the same name and guildID exists in the database.
            params = (name, str(context.guild_id),)
            res = cur.execute(f"SELECT authorID FROM tags WHERE name = ? AND guildID = ?", params)

            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is an existing tag in the database.
            if (fetch is None):
                # If the the specified tag is not in the database we will respond to the user who invoked this command and tell them so.
                await context.send(f"No tags with name '{name}' found!")
            elif (fetch[0] == str(context.author_id) or config["owner_id"] == str(context.author_id)):
                # Delete the tag with the same name and guildID from the database.
                params = (name, str(context.guild_id),)
                cur.execute(f"DELETE FROM tags WHERE name = ? AND guildID = ?", params)
                
                # Commit the changes to the database.
                con.commit()

                # Respond to the user who invoked this command and tell them that the tag was deleted.
                await context.send(f"Deleted tag '{name}'")
            else:
                # If the user invoking this command isn't the author or bot owner we will tell them so.
                await context.send("This tag can only be deleted by it's author or the bot owner!")
            
            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")

    """
    Tag Info Command.
    Displays the specified tag's info to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param name The tag's name.
    """
    @slash_command(
        name="tag_info",
        description="Displays the info about a specified tag",
        dm_permission=False
    )
    @slash_option(
        name="name",
        description="The tag's name",
        required=True,
        opt_type=OptionType.STRING
    )
    async def tag_info(self, context: InteractionContext, name: str):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Check if any tags with the same name and guildID exists in the database.
            params = (name, str(context.guild_id),)
            res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags WHERE name = ? AND guildID = ?", params)
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is an existing tag in the database.
            if (fetch is None):
                # If the the specified tag is not in the database we will respond to the user who invoked this command and tell them so.
                await context.send(f"No tag with name '{name}' found!")
            else:
                # Get the user object of the author of the tag.
                authorUser = context.client.get_user(fetch[2])

                # Create an embedded message to display the info of the tag in.
                embed = Embed()
                embed.set_author(authorUser.tag, icon_url=authorUser.display_avatar.url)
                embed.add_field(f"Name: {fetch[0]}", f"Date Created: {fetch[4]}\nTimes Used: {fetch[5]}\n Content: {fetch[1]}")

                # Respond to the user who invoked this command with the embedded message.
                await context.send(embeds=embed)

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")
    
    """
    Tag All Command.
    Displays the info for every tag in the database to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @slash_command(
        name="tag_all",
        description="Displays the info of every tag",
        dm_permission=False
    )
    async def tag_all(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()

            # Pull all of the tags from database with the same guildID.
            res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags WHERE guildID = ?", (str(context.guild_id),))
            
            # Store the results of our database query.
            fetch = res.fetchall()
            
            # Check if the list of tags is empty
            if (not fetch):
                # If the list of tags is empty we will respond to the user who invoked this command.
                await context.send("There are no tags yet!")
                return

            # Store a list of embeds for each page in the paginator.
            embeds = []

            # Loop over every row in the fetched results.
            for tag in fetch:
                # Get the user object of the author of the tag.
                authorUser = context.client.get_user(tag[2])

                # Create an embed to display the info of the tag in.
                embed = Embed()
                embed.set_author(authorUser.tag, icon_url=authorUser.display_avatar.url)
                embed.add_field(f"Name: {tag[0]}", f"Date Created: {tag[4]}\nTimes Used: {tag[5]}\n Content: {tag[1]}")

                # Add the embed to the list of embeds.
                embeds.append(embed)

            # Create a paginator from the list of embeds and respond to the user who invoked this command with it.
            paginator = Paginator.create_from_embeds(context.client, *embeds)
            await paginator.send(context)

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")

    """
    Tag Random Command.
    Displays a random tag's content to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @slash_command(
        name="tag_random",
        description="Displays the content of a random tag",
        dm_permission=False
    )
    async def tag_random(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Pull a random tag with the same guildID from the database.
            res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE guildID = ? ORDER BY RANDOM() LIMIT 1", (str(context.guild_id),))
            
            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is an existing tag in the database.
            if (fetch is None):
                await context.send("There are no tags saved to the database.")
            else:
                # Get the tag name.
                tagName = fetch[0]
                
                # Update the amountUsed counter for the tag.
                used_counter = fetch[2]
                used_counter += 1
                params = (used_counter, tagName, str(context.guild_id),)
                cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ? AND guildID = ?", params)
                
                # Commit the changes to the database.
                con.commit()

                # Respond to the user who invoked this command with the content of the tag.
                content = fetch[1]
                await context.send(f"{content}")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")
    
    """
    Tag Clear Command.
    Clears the bot database of tags that meet a specified condition. This command can only be used by the owner of the bot.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    @param userid An optional argument which will cause this command to clear all tags with an author who has the specified user ID.
    @param guildid An optional argument which will cause this command to clear all tags with the specified guild ID.
    """
    @slash_command(
        name="tag_clear",
        description="Clears tags that meet a condition. Only the owner of the bot can use this command",
        dm_permission=False
    )
    @slash_option(
        name="userid",
        description="If specified this command will clear tags created by the person with the userID",
        required=False,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="guildid",
        description="If specified this command will clear tags created within a server with the guildID",
        required=False,
        opt_type=OptionType.STRING
    )
    async def tag_clear(self, context: InteractionContext, userid: str = "", guildid: str = ""):
        # Check if the user invoking this command is the owner specified in the config.
        config = Config.get_config()
        if (config["owner_id"] != str(context.author_id)):
            # If the user is not the owner we will respond to the user and tell them so.
            await context.send("You are not specified as an owner in the config!")
            return
        
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Check the different combinations of options and delete the tags from the database based off of them.
            if (userid == "" and guildid == ""):
                # If no options are specified we will delete all tags from the database.
                params = (str(context.guild_id),)
                cur.execute(f"DELETE FROM tags")
            elif (userid != "" and guildid == ""):
                # If a user ID is specified but not a guild ID, we will delete all tags with the specified user ID.
                params = (userid,)
                cur.execute(f"DELETE FROM tags WHERE authorID = ?", params)
            elif (userid == "" and guildid != ""):
                # If a guild ID is specified but not a user ID, we will delete all tags with the specified guild ID.
                params = (guildid,)
                cur.execute(f"DELETE FROM tags WHERE guildID = ?", params)
            else:
                # If both a user ID and guild ID is specified, we will delete all tags with the specified user ID and guild ID.
                params = (userid, guildid,)
                cur.execute(f"DELETE FROM tags WHERE authorID = ? AND guildID = ?", params)
             
            # Commit the changes to the database.
            con.commit()

            # Respond to the user who invoked this command.
            await context.send("Cleared tags from database with specified conditions.")

            # Close the connection to the database now that we are done accessing it.
            con.close()
        else:
            # If we are unable to get a valid connection to the database we will respond the user who invoked this command and tell them so.
            await context.send("Unable to access bot database!")