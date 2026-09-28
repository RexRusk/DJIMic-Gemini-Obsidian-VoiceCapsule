# Setup Checklist for mic3.bluehawana.com

## ✅ Pre-Deployment

### 1. Get Gemini API Key
- [ ] Visit: https://aistudio.google.com/app/apikey
- [ ] Click "Create API Key"
- [ ] Copy the key (keep it secure!)

### 2. Configure Cloudflare DNS
- [ ] Login to Cloudflare dashboard
- [ ] Select domain: bluehawana.com
- [ ] Add DNS record:
  ```
  Type: A
  Name: mic3
  Content: YOUR_VPS_IP
  Proxy: Proxied (orange cloud)
  TTL: Auto
  ```
- [ ] Wait for DNS propagation (usually 1-5 minutes)

### 3. Verify DNS
```bash
# Check DNS resolution
dig mic3.bluehawana.com

# Or use
nslookup mic3.bluehawana.com
```

## 🚀 Deployment Steps

### Step 1: SSH to VPS
```bash
ssh root@YOUR_VPS_IP
```

### Step 2: Run Deployment Script
```bash
cd /opt
git clone https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git
cd DjiMic3-Gemini-Obsidian-VoiceCapsule/deploy
chmod +x deploy.sh
./deploy.sh
```

This will:
- ✅ Install system dependencies
- ✅ Setup Python environment
- ✅ Configure Nginx
- ✅ Setup SSL certificate
- ✅ Create systemd service

### Step 3: Configure Credentials
```bash
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/deploy
chmod +x setup-credentials.sh
./setup-credentials.sh
```

You'll be prompted for:
1. **Gemini API Key** (paste your key)
2. **Obsidian Vault Path** (e.g., `/home/harvad/Obsidian/Personal-OS`)

The script will:
- ✅ Validate API key
- ✅ Test connection
- ✅ Set secure permissions
- ✅ Start the service

## 🔍 Verification

### Check Service Status
```bash
systemctl status voice-capsule
```

Expected output:
```
● voice-capsule.service - Voice Capsule API
   Loaded: loaded
   Active: active (running)
```

### Check Logs
```bash
journalctl -u voice-capsule -f
```

### Test API
```bash
curl https://mic3.bluehawana.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "jobs_active": 0,
  "jobs_total": 0
}
```

### Test Web Interface
Open browser: https://mic3.bluehawana.com

You should see the Voice Capsule upload interface.

## 🐛 Troubleshooting

### DNS Not Resolving
```bash
# Check Cloudflare DNS
dig mic3.bluehawana.com @1.1.1.1

# Clear local DNS cache (Mac)
sudo dscacheutil -flushcache

# Wait 5-10 minutes for propagation
```

### SSL Certificate Issues
```bash
# Check certificate
certbot certificates

# Renew if needed
certbot renew --force-renewal

# Restart Nginx
systemctl restart nginx
```

### Service Won't Start
```bash
# Check detailed logs
journalctl -u voice-capsule -n 100 --no-pager

# Test manually
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/web-app
python3 main.py

# Check .env file
cat .env
```

### API Key Invalid
```bash
# Re-run credential setup
cd /opt/DjiMic3-Gemini-Obsidian-VoiceCapsule/deploy
./setup-credentials.sh
```

## 📊 Post-Deployment

### Monitor Service
```bash
# Real-time logs
journalctl -u voice-capsule -f

# Service status
systemctl status voice-capsule

# Nginx status
systemctl status nginx
```

### Test Upload
1. Visit https://mic3.bluehawana.com
2. Upload a test audio file (WAV/MP3)
3. Wait for transcription
4. Verify note created in Obsidian

### Setup Monitoring (Optional)
```bash
# Install monitoring tools
apt-get install htop iotop

# Check resource usage
htop

# Monitor disk space
df -h
```

## 🔐 Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] Fail2ban installed
- [ ] SSL certificate active
- [ ] .env file permissions: 600
- [ ] Regular backups configured

## 📝 Notes

### Cloudflare SSL Mode
If using Cloudflare proxy (orange cloud):
1. Go to SSL/TLS settings
2. Set mode to "Full (strict)"
3. Origin certificate will be from Let's Encrypt

### Obsidian Vault Access
Make sure the vault path is accessible by the www-data user:
```bash
# Check permissions
ls -la /path/to/obsidian/vault

# Fix if needed
chown -R www-data:www-data /path/to/obsidian/vault
chmod -R 755 /path/to/obsidian/vault
```

## ✅ Success Criteria

You're done when:
- ✅ https://mic3.bluehawana.com loads
- ✅ Can upload audio file
- ✅ Transcription completes successfully
- ✅ Note appears in Obsidian vault
- ✅ Service runs without errors
- ✅ SSL certificate is valid

## 🎉 Next Steps

1. Test with real DJI Mic 3 recordings
2. Customize note templates
3. Setup personal vocabulary list
4. Configure auto-categorization
5. Share with team/family

---

**Need help?** Open an issue: https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule/issues
