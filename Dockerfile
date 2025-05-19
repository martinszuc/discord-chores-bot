FROM python:3.10-slim

WORKDIR /app

# Add a label to help identify the container
LABEL maintainer="discord-chores-bot"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Copy source code
COPY . .

# Set correct permissions
RUN chmod -R 755 /app

# Run the bot
CMD ["python", "-m", "src.main"]