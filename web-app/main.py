#!/usr/bin/env python3
"""
Voice Capsule Web Application
FastAPI backend for mic3.bluehawana.com
"""

import os
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(
    title="Voice Capsule API",
    description="Transform voice recordings into organized knowledge",
    version="1.0.0"
)

# Serve static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the web interface"""
    return FileResponse(str(static_dir / "index.html"))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/voice-capsule/uploads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 104857600))  # 100MB
CLEANUP_HOURS = int(os.getenv("CLEANUP_AFTER_HOURS", 24))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job storage (use Redis in production)
jobs: Dict[str, Dict[str, Any]] = {}


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    result: Optional[Dict[str, Any]] = None


# Serve static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
async def root():
    """Serve main page"""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/api/upload")
async def upload_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload audio file for processing"""
    
    # Validate file
    if not file.filename.endswith(('.wav', '.mp3', '.m4a', '.ogg')):
        raise HTTPException(400, "Invalid file format. Use WAV, MP3, M4A, or OGG")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save file
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    file_path.write_bytes(content)
    
    # Create job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "File uploaded, queued for processing",
        "filename": file.filename,
        "file_path": str(file_path),
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    # Start background processing
    background_tasks.add_task(process_audio, job_id)
    
    return {"job_id": job_id, "message": "Upload successful"}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Check processing status"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    return JobStatus(**jobs[job_id])


@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """Get transcription result"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(400, "Job not completed yet")
    
    return job["result"]


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job and cleanup files"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    job = jobs[job_id]
    
    # Delete file
    file_path = Path(job["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Remove job
    del jobs[job_id]
    
    return {"message": "Job deleted"}


async def process_audio(job_id: str):
    """Background task to process audio file"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent / "scripts" / "python"))
    
    try:
        from transcribe import VoiceCapsuleTranscriber
        from obsidian_sync import ObsidianSync
        
        job = jobs[job_id]
        file_path = Path(job["file_path"])
        
        # Update status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Transcribing audio..."
        
        # Transcribe
        transcriber = VoiceCapsuleTranscriber()
        transcription = transcriber.transcribe_audio(file_path)
        
        if not transcription:
            raise Exception("Transcription failed")
        
        jobs[job_id]["progress"] = 60
        jobs[job_id]["message"] = "Creating Obsidian note..."
        
        # Create Obsidian note
        sync = ObsidianSync()
        note_path = sync.create_note(
            transcription=transcription,
            audio_filename=job["filename"]
        )
        
        jobs[job_id]["progress"] = 90
        jobs[job_id]["message"] = "Finalizing..."
        
        # Store result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Processing complete"
        jobs[job_id]["result"] = {
            "transcription": transcription,
            "note_path": str(note_path),
            "word_count": len(transcription.split()),
            "completed_at": datetime.now().isoformat()
        }
        
        # Cleanup file after delay
        await asyncio.sleep(CLEANUP_HOURS * 3600)
        if file_path.exists():
            file_path.unlink()
            
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["progress"] = 0


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "jobs_active": len([j for j in jobs.values() if j["status"] == "processing"]),
        "jobs_total": len(jobs)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
