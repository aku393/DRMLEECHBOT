FROM python:3.9-slim

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

# Download and set up Bento4
RUN wget https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && mv Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && rm -rf Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script and other necessary files
COPY . .

# Expose a default port (if your bot needs to listen on a specific port)
EXPOSE 8080

# Use ENTRYPOINT for better compatibility
ENTRYPOINT ["python", "bot.py"]