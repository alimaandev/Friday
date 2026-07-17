import sys
import shutil
import argparse
from core.registry import discover_plugins
from agent.core import Agent
from browser import close_browser


BANNER = r"""
  _____  _     _     _
 |  ___(_) __| |_   _| | ___
 | |_  | |/ _` | | | | |/ _ \
 |  _| | | (_| | |_| | |  __/
 |_|   |_|\__,_|\__, |_|\___|
                |___/
"""

LANG_LABELS = {"english": "English", "hinglish": "Hinglish"}


def get_terminal_width() -> int:
    return shutil.get_terminal_size((80, 20)).columns


def print_colored(text: str, color_code: str = "37"):
    print(f"\033[{color_code}m{text}\033[0m")


def main():
    parser = argparse.ArgumentParser(description="Friday — AI Assistant")
    parser.add_argument("--lang", choices=["english", "hinglish"], default="english",
                        help="Language (default: english)")
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")

    lang = args.lang
    label = LANG_LABELS.get(lang, "English")

    print_colored(BANNER, "36")
    print_colored("─" * get_terminal_width(), "90")
    print_colored(f"Friday — {label} AI Assistant (Ctrl+C to exit, /help for commands)", "33")
    print_colored("─" * get_terminal_width(), "90")
    print()

    discover_plugins()
    agent = Agent(language=lang)

    try:
        _repl_loop(agent)
    finally:
        close_browser()


def _repl_loop(agent: Agent):
    while True:
        try:
            user_input = input("\033[32m❯\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print_colored("Bye bye! 👋", "33")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.startswith("/"):
            handled = _handle_command(user_input, agent)
            if handled == "exit":
                break
            continue

        print()
        for event in agent.run(user_input):
            if event["type"] == "tokens":
                print(event["content"], end="", flush=True)
            elif event["type"] == "tool_result":
                for t in event.get("tools", []):
                    print_colored(f"  🛠 {t['name']}({t['args']})", "90")
                    print_colored(f"     Result: {t['result']}", "90")
            elif event["type"] == "done":
                pass
        print("\n")


def _voice_loop(agent: Agent):
    if not is_voice_available():
        print_colored("Voice not available — no microphone detected. Install pyaudio for voice support.", "31")
        return

    print_colored("Voice mode active. Speak now. Say 'exit' or press Ctrl+C to return to text mode.", "33")
    print_colored("Listening...", "33")

    while True:
        try:
            result = listen()
            if not result.get("success"):
                if "timeout" in result.get("error", ""):
                    print_colored("Listening... (no speech detected, keep talking or say 'exit')", "33")
                    continue
                print_colored(f"STT error: {result.get('error')}", "31")
                continue

            text = result["text"].strip().lower()
            print_colored(f"\nYou (voice): {result['text']}", "90")

            if text in ("exit", "exit voice", "band karo", "stop"):
                print_colored("Exiting voice mode.", "33")
                return

            print()
            full_response = ""
            for event in agent.run(result["text"]):
                if event["type"] == "tokens":
                    full_response += event["content"]
                    print(event["content"], end="", flush=True)
                elif event["type"] == "tool_result":
                    for t in event.get("tools", []):
                        print_colored(f"  🛠 {t['name']}({t['args']})", "90")
                        print_colored(f"     Result: {t['result']}", "90")

            if full_response.strip():
                speak(full_response)

            print_colored("\n\nListening...", "33")

        except KeyboardInterrupt:
            print()
            return
        except Exception as e:
            print_colored(f"Voice error: {e}", "31")
            return


def _handle_command(cmd: str, agent: Agent):
    cmd = cmd.lower().strip()

    if cmd in ("/exit", "/quit"):
        print_colored("Bye bye! 👋", "33")
        return "exit"

    elif cmd == "/clear":
        agent.clear()
        print_colored("Conversation cleared! ✅" if agent.language == "english" else "Baat-cheet clear ho gayi! ✅", "33")

    elif cmd == "/voice":
        _voice_loop(agent)

    elif cmd.startswith("/lang"):
        parts = cmd.split()
        if len(parts) == 1:
            current = LANG_LABELS.get(agent.language, agent.language)
            print_colored(f"Current language: {current}. Usage: /lang english or /lang hinglish", "33")
        else:
            target = parts[1]
            if target in ("english", "en"):
                agent.set_language("english")
                print_colored("Switched to English 🇬🇧", "33")
            elif target in ("hinglish", "hi", "hindi"):
                agent.set_language("hinglish")
                print_colored("Hinglish mein switch ho gaya 🇮🇳", "33")
            else:
                print_colored(f"Unknown language: {target}. Use: english or hinglish", "31")

    elif cmd in ("/help", "/?"):
        _print_help(agent.language)

    else:
        print_colored(f"Unknown: {cmd}. Type /help for commands.", "31")


def _print_help(lang: str):
    if lang == "english":
        print_colored("""
Commands:
  /help               Show this help
  /clear              Reset conversation
  /voice              Enter voice mode (speak, assistant responds)
  /lang <language>    Switch language: english or hinglish
  /exit               Quit

The assistant has tools for:
  - Shell commands, file operations, web fetching
  - Browser automation (navigate, click, type, screenshot)
  - Python code execution
  - Persistent memory (remember/recall)
  - File/content search
  - System information
""", "33")
    else:
        print_colored("""
Commands:
  /help               Yeh help message
  /clear              Baat-cheet reset karo
  /voice              Voice mode mein jao (bolo, assistant jawab dega)
  /lang <language>    Language badlo: english ya hinglish
  /exit               Band karo

Assistant ke paas tools hain:
  - Shell commands, file operations, web fetching
  - Browser automation (navigate, click, type, screenshot)
  - Python code execution
  - Persistent memory (remember/recall)
  - File/content search
  - System information
""", "33")


if __name__ == "__main__":
    main()
