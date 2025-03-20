#!/usr/bin/env python3

from pymongo import MongoClient
from datetime import datetime
import gridfs
import json
import base64
import sys
import requests

class StoreInMongo:
    def __init__(self, db_name, db_address):
        # Connect to the local MongoDB server
        self.client = MongoClient(db_address)
        self.db = self.client[db_name]
        self.fs = gridfs.GridFS(self.db, collection='images')
        self.captions_collection = self.db['captions']

    def insert_data(self, data_list):
        for item in data_list:
            image_url = item.get("full_img_url")
            caption_url = item.get("caption_url")
            caption = item.get("caption")
            scrape_time = item.get("scrape_time")
            image_hash = item.get("image_hash")
            
            # Load image from the image URL
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = response.content
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving image: {e}", file=sys.stderr)
                continue

            # Store image in GridFS
            file_id = self.fs.put(image_data, filename=image_url)

            # Store caption details in MongoDB
            caption_doc = {
                'caption': caption,
                'image_id': file_id,
                'created_at': datetime.now(),
                'caption_url': caption_url,
                'scrape_time': scrape_time,
                'image_hash': image_hash
            }
            self.captions_collection.insert_one(caption_doc)

    def close_connection(self):
        self.client.close()

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 store_in_mongo.py <checked_data.json>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    db_name = sys.argv[2]
    db_adress = sys.argv[3]

    try:
        with open(input_file, 'r') as f:
            data_list = json.load(f)
    except Exception as e:
        print(f"Error loading data file: {e}", file=sys.stderr)
        sys.exit(1)

    # Store in MongoDB
    mongo_store = StoreInMongo(db_name,db_adress)
    mongo_store.insert_data(data_list)
    mongo_store.close_connection()


if __name__ == "__main__":
    main()
