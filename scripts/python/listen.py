#!/usr/bin/env python3
"""
Record from the system microphone and transcribe with Gemini.

The DJI Mic Mini receiver, once paired and selected as a Windows input
device, is used like any other microphone. This script does not talk to
the mic over USB HID.
"""

import argparse
import os
import sys
import tempfile
import threading
import wave
from pathlib import Path
from typing import List, Optional

try:
    import numpy as np
    import sounddevice as sd
except ImportError as e:
    print("Error: Missing microphone packages.")
    print("Run: pip install sounddevice numpy")
    print(f"Details: {e}")
    sys.exit(1)

from dotenv import load_dotenv

from transcribe import VoiceCapsuleTranscriber, console


class RecordingError(RuntimeError):
    """Microphone capture failed. `code` is the process exit code."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


def load_local_env(config_path: Optional[str]) -> None:
    """Load the same .env locations used by transcribe.py."""
    if config_path:
        load_dotenv(config_path)
        return
    for path in (
        Path.cwd() / "configs" / ".env",
        Path.cwd() / ".env",
        Path.home() / ".personal-voice-capsule" / ".env",
    ):
        if path.exists():
            load_dotenv(path)
            return


def default_input_index() -> int:
    raw = sd.default.device[0]
    try:
        return int(raw)
    except (TypeError, ValueError):
        return -1


def list_input_devices() -> None:
    """Print every capture device PortAudio can see."""
    default_input = default_input_index()
    found = False
    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] <= 0:
            continue
        found = True
        marker = " (系统默认)" if index == default_input else ""
        rate = int(device["default_samplerate"])
        console.print(f"[{index}] {device['name']}{marker}  {rate} Hz")
    if not found:
        console.print("[red]没有找到麦克风输入设备。[/red]")


def resolve_device(requested: Optional[str]) -> int:
    """Pick an input device by index, name fragment, DJI match, or the system default."""
    devices = list(sd.query_devices())
    inputs = [
        (index, device)
        for index, device in enumerate(devices)
        if device["max_input_channels"] > 0
    ]
    if not inputs:
        console.print("[red]没有找到麦克风输入设备。[/red]")
        console.print("把 DJI Mic Mini 接收器用 Type-C 接上，RX 绿灯常亮后，在 Windows 声音设置里把它选为输入设备。")
        sys.exit(1)

    if requested:
        if requested.isdigit():
            index = int(requested)
            if index < 0 or index >= len(devices) or devices[index]["max_input_channels"] <= 0:
                console.print(f"[red]输入设备编号无效: {requested}[/red]")
                list_input_devices()
                sys.exit(1)
            return index
        needle = requested.lower()
        for index, device in inputs:
            if needle in device["name"].lower():
                return index
        console.print(f"[red]没有名称包含 \"{requested}\" 的麦克风。[/red]")
        list_input_devices()
        sys.exit(1)

    for index, device in inputs:
        name = device["name"].lower()
        if "dji" in name or "mic mini" in name:
            return index

    default_input = default_input_index()
    if default_input >= 0:
        return default_input
    return inputs[0][0]


def _open_stream(device: int, samplerate: int, channels: int, callback):
    return sd.InputStream(
        device=device,
        channels=channels,
        samplerate=samplerate,
        dtype="int16",
        callback=callback,
    )


def record_audio(device: int, seconds: Optional[float]) -> tuple:
    """Record mono int16 audio. Returns (samples, samplerate)."""
    info = sd.query_devices(device, "input")
    samplerate = int(info["default_samplerate"])
    channel_options = [1]
    max_channels = int(info["max_input_channels"])
    if max_channels > 1:
        channel_options.append(max_channels)

    chunks: List[np.ndarray] = []
    stop = threading.Event()
    limit = seconds if seconds is not None else 600.0

    def callback(indata, frames, time_info, status):
        if status:
            console.print(f"[yellow]{status}[/yellow]")
        chunks.append(indata.copy())
        recorded = sum(chunk.shape[0] for chunk in chunks) / samplerate
        if recorded >= limit:
            stop.set()

    stream = None
    last_error = None
    for channels in channel_options:
        candidate = None
        try:
            candidate = _open_stream(device, samplerate, channels, callback)
            candidate.start()
            stream = candidate
            break
        except sd.PortAudioError as exc:
            last_error = exc
            if candidate is not None:
                candidate.close()
            chunks.clear()
    if stream is None:
        raise RecordingError(f"无法打开麦克风: {last_error}")

    console.print(f"使用麦克风: [bold]{info['name']}[/bold]  {samplerate} Hz")
    try:
        if seconds is not None:
            console.print(f"正在录音 {seconds:g} 秒……")
            stop.wait(seconds)
        else:
            console.print("正在录音。说完后按 [bold]Enter[/bold] 停止（最长 10 分钟）。")
            threading.Thread(target=lambda: (input(), stop.set()), daemon=True).start()
            stop.wait()
    except KeyboardInterrupt:
        console.print("\n[yellow]录音已取消。[/yellow]")
        raise
    finally:
        stream.stop()
        stream.close()

    if not chunks:
        raise RecordingError("没有录到音频。")

    audio = np.concatenate(chunks, axis=0)
    if audio.ndim == 2:
        audio = audio.astype(np.float32).mean(axis=1)
        audio = np.clip(audio, -32768, 32767).astype(np.int16)
    else:
        audio = np.asarray(audio, dtype=np.int16).reshape(-1)

    duration = len(audio) / samplerate
    peak = int(np.max(np.abs(audio))) if len(audio) else 0
    console.print(f"录音结束，时长 {duration:.1f} 秒。")
    if peak < 200:
        raise RecordingError("录音几乎没有声音。确认 Mic Mini 的 RX 绿灯常亮，并且 Windows 当前输入设备就是这只麦克风。")
    return audio, samplerate


def write_wav(path: Path, audio: np.ndarray, samplerate: int) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(samplerate)
        handle.writeframes(audio.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="从麦克风录音并用 Gemini 转成文字")
    parser.add_argument("--list-devices", action="store_true", help="列出麦克风后退出")
    parser.add_argument("--device", help="设备编号，或名称中的一段文字，例如 DJI")
    parser.add_argument("--seconds", type=float, help="固定录音秒数。省略时按 Enter 停止")
    parser.add_argument("--output", help="把转写文字写入这个文件")
    parser.add_argument("--keep-wav", help="保留录音 wav 的路径")
    parser.add_argument("--config", help="指定 .env 配置文件")
    args = parser.parse_args()

    if args.list_devices:
        list_input_devices()
        return

    load_local_env(args.config)

    if args.seconds is not None and args.seconds <= 0:
        console.print("[red]--seconds 必须大于 0。[/red]")
        sys.exit(2)

    requested = args.device or os.getenv("MIC_INPUT_DEVICE")
    device = resolve_device(requested)
    try:
        audio, samplerate = record_audio(device, args.seconds)
    except RecordingError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(exc.code)

    if args.keep_wav:
        wav_path = Path(args.keep_wav)
        wav_path.parent.mkdir(parents=True, exist_ok=True)
        write_wav(wav_path, audio, samplerate)
        temporary = False
    else:
        handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_path = Path(handle.name)
        handle.close()
        write_wav(wav_path, audio, samplerate)
        temporary = True

    try:
        transcriber = VoiceCapsuleTranscriber(config_path=args.config)
        text = transcriber.transcribe_audio(wav_path)
    finally:
        if temporary:
            wav_path.unlink(missing_ok=True)

    if not text:
        sys.exit(1)

    console.print("\n[bold]转写结果[/bold]")
    console.print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(text, encoding="utf-8")
        console.print(f"[green]已保存到: {output_path}[/green]")


if __name__ == "__main__":
    main()
