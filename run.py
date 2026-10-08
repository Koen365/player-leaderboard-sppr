"""Start de API in een eigen virtuele omgeving, ook vanuit een andere map."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

PROJECT_DIR = Path(__file__).resolve().parent


def ensure_dependencies(script_path=None):
    env_dir = PROJECT_DIR / ".venv"
    executable = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not executable.exists():
        print("Virtuele Python-omgeving aanmaken...", flush=True)
        venv.create(env_dir, with_pip=True)
    if Path(sys.prefix).resolve() != env_dir.resolve():
        script = Path(script_path or __file__).resolve()
        result = subprocess.run([str(executable), str(script), *sys.argv[1:]])
        raise SystemExit(result.returncode)
    try:
        import fastapi  # noqa: F401
        import sqlalchemy  # noqa: F401
        import uvicorn  # noqa: F401
        import pwdlib  # noqa: F401
        import argon2  # noqa: F401
        import python_multipart  # noqa: F401
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(PROJECT_DIR / "requirements.txt"),
        ])


def start_server():
    import uvicorn

    parser = argparse.ArgumentParser(description="Start Player Leaderboard API")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Herstart na codewijzigingen")
    args = parser.parse_args()
    print(f"API: http://127.0.0.1:{args.port}")
    print(f"Swagger: http://127.0.0.1:{args.port}/docs", flush=True)
    uvicorn.run("api:app", host="127.0.0.1", port=args.port, reload=args.reload,
                app_dir=str(PROJECT_DIR), reload_dirs=[str(PROJECT_DIR)] if args.reload else None)


if __name__ == "__main__":
    ensure_dependencies()
    start_server()
