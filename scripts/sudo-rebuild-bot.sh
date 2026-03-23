#!/bin/bash
# Rebuild Discord Bot with Cleanup - with sudo
# Safely rebuilds the bot image and cleans up old versions
# Usage: ./sudo-rebuild-bot.sh [--no-cache] [-y|--yes]

# Parse flags
NO_CACHE_FLAG=""
AUTO_YES=false

for arg in "$@"; do
    case $arg in
        --no-cache) NO_CACHE_FLAG="--no-cache" ;;
        -y|--yes) AUTO_YES=true ;;
    esac
done

if [[ -n "$NO_CACHE_FLAG" ]]; then
    echo "⚠️  Building WITHOUT cache (slower but ensures fresh dependencies)"
else
    echo "ℹ️  Building WITH cache (faster, uses cached dependencies)"
fi
echo ""

echo "=== Discord Chores Bot - Rebuild with Cleanup ==="
echo ""

# Check if bot is running
BOT_RUNNING=$(sudo docker ps -q -f name=discord-chores-bot)

if [ ! -z "$BOT_RUNNING" ]; then
    echo "✓ Bot is currently running"
fi
echo ""

# Show current bot image
echo "Current bot image(s):"
sudo docker images | grep discord-chores-bot
echo ""

# Count dangling images
DANGLING_COUNT=$(sudo docker images -f "dangling=true" -q | wc -l)
echo "Dangling images: $DANGLING_COUNT"
echo ""

# Ask for confirmation
echo "This will:"
echo "  1. Stop the current bot"
echo "  2. Remove old container"
echo "  3. Remove old images"
if [[ -z "$NO_CACHE_FLAG" ]]; then
    echo "  4. Build image (using cached dependencies)"
else
    echo "  4. Build image (NO cache - fresh download)"
fi
echo "  5. Start bot"
echo "  6. Clean up"
echo ""
echo "Your data (config.json, data/, music/) will NOT be deleted."
echo ""
if [[ "$AUTO_YES" == true ]]; then
    echo "Proceeding automatically (-y flag set)."
else
    read -p "Proceed? (yes/no): " -r REPLY
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]] && [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Navigate to bot directory
cd /home/sysadmin/discord-chores-bot/ || exit 1

echo "Step 1: Stopping bot..."
sudo docker-compose down
echo ""

echo "Step 2: Removing old bot container..."
sudo docker rm discord-chores-bot 2>/dev/null || echo "  (already removed)"
echo ""

echo "Step 3: Removing old bot images..."
sudo docker images | grep discord-chores-bot | awk '{print $3}' | xargs -r sudo docker rmi -f 2>/dev/null || echo "  (no old images)"
echo ""

if [[ -z "$NO_CACHE_FLAG" ]]; then
    echo "Step 4: Building image (using cached dependencies)..."
    # Enable BuildKit for cache mounts if available
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    sudo docker-compose build
else
    echo "Step 4: Building image (NO cache - fresh download)..."
    sudo docker-compose build --no-cache
fi
echo ""

echo "Step 5: Starting bot..."
sudo docker-compose up -d
echo ""

echo "Step 6: Cleaning up dangling images..."
sudo docker image prune -f
echo ""

echo "Step 7: General cleanup..."
sudo docker container prune -f
sudo docker volume prune -f
sudo docker network prune -f
echo ""

echo "=== Rebuild Complete ==="
echo ""

echo "Bot status:"
sudo docker ps | grep discord-chores-bot
echo ""

echo "New image:"
sudo docker images | grep discord-chores-bot
echo ""

echo "Checking logs..."
sleep 3
sudo docker logs discord-chores-bot --tail 20
