Here's a simplified and more readable README version of your content:

# ML Web Scraper

This project is a modular web scraping pipeline designed to extract images and captions from webpages, check for duplicates, and store data efficiently in MongoDB. The scraper is highly configurable, allowing easy adjustments without modifying the code.

## Initial Setup

- **Logger Initialization**: Captures errors, exceptions, and status messages into `scraper.log` for easy debugging and monitoring.
- **Configuration File (`config.json`)**: Defines key parameters such as:
  - Website URL and keyword
  - HTML tags for content extraction (`top_tag_name`, `img_tag_1`, `img_tag_2`, etc.)
  - Database details (`database_name`, `client_address`)

## Pipeline Modules

### 1. HTML Content Extraction (`find_site.py`)

Fetches HTML content from the configured webpage URL for further processing.

### 2. Subpage URL Extraction (`find_subpage.py`)

Identifies and extracts the URL of the relevant subpage (e.g., "Top Stories") based on the specified keyword.

### 3. Image and Caption Extraction (`find_pic_caption.py`)

Parses the subpage using BeautifulSoup to extract image-caption pairs.

**Key Features:**
- **Dynamic Configuration**: Supports multiple image tags to handle various page layouts.
- **Lazy Loading Handling**: Detects lazy-loaded images by checking attributes like `srcset`, ensuring accurate extraction.
- **Duplicate Preparation**: Temporarily downloads images to compute hashes for duplicate detection.
- **Temporary Data Storage**: Stores extracted data (image URLs, captions, timestamps) in a JSON file for further processing.

### 4. Duplicate Checking (`check_duplicate.py`)

Ensures data uniqueness by:
- Checking duplicates within the extracted JSON data.
- Comparing new data against existing database entries using:
  - Caption similarity (Levenshtein distance)
  - Image hash similarity
- Adjustable thresholds allow flexible duplicate detection criteria.

### 5. Data Storage in MongoDB (`store_in_mongo.py`)

Stores verified unique data into MongoDB efficiently.

**Storage Details:**
- **Image Re-downloading**: Ensures high-quality image storage.
- **GridFS Integration**: Uses MongoDB's GridFS for efficient management of large image files.
- **Metadata Storage**: Stores associated metadata (URLs, captions, timestamps) in dedicated collections for easy retrieval and analysis.
