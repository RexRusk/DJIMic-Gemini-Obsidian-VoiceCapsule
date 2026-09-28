#!/bin/bash
# Secure credential setup script
# Run this on your VPS to configure API keys

set -e

echo "🔐 Voice Capsule - Secure Credential Setup"
echo "=========================================="
echo ""

# Check if running on VPS
if [ ! -d "/opt/DjiMic3-Gemini-Obsidian-VoiceCapsule" ]; then
    echo "❌ Error: Project not found at /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule"
    echo "Please deploy the application first using deploy.sh"
    exit 1
fi

cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/web-app

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
else
    echo "⚠️  .env file already exists, will update it"
fi

# Prompt for Gemini API Key
echo ""
echo "📝 Enter your Gemini API Key:"
echo "   (Get it from: https://aistudio.google.com/app/apikey)"
read -s GEMINI_KEY
echo ""

# Validate key format (basic check)
if [ -z "$GEMINI_KEY" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

# Prompt for Obsidian Vault Path
echo "📝 Enter your Obsidian Vault Path:"
echo "   Example: /home/harvad/Obsidian/Personal-OS"
read VAULT_PATH

if [ -z "$VAULT_PATH" ]; then
    echo "❌ Error: Vault path cannot be empty"
    exit 1
fi

# Update .env file
echo "⚙️  Updating configuration..."

# Use sed to replace values
sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_KEY|g" .env
sed -i "s|OBSIDIAN_VAULT_PATH=.*|OBSIDIAN_VAULT_PATH=$VAULT_PATH|g" .env

# Set secure permissions
chmod 600 .env
chown www-data:www-data .env

echo ""
echo "✅ Configuration updated successfully!"
echo ""
echo "📋 Current configuration:"
echo "   - Gemini API Key: ${GEMINI_KEY:0:10}...${GEMINI_KEY: -4}"
echo "   - Obsidian Vault: $VAULT_PATH"
echo ""

# Test API key
echo "🧪 Testing Gemini API connection..."
python3 << EOF
import os
os.environ['GEMINI_API_KEY'] = '$GEMINI_KEY'
try:
    import google.generativeai as genai
    genai.configure(api_key='$GEMINI_KEY')
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Say "API key works!"')
    print('✅ API key is valid!')
except Exception as e:
    print(f'❌ API key test failed: {e}')
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Ready to start the service!"
    echo ""
    read -p "Start Voice Capsule service now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl restart voice-capsule
        echo "✅ Service restarted"
        echo ""
        echo "Check status: systemctl status voice-capsule"
        echo "View logs: journalctl -u voice-capsule -f"
    fi
else
    echo "⚠️  Please check your API key and try again"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo "🌐 Your app should be live at: https://mic3.bluehawana.com"
