from util.config_manager import Config
from util.database_manager import Database

import interactions
from interactions import Intents


# Get the config for the bot.
Config.read_config()
config = Config.get_config()

# Setup the tag database.
Database.setup_tag_database()

# Create a client instance for connecting to discord.
if (config["testing_mode_enabled"]):
    # If the testing mode is enabled in the config we will set the debug scope to the guild ID specified in the config
    # and enable the deletion of unused application commands along with the sending of command tracebacks.
    print("Testing mode enabled.\nSlash commands will be automatically instantiated with guild ID scope specified in config.")
    client = interactions.Client(
        token=config["token"],
        intents=Intents.DEFAULT,
        delete_unused_application_cmds=True,
        send_command_tracebacks=True,
        debug_scope=config["testing_guild_id"])
    print("")
else:
    # If the testing mode is disabled in the config we will setup the client as normal.
    client = interactions.Client(
        token=config["token"],
        delete_unused_application_cmds=False,
        send_command_tracebacks=False,
        intents=Intents.DEFAULT)

# Listen for ready event.
@interactions.listen()
async def on_ready():
    print(f"Logged in as {client.user}")

# Load command extensions for the bot.
client.load_extension(name = ".general", package="commands")
client.load_extension(name = ".tags", package="commands")

# Start the bot and connect to discord.
client.start()