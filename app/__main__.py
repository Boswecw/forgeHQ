"""`python -m app` -> the forgeHQ producer CLI (see app/cli.py)."""
from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
