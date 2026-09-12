"""
Eén-commando starter voor de Player Leaderboard API.

Gebruik:
    python run.py

Dit script:
1. Installeert fastapi en uvicorn als die nog niet aanwezig zijn.
2. Start daarna de API-server op http://127.0.0.1:8000
   (Swagger UI op http://127.0.0.1:8000/docs)
"""

import subprocess
import sys


def ensure_dependencies():
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError:
        print("Benodigde packages ontbreken, bezig met installeren...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )


def start_server():
    import uvicorn

    print("\nServer start op http://127.0.0.1:8000")
    print("Swagger UI (testomgeving): http://127.0.0.1:8000/docs\n")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    ensure_dependencies()
    start_server()
