#!/bin/bash
# DigitalOcean deployment script for wildfire Discord bot

set -e

echo "🔥 Deploying Wildfire Discord Bot to DigitalOcean..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Installing..."
    
    # Detect OS and install doctl
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv
        sudo mv doctl /usr/local/bin
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install doctl
    else
        echo "❌ Unsupported OS. Please install doctl manually: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
fi

# Check if authenticated
if ! doctl auth list &> /dev/null; then
    echo "🔑 Please authenticate with DigitalOcean:"
    echo "1. Get your API token from: https://cloud.digitalocean.com/account/api/tokens"
    echo "2. Run: doctl auth init"
    exit 1
fi

# Check if Discord token is set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "⚠️  Discord token not set."
    echo "Please set DISCORD_TOKEN environment variable or add it during deployment."
fi

echo "📦 Creating DigitalOcean App..."

# Deploy using App Platform (buildpack only, ~$5/month)
echo "🏗️  Using Python buildpack deployment (cheaper than Docker)"
doctl apps create --spec .do/app.yaml --wait

# Get app ID
APP_ID=$(doctl apps list --format ID --no-header | head -n1)

echo "✅ App created with ID: $APP_ID"
echo ""
echo "🔧 Next steps:"
echo "1. Set your Discord token in the DigitalOcean dashboard:"
echo "   https://cloud.digitalocean.com/apps/$APP_ID/settings"
echo ""
echo "2. Monitor deployment progress:"
echo "   doctl apps get $APP_ID"
echo ""
echo "3. View logs:"
echo "   doctl apps logs $APP_ID --type run"
echo ""
echo "🎉 Your wildfire Discord bot will be live in ~2-3 minutes!"
echo "💰 Cost: ~$5/month for basic deployment"