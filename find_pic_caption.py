#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import json
import base64
import io
import imagehash
from PIL import Image

class FindPicCaption:
    def __init__(self, url, top_tag_name, img_tag_1, cap_tag, img_tag_2=None, img_tag_3=None):
        self.url = url
        self.top_tag_name = top_tag_name
        self.img_tag_1 = img_tag_1
        self.img_tag_2 = img_tag_2
        self.img_tag_3 = img_tag_3
        self.cap_tag = cap_tag

    def get_articles(self):
        data_list = []

        try:
            response = requests.get(self.url)
            response.raise_for_status()
            html_content = response.content
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving URL: {e}", file=sys.stderr)
            return data_list

        soup = BeautifulSoup(html_content, "html.parser")

        # First find all articles with the top tag name 
        articles = soup.find_all(self.top_tag_name)
        
        # Now sequentially find the lower tags if they are required
        for article in articles:
            img_tag = article.find(self.img_tag_1)
            if img_tag and self.img_tag_2:
                img_tag = img_tag.find(self.img_tag_2)
            if img_tag and self.img_tag_3:
                img_tag = img_tag.find(self.img_tag_3)
        # Check both srcset and src attributes to account for lazy loading
            if img_tag and "srcset" in img_tag.attrs:
                image_url = img_tag["srcset"].split(" ")[0]
            elif img_tag and "src" in img_tag.attrs:
                image_url = img_tag["src"]
            else:
                continue  # Skip if image URL is not found

        # Now look for a caption tag in the article. We will scip this if we have not found a img in the first place 
            caption_tags = article.find_all(self.cap_tag)
            caption = None
            caption_url = None
            for tag in caption_tags:
                text = tag.get_text(strip=True)
                if text:
                    caption = text
                    if tag.has_attr("href"):
                        caption_url = urljoin(self.url, tag["href"])
                    break
        # If we can not find a caption nor a picture we will skip this article
            if not image_url or not caption:
                continue  # Skip if no image or caption found

            full_img_url = urljoin(self.url, image_url)

        # Skip this article if image download fails
            try:
                img_response = requests.get(full_img_url)
                img_response.raise_for_status()
                img_data = img_response.content
        # Compute hash and store it 
                img = Image.open(io.BytesIO(img_data))
                image_hash = imagehash.phash(img)
            except requests.exceptions.RequestException:
                continue  

            scrape_time = datetime.now()

        # Store the data if successful up to here and then start with the next article 
            data_list.append((full_img_url, caption_url, image_hash, caption, scrape_time))
        return data_list

def main():
    if len(sys.argv) < 5:
        print("Usage: python find_pic_caption.py <url> <top_tag_name> <img_tag_1> <cap_tag> [img_tag_2] [img_tag_3]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    top_tag_name = sys.argv[2]
    img_tag_1 = sys.argv[3]
    cap_tag = sys.argv[4]
    img_tag_2 = sys.argv[5] if len(sys.argv) >= 6 else None
    img_tag_3 = sys.argv[6] if len(sys.argv) >= 7 else None

    articles = FindPicCaption(url, top_tag_name, img_tag_1, cap_tag, img_tag_2, img_tag_3).get_articles()


    # Prepare the output list by converting non-serializable types to strings.
    output = []
    for article in articles:
        full_img_url, caption_url, img_hash, caption, scrape_time = article
        entry = {
            "full_img_url": full_img_url,
            "caption_url": caption_url,
            "caption": caption,
            "image_hash": img_hash.__str__(),
            "scrape_time": scrape_time.isoformat(),
        }
        output.append(entry)
    
    # Save extracted data to a JSON file
    scraped_data_file = "scraped_data.json"
    store = json.dumps(output, indent=2)
    with open(scraped_data_file, "w") as f:
        f.write(store)


if __name__ == "__main__":
    main()
