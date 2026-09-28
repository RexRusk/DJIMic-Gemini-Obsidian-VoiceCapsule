# Deployment Guide - mic3.bluehawana.com

## ✅ Repository Status

**GitHub**: https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git  
**Status**: ✅ Pushed successfully  
**Branch**: main

## 🔒 Security Checklist

- ✅ `.env` files excluded from git
- ✅ API keys protected
- ✅ `.gitignore` configured properly
- ✅ Only templates committed (`.env.example`, `.env.template`)

## 🚀 Quick Deployment to VPS

### Option 1: Automated Deployment (Recommended)

```bash
# SSH to your VPS
ssh root@your-vps-ip

# Run deployment script
curl -sSL https://raw.githubusercontent.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule/main/deploy/deploy.sh | bash
```

### Option 2: Manual Deployment

```bash
# SSH to VPS
ssh root@your-vps-ip

# Clone repository
cd /opt
git clone https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git
cd DjiMic3-Gemini-Obsidian-VoiceCapsule

# Install dependencies
apt-get update
apt-get install -y python3.11 python3-pip nginx certbot python3-certbot-nginx ffmpeg

# Setup Python environment
cd web-app
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY and OBSIDIAN_VAULT_PATH

# Setup systemd service
cp ../deploy/voice-capsule.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable voice-capsule
systemctl start voice-capsule

# Configure Nginx
cp ../deploy/nginx.conf /etc/nginx/sites-available/mic3.bluehawana.com
ln -s /etc/nginx/sites-available/mic3.bluehawana.com /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Setup SSL
certbot --nginx -d mic3.bluehawana.com --email admin@bluehawana.com --agree-tos --non-interactive
```

## 🔧 Configuration

### Required Environment Variables

Create `/opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/web-app/.env`:

```bash
# CRITICAL: Add your actual values
GEMINI_API_KEY=your_actual_gemini_api_key_here
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault

# Optional (defaults are fine)
UPLOAD_DIR=/tmp/voice-capsule/uploads
MAX_FILE_SIZE=104857600
CLEANUP_AFTER_HOURS=24
GEMINI_MODEL=gemini-1.5-flash
TRANSCRIPTION_LANGUAGE=auto
OBSIDIAN_INBOX_FOLDER=00-inbox
```

### DNS Configuration

Point your domain to VPS:

```
Type: A
Name: mic3
Value: YOUR_VPS_IP
TTL: 3600
```

## 📊 Monitoring

### Check Service Status

```bash
# Service status
systemctl status voice-capsule

# View logs
journalctl -u voice-capsule -f

# Check Nginx
systemctl status nginx
nginx -t
```

### Health Check

```bash
# API health
curl https://mic3.bluehawana.com/api/health

# Expected response:
# {"status":"healthy","version":"1.0.0","jobs_active":0,"jobs_total":0}
```

## 🔄 Updates

### Pull Latest Changes

```bash
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule
git pull origin main
systemctl restart voice-capsule
```

### Update Dependencies

```bash
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/web-app
pip3 install -r requirements.txt --upgrade
systemctl restart voice-capsule
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u voice-capsule -n 100 --no-pager

# Test manually
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/web-app
python3 main.py
```

### SSL Certificate Issues

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

### Permission Issues

```bash
# Fix ownership
chown -R www-data:www-data /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule
chmod -R 755 /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart service
systemctl restart voice-capsule

# Reduce workers (edit service file)
nano /etc/systemd/system/voice-capsule.service
# Add: --workers 2
systemctl daemon-reload
systemctl restart voice-capsule
```

## 📈 Performance Optimization

### Enable Gzip Compression

Add to Nginx config:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### Add Caching

```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=upload:10m rate=10r/m;

location /api/upload {
    limit_req zone=upload burst=5;
}
```

## 🔐 Security Hardening

### Firewall

```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### Fail2ban

```bash
apt-get install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Auto-updates

```bash
apt-get install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

## 📞 Support

- GitHub Issues: https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule/issues
- Documentation: https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule/tree/main/docs

## 🎯 Next Steps

1. ✅ Deploy to VPS
2. ✅ Configure DNS
3. ✅ Setup SSL
4. ✅ Test upload functionality
5. ✅ Configure Obsidian vault path
6. ✅ Test end-to-end workflow
7. 🔄 Monitor and optimize

---

**Live URL**: https://mic3.bluehawana.com  
**Status**: Ready for deployment
