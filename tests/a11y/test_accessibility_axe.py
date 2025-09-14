import json
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
