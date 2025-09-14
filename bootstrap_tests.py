# bootstrap_tests.py
import argparse
from pathlib import Path

FILES = {
    # ----------------------- pytest.ini -----------------------
    "pytest.ini": r'''[pytest]
addopts = -q
testpaths = tests
markers =
    e2e: end-to-end tests using Playwright and a live server
# Uncomment to auto-update visual snapshots locally:
# addopts = -q --update-snapshots
''',

    # ----------------------- tests/conftest.py -----------------------
    "tests/conftest.py": r'''import os
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
    """
    Launch real Flask server on 127.0.0.1:5000 for E2E/a11y.
    Detects run.py (preferred) or app.py.
    """
    import requests

    env = os.environ.copy()
    env["FLASK_ENV"] = env.get("FLASK_ENV", "production")
    entry = "run.py" if Path("run.py").exists() else "app.py"
    proc = subprocess.Popen(
        [sys.executable, entry],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

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
''',

    # ----------------------- tests/test_routes.py -----------------------
    "tests/test_routes.py": r'''import re
import pytest

@pytest.mark.parametrize("path", ["/", "/index", "/contact", "/galerie", "/partenaires"])
def test_routes_exist(client, path):
    resp = client.get(path)
    assert resp.status_code in (200, 301, 302), f"{path} should respond OK/redirect"

def test_homepage_has_title(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert re.search(r"<title>.*</title>", html, re.I), "Page should have a <title>"

def test_security_headers(client):
    resp = client.get("/")
    # requires you to set header in app (before_request/after_request)
    assert "X-Content-Type-Options" in resp.headers
    assert resp.headers.get("X-Content-Type-Options", "").lower() == "nosniff"
''',

    # ----------------------- tests/test_templates_semantics.py -----------------------
    "tests/test_templates_semantics.py": r'''from bs4 import BeautifulSoup

def test_img_have_alt(client):
    html = client.get("/").get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")
    missing = [img.get("src") for img in imgs if not img.has_attr("alt")]
    assert not missing, f"Images without alt: {missing}"

def test_headings_hierarchy(client):
    html = client.get("/").get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    headings = [int(h.name[1]) for h in soup.find_all(["h1","h2","h3","h4","h5","h6"])]
    assert headings.count(1) <= 1, "Multiple <h1> found"
    last = 1
    for level in headings:
        assert level <= last + 1, f"Heading jumps too much: ... -> h{level}"
        last = level
''',

    # ----------------------- tests/test_static_assets.py -----------------------
    "tests/test_static_assets.py": r'''from bs4 import BeautifulSoup
from pathlib import Path

def test_static_links_exist_on_disk(client):
    html = client.get("/").get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")

    css_links = [l.get("href") for l in soup.find_all("link", rel="stylesheet")]
    js_links = [s.get("src") for s in soup.find_all("script") if s.get("src")]

    missing = []
    for href in (css_links + js_links):
        if not href:
            continue
        if href.startswith(("http://","https://","//")):
            continue
        p = href[1:] if href.startswith("/") else href
        if not Path(p).exists():
            missing.append(href)

    assert not missing, f"Static files not found on disk: {missing}"
''',

    # ----------------------- tests/test_links_local.py -----------------------
    "tests/test_links_local.py": r'''import requests
from bs4 import BeautifulSoup

def is_internal(href):
    return href and not href.startswith(("http://","https://","mailto:","#","tel:"))

def test_internal_links_ok(live_server):
    base = live_server["base_url"]
    r = requests.get(base, timeout=5)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links = set(a.get("href") for a in soup.find_all("a"))
    internal = {l for l in links if is_internal(l)}

    broken = []
    for href in internal:
        url = base + href if href.startswith("/") else f"{base}/{href}"
        try:
            resp = requests.get(url, timeout=5, allow_redirects=True)
            if resp.status_code >= 400:
                broken.append((href, resp.status_code))
        except Exception as e:
            broken.append((href, repr(e)))
    assert not broken, f"Broken internal links: {broken}"
''',

    # ----------------------- tests/test_contact_form_backend.py -----------------------
    "tests/test_contact_form_backend.py": r'''"""
Backend tests for /contact form:
- GET renders form
- POST valid data = 200/302 + success cue
- Invalid email rejected
- CSRF token support if present
"""
import re
from bs4 import BeautifulSoup

def _extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")
    token = soup.find("input", {"name": re.compile("csrf", re.I)})
    return token.get("value") if token and token.has_attr("value") else None

def test_contact_get_renders(client):
    resp = client.get("/contact")
    assert resp.status_code in (200, 302)
    if resp.status_code in (301, 302) and "Location" in resp.headers:
        # follow redirect once
        resp = client.get(resp.headers["Location"])
    assert resp.status_code == 200

def test_contact_post_valid(client):
    # first GET to fetch csrf if any
    r = client.get("/contact")
    html = r.get_data(as_text=True)
    csrf = _extract_csrf(html)

    data = {
        "name": "Alice",
        "email": "alice@example.com",
        "message": "Bonjour, test automatisé.",
    }
    if csrf:
        # guess common field name
        data["csrf_token"] = csrf

    resp = client.post("/contact", data=data, follow_redirects=True)
    assert resp.status_code in (200, 201, 302)
    text = resp.get_data(as_text=True)
    # Adapt this keyword to your flash message or success zone:
    assert re.search(r"(merci|thank you|envoyé|message reçu)", text, re.I), \
        "No success confirmation found in contact response."

def test_contact_invalid_email_rejected(client):
    r = client.get("/contact")
    html = r.get_data(as_text=True)
    csrf = _extract_csrf(html)

    bad = {
        "name": "Bob",
        "email": "not-an-email",
        "message": "Test invalide",
    }
    if csrf:
        bad["csrf_token"] = csrf

    resp = client.post("/contact", data=bad, follow_redirects=True)
    text = resp.get_data(as_text=True)
    # Expect 200 with validation errors OR 400/422
    assert resp.status_code in (200, 400, 422)
    assert re.search(r"(email.*(invalide|invalid)|format)", text, re.I) or resp.status_code in (400, 422), \
        "Invalid email not rejected properly."
''',

    # ----------------------- tests/e2e/test_e2e_flow.py -----------------------
    "tests/e2e/test_e2e_flow.py": r'''import re
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_user_main_flow(live_server, page: Page):
    base = live_server["base_url"]
    page.goto(base, wait_until="domcontentloaded")

    expect(page).to_have_title(re.compile(r"(FUSIKAB|Fusikab|DJ)", re.I))

    for selector in ["a[href*='galerie']", "a[href*='partenaires']", "a[href*='contact']"]:
        link = page.locator(selector)
        if link.count():
            link.first.click()
            expect(page).to_have_url(re.compile(r"127\.0\.0\.1:5000"))
            page.go_back()

    nav = page.locator("nav")
    if nav.count():
        expect(nav.first).to_be_visible()
''',

    # ----------------------- tests/e2e/test_contact_form_e2e.py -----------------------
    "tests/e2e/test_contact_form_e2e.py": r'''import re
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_contact_form_flow(live_server, page: Page):
    base = live_server["base_url"]
    page.goto(f"{base}/contact", wait_until="domcontentloaded")

    # Robust selectors: try common name/id placeholders
    name_input = page.locator("input[name*='name' i], input#name, input[aria-label*='name' i]").first
    email_input = page.locator("input[type='email'], input[name*='mail' i], input#email").first
    msg_textarea = page.locator("textarea[name*='message' i], textarea#message, textarea").first
    submit_btn = page.get_by_role("button", name=re.compile(r"(envoyer|send|submit)", re.I))
    if submit_btn.count() == 0:
        submit_btn = page.locator("button[type='submit'], input[type='submit']").first

    # Fill
    if name_input().count(): name_input().fill("Alice")
    if email_input().count(): email_input().fill("alice@example.com")
    if msg_textarea().count(): msg_textarea().fill("Message via Playwright E2E.")

    # Submit
    if submit_btn.count():
        submit_btn.first.click()
    else:
        page.keyboard.press("Enter")

    # Expect success page/flash/anchor
    expect(page).to_have_url(re.compile(r"contact|merci|thank", re.I))
    expect(page.locator("body")).to_contain_text(re.compile(r"(merci|thank you|reçu)", re.I))
''',

    # ----------------------- tests/e2e/test_visual_regression.py -----------------------
    "tests/e2e/test_visual_regression.py": r'''import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_homepage_visual_snapshot(live_server, page: Page):
    base = live_server["base_url"]
    page.goto(base, wait_until="networkidle")
    expect(page).to_have_screenshot("homepage.png", full_page=True)
''',

    # ----------------------- tests/a11y/test_accessibility_axe.py -----------------------
    "tests/a11y/test_accessibility_axe.py": r'''import json
import pytest
from playwright.sync_api import Page

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"

@pytest.mark.e2e
def test_accessibility_homepage(live_server, page: Page):
    base = live_server["base_url"]
    page.goto(base, wait_until="domcontentloaded")
    page.add_script_tag(url=AXE_CDN)

    results = page.evaluate("""
        async () => {
            return await axe.run(document, {
              runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
              rules: {
                'color-contrast': { enabled: true },
                'image-alt': { enabled: true },
                'link-name': { enabled: true }
              }
            });
        }
    """)

    violations = [
        v for v in results["violations"]
        if v.get("impact") in {"serious", "critical"}
    ]
    assert not violations, "A11y violations:\n" + json.dumps(violations, indent=2)
''',
}

def main():
    ap = argparse.ArgumentParser(description="Create full test scaffolding (backend, frontend, e2e, a11y) + pytest.ini")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    created, skipped = [], []
    for rel, content in FILES.items():
        path = Path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            skipped.append(rel)
            continue
        path.write_text(content, encoding="utf-8")
        created.append(rel)

    print("Created:", *created, sep="\n  - " if created else "\n  ")
    if skipped:
        print("\nSkipped (use --force to overwrite):", *skipped, sep="\n  - ")

    print("""
Dependencies (once):
  pip install -U pytest beautifulsoup4 requests playwright pytest-playwright
  python -m playwright install --with-deps

Run:
  pytest         # unit + front checks
  pytest -m e2e  # E2E + a11y + visual
""")

if __name__ == "__main__":
    main()
