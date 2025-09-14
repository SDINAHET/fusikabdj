import re
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
