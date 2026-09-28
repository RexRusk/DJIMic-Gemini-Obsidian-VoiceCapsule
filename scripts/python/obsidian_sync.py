#!/usr/bin/env python3
"""
Personal Voice Capsule - Obsidian Integration
Handles saving transcriptions as formatted Obsidian notes
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    from rich.console import Console
except ImportError as e:
    print(f"Error: Missing required package. Run: pip install -r requirements.txt")
    print(f"Details: {e}")
    exit(1)

console = Console()


@dataclass
class NoteMetadata:
    """Metadata for voice note"""
    title: str
    category: str
    date: str
    time: str
    duration: Optional[str] = None
    tags: list = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ObsidianSync:
    """Handles Obsidian vault integration"""
    
    CATEGORIES = {
        "meeting": "Meeting",
        "brainstorm": "Brainstorm", 
        "discussion": "Discussion",
        "mumbling": "Mumbling",
        "self-awareness": "Self-Awareness",
        "product-ideas": "Product Ideas",
        "learning": "Learning",
        "quick-note": "Quick Note"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Obsidian sync with configuration"""
        self.config = self._load_config(config_path)
        self.vault_path = Path(self.config["vault_path"])
        self.inbox_folder = self.config["inbox_folder"]
        self.template_path = self._get_template_path()
        
        # Ensure inbox folder exists
        self.inbox_path = self.vault_path / self.inbox_folder
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from .env file"""
        if config_path:
            load_dotenv(config_path)
        else:
            # Try multiple locations
            possible_paths = [
                Path.cwd() / "configs" / ".env",
                Path.cwd() / ".env",
                Path.home() / ".personal-voice-capsule" / ".env"
            ]
            for path in possible_paths:
                if path.exists():
                    load_dotenv(path)
                    break
        
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        if not vault_path or vault_path == "/path/to/your/obsidian/vault":
            console.print("[red]Error: OBSIDIAN_VAULT_PATH not set in .env file[/red]")
            exit(1)
            
        return {
            "vault_path": vault_path,
            "inbox_folder": os.getenv("OBSIDIAN_INBOX_FOLDER", "00-inbox"),
            "template": os.getenv("OBSIDIAN_TEMPLATE", "voice-note-template"),
            "date_format": os.getenv("DATE_FORMAT", "%Y-%m-%d"),
            "time_format": os.getenv("TIME_FORMAT", "%H:%M:%S"),
        }
    
    def _get_template_path(self) -> Optional[Path]:
        """Get template file path"""
        template_name = self.config["template"]
        
        # Try multiple locations
        possible_paths = [
            Path.cwd() / "templates" / f"{template_name}.md",
            self.vault_path / "templates" / f"{template_name}.md",
            self.vault_path / ".templates" / f"{template_name}.md",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        return None
    
    def create_note(
        self, 
        transcription: str,
        metadata: Optional[NoteMetadata] = None,
        audio_filename: Optional[str] = None
    ) -> Path:
        """
        Create Obsidian note from transcription
        
        Args:
            transcription: Transcribed text
            metadata: Note metadata (auto-generated if None)
            audio_filename: Original audio filename
            
        Returns:
            Path to created note
        """
        # Generate metadata if not provided
        if metadata is None:
            metadata = self._generate_metadata(transcription, audio_filename)
        
        # Generate note content
        content = self._generate_note_content(transcription, metadata, audio_filename)
        
        # Generate filename
        filename = self._generate_filename(metadata)
        note_path = self.inbox_path / filename
        
        # Ensure unique filename
        counter = 1
        while note_path.exists():
            stem = note_path.stem
            note_path = self.inbox_path / f"{stem}-{counter}.md"
            counter += 1
        
        # Write note
        note_path.write_text(content, encoding="utf-8")
        
        console.print(f"[green]✓ Created note: {note_path.name}[/green]")
        return note_path
    
    def _generate_metadata(
        self, 
        transcription: str, 
        audio_filename: Optional[str]
    ) -> NoteMetadata:
        """Auto-generate metadata from transcription"""
        now = datetime.now()
        
        # Auto-detect category (simple keyword matching)
        category = self._detect_category(transcription)
        
        # Extract title from first line or generate from content
        title = self._extract_title(transcription)
        
        # Generate tags
        tags = ["voice-note", category.lower()]
        
        return NoteMetadata(
            title=title,
            category=category,
            date=now.strftime(self.config["date_format"]),
            time=now.strftime(self.config["time_format"]),
            tags=tags
        )
    
    def _detect_category(self, text: str) -> str:
        """Auto-detect note category from content"""
        text_lower = text.lower()
        
        # Keyword matching (simple heuristic)
        if any(word in text_lower for word in ["meeting", "agenda", "action items"]):
            return "Meeting"
        elif any(word in text_lower for word in ["idea", "brainstorm", "what if"]):
            return "Brainstorm"
        elif any(word in text_lower for word in ["product", "feature", "user story"]):
            return "Product Ideas"
        elif any(word in text_lower for word in ["i feel", "i think", "reflection"]):
            return "Self-Awareness"
        elif any(word in text_lower for word in ["learn", "understand", "explain"]):
            return "Learning"
        else:
            return "Quick Note"
    
    def _extract_title(self, text: str, max_length: int = 50) -> str:
        """Extract or generate title from transcription"""
        # Try to use first sentence
        sentences = re.split(r'[.!?]\s+', text.strip())
        if sentences:
            title = sentences[0].strip()
            if len(title) > max_length:
                title = title[:max_length] + "..."
            return title
        
        # Fallback to first N characters
        return text[:max_length].strip() + "..."
    
    def _generate_filename(self, metadata: NoteMetadata) -> str:
        """Generate filename from metadata"""
        # Format: YYYY-MM-DD [Category] - Title.md
        safe_title = re.sub(r'[^\w\s-]', '', metadata.title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        
        filename = f"{metadata.date} [{metadata.category}] - {safe_title}.md"
        return filename
    
    def _generate_note_content(
        self,
        transcription: str,
        metadata: NoteMetadata,
        audio_filename: Optional[str]
    ) -> str:
        """Generate formatted note content"""
        
        # Use template if available
        if self.template_path and self.template_path.exists():
            template = self.template_path.read_text(encoding="utf-8")
            return self._apply_template(template, transcription, metadata, audio_filename)
        
        # Default template
        content = f"""---
title: {metadata.title}
category: {metadata.category}
date: {metadata.date}
time: {metadata.time}
tags: {', '.join(metadata.tags)}
source: voice-recording
"""
        
        if audio_filename:
            content += f"audio_file: {audio_filename}\n"
        
        if metadata.duration:
            content += f"duration: {metadata.duration}\n"
        
        content += f"""---

# {metadata.title}

**Category:** {metadata.category}  
**Date:** {metadata.date} {metadata.time}

## Transcription

{transcription}

## Notes

<!-- Add your notes and reflections here -->

## Related

<!-- Link to related notes -->

---
*Generated by Voice Capsule*
"""
        
        return content
    
    def _apply_template(
        self,
        template: str,
        transcription: str,
        metadata: NoteMetadata,
        audio_filename: Optional[str]
    ) -> str:
        """Apply template with variable substitution"""
        replacements = {
            "{{title}}": metadata.title,
            "{{category}}": metadata.category,
            "{{date}}": metadata.date,
            "{{time}}": metadata.time,
            "{{tags}}": ", ".join(metadata.tags),
            "{{transcription}}": transcription,
            "{{audio_file}}": audio_filename or "N/A",
            "{{duration}}": metadata.duration or "N/A",
        }
        
        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Personal Voice Capsule - Obsidian Integration"
    )
    parser.add_argument(
        "text_file",
        help="Path to transcription text file"
    )
    parser.add_argument(
        "--category",
        choices=list(ObsidianSync.CATEGORIES.keys()),
        help="Note category"
    )
    parser.add_argument(
        "--title",
        help="Custom note title"
    )
    parser.add_argument(
        "--config",
        help="Path to .env configuration file"
    )
    
    args = parser.parse_args()
    
    # Load transcription
    text_path = Path(args.text_file)
    if not text_path.exists():
        console.print(f"[red]Error: File not found: {text_path}[/red]")
        return
    
    transcription = text_path.read_text(encoding="utf-8")
    
    # Initialize sync
    sync = ObsidianSync(config_path=args.config)
    
    # Create metadata if custom values provided
    metadata = None
    if args.category or args.title:
        now = datetime.now()
        metadata = NoteMetadata(
            title=args.title or sync._extract_title(transcription),
            category=ObsidianSync.CATEGORIES.get(args.category, "Quick Note"),
            date=now.strftime(sync.config["date_format"]),
            time=now.strftime(sync.config["time_format"]),
            tags=["voice-note"]
        )
    
    # Create note
    note_path = sync.create_note(
        transcription=transcription,
        metadata=metadata,
        audio_filename=text_path.stem
    )
    
    console.print(f"[cyan]Note created at: {note_path}[/cyan]")


if __name__ == "__main__":
    main()
