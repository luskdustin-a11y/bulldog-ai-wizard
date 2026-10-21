# Bulldawg AI Wizard v1.4.0 (source)

Windows Python/Tkinter wizard. Requires Python 3 and, for catalog search and Windows package installs, Microsoft App Installer / winget already installed.

Run: `python bulldog_install_wizard.py`

New: Searches winget catalog; installs ONLY explicitly selected allowlisted package IDs after owner approval. Does not automatically choose arbitrary search results, does not install FORScan (opens official page), and does not install the full Bulldawg AI system.

Security: catalog packages may use third-party installers; winget source and exact IDs reduce ambiguity but do not independently prove publisher identity or cryptographic integrity. Review package/publisher details before approval. No admin bypass. Internet required for downloads. Some packages can prompt for elevation. Check logs at ~/.bulldog_ai/wizard.log.

Validation: Python syntax and ZIP structure tested in Linux; Windows runtime, winget behavior, and executable build NOT tested.
