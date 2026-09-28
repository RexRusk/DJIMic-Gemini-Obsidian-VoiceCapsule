#!/usr/bin/env python3
"""Ask a fixed list of questions, record each answer, and transcribe it."""

import argparse
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from listen import RecordingError, load_local_env, record_audio, resolve_device, write_wav
from transcribe import VoiceCapsuleTranscriber, console


def load_questions(path: Path) -> List[str]:
    if not path.exists():
        console.print(f"[red]找不到问题文件: {path}[/red]")
        sys.exit(1)
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        questions.append(text)
    if not questions:
        console.print(f"[red]{path} 里没有问题。一行写一个问题。[/red]")
        sys.exit(1)
    return questions


def render_dialogue(pairs: List[Tuple[str, str]]) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# 预设对话 {stamp}", ""]
    for index, (question, answer) in enumerate(pairs, start=1):
        lines.extend([f"## {index}. {question}", "", answer, ""])
    return "\n".join(lines).rstrip() + "\n"


def record_answer(device: int, seconds: Optional[float], transcriber: VoiceCapsuleTranscriber) -> str:
    while True:
        try:
            audio, samplerate = record_audio(device, seconds)
        except RecordingError as exc:
            console.print(f"[red]{exc}[/red]")
            if input("按 Enter 重录这一题，输入 s 跳过：").strip().lower() == "s":
                return "（跳过）"
            continue

        handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_path = Path(handle.name)
        handle.close()
        write_wav(wav_path, audio, samplerate)
        try:
            text = transcriber.transcribe_audio(wav_path)
        finally:
            wav_path.unlink(missing_ok=True)

        if text:
            console.print("\n[bold]回答[/bold]")
            console.print(text)
            return text
        if input("转写失败。按 Enter 重录，输入 s 跳过：").strip().lower() == "s":
            return "（转写失败）"


def main() -> None:
    parser = argparse.ArgumentParser(description="按固定问题录音并转成文字")
    parser.add_argument(
        "--questions",
        default="configs/preset_questions.txt",
        help="问题列表，一行一个问题",
    )
    parser.add_argument("--output", help="保存问答 Markdown 的路径")
    parser.add_argument("--device", help="麦克风编号，或名称中的一段文字，例如 DJI")
    parser.add_argument("--seconds", type=float, help="每题固定录音秒数。省略时按 Enter 停止")
    parser.add_argument("--config", help="指定 .env 配置文件")
    args = parser.parse_args()

    if args.seconds is not None and args.seconds <= 0:
        console.print("[red]--seconds 必须大于 0。[/red]")
        sys.exit(2)

    load_local_env(args.config)
    questions = load_questions(Path(args.questions))
    device = resolve_device(args.device or os.getenv("MIC_INPUT_DEVICE"))
    transcriber = VoiceCapsuleTranscriber(config_path=args.config)

    if args.output:
        output_path = Path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = Path("dialogues") / f"dialogue-{stamp}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pairs: List[Tuple[str, str]] = []
    console.print(f"共 {len(questions)} 个问题。结果会写到 [bold]{output_path}[/bold]")
    try:
        for index, question in enumerate(questions, start=1):
            console.print(f"\n[bold]问题 {index}/{len(questions)}[/bold]")
            console.print(question)
            answer = record_answer(device, args.seconds, transcriber)
            pairs.append((question, answer))
            output_path.write_text(render_dialogue(pairs), encoding="utf-8")
    except KeyboardInterrupt:
        console.print("\n[yellow]已停止。[/yellow]")

    if not pairs:
        console.print("[yellow]没有完成任何一题。[/yellow]")
        return
    console.print(f"\n[green]已保存到: {output_path}[/green]")


if __name__ == "__main__":
    main()
