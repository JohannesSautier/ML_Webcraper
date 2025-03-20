#!/usr/bin/env python3
import subprocess
import sys
import json
import logging

def main():
    # Configure logging
    logging.basicConfig(
        filename='scraper.log', 
        level=logging.DEBUG,      
        format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Load configuration from config.json
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            website_url = config.get('website_url')
            keyword = config.get('keyword')
            top_tag_name = config.get('top_tag_name')
            img_tag_1 = config.get('img_tag_1')
            cap_tag = config.get('cap_tag')
            database_name = config.get('database_name')
            client_address = config.get('client_adress')
            scraped_data_file = config.get('scraped_data_file')
            img_tag_2 = config.get('img_tag_2', None)
            img_tag_3 = config.get('img_tag_3', None)
            
    except Exception as e:
        logging.exception("Error loading configuration")
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    logging.info("Configuration loaded successfully.")

    # ############################################################################ #
    #                Module 1 : Extract html_content (find_site.py)                #
    # ############################################################################ #
    try:
        find_site_proc = subprocess.Popen(
            ['python3', 'find_site.py', website_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        html_content, err = find_site_proc.communicate()
        
        if find_site_proc.returncode != 0:
            error_message = err.decode().strip()
            logging.error(f"Error in find_site.py: {error_message}")
            print("Error in find_site.py:", err.decode(), file=sys.stderr)
            sys.exit(find_site_proc.returncode)

    except Exception as e:
        logging.exception("Error executing find_site.py")
        print("Error executing find_site.py:", str(e), file=sys.stderr)
        sys.exit(1)
    logging.info("HTML content retrieved successfully.")

    # ############################################################################ #
    #           Module 2 : Extract subpage subpage_url (find_subpage.py)           #
    # ############################################################################ #
    try:
        find_subpage_proc = subprocess.Popen(
            ['python3', 'find_subpage.py', keyword],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subpage_url, err2 = find_subpage_proc.communicate(input=html_content)
        
        if find_subpage_proc.returncode != 0:
            error_message = err2.decode().strip()
            logging.error(f"Error in find_subpage.py: {error_message}")
            print("Error in find_subpage.py:", err2.decode(), file=sys.stderr)
            sys.exit(find_subpage_proc.returncode)

    except Exception as e:
        print("Error executing find_subpage.py:", str(e), file=sys.stderr)
        logging.exception("Error executing find_subpage.py")
        sys.exit(1)
    
    subpage_url = subpage_url.decode().strip()
    logging.info(f"Subpage URL found: {subpage_url}")

    # ############################################################################ #
    #        Module 3: Extract image and caption data (find_pic_caption.py)        #
    # ############################################################################ #
    cmd = ['python3', 'find_pic_caption.py', subpage_url, top_tag_name, img_tag_1, cap_tag]
    # Optional image tags if webpage changes format
    if img_tag_2:
        cmd.append(img_tag_2)
    if img_tag_3:
        cmd.append(img_tag_3)

    try:
        find_pic_caption_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, err3 = find_pic_caption_proc.communicate()
        
        if find_pic_caption_proc.returncode != 0:
            error_message = err3.decode().strip()
            logging.error(f"Error in find_pic_caption.py: {error_message}")
            print("Error in find_pic_caption.py:", err3.decode(), file=sys.stderr)
            sys.exit(find_pic_caption_proc.returncode)

    except Exception as e:
        logging.exception("Error executing find_pic_caption.py")
        print("Error executing find_pic_caption.py:", str(e), file=sys.stderr)
        sys.exit(1)

    logging.info(f"Scraped data saved ")

     # ############################################################################ #
     #              Module 5: Check for duplicates (check_duplicate.py)             #
     # ############################################################################ #


    try:
        check_duplicate_proc = subprocess.Popen(
            ['python3', 'check_duplicate.py', scraped_data_file, database_name, client_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print ("Checking for duplicates...")
        out, err4 = check_duplicate_proc.communicate()
        
        if check_duplicate_proc.returncode != 0:
            error_message = err4.decode().strip()
            logging.error(f"Error in check_duplicate.py: {error_message}")
            print("Error in check_duplicate.py:", err4.decode(), file=sys.stderr)
            sys.exit(check_duplicate_proc.returncode)
        else:
            print(out.decode())

    except Exception as e:
        logging.exception("Error executing check_duplicate.py")
        print("Error executing check_duplicate.py:", str(e), file=sys.stderr)
        sys.exit(1)

    logging.info("Duplicates checked successfully.")

    # ############################################################################ #
    #              Module 4: Store data in MongoDB (store_in_mongo.py)             #
    # ############################################################################ #

    try:
        store_in_mongo_proc = subprocess.Popen(
            ['python3', 'store_in_mongo.py', scraped_data_file , database_name, client_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mongo_output, err5 = store_in_mongo_proc.communicate()
        
        if store_in_mongo_proc.returncode != 0:
            error_message = err5.decode().strip()
            logging.error(f"Error in store_in_mongo.py: {error_message}")
            print("Error in store_in_mongo.py:", err5.decode(), file=sys.stderr)
            sys.exit(store_in_mongo_proc.returncode)

    except Exception as e:
        logging.exception("Error executing store_in_mongo.py")
        print("Error executing store_in_mongo.py:", str(e), file=sys.stderr)
        sys.exit(1)

    logging.info("Data stored in MongoDB successfully.")

if __name__ == '__main__':
    main()