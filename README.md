# mini-bot
A simple Discord bot with the following major features:
* General commands
* User generated tags
* Timezone registration
* Blacklist filter

---

## Dependencies
The following dependencies are required to contribute to or run this bot:
* [interactions.py](https://github.com/interactions-py/interactions.py)
* [Geocoder](https://geocoder.readthedocs.io/providers/GeoNames.html)
* [tzdata](https://pypi.org/project/tzdata/)

You can use the following commands to install the requirements.
```
pip install -U discord-py-interactions
pip import geocoder
pip install tzdata
```

---

## Configuration
Upon running the bot for the first time, a config file will be created in the working directory.  
You must edit `config.json` in order for the bot to connect to the Discord API.

The default `config.json` will contain the following:
```
"token": "token",
"geoname_api_username": "username",
"invite_oauth2_link": "oauth2_link",
"bot_database_name": "database_name.db",
"clean_user_data": False,
"testing_mode_enabled": False,
"testing_guild_id": "guild_id",
"blacklist": ["word1", "word2"],
"owner_id": "owner_id"
 ```
As can be seen, the default config file is populated with example values, however some of these need to be changed in order for them to function as intended.  
The following describes the function each field in the config file:
* **token:** This is the unique token that is generated at the [Discord Developer Portal](https://discord.com/developers/applications) when you create a bot. This is required for the bot to function.
* **geoname_api_username:** This is the username of the GeoNames account used to access the GeoNames geographical database. If this field is not provided or is otherwise invalid, the timezone registration feature won't work. You can create a GeoNames account [here](http://www.geonames.org/).
* **invite_oauth2_link:** This is the link generated at the [Discord Developer Portal](https://discord.com/developers/applications) under the `OAuth2`->`URL Generator` page. The link provided here will be provided when a user invokes the `invite` command (If no link is provided, then a predefined message will be sent). When generating the `OAuth2` link, the scopes and bot permissions you choose to include is ultimately up to you, but it is imperitive that the `bot` and `applications.commands` scopes are enabled.
* **bot_database_name:** This is the name of the database file that will store timezone and tag information for the bot.
* **clean_user_data:** This flag determines whether or not user specific data (tags & timezone registrations) are automatically removed from the bot database when a user is removed from a server.
* **testing_mode_enabled:** This flag determines whether or not the bot is in testing mode. While in testing mode unused application commands will automatically be deleted from Discord, and global commands will be synced to the provided `guild ID` for quicker command updates. The testing mode is generally only used during development and not during normal operation.
* **testing_guild_id:** This is the `guild ID` of the server for which global commands will be synced to when the testing mode is enabled. This can be obtained by enabling `Developer Mode`, under the `Advanced` tab in the Discord settings, and then right clicking on a server and selecting `Copy Server ID`.
* **blacklist:** This is a list of words to prevent from being sent by users. If a user sends a message containing any of the words in this list, the message will be automatically deleted. You can add as many words to the blacklist as you'd like.
* **owner_id:** This is the `user ID` of the owner of the bot. This ID is checked for when using certain commands only available to the bot owner. This can be obtained by enabling `Developer Mode`, under the `Advanced` tab in the Discord settings, and then right clicking on a user and selecting `Copy User ID`.

---

## License
Licensed under the MIT liscense: https://github.com/KyleMinter/mini-bot/blob/main/LICENSE
