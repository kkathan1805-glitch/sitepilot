import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()
results = []

MAX_URLS = 100

def crawl(url, domain):

    if url in visited:
        return

    if len(visited) >= MAX_URLS:
        return

    visited.add(url)

    try:

        response = requests.get(url, timeout=5)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = (
            soup.title.text.strip()
            if soup.title
            else "Missing"
        )

        meta_desc = soup.find(
            "meta",
            attrs={"name":"description"}
        )

        description = (
            meta_desc["content"]
            if meta_desc and meta_desc.get("content")
            else "Missing"
        )

        h1 = soup.find("h1")

        h1_text = (
            h1.text.strip()
            if h1
            else "Missing"
        )

        canonical = soup.find(
            "link",
            rel="canonical"
        )

        canonical_url = (
            canonical.get("href")
            if canonical
            else "Missing"
        )

        results.append({
            "URL": url,
            "Status": response.status_code,
            "Title": title,
            "Meta Description": description,
            "H1": h1_text,
            "Canonical": canonical_url
        })

        print("Crawled:", url)

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = urljoin(
                url,
                link["href"]
            )

            parsed = urlparse(href)

            clean_url = (
                parsed.scheme +
                "://" +
                parsed.netloc +
                parsed.path
            )

            if parsed.netloc == domain:
                crawl(clean_url, domain)

    except:
        pass