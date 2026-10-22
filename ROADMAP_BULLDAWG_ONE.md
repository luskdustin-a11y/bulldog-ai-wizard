# Bulldawg One — Competitive Feature Integration Plan
Research date: 2026-10-22
Status: PLANNED; no integrations described below are implemented merely by this document.

## Product identity
App working name: Bulldawg One. Company/technology: Bulldawg AI. Renaming installers and repositories requires a coordinated migration.

## Phase 1 — Secure working foundation
- Owner-only authentication with locally stored, properly hashed credentials; no public registration.
- Encrypt sensitive records at rest; current prototype SQLite data is NOT encrypted.
- Desktop dashboard with modular departments and accessible touchscreen UI.
- System supervisor: health, error logs, backup/restore, migration tests, explicit action approvals.
- Local AI model adapter with clear offline/cloud mode indicators and no silent data uploads.
- Continuous tests and Windows builds. Android builds require a separate actual Android project.

## Phase 2 — Shop AI and VAL
- Vehicle profiles, service history, inventory and part provenance.
- Import verified OBD-II logs; read-only diagnostics first.
- OBDLink and FORScan integration only via documented compatible interfaces and with owner consent.
- No automatic ECU programming, code clearing, actuator tests or vehicle control.
- Guided diagnostic evidence, confidence levels, citations, and safe next checks.
- PWC support as a separately validated hardware/adapter matrix.

## Phase 3 — Hunting and property
- Photo imports, EXIF and camera metadata, deduplication and date/time normalization.
- Individual deer ID suggestions with confidence and manual corrections.
- Camera locations, movement timelines, environmental overlays, offline property maps.
- SPYPOINT, REVEAL and WiseEye automation only where permitted by supported integrations.
- Camera account credentials kept outside source code.

## Phase 4 — Business and finances
- Job/project records, invoices, inventory, property renovations, hotshot trip costs.
- Optional accounting and investment connectors only after permission and provider verification.
- Separate financial access permissions, audit log, exports and backups.

## Phase 5 — Phone app and voice
- Android client with authentication and privacy controls; build signed APK after real Android tests.
- Optional phone/laptop sync over an authenticated encrypted connection.
- Push-to-talk and later low-latency full-duplex voice; explicit microphone permissions.
- Clear offline/online behavior and no automatic public hosting.

## Competitor inspiration and boundaries
- ChatGPT / Gemini / Claude: voice, connectors, coding, multimodal tools.
- OBDLink / FORScan / BlueDriver: live parameters, DTCs, guided diagnostics.
- Tactacam REVEAL / onX Hunt / HuntStand: camera management, buck histories, maps.
- Housecall Pro: scheduling, invoicing, jobs, analytics.
These are design references, not licensed integrations or copied code.

## Verification gates
1. Unit tests and static analysis.
2. Windows build and GUI smoke test.
3. Real supported adapter/camera integration tests, read-only first.
4. Android build, device testing and signing.
5. Privacy and backup recovery test.
6. Owner approval before installing software, connecting accounts, spending, deployment, or external data transmission.

## Sources reviewed
- https://help.openai.com/en/articles/20001274-chatgpt-voice
- https://www.obdlink.com/obd-apps/obdlink-app/
- https://www.obdlink.com/compatible-apps/
- https://www.tactacam.com/reveal-app-plan
- https://support.onxmaps.com/hc/en-us/articles/19492619731597-Adding-and-Editing-Trail-Cameras
- https://www.huntstand.com/
- https://www.housecallpro.com/Features/
