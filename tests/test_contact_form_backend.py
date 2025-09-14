"""
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
