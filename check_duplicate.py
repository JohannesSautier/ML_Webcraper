#!/usr/bin/env python3
import sys
import json
import imagehash
from pymongo import MongoClient
import gridfs
from PIL import Image
import io
import Levenshtein
import base64

class CheckDuplicate:
    def __init__(self, db_name, client_address):
        self.client = MongoClient(client_address)
        self.db = self.client[db_name]
        # Only look at the captions.
        self.captions_collection = self.db["captions"]

    def remove_duplicates(self, scraped_data):
        filtered_data = []
        seen_items= set()

        for item in scraped_data:
            current_hash = item["image_hash"]
            current_caption = item["caption"]
            # Skip if a similar hash has already been seen
            if any(self.are_similar(current_hash, current_caption, seen_hash, seen_caption) for seen_hash, seen_caption in seen_items):
                continue
            seen_items.add((current_hash,current_caption))
            # Check if the image is a duplicate to the db articles
            if not self.is_duplicate(item["image_hash"], item["caption"]):
                filtered_data.append(item)

        return filtered_data
    
    def are_similar(self, hash1, caption1, hash2, caption2, hash_threshold=5, caption_threshold=0.8):
        # Check image similarity
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        if (h1 - h2) <= hash_threshold:
            return True

        # Check caption similarity (
        similarity = Levenshtein.ratio(caption1.lower(), caption2.lower())
        if similarity >= caption_threshold:
            return True

        return False


    def is_duplicate(self, image_hash, caption, hash_threshold=5, caption_threshold=0.8):
        # Check against similarities to stored images (here we compare against stored image hashes in the captions_collection)
        if image_hash is None:
            return False
        test_hash_obj = imagehash.hex_to_hash(image_hash)
        for existing in self.captions_collection.find({}, {"image_hash": 1}):
            existing_hash = existing.get("image_hash")
            if existing_hash:
                # Convert the stored hash string back to an imagehash object.
                existing_hash_obj = imagehash.hex_to_hash(existing_hash)
                distance = test_hash_obj - existing_hash_obj
                if distance <= hash_threshold:
                    print(f"Duplicate found based on image hash. Distance: {distance}")
                    return True
        # Check against similarities to stored captions
        if caption:
            for existing in self.captions_collection.find({}, {"caption": 1}):
                if existing.get("caption"):
                    similarity = Levenshtein.ratio(caption.lower(), existing["caption"].lower())
                    if similarity >= caption_threshold:
                        print(f"Duplicate found based on caption similarity. Similarity: {similarity}")
                        return True
        return False

    def close_connection(self):
        self.client.close()

def main():
    
    if len(sys.argv) != 4:
        print("Usage: python3 check_duplicate.py <scraped_data.json>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as f:
            scraped_data = json.load(f)
    except Exception as e:
        print(f"Error reading input data: {e}", file=sys.stderr)
        sys.exit(1)
    

    # Load configuration to get the database name.
    db_name = sys.argv[2]
    client_address = sys.argv[3]


    # Check if the database and collection exist.
    client = MongoClient(client_address)
    if db_name not in client.list_database_names():
        print(f"Database '{db_name}' does not exist. Skipping duplicate check.", file=sys.stderr)
        filtered_data = scraped_data
    else:
        # Check for duplicates.
        duplicate_checker = CheckDuplicate(db_name, client_address)
        filtered_data = duplicate_checker.remove_duplicates(scraped_data)
        duplicate_checker.close_connection()


    # Save the filtered data to a new file.
    
    with open(input_file, 'w') as f:
        json.dump(filtered_data, f, indent=2, default=str)


if __name__ == '__main__':
    main()
