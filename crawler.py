import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

MAX_URLS = 500

def normalize_url(url):

    parsed = urlparse(url)

    return (
        parsed.scheme +
        "://" +
        parsed.netloc +
        parsed.path.rstrip("/")
    )

def run_crawler(start_url):

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    visited = set()

    queue = deque()

    results = []

    start_url = normalize_url(start_url)

    domain = urlparse(start_url).netloc

    queue.append(start_url)

    session = requests.Session()

    while queue and len(visited) < MAX_URLS:

        current_url = queue.popleft()

        current_url = normalize_url(current_url)

        if current_url in visited:
            continue

        visited.add(current_url)

        try:

            response = session.get(
                current_url,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )

            status = response.status_code

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            if "text/html" not in content_type:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # TITLE
            title = "Missing"

            if soup.title and soup.title.text:

                title = soup.title.text.strip()

            # META DESCRIPTION
            meta_description = "Missing"

            meta = soup.find(
                "meta",
                attrs={"name":"description"}
            )

            if meta and meta.get("content"):

                meta_description = (
                    meta.get("content").strip()
                )

            # H1
            h1 = "Missing"

            h1_tag = soup.find("h1")

            if h1_tag:

                h1 = h1_tag.get_text().strip()

            # CANONICAL
            canonical = "Missing"

            canonical_tag = soup.find(
                "link",
                rel="canonical"
            )

            if canonical_tag and canonical_tag.get("href"):

                canonical = canonical_tag.get("href")

            # WORD COUNT
            text = soup.get_text(
                separator=" ",
                strip=True
            )

            word_count = len(
                text.split()
            )

            # IMAGES
            images = soup.find_all("img")

            image_count = len(images)

            missing_alt = 0

            for img in images:

                alt = img.get("alt")

                if not alt or alt.strip() == "":

                    missing_alt += 1

            # LINKS
            internal_links = 0
            external_links = 0

            links = soup.find_all(
                "a",
                href=True
            )

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                if href.startswith("#"):
                    continue

                if href.startswith("mailto:"):
                    continue

                if href.startswith("tel:"):
                    continue

                full_url = urljoin(
                    current_url,
                    href
                )

                parsed = urlparse(full_url)

                clean_url = normalize_url(
                    full_url
                )

                if parsed.netloc == domain:

                    internal_links += 1

                    if clean_url not in visited:

                        queue.append(clean_url)

                else:

                    external_links += 1

            results.append({

                "URL": current_url,

                "Status": status,

                "Title": title,

                "Title Length": len(title),

                "Meta Description": meta_description,

                "Meta Length": len(meta_description),

                "H1": h1,

                "Canonical": canonical,

                "Word Count": word_count,

                "Images": image_count,

                "Missing Alt": missing_alt,

                "Internal Links": internal_links,

                "External Links": external_links
            })

        except Exception as e:

            print(
                "ERROR:",
                current_url,
                e
            )

    return results