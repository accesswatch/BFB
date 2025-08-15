This PR bootstraps the BFB (BITS Form Builder) project.

Changes:
- Adds `PRD.md` with finalized product requirements
- Adds minimal PySide6 app skeleton (`app/`), models (`app/models/form_model.py`), and a WPClient stub
- Adds basic unit test(s) and README files

Acceptance criteria:
- App can be launched with `python -m app.main`
- Tests (`pytest`) pass
- PRD reflects the expected MVP and integration plan

Next steps:
- Implement Add Field dialog and Field Editor
- Wire Save/Load and Publish calls
- Add CI workflow and accessibility smoke tests
