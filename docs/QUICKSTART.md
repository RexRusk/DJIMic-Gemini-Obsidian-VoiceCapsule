# Quick Start Guide - Gemini-Powered Voice Capsule

## Your Simple Stack

**Hardware**: DJI Mic 3 (~$500-600)  
**Software**: Gemini API (FREE tier) + Obsidian (FREE)  
**Cost**: ~$0/month for personal use

No Chinese services needed. No complicated pipelines. Just Gemini + your vault.

## 5-Minute Setup

### 1. Get Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key

### 2. Install Dependencies

```bash
cd DjiMic3-Gemini-Obsidian-VoiceCapsule
pip install -r scripts/python/requirements.txt
```

### 3. Configure

```bash
# Copy template
cp configs/.env.template configs/.env

# Edit with your values
nano configs/.env
```

Required settings:
```bash
GEMINI_API_KEY=your_key_here
OBSIDIAN_VAULT_PATH=/path/to/your/vault
```

### 4. Test

```bash
# Test API connection
python scripts/python/transcribe.py --test

# Transcribe a file
python scripts/python/transcribe.py recording.wav
```

## Daily Workflow

### Simple 3-Step Process

```
1. RECORD → 2. TRANSCRIBE → 3. SAVE
   (DJI Mic)    (Gemini API)    (Obsidian)
```

### Step 1: Record

- Clip DJI Mic to clothing
- Press record button
- Speak naturally
- Press stop when done

### Step 2: Transfer & Transcribe

```bash
# Connect DJI Mic via USB
# Copy files
cp /Volumes/DJI\ MIC\ 3/RECORD/*.wav ~/voice-inbox/

# Transcribe
python scripts/python/transcribe.py ~/voice-inbox/recording.wav
```

Gemini automatically:
- ✅ Transcribes speech to text
- ✅ Adds punctuation
- ✅ Formats paragraphs
- ✅ Identifies speakers
- ✅ Removes filler words

### Step 3: Create Obsidian Note

```bash
# Auto-create note
python scripts/python/obsidian_sync.py transcription.txt
```

Done! Your note is in Obsidian inbox.

## Web App Workflow (Coming Soon)

For even simpler workflow:

1. Plug in DJI Mic
2. Browser auto-opens: mic3.bluehawana.com
3. Files auto-upload
4. Transcription happens automatically
5. Notes sync to Obsidian

## Personal Vocabulary (Optional)

For specialized terms, maintain a vocabulary list:

```bash
# Add to configs/.env
PERSONAL_VOCABULARY="DJI Mic 3, Gemini, Obsidian, Feynman Technique, Voice Capsule"
```

Gemini will prioritize these terms during transcription.

## Use Cases

### Quick Capture
```bash
# Record thought → Instant note
python scripts/python/transcribe.py thought.wav | \
python scripts/python/obsidian_sync.py --category quick-note
```

### Meeting Notes
```bash
# 2-hour meeting → Formatted minutes
python scripts/python/transcribe.py meeting.wav --output meeting.txt
python scripts/python/obsidian_sync.py meeting.txt --category meeting
```

### Learning (Feynman)
```bash
# Explain concept → Study note
python scripts/python/transcribe.py explanation.wav
python scripts/python/obsidian_sync.py explanation.txt --category learning
```

## Cost Breakdown

### Free Tier (Gemini)
- 60 requests/minute
- ~1500 requests/day
- Enough for: 25+ hours of audio/day

### If you exceed free tier
- Gemini 1.5 Flash: $0.35 per 1M tokens
- 1 hour audio ≈ 10K tokens
- Cost: ~$0.0035 per hour
- 100 hours/month = $0.35

**Compare to market**:
- Otter.ai: $17/month
- Your solution: $0-0.35/month

**Savings: 98%+**

## Troubleshooting

### "API key not found"
```bash
# Check .env file exists
ls configs/.env

# Verify key is set
grep GEMINI_API_KEY configs/.env
```

### "Audio file too large"
```bash
# Split large files
ffmpeg -i large.wav -f segment -segment_time 600 -c copy part%03d.wav
```

### "Transcription quality poor"
- Use DJI Mic (not phone mic)
- Record in quiet environment
- Speak clearly (not necessarily slowly)
- Add specialized terms to vocabulary list

## Next Steps

1. ✅ Record your first audio
2. ✅ Transcribe with Gemini
3. ✅ Create Obsidian note
4. ✅ Review and link to other notes
5. ✅ Repeat daily

Build your voice knowledge base one recording at a time!

## Advanced: Automation

### Auto-process on USB connect

```bash
# Install USB monitor
brew install fswatch

# Run watcher
./scripts/mac/watch-and-process.sh
```

This will:
- Detect DJI Mic connection
- Auto-copy files
- Auto-transcribe
- Auto-create notes

Zero manual work!

---

**Questions?** Check [WORKFLOW.md](WORKFLOW.md) for detailed guide.
