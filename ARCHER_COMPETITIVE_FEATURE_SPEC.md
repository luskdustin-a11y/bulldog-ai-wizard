# ARCHER competitive feature integration specification

This is a design and implementation backlog, not a claim of installed third-party integrations.
Do not copy proprietary code, branding, data, or bypass provider access controls.

## Universal UX
- One unified owner-only dashboard on Windows, Android and eventually watch.
- Fast launch, searchable department switcher, visible offline/online state.
- Local-first storage, opt-in network features, explicit consent for device actions.
- Clear errors, retry/backoff only for verified transient failures, health monitoring.
- Measure cold start, navigation latency, crash rate, battery, memory and offline usability.

## ARCHER brain (ChatGPT, Gemini, Claude, Ollama, LM Studio benchmarks)
- Model adapter interface with explicit selection of local vs approved cloud provider.
- Streaming chat, citations when sourced, tool permissions, conversation memory controls.
- Ollama/LM Studio candidate local backends: verify API compatibility before connecting.
- Never claim an LLM is present when only deterministic routing exists.

## Shop AI and VAL (BlueDriver, FORScan, Autel benchmarks)
- Read-only OBD live data and DTCs first; verified adapter support and make/model coverage.
- Guided troubleshooting with evidence, repair history, parts compatibility verification.
- No ECU writes or vehicle control without explicit authorization and safety interlocks.

## Hunting (Tactacam REVEAL, SPYPOINT, WiseEye, Moultrie benchmarks)
- Authorized import from supported exports or official APIs only.
- Deduplicate images, camera/date metadata, individual deer tracking, maps, notifications.
- Do not claim automatic account sync until provider permission/API confirmed.

## Business and hotshot (Jobber, Housecall Pro, DAT, Truckstop benchmarks)
- Jobs, clients, quotes, invoices, dispatch, expenses and reminders.
- Broker/load information only via licensed or explicitly permitted integrations.

## Finances and stocks (Xero, QuickBooks benchmarks)
- Local categorization, reconciliations, dashboards and audit trails.
- Read-only account connections initially; no trading or payments without approval.
- Encrypted storage and access controls are prerequisites for sensitive financial data.

## Release gates
1. Verify baseline tests and stress tests in CI.
2. Real LLM conversation integration with privacy controls and model-failure fallback.
3. Secure authentication, encrypted storage, backup and restore verification.
4. Windows build and real device smoke test; Android signed debug APK and phone test.
5. Authorized integrations one by one with test fixtures and observable failure states.
6. Compare task success, speed, usability and reliability against named benchmark products.

No external account connections, subscriptions, spending or deployment authorized by this file.
