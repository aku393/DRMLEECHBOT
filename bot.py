import os
import subprocess
from telethon import TelegramClient, events

api_id = '20176556'
api_hash = '8136bd26f62a889221fc6d25cebe4e6a'
bot_token = '8053835563:AAHa1a1WOMKBxZeAAjXOipIcv2zwCGy5AZI'

print("Starting client...")
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
print("Client started.")

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

        await event.reply(f"Starting: {name}")

        await event.reply("Downloading and decrypting...")
        cmd_n = ['./N_m3u8DL-RE', url, '--key', key, '--save-name', 'temp']
        result_n = subprocess.run(cmd_n, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"N_m3u8DL-RE output: {result_n.stdout.decode()}")

        if not os.path.exists('temp.mp4'):
            await event.reply("N_m3u8DL-RE failed, trying mp4decrypt...")
            cmd_m = ['mp4decrypt', '--key', key, 'temp.mp4d', temp_file]
            result_m = subprocess.run(cmd_m, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"mp4decrypt output: {result_m.stdout.decode()}")
        else:
            os.rename('temp.mp4', temp_file)

        await event.reply("Muxing audio and video...")
        cmd_f = ['ffmpeg', '-i', temp_file, '-c:v', 'copy', '-c:a', 'copy', '-y', final_file]
        result_f = subprocess.run(cmd_f, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"ffmpeg output: {result_f.stdout.decode()}")

        await event.reply("Uploading...")
        await client.send_file(event.chat_id, final_file, caption=f"Done: {name}")

        for f in [temp_file, final_file, 'temp.mp4d']:
            if os.path.exists(f):
                os.remove(f)

        await event.reply("Finished, boss.")
    except subprocess.CalledProcessError as e:
        await event.reply(f"Command failed: {e.stderr.decode()}")
    except Exception as e:
        await event.reply(f"Shit broke: {str(e)}")

@client.on(events.NewMessage(pattern=r'^/ping'))
async def ping(event):
    await event.reply("Pong, boss.")

print("Bot running...")
client.run_until_disconnected()