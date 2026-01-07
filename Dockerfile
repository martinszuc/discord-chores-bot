FROM python:3.10-slim

WORKDIR /app

# Add a label to help identify the container
LABEL maintainer="discord-chores-bot"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies with pip cache
# Copy requirements first for better Docker layer caching
# Uses BuildKit cache mount for faster rebuilds (requires: DOCKER_BUILDKIT=1)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --cache-dir=/root/.cache/pip -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Copy source code
COPY . .

# Set correct permissions
RUN chmod -R 755 /app

# Run the bot
CMD ["python", "-m", "src.main"]