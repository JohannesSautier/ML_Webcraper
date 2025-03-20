#!/usr/bin/env python3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

class FindSubPage:
    def __init__(self, keyword, html):
        self.keyword = keyword
        self.html = html

    def get_url(self):
        soup = BeautifulSoup(self.html, "html.parser")
        links = soup.find_all('a')
        
        for link in links:
            # Look for the keyword in the text of the link
            if self.keyword in link.get_text(strip=True):
                sub_link = link.get('href')
                if not sub_link:
                    continue
                base_tag = soup.find("base")
                base_url = base_tag.get("href") if base_tag else ""
                full_link = urljoin(base_url, sub_link)  # Join base URL and relative link
                return full_link
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python find_subpage.py <keyword>", file=sys.stderr)
        sys.exit(1)
    
    keyword = sys.argv[1]
    html = sys.stdin.buffer.read()
    url = FindSubPage(keyword, html).get_url()
    if url:
        print(url)
    else:
        print("No subpage URL found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
