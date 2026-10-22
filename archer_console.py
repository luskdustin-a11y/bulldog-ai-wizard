#!/usr/bin/env python3
"""ARCHER local interactive console; optional text-to-speech, no external network."""
import argparse
from archer_brain import respond, remember, recall
from archer_voice import speak

def main():
    parser = argparse.ArgumentParser(description="ARCHER local assistant")
    parser.add_argument("--speak", action="store_true", help="Speak replies using OS voice")
    args = parser.parse_args()
    print("ARCHER local console. Commands: /save DEPARTMENT: note, /notes DEPARTMENT, /quit")
    while True:
        try:
            message = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.lower() in ("/quit", "/exit"):
            break
        try:
            if message.startswith("/save "):
                dept, note = message[6:].split(":", 1)
                remember(dept.strip(), note.strip())
                answer = "Note saved locally."
            elif message.startswith("/notes "):
                notes = recall(message[7:].strip())
                answer = "\n".join(x["text"] for x in notes[:20]) or "No notes."
            else:
                answer = respond(message).text
        except (ValueError, OSError) as exc:
            answer = f"Unable to complete: {exc}"
        print("ARCHER>", answer)
        if args.speak:
            try:
                if not speak(answer):
                    print("(No supported local voice available.)")
            except Exception as exc:
                print(f"(Voice output unavailable: {exc})")

if __name__ == "__main__":
    main()
