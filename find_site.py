#!/usr/bin/env python3
import sys
import requests

class FindSite:
    def __init__(self, website_url):
        self.url = website_url

    def get_html(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raises an error for bad status codes
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}", file=sys.stderr)
            return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python find_site.py <URL>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    finder = FindSite(url)
    html = finder.get_html()
    
    if html is not None:
        sys.stdout.buffer.write(html)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
