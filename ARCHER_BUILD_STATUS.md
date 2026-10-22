# ARCHER: build status and run instructions

## What works in source
- Local SQLite note records in eight departments (unencrypted).
- Deterministic department routing and safety-mode labeling (not an LLM).
- Local Tkinter desktop dashboard (Windows GUI not yet smoke-tested).
- Local interactive command-line console.
- Optional text-to-speech using an OS voice, where supported.
- Password hash/verify utilities (NOT yet wired to application login).
- Automated tests for routing, notes, personality and password utilities.

## Try locally (after reviewing code)
Install Python 3.13; no third-party Python packages required for these modules.

```bash
python archer_dashboard.py
python archer_console.py
python archer_console.py --speak
python -m unittest discover -s tests -v
```

## NOT implemented
- Actual language model, retrieval memory or autonomous agent.
- Microphone input, actor voice cloning, real-time conversation.
- User login, database encryption, secure sync or backups.
- OBD diagnostic hardware, camera account connections, financial accounts.
- Android APK, phone/watch application, or production deployment.

## Next build gates
1. Add explicit model adapter with local/cloud privacy toggle and model tests.
2. Implement encryption and authenticated login before sensitive records.
3. Test dashboard and OS voice on Windows runner.
4. Create a separate Android project, build APK on Android runner and test on a real phone.
5. Add authorized integrations one by one, with read-only diagnostics first.

**Security:** Do not enter passwords, financial records or sensitive data into the prototype database. The GitHub Pages website is not an authenticated private dashboard.
