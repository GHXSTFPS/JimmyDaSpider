import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

visited = set()
start_url = input("Give a starting URL to crawl: ")
queue = [start_url]
#soup

while queue:
    current_url = queue.pop()
    if current_url in visited:
        continue
    try:
        response = requests.get(current_url)
        if response.status_code == requests.codes.ok:
            print(f"Working: {current_url}. Next: {queue}")
            visited.add(current_url)
            #parsing
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")
            for link in links:
                href = link.get("href")
                if href:
                    absolute_url = urljoin(current_url, href)
                    if absolute_url not in visited:
                        queue.append(absolute_url)
    except:
        print("error")
