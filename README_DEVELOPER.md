Developer notes

- Branch: create `feature/prd-complete` for initial skeleton.
- Run app locally:

  pwsh
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  python -m app.main

- Tests:
  pip install -r requirements.txt
  pytest -q

- Create a WordPress test site and generate Application Password for testing publish flow.
