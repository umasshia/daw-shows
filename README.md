# Economic Update Podcast Database

A comprehensive scraper and manager for the Economic Update podcast from libsyn. Pulls all episode metadata and organizes it for easy distribution and management across multiple platforms.

## Overview

This project scrapes the Economic Update podcast RSS feed and collects:
- **Episode Title & Number**
- **Season Information**
- **Description**
- **Publication Date**
- **Duration**
- **Author**
- **Libsyn Link**
- **YouTube Video Name** (generated from episode title)
- **Image/Cover Art URLs**
- **Episode Type** (full, trailer, etc.)

## Project Structure

```
economic_update_podcast/
├── scraper.py          # Main scraper script
├── manager.py          # Episode management & utilities
├── README.md           # This file
└── data/               # Output directory
    ├── episodes.csv    # Master database (CSV format)
    ├── episodes.json   # Episodes in JSON format
    ├── episodes.jsonl  # Episodes in JSONL format (one per line)
    └── metadata.txt    # Scraping metadata
```

## Setup

### Requirements
- Python 3.7+
- requests library

### Installation

```bash
# Install required packages
pip install requests

# Make scripts executable (optional)
chmod +x scraper.py manager.py
```

## Usage

### 1. Scrape All Episodes

```bash
python scraper.py
```

This will:
- Fetch the RSS feed from economicupdate.libsyn.com
- Extract all episode metadata
- Save to `data/episodes.csv`
- Generate metadata file

**Output:**
- `data/episodes.csv` - Master database
- `data/metadata.txt` - Scraping info and stats

### 2. Manage Episodes

```bash
python manager.py
```

This will:
- Load all episodes from CSV
- Display podcast statistics
- Export to JSON and JSONL formats
- Show example searches

### 3. Using the Manager Class Programmatically

```python
from manager import EpisodeManager

# Load episodes
manager = EpisodeManager("data/episodes.csv")

# Search by keyword
results = manager.search_by_keyword("capitalism")
for ep in results:
    manager.print_episode(ep)

# Get statistics
stats = manager.get_stats()
print(f"Total episodes: {stats['total_episodes']}")

# Export to different formats
manager.export_to_json()
manager.export_to_json_lines()

# Get specific episode
ep = manager.get_by_episode_number(123)
if ep:
    manager.print_episode(ep)
```

## CSV Fields

The `episodes.csv` file contains the following columns:

| Field | Description |
|-------|-------------|
| `title` | Episode title/name |
| `author` | Episode author |
| `episode` | Episode number |
| `season` | Season number (default: 1) |
| `episode_type` | Type of episode (full, trailer, etc.) |
| `description` | Full episode description (HTML stripped) |
| `pub_date` | Publication date |
| `duration` | Episode duration (HH:MM:SS format) |
| `libsyn_link` | Direct link to libsyn episode page |
| `youtube_name` | Generated YouTube video name |
| `image_url` | Cover art/image URL |
| `scraped_date` | Date/time the episode was scraped |

## Features

### Current
- ✅ Scrapes all episodes from RSS feed
- ✅ Extracts comprehensive metadata
- ✅ Organizes data in multiple formats (CSV, JSON, JSONL)
- ✅ Search functionality by title/keyword
- ✅ Statistics generation
- ✅ Episode number extraction from titles
- ✅ YouTube name generation

### Planned
- 🔄 Database integration (SQLite/PostgreSQL)
- 🔄 Platform-specific export templates (YouTube, Spotify, etc.)
- 🔄 Duplicate detection and merging
- 🔄 Incremental updates (only fetch new episodes)
- 🔄 Tag generation and categorization
- 🔄 Web interface for browsing/searching

## Distribution

The organized data can be used for:

- **CSV Distribution**: Direct import into spreadsheets or databases
- **JSON/JSONL**: API consumption and web applications
- **Platform Export**: Templates for uploading to YouTube, Spotify, Apple Podcasts, etc.

## Data Quality

- Episode numbers are extracted from titles, season numbers inferred from iTunes metadata
- Descriptions have HTML tags stripped for cleanliness
- Links are preserved as-is from the RSS feed
- All data is UTF-8 encoded for international character support

## Troubleshooting

### No episodes found
- Check internet connection
- Verify RSS URL is accessible: https://economicupdate.libsyn.com/rss
- Check if libsyn has changed their RSS structure

### Special characters appearing incorrectly
- Ensure terminal/file handler supports UTF-8
- Files are saved with UTF-8 encoding

### Need more episodes
- Run `scraper.py` again - it will fetch the latest RSS feed
- RSS typically contains the most recent episodes (usually last 100-500)

## Notes

- The RSS feed is the most reliable source for complete episode data
- Episode numbers may have gaps if some episodes were removed from the feed
- YouTube links are generated based on episode titles - they may need verification
- Duration and image URLs depend on what libsyn provides in the RSS feed

## License

This project is for personal use and podcast metadata aggregation purposes.
