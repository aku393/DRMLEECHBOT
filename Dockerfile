FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . .

# Install system dependencies for ffmpeg and DRM tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Ensure required tools are available
RUN wget -q https://github.com/nilaoda/N_m3u8DL-RE/releases/latest/download/N_m3u8DL-RE && chmod +x N_m3u8DL-RE
RUN wget -q https://zebulon.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-640.x86_64-unknown-linux.tar.gz && tar -xzf Bento4-SDK-1-6-0-640.x86_64-unknown-linux.tar.gz && mv Bento4-SDK-1-6-0-640.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/

# Set execution permissions
RUN chmod +x /usr/local/bin/mp4decrypt

# Expose port (if running a web server for Render, e.g., FastAPI)
EXPOSE 8080

# Start the bot
CMD ["python", "bot.py"]
