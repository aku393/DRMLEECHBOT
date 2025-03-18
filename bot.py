import os
import subprocess
import logging
import uuid
import time
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Validate environment variables
def get_env_var(name):
    value = os.getenv(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        exit(1)
    return value

# Fetch credentials
API_ID = get_env_var('API_ID')
API_HASH = get_env_var('API_HASH')
BOT_TOKEN = get_env_var('BOT_TOKEN')

# Initialize Telegram client
try:
    client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    logger.info("Telegram client initialized successfully")
except Exception as e:
    logger.error(f"Client initialization failed: {str(e)}")
    exit(1)

# Function to process MPD download, decryption, and merging
def process_mpd(mpd_url, key, name):
    unique_id = uuid.uuid4().hex
    temp_dir = f"downloads/{unique_id}"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = f"{temp_dir}/{name}.mp4"
    decrypted_file = f"{temp_dir}/{name}_decrypted.mp4"
    final_file = f"{temp_dir}/{name}_final.mp4"

    try:
        # Step 1: Download MPD
        logger.info(f"Downloading MPD for {name}")
        cmd_download = ["./N_m3u8DL-RE", mpd_url, "--save-dir", temp_dir, "--save-name", name]
        subprocess.run(cmd_download, check=True)

        # Step 2: Decrypt MPD
        logger.info(f"Decrypting MPD for {name}")
        decrypt_cmd = ["mp4decrypt", "--key", key, temp_file, decrypted_file]
        subprocess.run(decrypt_cmd, check=True)

        # Step 3: Mux Video and Audio
        logger.info(f"Muxing video/audio for {name}")
        cmd_ffmpeg = ["ffmpeg", "-i", decrypted_file, "-c:v", "copy", "-c:a", "copy", "-y", final_file]
        subprocess.run(cmd_ffmpeg, check=True)

        return final_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing {name}: {e}")
        return None
    finally:
        time.sleep(3)  # Allow files to be written properly before cleanup

@client.on(events.NewMessage(pattern=r'^/leech (.+)'))
async def leech(event):
    args = event.pattern_match.group(1).split('|')
    logger.info(f"Received arguments: {args}")  # Debugging line

    if len(args) != 3:
        await event.reply("❌ Invalid format. Use: /leech <url>|<key>|<name>")
        return

    url, key, name = args[0], args[1], args[2]
    await event.reply(f"🚀 Processing: {name}")

    final_file = process_mpd(url, key, name)

    if final_file and os.path.exists(final_file):
        await event.reply("📤 Uploading...")
        await client.send_file(event.chat_id, final_file, caption=f"✅ {name}")
    else:
        await event.reply("❌ Processing failed.")

@client.on(events.NewMessage(pattern=r'^/ping'))
async def ping(event):
    await event.reply("🏓 Pong!")
    logger.info("Ping-pong handled")

if __name__ == "__main__":
    logger.info("Bot starting...")
    client.run_until_disconnected()
