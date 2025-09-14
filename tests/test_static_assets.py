from bs4 import BeautifulSoup
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
