"""Root entrypoint.

Supports both:
- `uv run streamlit run main.py`
- `python3 main.py --port 8502`
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _running_inside_streamlit() -> bool:
    argv0 = Path(sys.argv[0]).name.lower()
    return "streamlit" in argv0 or "STREAMLIT_SERVER_PORT" in os.environ


def _launch_streamlit(port: int) -> int:
    app_path = Path(__file__).parent / "frontend" / "main.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
    ]
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Unidade frontend")
    parser.add_argument("--port", type=int, default=8501, help="Streamlit server port")
    args = parser.parse_args()
    return _launch_streamlit(args.port)


if _running_inside_streamlit():
    # When executed by Streamlit, import and run the real app module.
    from frontend import main as _frontend_main  # noqa: F401


if __name__ == "__main__" and not _running_inside_streamlit():
    raise SystemExit(main())
