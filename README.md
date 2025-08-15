BFB — BITS Form Builder

A desktop Gravity Forms-like builder for Windows using PySide6.

Goals
- Accessible, keyboard-first form builder
- Save forms locally as JSON
- Publish forms to WordPress (Gravity Forms) via REST API

Getting started (developer)
1. Create a Python 3.10+ virtualenv.

   pwsh
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Install dependencies:

   pwsh
   pip install -r requirements.txt

3. Run the app:

   pwsh
   python -m app.main

Structure
- app/: application source
- tests/: unit tests
- PRD.md: product requirements document

Next steps
- Implement UI skeleton and WP integration stubs
- Add unit tests and CI
