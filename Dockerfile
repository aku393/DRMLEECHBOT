# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Update pip to the latest version
RUN pip install --upgrade pip

# Install necessary packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    tar \
    unzip \
    && apt-get clean

# Download N_m3u8DL-RE
RUN wget https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.3.0-beta/N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz \
    && tar -xvf N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz \
    && chmod +x N_m3u8DL-RE \
    && mv N_m3u8DL-RE /usr/local/bin/ \
    && rm N_m3u8DL-RE_v0.3.0-beta_linux-x64_20241203.tar.gz

# Download Bento4 for mp4decrypt
RUN wget https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && mv Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && rm -rf Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot script and other necessary files
COPY . .

# Expose a port for health checks (if needed)
EXPOSE 8080

# Set environment variables (these should be configured via Koyeb or passed during deployment)
ENV API_ID=xxx
ENV API_HASH=xxx
ENV BOT_TOKEN=aa:xx

# Run the bot script
ENTRYPOINT ["python", "bot.py"]