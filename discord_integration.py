import discord
import requests
import threading
from flask import Flask, request, jsonify
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True

# Use discord.Client instead of commands.Bot for slash commands only
client = discord.Client(intents=intents) # No command_prefix needed

# Load configuration from config.json
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        BOT_TOKEN = config["bot_token"]
        CHANNEL_ID = config["channel_id"]
        BROADCAST_URL = config["broadcast_url"]
        BROADCAST_API_KEY = config["broadcast_key"]
        APPLICATION_ID = config["application_id"]
except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
    print(f"Error loading configuration: {e}")
    print("Please ensure config.json exists and contains the correct keys.")
    exit()

@client.event
async def on_ready():
    print(f'Logged in with bot token {BOT_TOKEN}')
    print('------')
    await register_ping_command()
@client.event
async def on_message(message):
    print(message)
    if message.author.bot:
        print("User is a bot")
        return
    if message.channel.id == CHANNEL_ID:
        global_name = message.author.global_name
        content = message.content
        print("Message to minecraft:", content)
        broadcast_message = f"<§5{global_name}§f> {content}"
        broadcast_to_minecraft(broadcast_message)

def broadcast_to_minecraft(message):
    headers = {
        "accept": "application/json",
        "key": BROADCAST_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"message": message}
    try:
        response = requests.post(f"{BROADCAST_URL}/v1/chat/broadcast", headers=headers, data=data)
        response.raise_for_status()
        print(f"Message broadcasted successfully: {message}")
    except requests.exceptions.RequestException as e:
        print(f"Error broadcasting message: {e}")

app = Flask(__name__)
discord_api_lock = threading.Lock()
async def register_ping_command():
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    json_data = {
        "name": "ping",
        "description": "Responds with pong!",
        "type": 1  # CHAT_INPUT
    }

    try:
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Successfully registered /ping command: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to register /ping command: {e}")

def send_message(channel_id, message):
    """Sends a message to a specific channel."""
    with discord_api_lock:
      url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
      headers = {
          "Authorization": f"Bot {BOT_TOKEN}",
          "Content-Type": "application/json",
      }
      data = {"content": message}
      response = requests.post(url, headers=headers, json=data)
      if response.status_code == 200:
          print("Message sent successfully!")
          print(response.json())
      else:
          print(f"Error sending message: {response.status_code}")
          print(response.text)
@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """Handles incoming webhook events."""
    try:
        data = request.get_json()
        event_type = data.get("eventType")

        if event_type == "PlayerChat":
            player_name = data.get("playerName")
            message = data.get("message")
            discord_message = f"**{player_name}**: {message}"
        elif event_type == "PlayerJoin":
            join_message = data.get("joinMessage")
            discord_message = f":green_circle: {join_message}"
        elif event_type == "PlayerQuit":
            quit_message = data.get("quitMessage")
            discord_message = f":red_circle: {quit_message}"
        elif event_type == "PlayerKick":
            player_name = data.get("player").get("displayName")
            reason = data.get("reason")
            discord_message = f":no_entry: **{player_name}** was kicked: {reason}"
        elif event_type == "PlayerDeath":
            death_message = data.get("deathMessage")
            discord_message = f":skull_crossbones: {death_message}"
        else:
            print(f"Unknown event type: {event_type}")
            return jsonify({"message": "Unknown event type"}), 400
        print("Message to discord:",discord_message)
        channel = client.get_channel(CHANNEL_ID)
        print(channel.id, channel.name)
        send_message(channel.id, discord_message)
        return jsonify({"message": "Event processed successfully"}), 200
    except Exception as e:
        print(f"Error processing webhook event: {e}")
        return jsonify({"message": "Error processing event"}), 500

def run_webhook_server():
    app.run(debug=False, port=5000, host='0.0.0.0')

@client.event  # Use @client.event for interaction handling
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.application_command:
        if interaction.data['name'] == 'ping':
            status_message = ping()  # Call the ping function
            await interaction.response.send_message(status_message)

def ping():
    headers = {
        "accept": "application/json",
        "key": BROADCAST_API_KEY,  # Make sure this is defined somewhere
    }
    try:
        response = requests.get(f"{BROADCAST_URL}/v1/server", headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json() # Parse the JSON response

        version = data.get("version", "Unknown")
        tps = data.get("tps", "Unknown")
        online_players = data.get("onlinePlayers", "Unknown")

        message = f"Server Version: {version}\nTPS: {tps}\nOnline Players: {online_players}"
        
        print(f"Ping successful")  # Keep this for logging purposes
        return message # Return the formatted message

    except requests.exceptions.RequestException as e:
        print(f"Ping Error: {e}")
        return f"Error pinging server: {e}" # Return an error message


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    webhook_thread = threading.Thread(target=run_webhook_server)
    webhook_thread.daemon = True
    webhook_thread.start()

    client.run(BOT_TOKEN)