"""Sla het API-contract op, of controleer of het nog bij de code past."""

if __name__ == "__main__":
    from run import ensure_dependencies
    ensure_dependencies(__file__)

import argparse
import json

from api import app
from database import PROJECT_DIR


def main():
    parser = argparse.ArgumentParser(description="OpenAPI-contract exporteren")
    parser.add_argument("--check", action="store_true", help="Alleen controleren, niets overschrijven")
    args = parser.parse_args()
    target = PROJECT_DIR / "openapi.json"
    schema = app.openapi()
    if args.check:
        if not target.exists() or json.loads(target.read_text(encoding="utf-8")) != schema:
            parser.exit(1, "Het contract is verouderd. Voer python export_openapi.py uit.\n")
        print("Het OpenAPI-contract komt overeen met de code.")
    else:
        target.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Contract opgeslagen: {target}")


if __name__ == "__main__":
    main()
