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

## CSV schedule exchange

The desktop app can export a selected profile's schedule to CSV and import CSV into a selected profile. Columns are `time,supplement,form,quantity,unit`. Times must use 30-minute increments. Import validates rows before writing and rolls back on database errors. Imports append doses and may create duplicates on repeat import. Export and database backup refuse to overwrite existing files. Restore is not yet available in the UI; preserve the original database before any manual recovery.

## Restore safeguards

Use **Restore Backup...** in the desktop application. Select an existing Supplement Barista SQLite backup, confirm replacement, and choose a **new** recovery-backup filename. The application checks SQLite integrity and schema version before modifying the current database, saves the current database to the recovery file, then restores the selected backup. Existing recovery files cannot be overwritten. Restoring replaces all profiles, supplements, and scheduled doses. Keep recovery backups in a separate safe location.
