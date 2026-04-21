
# Sanitization Notes for v0.1.1

This package was rebuilt to exclude private or unsafe content from the uploaded prototype archives.

Removed from the public package:

- SQLite database snapshots (`*.db`)
- local logs (`*.log`)
- historical reports and generated figures
- absolute Windows paths from prior run logs
- bundled `__pycache__`
- prior demo workspace artifacts
- Telegram secrets and chat identifiers

Kept in sanitized form:

- queue and worker architecture
- public-safe config pattern
- dataset schema skeleton
- Z-Orchestrator style manifest structure
- scaffolded project layout
