# Delegated Technical Approval (prototype)

Primary ownership: Coding/Software Development. Integrations: Security, AI Management, Communications, Memory.

Owner first: no advisor contact until owner delegates a specific issue and scope. Natasha can approve within that scope; owner can revoke at any time. Never authorize changes to emergency stop, ownership, identity controls, or approval boundaries via delegated approval.

This module is an **in-memory policy prototype**, not production authorization. Actor strings must come from independently authenticated sessions, never email sender names or AI text. Persist tamper-evident audit events, use expiration and replay protection, require isolated builds/tests and rollback, and require owner-approved email dispatch before production. No automatic emailing, merging, deployment, or self-modification is enabled.

Test: `python -m unittest discover -s tests -p 'test_delegated_approval.py'` (ensure project root is on PYTHONPATH).
