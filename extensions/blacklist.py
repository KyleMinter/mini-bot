import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from util.config_manager import Config

from interactions import listen, Message, Extension
from interactions.api.events import MessageCreate, MessageUpdate

"""
A class representing an extension of the bot. This extention contains the functionality for the blacklist provided by the bot.
"""
class BlacklistExtension(Extension):
    """
    MessageCreate event listener.
    This is a callback function that is called when a MessageCreate event is triggered.
    This function will delete the message that triggered the event if it contains any blacklisted words.

    @param event The event context.
    """
    @listen(MessageCreate)
    async def on_message_create(self, event: MessageCreate):
        if (self.message_contains_blacklisted_word(event.message.content)):
            await event.message.delete()
    
    """
    MessageUpdate event listener.
    This is a callback function that is called when a MessageUpdate event is triggered.
    This function will delete the message that triggered the event if it contains any blacklisted words.

    @param event The event context.
    """
    @listen(MessageUpdate)
    async def on_message_update(self, event: MessageUpdate):
        if (self.message_contains_blacklisted_word(event.after.content)):
            await event.after.delete()
    
    """
    Determines if a message contains a blacklisted word.
    Checks if any of the blacklisted words, specified in the config, are present in the message. Returns True if any are present, False if not.

    @param message The contents of the message.
    @return True if the message contains any blacklisted words, Flase if not.
    """
    @staticmethod
    def message_contains_blacklisted_word(message: str):
        # Get the blacklist from the config.
        blacklist = Config.get_config()["blacklist"]

        # Loop through the blacklist.
        for blacklisted_word in blacklist:
            # If the message contains the current word we are indexing, return True.
            if (blacklisted_word != "" and message.__contains__(blacklisted_word)):
                return True
        
        # If no blacklisted words were found in the message, return False.
        return False