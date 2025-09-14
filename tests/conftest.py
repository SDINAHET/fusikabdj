import os
import sys
import time
import subprocess
import signal
import contextlib
from pathlib import Path

import pytest

APP_IMPORTS = ("app:app", "run:app")

def _resolve_app():
    for dotted in APP_IMPORTS:
        module_name, attr = dotted.split(":")
        try:
            mod = __import__(module_name, fromlist=[attr])
            app = getattr(mod, attr)
            app.config.update(TESTING=True)
            return app
        except Exception:
            continue
    raise RuntimeError("Impossible d'importer Flask app depuis app.py ou run.py (attr 'app').")

@pytest.fixture(scope="session")
def app():
    return _resolve_app()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def live_server():
    env = os.environ.copy()
    env["FLASK_ENV"] = env.get("FLASK_ENV", "production")
    entry = "run.py" if Path("run.py").exists() else "app.py"
    proc = subprocess.Popen(
        [sys.executable, entry],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    import requests
    base = "http://127.0.0.1:5000"
    for _ in range(60):
        try:
            r = requests.get(base, timeout=1.5)
            if r.status_code < 500:
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        with contextlib.suppress(Exception):
            out = proc.stdout.read().decode("utf-8", errors="ignore")
            print("Server boot log:\n", out)
        proc.kill()
        raise RuntimeError("Le serveur Flask n'a pas démarré sur :5000")

    yield {"base_url": base, "proc": proc}

    with contextlib.suppress(Exception):
        proc.send_signal(signal.SIGINT)
        proc.terminate()
        proc.wait(timeout=5)
