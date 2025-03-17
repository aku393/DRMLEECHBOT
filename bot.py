import os
import subprocess
from telethon import TelegramClient, events

# Telegram credentials (replace these)
api_id = '20176556'
api_hash = '8136bd26f62a889221fc6d25cebe4e6a'
bot_token = '8053835563:AAHa1a1WOMKBxZeAAjXOipIcv2zwCGy5AZI'

# Start client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern=r'^/leech (.+)'))
async def leech(event):
    try:
        # Parse command: /leech <url>|<kid>|<key>|<name>
        args = event.pattern_match.group(1).split('|')
        if len(args) != 4:
            await event.reply("Format: /leech <url>|<kid>|<key>|<name>")
            return
        url, kid, key, name = args[0], args[1], args[2], args[3]
        temp_file = "temp_output.mp4"
        final_file = f"{name}.mp4"

        # Notify user
        await event.reply(f"Starting: {name}")

        # Download + Decrypt with N_m3u8DL-RE
        await event.reply("Downloading and decrypting...")
        cmd_n = ['./N_m3u8DL-RE', url, '--key', f'{kid}:{key}', '--save-name', 'temp']
        subprocess.run(cmd_n, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check output, fallback to mp4decrypt
        if not os.path.exists('temp.mp4'):
            await event.reply("N_m3u8DL-RE failed, trying mp4decrypt...")
            cmd_m = ['mp4decrypt', '--key', f'{kid}:{key}', 'temp.mp4d', temp_file]
            subprocess.run(cmd_m, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            os.rename('temp.mp4', temp_file)

        # Mux/Merge with ffmpeg
        await event.reply("Muxing audio and video...")
        cmd_f = ['ffmpeg', '-i', temp_file, '-c:v', 'copy', '-c:a', 'aac', '-y', final_file]
        subprocess.run(cmd_f, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Upload to Telegram
        await event.reply("Uploading...")
        await client.send_file(event.chat_id, final_file, caption=f"Done: {name}")

        # Cleanup
        for f in [temp_file, final_file, 'temp.mp4d']:
            if os.path.exists(f):
                os.remove(f)

        await event.reply("Finished, boss.")
    except subprocess.CalledProcessError as e:
        await event.reply(f"Command failed: {e.stderr.decode()}")
    except Exception as e:
        await event.reply(f"Shit broke: {str(e)}")

print("Bot running...")
client.run_until_disconnected()