# Bulldawg AI: ordered acceptance plan (draft)

Status: NOT 100% operational. Current 32% is a subjective estimate, not a measured pass rate. Never advance based only on files existing.

## Gate 1: Inventory and baseline
1. Enumerate all source, Android, Windows, workflow, and test artifacts. Confirm actual implementation, not README claims.
2. Run Windows CI tests, isolated imports, acceptance suite, packaging smoke test, and full integration report. Preserve failed checks.
3. Assign each feature one owner, real acceptance test, and result: PASS / FAIL / BLOCKED / UNTESTED.

## Gate 2: Private working Windows core
4. Integrate installer with verified, signed/hashed bundle and owner approval; ensure rollback, no silent downloads, and no bypass of Windows security.
5. Connect local Ollama chat to brain/dashboard, with explicit offline model selection, timeouts, error handling, conversation history, and no cloud fallback. Test with real local model.
6. Replace plaintext notes database with SQLCipher or equivalent verified encryption. Migrate existing data only after encrypted backup and user approval; test wrong keys, power interruption, migration rollback, and no plaintext artifacts.
7. Add supervisor health checks, crash-safe restart, opt-in recovery, backup integrity, and immutable failure logs. No automatic destructive repairs.
8. Add offline speech recognition and voice output with permission controls and device-specific tests.
9. Integrate all eight departments with real data contracts, not placeholder routing. Mark unconnected third-party services as unavailable.

## Gate 3: Android and private synchronization
10. Produce real Android source, signed test APK, Android 16 compatibility tests, login, encrypted storage, and secure local-only configuration.
11. Implement opt-in paired-device sync with authenticated encryption, replay protection, conflict resolution, explicit folder/data scope, revocation, and offline retries. Do not expose local services publicly by default.
12. Test laptop/phone pairing, disconnection, restore, duplicate messages, conflicts, and lost-device revocation on actual devices.

## Gate 4: Hardware and department integrations
13. Verify shop diagnostics against actual approved OBD hardware, safe read-only defaults, supported vehicle protocols and licensing.
14. Verify trail camera integrations only where vendor APIs or approved import workflows exist; no fabricated auto-sync.
15. Verify business/property/hotshot integrations and least-privilege permissions; do not import private accounts without approval.

## Gate 5: Release acceptance
16. Run automated unit/integration/security/regression tests in Windows and Android CI; all required tests must pass without skip, forced success, or hardcoded false-positive results.
17. Validate privacy (no telemetry, public registration, or unauthorized outbound calls), backup/restore, cold-start, recovery, upgrade/rollback, and performance.
18. Test signed Windows installer and Android APK on the owner's actual devices with approval. CI and simulation alone are not proof.
19. Freeze dependencies, record licenses/SBOM, pin versions and hashes, publish reproducible builds and checksums.
20. Release only after every required acceptance gate passes; record unsupported optional features separately and never count them as working.

## Open-source building blocks to evaluate
- Ollama local API: https://github.com/ollama/ollama
- SQLCipher encrypted SQLite: https://github.com/sqlcipher/sqlcipher
- Syncthing peer-to-peer file sync concepts: https://github.com/syncthing/syncthing
Reuse APIs/libraries under their licenses; do not blindly paste code or treat external tools as verified integrations.

## Percentage reporting
Keep the 32% estimate unchanged until baseline is measured. For future updates, show estimated completion, remaining percentage, new passing acceptance tests, and outstanding blockers. 100% means the defined release scope works on actual Windows and Android devices, not every conceivable feature.
