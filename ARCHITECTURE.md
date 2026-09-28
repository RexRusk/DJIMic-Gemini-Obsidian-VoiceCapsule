# Voice Capsule Architecture

## Overview

Voice Capsule supports two deployment modes:
1. **Local Mode**: Desktop automation (Mac/Windows)
2. **SaaS Mode**: Web application hosted at mic3.bluehawana.com

## Current Workflow (Workaround)

```
┌─────────────────┐
│  DJI Mic 3      │  Record audio
└────────┬────────┘
         │ Bluetooth (iPhone only - Mac Mini pairing issues)
         ▼
┌─────────────────┐
│  iPhone         │  Download WAV files via DJI Mimo app
│  (DJI Mimo)     │
└────────┬────────┘
         │ Transfer files
         ▼
┌─────────────────┐
│  Mac Mini       │  Upload to web app
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web App        │  mic3.bluehawana.com
│  (SaaS)         │  - Upload WAV files
└────────┬────────┘  - ASR transcription (Gemini)
         │           - Categorize (meeting/brainstorm/idea/etc)
         ▼           - Generate title with date
┌─────────────────┐
│  Obsidian       │  Import as formatted notes
│  (Knowledge)    │
└─────────────────┘
```

## Target Workflow (Ideal)

```
┌─────────────────┐
│  DJI Mic 3      │  Record audio
└────────┬────────┘
         │ USB Cable
         ▼
┌─────────────────┐
│  Mac Mini       │  Auto-detect device
│                 │  Auto-open mic3.bluehawana.com
└────────┬────────┘  Auto-upload files
         │
         ▼
┌─────────────────┐
│  Web App        │  Process automatically
│  (SaaS)         │  - ASR transcription
└────────┬────────┘  - Smart categorization
         │           - Auto-generate title
         ▼
┌─────────────────┐
│  Obsidian       │  Sync via Obsidian API
│  (Knowledge)    │  or local file system
└─────────────────┘
```

## System Components

### 1. Desktop Client (Local Mode)
- **USB Device Monitor**: Detect DJI Mic 3 connection
- **File Watcher**: Monitor for new WAV files
- **Auto-Upload**: Send files to web app
- **Browser Launcher**: Open mic3.bluehawana.com automatically

**Tech Stack:**
- Python 3.11+
- watchdog (file monitoring)
- pyusb (USB detection)
- requests (HTTP client)

### 2. Web Application (SaaS Mode)
- **Frontend**: Upload interface, progress tracking
- **Backend API**: File processing, ASR, categorization
- **Storage**: Temporary file storage (S3/local)
- **Database**: User sessions, processing history

**Tech Stack:**
- Frontend: React/Vue.js or simple HTML5
- Backend: FastAPI (Python) or Flask
- Storage: MinIO/S3 or local filesystem
- Database: SQLite/PostgreSQL

### 3. Transcription Engine
- **Primary**: Google Gemini API (FREE tier, audio-native)
- **Fallback**: OpenAI Whisper API
- **Local**: Whisper.cpp (privacy mode)

**Why Gemini?**
- Direct audio processing (no separate ASR needed)
- Excellent multilingual support
- FREE tier: 60 requests/min
- Works globally
- Auto-formatting and punctuation

### 4. AI Categorization
- **Auto-detect note type**: meeting, brainstorm, discussion, mumbling, self-awareness, product ideas
- **Generate smart titles**: Date + Category + Key topic
- **Extract metadata**: Duration, speakers, key concepts

### 5. Obsidian Integration
- **Method A**: Direct file system write (local vault)
- **Method B**: Obsidian Local REST API plugin
- **Method C**: Obsidian Sync API (cloud vaults)

## Note Categorization System

### Categories
1. **Meeting** - Formal discussions, work meetings
2. **Brainstorm** - Creative ideation sessions
3. **Discussion** - Casual conversations, debates
4. **Mumbling** - Stream of consciousness, thinking out loud
5. **Self-Awareness** - Personal reflections, journaling
6. **Product Ideas** - Feature requests, product concepts
7. **Learning** - Explaining concepts (Feynman Technique)
8. **Quick Note** - Short reminders, to-dos

### Title Format
```
YYYY-MM-DD [Category] - Key Topic
```

Examples:
- `2024-03-15 [Meeting] - Q1 Planning Discussion`
- `2024-03-15 [Product Ideas] - Voice Capsule SaaS Features`
- `2024-03-15 [Self-Awareness] - Morning Reflections`

## Deployment Architecture

### VPS Hosting (mic3.bluehawana.com)

```
┌─────────────────────────────────────────┐
│  VPS Server (Ubuntu 22.04)              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Nginx (Reverse Proxy + SSL)    │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │  FastAPI Application             │   │
│  │  - Upload endpoint               │   │
│  │  - Processing queue              │   │
│  │  - WebSocket (progress updates)  │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │  Worker Processes                │   │
│  │  - Gemini ASR                    │   │
│  │  - AI Categorization             │   │
│  │  - Markdown Generation           │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │  Storage                         │   │
│  │  - /tmp (processing)             │   │
│  │  - /backups (optional)           │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Security Considerations
- HTTPS only (Let's Encrypt)
- API key authentication
- Rate limiting
- File size limits (max 100MB per file)
- Automatic cleanup (delete after 24h)

## Development Phases

### Phase 1: Core Functionality (Current)
- ✅ Local transcription script
- ✅ Configuration system
- ⏳ Obsidian integration
- ⏳ Basic web upload interface

### Phase 2: Web Application
- ⏳ FastAPI backend
- ⏳ Upload interface
- ⏳ Processing queue
- ⏳ AI categorization

### Phase 3: Desktop Automation
- ⏳ USB device detection
- ⏳ Auto-upload client
- ⏳ Browser launcher

### Phase 4: Advanced Features
- ⏳ Multi-user support
- ⏳ Obsidian Sync API
- ⏳ Mobile app (iOS/Android)
- ⏳ Real-time transcription

## Cost Analysis

### Self-Hosted (VPS)
- VPS: $5-20/month (Hetzner/DigitalOcean)
- Domain: $12/year
- SSL: Free (Let's Encrypt)
- Gemini API: ~$0-5/month (free tier sufficient)

**Total: ~$7-25/month** for unlimited users

### vs. Market Solutions
- Otter.ai: $16.99/user/month
- Notion AI: $10/user/month
- Mem.ai: $14.99/user/month

**Savings: 90%+ for personal use, 95%+ for teams**

## Privacy & Data Handling

### Data Flow
1. Audio uploaded → Encrypted in transit (HTTPS)
2. Stored temporarily → Processed → Deleted
3. Transcription → Sent to user's Obsidian
4. No permanent storage on server (optional backup)

### Privacy Modes
- **Cloud Mode**: Use Gemini API (data sent to Google)
- **Hybrid Mode**: Local Whisper + Cloud enhancement
- **Local Only**: All processing on-device (no internet)

## API Endpoints

### Web Application API

```
POST /api/upload
- Upload audio file
- Returns: job_id

GET /api/status/{job_id}
- Check processing status
- Returns: progress, status

GET /api/result/{job_id}
- Get transcription result
- Returns: text, metadata, markdown

POST /api/categorize
- Manually categorize note
- Body: {text, category}

GET /api/health
- Health check
- Returns: status, version
```

## Configuration

### Environment Variables (Web App)
```bash
# API Keys
GEMINI_API_KEY=xxx
OPENAI_API_KEY=xxx (optional)

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Storage
UPLOAD_DIR=/tmp/voice-capsule/uploads
MAX_FILE_SIZE=104857600  # 100MB

# Processing
MAX_CONCURRENT_JOBS=10
CLEANUP_AFTER_HOURS=24

# Features
ENABLE_AI_CATEGORIZATION=true
ENABLE_BACKUPS=false
```

## Next Steps

1. Build FastAPI web application
2. Create upload interface
3. Implement USB detection for Mac Mini
4. Deploy to VPS
5. Test end-to-end workflow
