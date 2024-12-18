# Discord integration using servertap

This Python program bridges the gap between a Discord server and a Minecraft server, allowing for two-way communication and server status checks. It uses the Discord API, a Minecraft server with the servertap plugin, and Flask for handling incoming webhooks.
Inspired by [Discord Chat Merge](https://www.spigotmc.org/resources/discord-chat-merge.82981/)
## Features

* **Two-way chat:** Sends messages from Discord to Minecraft and vice versa.
* **Discord:** Shows player join/leave messages, deaths, kicks and chat messages.
* **`/ping` command:** Checks the Minecraft server's status (version, TPS, online players).
* **Configuration via `config.json`:** Easily customizable settings.

## Requirements

* Python 3.6+
* `discord.py` library
* `requests` library
* `Flask` library
* A Minecraft server with servertap.
* A Discord bot token.
## Bot creation
   For now, follow the guide from [Discord Chat Merge](https://www.spigotmc.org/resources/discord-chat-merge.82981/). The only difference is that the bot also requires the text permission **Read Message History**
## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/discord-minecraft-chat-bridge.git
   ```
2. Edit config.json file
   The file should contain the following:
   ```
   {
    "bot_token": "YOUR_DISCORD_BOT_TOKEN",
    "channel_id": YOUR_DISCORD_CHANNEL_ID,
    "broadcast_url": "YOUR_MINECRAFT_WEBHOOK_URL",  # e.g., http://your-server-ip:port
    "broadcast_key": "YOUR_WEBHOOK_API_KEY", # Used to authorize minecraft webhooks
    "application_id": YOUR_DISCORD_APPLICATION_ID
   }
   ```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
