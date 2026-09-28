#!/usr/bin/env python3
"""Answer questions from a folder of markdown notes."""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from transcribe import VoiceCapsuleTranscriber, console

SKIP_DIRS = {".obsidian", ".git", ".venv", "node_modules"}
CHUNK_CHARS = 1200
CONTEXT_CHARS = 12000


def load_questions(path: Path) -> List[str]:
    if not path.exists():
        console.print(f"[red]Question file not found: {path}[/red]")
        sys.exit(1)
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        questions.append(text)
    if not questions:
        console.print(f"[red]{path} has no questions. Put one question on each line.[/red]")
        sys.exit(1)
    return questions


def resolve_knowledge_dir(explicit: str) -> Path:
    if explicit:
        path = Path(explicit)
    else:
        configured = os.getenv("OBSIDIAN_VAULT_PATH", "")
        placeholder = configured in {"", "/path/to/your/obsidian/vault"}
        path = Path("knowledge") if placeholder or not Path(configured).is_dir() else Path(configured)
    if not path.is_dir():
        console.print(f"[red]Knowledge directory not found: {path}[/red]")
        console.print("Put Markdown notes in the knowledge folder, or pass --knowledge with your notes directory.")
        sys.exit(1)
    return path


def note_files(root: Path) -> List[Path]:
    files = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def tokens(text: str) -> set:
    found = set()
    for piece in re.findall(r"[\u4e00-\u9fff]+|[A-Za-z0-9_]+", text.lower()):
        if re.match(r"[\u4e00-\u9fff]", piece):
            if len(piece) == 1:
                found.add(piece)
            found.update(piece[i : i + 2] for i in range(len(piece) - 1))
        else:
            found.add(piece)
    return found


def chunks_for(path: Path, root: Path) -> List[Dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    title = path.stem
    relative = path.relative_to(root).as_posix()
    blocks = [block.strip() for block in re.split(r"\n(?=#+\s)", text) if block.strip()]
    if not blocks:
        blocks = [text.strip()]
    pieces = []
    for block in blocks:
        while len(block) > CHUNK_CHARS:
            pieces.append(block[:CHUNK_CHARS])
            block = block[CHUNK_CHARS:]
        if block:
            pieces.append(block)
    return [{"source": relative, "title": title, "text": piece} for piece in pieces]


def select_chunks(question: str, library: List[Dict[str, str]]) -> List[Dict[str, str]]:
    wanted = tokens(question)
    ranked = []
    for chunk in library:
        overlap = len(wanted & tokens(chunk["title"] + "\n" + chunk["text"]))
        if overlap:
            ranked.append((overlap, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    chosen = []
    used = 0
    for _, chunk in ranked:
        size = len(chunk["text"])
        if chosen and used + size > CONTEXT_CHARS:
            break
        chosen.append(chunk)
        used += size
    if not chosen:
        for chunk in library:
            size = len(chunk["text"])
            if chosen and used + size > CONTEXT_CHARS:
                break
            chosen.append(chunk)
            used += size
    return chosen


def source_names(selected: List[Dict[str, str]]) -> List[str]:
    names = []
    for chunk in selected:
        name = chunk["source"]
        if name not in names:
            names.append(name)
    return names


def answer_question(model, question: str, selected: List[Dict[str, str]]) -> str:
    excerpts = "\n\n".join(
        f"[{chunk['source']}]\n{chunk['text']}" for chunk in selected
    )
    prompt = f"""Answer using only the notes below.
Write in the same language as the question. Do not repeat the question.
If the question has several parts, answer every part the notes support.
For a part the notes do not mention, say so in that same language. Do not invent the missing fact.
Do not add a sources section; the program lists the files.

Notes:
{excerpts}

Question: {question}
"""
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.2},
    )
    return (response.text or "").strip()


def render(pairs: List[Tuple[str, str]], knowledge: Path) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# Knowledge answers {stamp}", "", f"Knowledge: {knowledge}", ""]
    for index, (question, answer) in enumerate(pairs, start=1):
        lines.extend([f"## {index}. {question}", "", answer, ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer questions from Markdown notes")
    parser.add_argument("question", nargs="?", help="Ask one question directly")
    parser.add_argument(
        "--questions",
        default="configs/preset_questions.txt",
        help="Question list, one question per line. Ignored when a question is passed on the command line",
    )
    parser.add_argument("--knowledge", help="Notes directory. Defaults to knowledge, or a configured Obsidian vault")
    parser.add_argument("--output", help="Markdown file where answers are saved")
    parser.add_argument("--config", help="Path to a .env configuration file")
    args = parser.parse_args()

    transcriber = VoiceCapsuleTranscriber(config_path=args.config)
    knowledge = resolve_knowledge_dir(args.knowledge)
    files = note_files(knowledge)
    if not files:
        console.print(f"[red]No Markdown notes in {knowledge}.[/red]")
        sys.exit(1)

    library = []
    for path in files:
        library.extend(chunks_for(path, knowledge))
    questions = [args.question] if args.question else load_questions(Path(args.questions))
    console.print(
        f"Knowledge [bold]{knowledge}[/bold]: {len(files)} note(s), {len(questions)} question(s)"
    )

    if args.output:
        output_path = Path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = Path("dialogues") / f"answers-{stamp}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pairs: List[Tuple[str, str]] = []
    for index, question in enumerate(questions, start=1):
        console.print(f"\n[bold]Question {index}/{len(questions)}[/bold]")
        console.print(question)
        selected = select_chunks(question, library)
        sources = source_names(selected)
        try:
            answer = answer_question(transcriber.model, question, selected)
        except Exception as exc:
            console.print(f"[red]Answer failed: {type(exc).__name__}[/red]")
            answer = "(answer failed)"
        if not answer:
            answer = "(no answer)"
        source_lines = "\n".join(f"- {name}" for name in sources) if sources else "- (none)"
        answer = f"{answer}\n\nSources:\n{source_lines}"
        console.print("\n[bold]Answer[/bold]")
        console.print(answer)
        pairs.append((question, answer))
        output_path.write_text(render(pairs, knowledge), encoding="utf-8")

    console.print(f"\n[green]Saved to: {output_path}[/green]")


if __name__ == "__main__":
    main()
