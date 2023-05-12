from util.config_manager import Config
from util.database_manager import Database
from extensions.database_cleanup import DatabaseCleanupExtension

from interactions import Intents, Client, listen


# Get the config for the bot.
Config.read_config()
config = Config.get_config()

# Setup the bot database.
Database.setup_bot_database()

# Create a client instance for connecting to discord.
client = Client(
        token=config["token"],
        intents=Intents.new(default=True, message_content=True, guild_members=True, direct_messages=True),
        delete_unused_application_cmds=True,
        fetch_members=True,
        send_command_tracebacks=False)

# Check if the testing mode is enabled in the config.
if (config["testing_mode_enabled"]):
    # If the testing mode is enabled we will set the debug scope to the guild ID specified in the config and enable the sending of command tracebacks.
    print("Testing mode enabled.\nSlash commands will be automatically instantiated with guild ID scope specified in config.")
    client.send_command_tracebacks=True
    client.debug_scope=config["testing_guild_id"]

# Listen for ready event.
@listen()
async def on_ready():
    DatabaseCleanupExtension.on_ready_cleanup(client)
    print("")
    print(f"Logged in as {client.user}")

# Load the extensions for the bot.
client.load_extension(name=".general", package="extensions")
client.load_extension(name=".tags", package="extensions")
client.load_extension(name=".blacklist", package="extensions")
client.load_extension(name=".timezones", package="extensions")
client.load_extension(name=".database_cleanup", package="extensions")

# Start the bot and connect to discord.
client.start()