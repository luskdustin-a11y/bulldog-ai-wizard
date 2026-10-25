# RG6 platform hardening review

The legacy report, relay, runtime checker, model adapter and wizard now share a restricted Python network adapter. It refuses redirects, proxy routing, unapproved URL schemes/hosts and insecure TLS contexts. The wizard launches only owner-confirmed allowlisted applications as argument lists, rejecting script wrappers and current-directory/relative targets.

Further fixes reject malformed or oversized model data, invalid packet timestamps, invalid signatures and invalid Unicode payloads. Accepted messages are copied, capacity is bounded and exact retries remain idempotent. These changes preserve the inherited owner-authority rejection fix; they do not grant permissions or claim full integration with the separate Node shared core.

Local Linux evidence: 201 RG6 tests and six coding tests passed. The final focused suite passed 1,000 rounds (29,000 test executions, zero skips), with 6,000 concurrent delivery attempts, 2,000 changed-content rejections, 10,000 hostile URL rejections and 10,000 command-injection rejections. Repeated-run thread and descriptor counts remained stable after runtime initialization. Bandit 1.9.4 found zero medium/high findings and zero scan errors over the source excluding tests/history.

The local source baseline is commit `6e2afca20659db579f75bce4a36d48057dc4f0c9`. Original versions remain in Git history and separate local archives. No installer was deployed or installed. Dustin Lusk explicitly approved uploading this repair for Windows verification; main and installed software are unchanged.

The new workflow runs the full regressions, 1,000-round stress harness and blocking source scan on Windows and Linux. A passing workflow will verify software behavior on disposable CI machines. It will not verify a compiled installer, Dustin's laptop, real model inference, microphone/voice, live remote relay deployment or the historical secrets-scan findings.
