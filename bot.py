import os
import subprocess
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Retrieve environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# Check for missing environment variables
if not api_id or not api_hash or not bot_token:
    logger.error("Missing environment variables. Please check your .env file.")
    exit(1)

print("Starting client...")
try:
    client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
    logger.info("Client started successfully.")
except Exception as e:
    logger.error(f"Failed to start client: {str(e)}")
    exit(1)

@client.on(events.NewMessage(pattern=r'^/leech (.+)'))
async def leech(event):
    try:
        args = event.pattern_match.group(1).split('|')
        if len(args) != 3:
            await event.reply("Format: /leech <url>|<key>|<name>")
            return
        url, key, name = args[0], args[1], args[2]
        temp_file = "temp_output.mp4"
        final_file = f"{name}.mp4"

        await event.reply(f"Starting download and decryption for: {name}")
        logger.info(f"Received leech command for: {name}")

        # Step 1: Download and decrypt with N_m3u8DL-RE
        try:
            cmd_n = ['./N_m3u8DL-RE', url, '--key', key, '--save-name', 'temp']
            result_n = subprocess.run(cmd_n, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"N_m3u8DL-RE output: {result_n.stdout.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"N_m3u8DL-RE failed: {e.stderr.decode()}")
            await event.reply(f"N_m3u8DL-RE failed: {e.stderr.decode()}")
            return

        # Step 2: Check and decrypt using mp4decrypt if needed
        if not os.path.exists('temp.mp4'):
            try:
                await event.reply("N_m3u8DL-RE failed, trying mp4decrypt...")
                cmd_m = ['mp4decrypt', '--key', key, 'temp.mp4d', temp_file]
                result_m = subprocess.run(cmd_m, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info(f"mp4decrypt output: {result_m.stdout.decode()}")
            except subprocess.CalledProcessError as e:
                logger.error(f"mp4decrypt failed: {e.stderr.decode()}")
                await event.reply(f"mp4decrypt failed: {e.stderr.decode()}")
                return
        else:
            os.rename('temp.mp4', temp_file)

        # Step 3: Muxing audio and video using ffmpeg
        try:
            await event.reply("Muxing audio and video...")
            cmd_f = ['ffmpeg', '-i', temp_file, '-c:v', 'copy', '-c:a', 'copy', '-y', final_file]
            result_f = subprocess.run(cmd_f, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"ffmpeg output: {result_f.stdout.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e.stderr.decode()}")
            await event.reply(f"ffmpeg failed: {e.stderr.decode()}")
            return

        # Step 4: Upload the final file
        await event.reply("Uploading file...")
        await client.send_file(event.chat_id, final_file, caption=f"Done: {name}")
        logger.info(f"File uploaded successfully: {final_file}")

        # Step 5: Cleanup temporary files
        for f in [temp_file, final_file, 'temp.mp4d']:
            if os.path.exists(f):
                os.remove(f)
        await event.reply("Operation complete.")
        logger.info("Temporary files cleaned up.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await event.reply(f"Unexpected error: {str(e)}")

@client.on(events.NewMessage(pattern=r'^/ping'))
async def ping(event):
    await event.reply("Pong, boss.")
    logger.info("Ping command received and responded.")

print("Bot running...")
client.run_until_disconnected()