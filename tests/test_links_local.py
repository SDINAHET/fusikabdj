import requests
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
