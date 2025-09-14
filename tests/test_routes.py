import re
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
    assert "X-Content-Type-Options" in resp.headers
    assert resp.headers.get("X-Content-Type-Options", "").lower() == "nosniff"
