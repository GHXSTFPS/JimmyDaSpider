import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import json

def parse_args():
    parser = argparse.ArgumentParser(description="JimmyDaSpider - a custom web crawler")
    parser.add_argument("-u", "--url", required=True, help="Starting URL to crawl")
    parser.add_argument("-d", "--depth", type=int, default=10, help="Maximum crawl depth")
    parser.add_argument("-p", "--pages", type=int, default=10, help="Maximum number of pages to crawl")
    return parser.parse_args()

def crawl_site(start_url, max_depth=10, max_pages=10):
    pages_crawled = 0
    visited = set()
    queue = [{"url": start_url, "depth": 0, "parent": None}]
    sitemap = {}
    header = {"User-Agent": "JimmyDaSpider/1.0"}

    while queue:
        job = queue.pop(0)
        current_url = job["url"]
        depth = job["depth"]

        if current_url in visited:
            continue

        try:
            response = requests.get(current_url, headers=header)
            if response.status_code == requests.codes.ok:
                # Progress bar
                percent = int((pages_crawled / max_pages) * 100)
                bar_length = 30
                filled_length = int(bar_length * pages_crawled // max_pages)
                bar = "█" * filled_length + '-' * (bar_length - filled_length)
                short_url = current_url[:50] + "..." if len(current_url) > 50 else current_url
                print(f"\rCrawling: |{bar}| {percent}% ({pages_crawled}/{max_pages}) {short_url}", end="")
                sys.stdout.flush()

                pages_crawled += 1
                visited.add(current_url)

                # Fingerprint logging
                fingerprint = {
                    "url": current_url,
                    "status_code": response.status_code,
                    "server": response.headers.get("Server", ""),
                    "content_type": response.headers.get("Content-Type", "")
                }
                with open("fingerprint_log.json", "a") as f:
                    f.write(json.dumps(fingerprint) + "\n")

                # Sitemap
                if current_url not in sitemap:
                    sitemap[current_url] = []

                # Stop if max pages reached
                if pages_crawled >= max_pages:
                    print("\nPage limit reached, halting...")
                    break

                # Parse links
                soup = BeautifulSoup(response.content, "html.parser")
                links = soup.find_all("a")
                for link in links:
                    href = link.get("href")
                    if href:
                        absolute_url = urljoin(current_url, href)
                        if absolute_url not in visited and depth < max_depth:
                            queue.append({"url": absolute_url, "depth": depth + 1, "parent": current_url})
                            sitemap[current_url].append(absolute_url)

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] Failed to fetch {current_url}: {e}")

    # Save sitemap
    with open("sitemap.json", "w") as f:
        json.dump(sitemap, f, indent=2)
    print("\nCrawl complete. Sitemap saved to sitemap.json and fingerprints to fingerprint_log.json")

if __name__ == "__main__":
    args = parse_args()
    crawl_site(args.url, args.depth, args.pages)

