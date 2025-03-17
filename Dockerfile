# Start with a slim Python base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system tools (ffmpeg, wget, tar, unzip)
RUN apt update && apt install -y ffmpeg wget tar unzip && rm -rf /var/lib/apt/lists/*

# Install N_m3u8DL-RE (latest binary as of 2025)
RUN wget https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.3.0-beta/N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz \
    && tar -xvf N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz \
    && chmod +x N_m3u8DL-RE \
    && rm N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz

# Install mp4decrypt (Bento4 suite)
RUN wget https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && mv Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && rm -rf Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
