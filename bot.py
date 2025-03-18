import os
import subprocess
import logging
import uuid
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
api_id = get_env_var('API_ID')
api_hash = get_env_var('API_HASH')
bot_token = get_env_var('BOT_TOKEN')

# Initialize Telegram client
try:
    client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
    logger.info("Telegram client initialized successfully")
except Exception as e:
    logger.error(f"Client initialization failed: {str(e)}")
    exit(1)

@client.on(events.NewMessage(pattern=r'^/leech (.+)'))
async def leech(event):
    try:
        args = event.pattern_match.group(1).split('|')
        if len(args) != 3:
            await event.reply("❌ Invalid format. Use: /leech <url>|<key1,key2,...>|<name>")
            return

        url, keys, name = args[0], args[1], args[2]
        unique_id = uuid.uuid4().hex
        temp_file = f"temp_{unique_id}.mp4"
        final_file = f"{name}_{unique_id}.mp4"
        
        await event.reply(f"🚀 Processing: {name}")
        logger.info(f"New leech request: {name}")
        
        # Step 1: Download with N_m3u8DL-RE
        try:
            cmd_n = ['./N_m3u8DL-RE', url, '--save-dir', 'downloads', '--save-name', 'temp']
            result_n = subprocess.run(cmd_n, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.debug(f"N_m3u8DL-RE output:\n{result_n.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed: {e.stderr}")
            await event.reply(f"❌ Download failed:\n`{e.stderr}`")
            return

        # Step 2: Handle decryption
        keys_list = keys.split(',')
        decrypt_cmd = ['mp4decrypt']
        for key in keys_list:
            decrypt_cmd.extend(['--key', key])
        decrypt_cmd.extend(['downloads/temp.mp4', temp_file])
        
        try:
            result_m = subprocess.run(decrypt_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.debug(f"mp4decrypt output:\n{result_m.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Decryption failed: {e.stderr}")
            await event.reply(f"❌ Decryption failed:\n`{e.stderr}`")
            return

        # Step 3: Mux with ffmpeg
        try:
            await event.reply("🔧 Muxing streams...")
            cmd_f = ['ffmpeg', '-i', temp_file, '-c:v', 'copy', '-c:a', 'copy', '-y', final_file]
            result_f = subprocess.run(cmd_f, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.debug(f"ffmpeg output:\n{result_f.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Muxing failed: {e.stderr}")
            await event.reply(f"❌ Muxing failed:\n`{e.stderr}`")
            return

        # Step 4: Upload file
        await event.reply("📤 Uploading...")
        await client.send_file(event.chat_id, final_file, caption=f"✅ {name}")
        logger.info(f"Upload completed: {final_file}")

        # Step 5: Cleanup
        for f in [temp_file, final_file, 'downloads/temp.mp4']:
            if os.path.exists(f):
                os.remove(f)
        logger.info("Cleanup completed")

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        await event.reply(f"🔥 Critical error:\n`{str(e)}`")

@client.on(events.NewMessage(pattern=r'^/ping'))
async def ping(event):
    await event.reply("🏓 Pong!")
    logger.info("Ping-pong handled")

if __name__ == "__main__":
    logger.info("Bot starting...")
    client.run_until_disconnected()
