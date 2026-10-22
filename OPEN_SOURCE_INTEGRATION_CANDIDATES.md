# Verified open-source integration candidates — 2026-10-22

These are **reference implementations/candidates**, not installed, merged, tested on owner hardware, or authorized to access personal data. Do not copy entire repositories without reviewing licenses, dependencies, native binaries, and security.

| Target | Project | Source | Integration gate |
|---|---|---|---|
| Android offline inference | ggml-org/llama.cpp | https://github.com/ggml-org/llama.cpp/tree/master/examples/llama.android | Pin revision; build NDK/Gradle, load GGUF, physical Android 16 test |
| Android private UI | jegly/OfflineLLM | https://github.com/jegly/OfflineLLM | Apache-2.0; adapt components, review signing, permission policy, verify model execution |
| Android alternative | its-hazratbilal/offline-ai-assistant | https://github.com/its-hazratbilal/offline-ai-assistant | MIT; independently verify Android build, voice and privacy |
| Speech-to-text | ggml-org/whisper.cpp | https://github.com/ggml-org/whisper.cpp/tree/master/examples/whisper.android | Confirm microphone consent, model download, latency and offline behavior |
| Text-to-speech | rhasspy/piper | https://github.com/rhasspy/piper | Original archived MIT repository; verify maintained fork and voice-model licenses |
| Windows voice architecture | YaPanBytes/LocalVox | https://github.com/YaPanBytes/LocalVox | Review dependencies, licenses, performance on CPU, don't assume NVIDIA GPU |
| Opt-in file transport | syncthing/syncthing | https://github.com/syncthing/syncthing | MPL-2.0; sync encrypted payloads only, pair explicitly, test conflicts and revocation |

## Integration sequence

1. Keep Windows CI green; fail builds on test regressions.
2. Add encrypted notes and verified recovery as **opt-in** modules; never silently migrate or delete existing plaintext database.
3. Replace ARCHER placeholder response with an installed local model only after verifying it on the owner's machine; do not use cloud fallback.
4. Establish reproducible Android project and CI APK build, starting from official llama.cpp Android example; do not import unsigned third-party APK binaries.
5. Add voice input/output with offline tests and microphone permission.
6. Implement end-to-end encrypted authenticated pairing before allowing sync; Syncthing alone does not resolve application conflicts, key revocation, or authorization.
7. Verify each department's real adapters with supported hardware and accounts, separately from simulations.
8. Track licenses, hashes, pinned revisions, unit/integration/real-device acceptance and only then mark complete.

No installation, copying of third-party code, network access from the app, or external data transfer has been performed by this document.
