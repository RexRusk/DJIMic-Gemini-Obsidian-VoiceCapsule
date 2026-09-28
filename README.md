# DJI Mic Mini Knowledge Q&A

Speech-to-text with Gemini, plus answers drawn from your own Markdown notes.

This repository starts from [DjiMic3-Gemini-Obsidian-VoiceCapsule](https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule) and its original [README](https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule/blob/main/README.md). That project describes a macOS flow: DJI Mic recording, automatic USB detection, Gemini transcription, and Obsidian notes. The one-command installer it documents, `./scripts/mac/install.sh`, is not in the tree. The scripts that actually run are the Python tools under `scripts/python/`.

This version keeps that transcription path and adds a **knowledge base**. You write the notes. The program answers fixed questions from those notes only.

Hardware control of the microphone is out of scope. [DJI-Mic-Control](https://github.com/ShadowBitBasher/DJI-Mic-Control) is a separate USB settings tool and is not used here. Any microphone that can select as an input device is enough. DJI Mic Mini is the one used during setup: connect the receiver by USB-C and wait until the MIC RX light is solid green, then choose it as the input device.

## What the knowledge base does

Notes live in [`knowledge/`](knowledge/) as Markdown files, one topic per file. [`scripts/python/ask_knowledge.py`](scripts/python/ask_knowledge.py) reads those files, picks passages related to the question, and asks Gemini to answer from that text.

- The knowledge base is whatever you put in `knowledge/`. Audio transcription does not edit those files.
- A run does not remember earlier questions. Each question is answered from the current notes.
- The question and answer are saved under `dialogues/` as a separate Markdown file. That folder is not read back into the knowledge base.
- If `OBSIDIAN_VAULT_PATH` in `configs/.env` points at a real directory, that directory is used instead of `knowledge/`. The Obsidian app does not need to be open. [`scripts/python/obsidian_sync.py`](scripts/python/obsidian_sync.py) is only for writing a transcription into a vault inbox.

## Setup

Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install google-generativeai python-dotenv PyYAML pydub rich PySocks
```

Create a Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey), then copy the template and edit the copy. `configs/.env` is gitignored.

```powershell
Copy-Item configs\.env.template configs\.env
```

Set at least:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

`gemini-2.5-flash` in the original template no longer accepts `generateContent`. Transcription and Q&A use the system proxy already configured for the browser (`Internet Settings`), so Python reaches the Gemini API the same way the browser does.

Check the key, then transcribe a file:

```powershell
python scripts\python\transcribe.py --test
python scripts\python\transcribe.py path\to\recording.m4a
```

`--test` only checks that the key is present in `configs/.env`. A real transcription is the network check.

## Ask the knowledge base

1. Add Markdown notes under `knowledge/`. Example `knowledge/general.md`:

```markdown
Voice Capsule uses Google Gemini 2.5 Flash to turn speech into text.
The microphone is a DJI Mic Mini, connected over USB-C and selected as the input device.
```

2. Put one question per line in [`configs/preset_questions.txt`](configs/preset_questions.txt). Lines starting with `#` are ignored.

3. Run:

```powershell
python scripts\python\ask_knowledge.py
```

Or ask a single question:

```powershell
python scripts\python\ask_knowledge.py "What does Voice Capsule use for speech to text?"
```

The script prints the answer and the note filenames it actually sent to the model. It also writes `dialogues/answers-YYYYMMDD-HHMMSS.md`.

## Layout added here

```text
knowledge/                         Your Markdown notes
configs/preset_questions.txt       Fixed questions for the knowledge base
scripts/python/transcribe.py       Gemini transcription, using the system proxy
scripts/python/ask_knowledge.py    Answer questions from knowledge/
dialogues/                         Saved Q&A transcripts (not part of the knowledge base)
```

Personal notes, `dialogues/`, audio files, and `configs/.env` stay out of git.
