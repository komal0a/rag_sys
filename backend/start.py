import os
import subprocess
import sys


def main():
    print("Running database migrations...", flush=True)

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
    )

    if result.returncode != 0:
        print("Database migration failed.", flush=True)
        sys.exit(result.returncode)

    print("Starting FastAPI...", flush=True)

    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            os.environ.get("PORT", "8000"),
        ],
    )


if __name__ == "__main__":
    main()