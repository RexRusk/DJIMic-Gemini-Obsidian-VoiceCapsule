# Voice Capsule Web Application

Web interface for mic3.bluehawana.com - Upload audio files and get instant transcriptions.

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run server
python main.py
```

Visit: http://localhost:8000

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### VPS Deployment

```bash
# On your VPS (as root)
cd /opt
git clone https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git
cd DjiMic3-Gemini-Obsidian-VoiceCapsule/deploy
chmod +x deploy.sh
./deploy.sh
```

This will:
- Install dependencies
- Setup Nginx reverse proxy
- Configure SSL with Let's Encrypt
- Create systemd service
- Start the application

## API Endpoints

### POST /api/upload
Upload audio file for transcription

**Request:**
- Content-Type: multipart/form-data
- Body: file (audio file)

**Response:**
```json
{
  "job_id": "uuid",
  "message": "Upload successful"
}
```

### GET /api/status/{job_id}
Check processing status

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "message": "Transcribing audio...",
  "result": null
}
```

### GET /api/result/{job_id}
Get transcription result

**Response:**
```json
{
  "transcription": "Full text...",
  "note_path": "/path/to/note.md",
  "word_count": 1234,
  "completed_at": "2024-03-15T10:30:00"
}
```

### GET /api/health
Health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "jobs_active": 2,
  "jobs_total": 10
}
```

## Configuration

Environment variables in `.env`:

```bash
# Required
GEMINI_API_KEY=your_key_here
OBSIDIAN_VAULT_PATH=/path/to/vault

# Optional
UPLOAD_DIR=/tmp/voice-capsule/uploads
MAX_FILE_SIZE=104857600
CLEANUP_AFTER_HOURS=24
GEMINI_MODEL=gemini-1.5-flash
```

## Security

- HTTPS only (enforced by Nginx)
- File size limits
- Automatic cleanup
- No permanent storage
- API key authentication (coming soon)

## Monitoring

```bash
# View logs
journalctl -u voice-capsule -f

# Check status
systemctl status voice-capsule

# Restart service
systemctl restart voice-capsule
```

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl -u voice-capsule -n 50

# Verify .env file
cat /opt/voice-capsule/web-app/.env

# Test manually
cd /opt/voice-capsule/web-app
python main.py
```

### SSL certificate issues
```bash
# Renew certificate
certbot renew

# Test renewal
certbot renew --dry-run
```

### High memory usage
```bash
# Reduce workers in systemd service
nano /etc/systemd/system/voice-capsule.service
# Change: --workers 2

systemctl daemon-reload
systemctl restart voice-capsule
```

## Development

### Running tests
```bash
pytest tests/
```

### Code formatting
```bash
black main.py
pylint main.py
```

## License

MIT License - see LICENSE file
