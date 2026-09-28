#!/bin/bash
# Deployment script for Voice Capsule on VPS

set -e

echo "🚀 Deploying Voice Capsule to mic3.bluehawana.com"

# Configuration
DOMAIN="mic3.bluehawana.com"
APP_DIR="/opt/voice-capsule"
REPO_URL="https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y \
    python3.11 \
    python3-pip \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    ffmpeg

# Clone or update repository
if [ -d "$APP_DIR" ]; then
    echo "📥 Updating repository..."
    cd "$APP_DIR"
    git pull
else
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# Install Python dependencies in virtual environment
echo "📦 Setting up Python virtual environment..."
cd "$APP_DIR/web-app"

# Install python3-venv if not present
apt-get install -y python3-venv python3-full

# Create virtual environment
python3 -m venv venv

# Install packages in venv
echo "📦 Installing Python packages..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Setup environment
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   nano $APP_DIR/web-app/.env"
    echo ""
    read -p "Press enter after editing .env file..."
fi

# Create systemd service
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/voice-capsule.service <<EOF
[Unit]
Description=Voice Capsule API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR/web-app
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=$APP_DIR/web-app/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx (HTTP only first)
echo "⚙️  Configuring Nginx..."
cp "$APP_DIR/deploy/nginx-http.conf" "/etc/nginx/sites-available/$DOMAIN"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Start services first
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable voice-capsule
systemctl restart voice-capsule
systemctl restart nginx

# Wait for service to be ready
sleep 5

# Setup SSL with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@bluehawana.com

# Restart Nginx with SSL
systemctl restart nginx

# Check status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service status:"
systemctl status voice-capsule --no-pager
echo ""
echo "🌐 Your app is now live at: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  - View logs: journalctl -u voice-capsule -f"
echo "  - Restart: systemctl restart voice-capsule"
echo "  - Stop: systemctl stop voice-capsule"
