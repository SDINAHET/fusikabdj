from bs4 import BeautifulSoup

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
