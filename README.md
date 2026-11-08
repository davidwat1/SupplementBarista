# Supplement Barista v2

Desktop-first, web-ready supplement catalog and scheduling application.

## Foundation

- Python package with SQLite persistence
- User profiles, supplement catalog, and daily scheduling
- Automated tests and GitHub Actions CI

This is an early foundation, not a released medical application. Supplement information is not a substitute for clinical advice.

## Run the desktop app (Windows PowerShell)

```powershell
py -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -e ".[dev]"
.\\.venv\\Scripts\\python.exe -m supplement_barista.desktop
```

The database is stored under your home directory in `SupplementBarista/supplements.sqlite3`. The desktop UI supports profile, supplement, and schedule management, plus manual backup. The initial GUI has not yet undergone an interactive Windows acceptance test.
