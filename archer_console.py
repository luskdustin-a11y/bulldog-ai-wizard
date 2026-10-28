#!/usr/bin/env python3
"""ARCHER local interactive console; optional text-to-speech, no external network."""
import argparse
from archer_brain import respond, remember, recall
from archer_voice import speak
from archer_model import chat, ModelUnavailable
from archer_persona import build_system_prompt, ResponseContext

def main():
    parser = argparse.ArgumentParser(description="ARCHER local assistant")
    parser.add_argument("--speak", action="store_true", help="Speak replies using OS voice")
    parser.add_argument("--local-ai", action="store_true", help="Use an explicitly running local Ollama model")
    parser.add_argument("--model", default="llama3.2", help="Installed local Ollama model name")
    args = parser.parse_args()
    import bulldawg_core as core
    if core.vault_enabled():
        import getpass
        if not core.unlock_vault(getpass.getpass("Vault passphrase: ")):
            raise SystemExit("Wrong passphrase")
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
            elif args.local_ai:
                routed = respond(message)
                prompt = build_system_prompt(ResponseContext(safety_critical=(routed.mode == 'serious')))
                try:
                    answer = chat(message, prompt, model=args.model)
                except ModelUnavailable:
                    answer = routed.text + ' Local AI model is unavailable.'
            else:
                answer = respond(message).text
        except (ValueError, OSError, PermissionError, RuntimeError) as exc:
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
