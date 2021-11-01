import configparser
import re
import requests
from telethon import TelegramClient, events

# IMPORT CONFIG FILE
settings = configparser.ConfigParser()
settings.read("config.ini")

# TELEGRAM AUTH
api_id = settings.get("TELEGRAM", "API_ID")
api_hash = settings.get("TELEGRAM", "API_HASH")
client = TelegramClient("me", api_id, api_hash)

# REGEX FOR KEYWORDS
keywordsRegex = re.compile(
    r"announcement|integrates|update|cooperation|launch|testnet|"
    r"partnership|announce|listing|listed|list|lists|airdrop|mainnet",
    re.I,
)

def get_tags(event):
    tags = keywordsRegex.findall(event.raw_text)
    tags = list(set([str(elem.lower()) for elem in tags]))
    return tags

# TRACK MESSAGES
@client.on(events.NewMessage)
async def my_event_handler(event):
    if not keywordsRegex.search(event.raw_text) is None:
        data = {
            "chat_id": event.peer_id.channel_id,
            "tags": get_tags(event),
            "message": event.raw_text
        }
        requests.post('http://127.0.0.1:8000/api/posts/', data=data)

# RUNNING SCRIPT
with client:
    client.run_until_disconnected()
