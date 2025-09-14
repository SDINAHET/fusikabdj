import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_homepage_visual_snapshot(live_server, page: Page):
    base = live_server["base_url"]
    page.goto(base, wait_until="networkidle")
    expect(page).to_have_screenshot("homepage.png", full_page=True)
