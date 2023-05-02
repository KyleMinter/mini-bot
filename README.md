# mini-bot
A simple Discord bot with general commands and support for tags.

---

## Dependencies
The following dependencies are required to contribute to or run this bot:
* [Python 3](https://www.python.org/downloads/)
* [interactions.py](https://github.com/interactions-py/interactions.py)

---

## Configuration
Upon running the bot for the first time, a config file will be created in the working directory.  
You must edit `config.json` in order for the bot to connect to the Discord API.

The default `config.json` will contain the following:
```
"token": "token",
"invite_oauth2_link": "oauth2_link",
"tag_database_name": "database_name.db",
"keep_server_tags_separate": True,
"testing_mode_enabled": True,
"testing_guild_id": "guild_id"
 ```
As can be seen, the default config file is populated with example values, however some of these need to be changed in order for them to function as intended.  
The following describes the function each field in the config file:
* **token:** This is the unique token that is generated at the [Discord Developer Portal](https://discord.com/developers/applications) when you create a bot. This is required for the bot to function.
* **invite_oauth2_link:** This is the link generated at the [Discord Developer Portal](https://discord.com/developers/applications) under the `OAuth2`->`URL Generator` page. The link provided here will be provided when a user invokes the `invite` command (If no link is provided, then a predefined message will be sent). When generating the `OAuth2` link, the scopes and bot permissions you choose to include is ultimately up to you, but it is imperitive that the `bot` and `applications.commands` scopes are enabled.
* **tag_database_name:** This is the name of the database file that will store the tags created users using this bot.
* **keep_server_tags_separate:** This flag determines whether or not tags are able to be accessed across Discord servers or not. When enabled, users will only be able to access tags created within the server they are invoking a tag command from.
* **testing_mode_enabled:** This flag determines whether or not the bot is in testing mode. While in testing mode unused application commands will automatically be deleted from Discord, and global commands will be synced to the provided `guild ID` for quicker command updates. The testing mode is generally only used during development and not during normal operation.
* **testing_guild_id:** This is the `guild ID` of the server for which global commands will be synced to when the testing mode is enabled. This can be obtained by enabling `Developer Mode`, under the `Advanced` tab in the Discord settings, and then right clicking on a server and selecting `Copy Server ID`.

---

## License
Licensed under the MIT liscense: https://github.com/KyleMinter/mini-bot/blob/main/LICENSE
