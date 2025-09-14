import re
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
