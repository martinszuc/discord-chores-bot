FROM python:3.12-slim

WORKDIR /app

LABEL maintainer="discord-chores-bot"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --cache-dir=/root/.cache/pip -r requirements.txt

RUN mkdir -p /app/data

COPY . .

RUN chmod -R 755 /app

CMD ["python", "-m", "src.main"]