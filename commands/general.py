import random
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config

import interactions
from interactions import InteractionContext, Extension, Embed

"""
A class representing an extension of the bot. This extention contains the functionality for the general slash commands provided by the bot.
"""
class GeneralExtension(Extension):
    """
    This is a dummy function called by interactions.py so that it knows how to load the extension.

    @param client The client for the bot.
    """
    def setup(client):
            GeneralExtension(client)

    #----------------------------------------
    # General commands:
    #----------------------------------------

    """
    About Command.
    Displays the credits for the bot to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @interactions.slash_command(
        name="about",
        description="Display the credits for the bot",
        dm_permission=True
    )
    async def about(self, context: InteractionContext):
        # Get the bot user.
        botUser = context.client.user

        # Create an embedded message containing info about the bot.
        embed = Embed()
        embed.set_author(botUser.tag, url="", icon_url=botUser.display_avatar.url)
        embed.add_field("About", "This is a simple discord bot with general commands and support for tags.\nThe source code for this bot can be found on GitHub [here](https://github.com/KyleMinter/mini-bot).")
        embed.add_field("Author", "[Kyle Minter](https://github.com/KyleMinter)")
        embed.add_field("Libraries", "This bot utilizes the following Python libraries:\n[interactions.py](https://github.com/interactions-py/interactions.py)\n[SQLite](https://sqlite.org/index.html)")

        # Respond to the user who invoked this command with the embedded message.
        await context.send(embeds=embed)

    """
    Invite Command.
    Displays the invite link for the bot to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @interactions.slash_command(
        name="invite",
        description="Invite this bot to another server",
        dm_permission=True
    )
    async def invite(self, context: InteractionContext):
        # Get the bot user and the invite link from the config.
        botUser = context.client.user
        inviteLink = Config.get_config()["invite_oauth2_link"]

        # Create an embedded message containing the invite link.
        embed = Embed()
        embed.set_author(botUser.tag, icon_url=botUser.display_avatar.url)
        
        # If no invite link is present in the config we will say so.
        if (inviteLink == ""):
            embed.add_field("Invite", "No invite link was provided by the bot host.")
        else:
            embed.add_field("Invite", f"Click [here]({inviteLink}) to invite this bot to another server!")

        # Respond to the user who invoked this command with the embedded message.
        await context.send(embeds=embed)

    """
    Coinflip Command.
    Flips a vitural coin and displays the results to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @interactions.slash_command(
        name="coinflip",
        description="Flip a coin and see the results",
        dm_permission=True
    )
    async def coin_flip(self, context: InteractionContext):
        results = random.randint(0,1)
        if (results == 0):
            await context.send(content="The coin landed on heads.")
        else:
            await context.send(content="The coin landed on tails.")


    """
    Cringe Command.
    Generates a random percentage value and displays as a measure of cringiness to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @interactions.slash_command(
        name="cringe",
        description="Get a percentage of how cringe you are",
        dm_permission=True
    )
    async def cringe(self, context: InteractionContext):
        percentage = random.randint(0,100)
        await context.send(f"You are {percentage}% cringe.")
    
    """
    8ball Command.
    Generates a random 8ball response and displays it to the user who invoked this command.
    This is function is registered as a slash command using interactions.py and it automatically called when the command is invoked by a Discord user.

    @param context The context for which this command was invoked.
    """
    @interactions.slash_command(
        name="8ball",
        description="Get a response from the 8ball",
        dm_permission=True
    )
    async def cringe(self, context: InteractionContext):
        # List of potential 8ball responses. Source: https://magic-8ball.com/magic-8-ball-answers/
        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
                     "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        
        # Sends a random response from the list.
        await context.send(f"{random.choice(responses)}")
