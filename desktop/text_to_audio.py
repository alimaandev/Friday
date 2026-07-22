#!/usr/bin/env python3
"""
Text-to-Audio Converter

Converts text from a string, a file, or command-line input into spoken audio.
Uses pyttsx3 (offline, no API keys required).

Installation:
    pip install pyttsx3

Usage examples:
    # Speak text directly
    python text_to_audio.py --text "Hello, world!"

    # Read text from a file and save to an audio file
    python text_to_audio.py --file input.txt --output output.mp3

    # Interactive mode (type text, Ctrl+D to finish)
    python text_to_audio.py --interactive
"""

import argparse
import sys


def get_engine():
    """Initialize and return the TTS engine."""
    import pyttsx3

    engine = pyttsx3.init()
    return engine


def speak_text(engine, text, output_path=None, rate=200, volume=1.0):
    """
    Convert text to audio.

    Args:
        engine: Initialized pyttsx3 engine.
        text (str): The text to convert.
        output_path (str, optional): If provided, save audio to this file
            (e.g. 'output.mp3'). Otherwise, play it aloud.
        rate (int): Speech rate in words per minute.
        volume (float): Volume from 0.0 to 1.0.
    """
    if not text or not text.strip():
        print("Warning: no text provided to convert.", file=sys.stderr)
        return

    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    if output_path:
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        print(f"Audio saved to: {output_path}")
    else:
        engine.say(text)
        engine.runAndWait()


def read_file_text(path):
    """Read text from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Convert text to audio.")
    parser.add_argument("--text", help="Text string to convert.")
    parser.add_argument("--file", help="Path to a text file to convert.")
    parser.add_argument("--output", help="Output audio file (e.g. output.mp3).")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Read text from stdin (interactive mode).",
    )
    parser.add_argument("--rate", type=int, default=200, help="Speech rate (default 200).")
    parser.add_argument(
        "--volume", type=float, default=1.0, help="Volume 0.0-1.0 (default 1.0)."
    )
    args = parser.parse_args()

    # Determine the source of text
    if args.file:
        text = read_file_text(args.file)
    elif args.text:
        text = args.text
    elif args.interactive:
        print("Enter text (Ctrl+D to finish):")
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    engine = get_engine()
    speak_text(engine, text, output_path=args.output, rate=args.rate, volume=args.volume)


if __name__ == "__main__":
    main()