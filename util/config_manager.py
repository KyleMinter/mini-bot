import json
import os
import sys

"""
This class manages the config file used for storing the bot settings.

Functionality includes seting up a default config file, if one is not present, and returning a dictionary object representing the config file.
"""
class Config:
    CONFIG_FILENAME = "config.json"

    config = {}

    """
    Returns a predefined config file with default settings.

    @return A dictionary object representing a config file with default settings.
    """
    @staticmethod
    def get_default_config():
        return  {
                    "token": "token",
                    "geoname_api_username": "username",
                    "invite_oauth2_link": "oauth2_link",
                    "bot_database_name": "database_name.db",
                    "keep_server_tags_separate": True,
                    "testing_mode_enabled": False,
                    "testing_guild_id": "guild_id",
                    "blacklist": ["word1", "word2"]
                }

    """
    Attempts to read the config file and load the settings from it. If the config is not found the deafult one will be written to the current directory.
    """
    @staticmethod
    def read_config():
        print("Attempting to read in config.json file...")

        # If the config file exists we will load it.
        if os.path.exists(Config.CONFIG_FILENAME):
            with open(Config.CONFIG_FILENAME, "r") as infile:
                Config.config = json.load(infile)
                print("Successfully read config.json.\n")
        # If the config file doesn't exit we will write a default one and exit the program.
        else:
            with open(Config.CONFIG_FILENAME, "w") as outfile:
                print("Unable to read config.json. Writing a default one to the current directory.\n")
                outfile.write(json.dumps(Config.get_default_config(), indent = 4))
                sys.exit(0)

    """
    Returns an the current config file store in memory.

    @return A dictionary object representing the config file that is currently stored in memory.
    """
    @staticmethod
    def get_config():
        return Config.config