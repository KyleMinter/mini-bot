import os
import sys
from datetime import date

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config
from util.database_manager import Database

import interactions
from interactions import Extension, InteractionContext, OptionType, Embed
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
    @interactions.slash_command(
        name="server",
        group_name="tag",
        dm_permission=False,
        sub_cmd_name="get",
        sub_cmd_description="Displays the specified tag's content"
    )
    @interactions.slash_option(
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
            
            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags will only be pulled if they have the same name and guildID.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Check if any tags with the same name and guildID exists in the database.
                params = (name, str(context.guild_id),)
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE name = ? AND guildID = ?", params)
            else:
                # Check if any tags with the same name exists in the database.
                params = (name,)
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE name = ?", params)
            
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

                # Check the config to see if the keep_server_tags_separate flag is set to true.
                if (Config.get_config()["keep_server_tags_separate"]):
                    # Only updates the tag if they share the same name and guildID.
                    params = (used_counter, name, str(context.guild_id),)
                    cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ? AND guildID = ?", params)
                else:
                    # Only updates the tag if they share the same name.
                    params = (used_counter, name,)
                    cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ?", params)
                
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
    @tag_get.subcommand(
        sub_cmd_name="add",
        sub_cmd_description="Creates a tag with a given name and content"
    )
    @interactions.slash_option(
        name="name",
        description="The name of the tag",
        required=True,
        opt_type=OptionType.STRING
    )
    @interactions.slash_option(
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
            
            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags can have the same name as long as they aren't created in the same server.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Check if any tags with the same name and guildID already exists in the database.
                params = (name, str(context.guild_id),)
                res = cur.execute(f"SELECT name FROM tags WHERE name = ? AND guildID = ?", params)
            else:
                # Check if any tags with the same name already exists in the database.
                params = (name,)
                res = cur.execute(f"SELECT name FROM tags WHERE name = ?", params)
            
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
    @tag_get.subcommand(
        sub_cmd_name="delete",
        sub_cmd_description="Deletes the specified tag"
    )
    @interactions.slash_option(
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
            
            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags will only be pulled if they have the same name and guildID.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Check if any tags with the same name and guildID exists in the database.
                params = (name, str(context.guild_id),)
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE name = ? AND guildID = ?", params)
            else:
                # Check if any tags with the same name exists in the database.
                params = (name,)
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE name = ?", params)

            # Store the results of our database query.
            fetch = res.fetchone()

            # Check if there is an existing tag in the database.
            if (fetch is None):
                # If the the specified tag is not in the database we will respond to the user who invoked this command and tell them so.
                await context.send(f"No tags with name '{name}' found!")
            else:
                # Check the config to see if the keep_server_tags_separate flag is set to true.
                # With this flag enabled tags will only be deleted if they have the same name and guildID.
                if (Config.get_config()["keep_server_tags_separate"]):
                    # Delete the tag with the same name and guildID from the database.
                    params = (name, str(context.guild_id),)
                    cur.execute(f"DELETE FROM tags WHERE name = ? AND guildID = ?", params)
                else:
                    # Delete the tag with the same name from the database.
                    params = (name,)
                    cur.execute(f"DELETE FROM tags WHERE name = ?", params)
                
                # Commit the changes to the database.
                con.commit()

                # Respond to the user who invoked this command and tell them that the tag was deleted.
                await context.send(f"Deleted tag '{name}'")

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
    @tag_get.subcommand(
        sub_cmd_name="info",
        sub_cmd_description="Displays the info about a specified tag"
    )
    @interactions.slash_option(
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
            
            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags will only be pulled if they have the same name and guildID.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Check if any tags with the same name and guildID exists in the database.
                params = (name, str(context.guild_id),)
                res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags WHERE name = ? AND guildID = ?", params)
            else:
                # Check if any tags with the same name exists in the database.
                params = (name,)
                res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags WHERE name = ?", params)
            
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
    @tag_get.subcommand(
        sub_cmd_name="all",
        sub_cmd_description="Displays the info of every tag."
    )
    async def tag_all(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()

            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags will only be pulled if they have the same guildID.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Pull all of the tags from database with the same guildID.
                res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags WHERE guildID = ?", (str(context.guild_id),))
            else:
                # Pull all of the tags from database.
                res = cur.execute(f"SELECT name, content, authorID, guildID, date, amountUsed FROM tags")
            
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
    @tag_get.subcommand(
        sub_cmd_name="random",
        sub_cmd_description="Displays the content of a random tag"
    )
    async def tag_random(self, context: InteractionContext):
        # Get a connection to the bot database.
        con = Database.get_connection()

        # Check if the connection is valid.
        if (con is not None):
            # Create a cursor to query the database.
            cur = con.cursor()
            
            # Check the config to see if the keep_server_tags_separate flag is set to true.
            # With this flag enabled tags will only be pulled if they have the same guildID.
            if (Config.get_config()["keep_server_tags_separate"]):
                # Pull a random tag with the same guildID from the database.
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags WHERE guildID = ? ORDER BY RANDOM() LIMIT 1", (str(context.guild_id),))
            else:
                # Pull a random tag from the database.
                res = cur.execute(f"SELECT name, content, amountUsed FROM tags ORDER BY RANDOM() LIMIT 1")
            
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

                # Check the config to see if the keep_server_tags_separate flag is set to true.
                if (Config.get_config()["keep_server_tags_separate"]):
                    # Only updates the tag if they share the same name and guildID.
                    params = (used_counter, tagName, str(context.guild_id),)
                    cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ? AND guildID = ?", params)
                else:
                    # Only updates the tag if they share the same name.
                    params = (used_counter, tagName,)
                    cur.execute(f"UPDATE tags SET amountUsed = ? WHERE name = ?", params)
                
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