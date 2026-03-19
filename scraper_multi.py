#!/usr/bin/env python3
"""
Generic RSS Scraper for Democracy at Work shows
Scrapes episodes from RSS feeds and saves to structured show directories
"""

import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import re

RSS_FEEDS = {
    'economic-update': 'https://rss.libsyn.com/shows/84104/destinations/398074.xml',
    'capitalism-hits-home': 'https://rss.libsyn.com/shows/129530/destinations/784100.xml',
    'global-capitalism': 'https://rss.libsyn.com/shows/113799/destinations/640710.xml',
    'the-dialectic-at-work': 'https://rss.libsyn.com/shows/535257/destinations/4606092.xml',
    'ask-prof-wolff': 'https://rss.libsyn.com/shows/412178/destinations/3416240.xml',
}

LOCAL_RSS = {
    'economic-update': 'rss/economic update.xml',
    'capitalism-hits-home': 'rss/capitalism hits home.xml',
    'global-capitalism': 'rss/global capitalism.xml',
    'the-dialectic-at-work': 'rss/the dialectic at work.xml',
    'ask-prof-wolff': 'rss/ask prof wolff.xml',
}

def download_rss(show_name):
    """Download fresh RSS feed and save locally"""
    url = RSS_FEEDS[show_name]
    local_path = Path(LOCAL_RSS[show_name])
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(local_path, 'wb') as f:
            f.write(data)
        print(f"   ✓ Downloaded RSS feed ({len(data) // 1024} KB)")
        return True
    except (URLError, OSError) as e:
        print(f"   ⚠️  Could not download RSS: {e}")
        if local_path.exists():
            print(f"   Using cached local file")
            return True
        return False

def parse_rss(rss_file):
    """Parse RSS XML file"""
    try:
        tree = ET.parse(rss_file)
        root = tree.getroot()
        
        # Define namespaces
        namespaces = {
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        }
        
        items = root.findall('.//item')
        episodes = []
        
        for item in items:
            # Extract basic info
            title = item.findtext('title', '').strip()
            pub_date = item.findtext('pubDate', '').strip()
            description = item.findtext('description', '')
            
            # Clean description
            if description:
                description = re.sub(r'<[^>]+>', '', description).strip()[:500]
            
            # Try to get duration from itunes:duration
            duration = item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration', '').strip()
            
            # Get link
            link = item.findtext('link', '')
            
            # Get author
            author = item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}author', '')
            if not author:
                author = item.findtext('author', '')
            
            # Extract episode number and season from itunes tags
            season = item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}season', '?').strip()
            episode_number = item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}episode', '?').strip()
            
            # Fall back to regex extraction from title if tags not found
            if season == '?' or episode_number == '?':
                match = re.search(r'S(\d+)E(\d+)', title, re.IGNORECASE)
                if match:
                    season = match.group(1)
                    episode_number = match.group(2)
            
            # Get episode type from itunes tag
            episode_type = item.findtext('{http://www.itunes.com/dtds/podcast-1.0.dtd}episodeType', 'full').strip()
            
            episodes.append({
                'title': title,
                'author': author,
                'episode': episode_number,
                'season': season,
                'episode_type': episode_type,
                'description': description,
                'pub_date': pub_date,
                'duration': duration,
                'libsyn_link': link,
                'image_url': '',
                'youtube_url': '',
                'youtube_id': '',
                'youtube_name': '',
                'scraped_date': datetime.now().isoformat(),
            })
        
        return episodes
    
    except Exception as e:
        print(f"❌ Error parsing RSS: {e}")
        return []

def load_existing_episodes(show_name):
    """Load existing episodes to preserve YouTube data"""
    json_file = Path(f'shows/{show_name}/data/episodes.json')
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                episodes = json.load(f)
            # Index by libsyn_link for quick lookup
            return {ep.get('libsyn_link', ''): ep for ep in episodes if ep.get('libsyn_link')}
        except Exception:
            return {}
    return {}

def merge_episodes(new_episodes, existing_map):
    """Merge new episodes with existing data, preserving YouTube info and scraped_date"""
    merged = []
    new_count = 0
    for ep in new_episodes:
        link = ep.get('libsyn_link', '')
        if link in existing_map:
            old = existing_map[link]
            # Preserve YouTube data and scraped_date from existing
            for key in ('youtube_url', 'youtube_id', 'youtube_name', 'scraped_date'):
                if old.get(key):
                    ep[key] = old[key]
        else:
            new_count += 1
        merged.append(ep)
    return merged, new_count

def save_episodes(show_name, episodes):
    """Save episodes to JSON format"""
    show_dir = Path(f'shows/{show_name}')
    data_dir = show_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    if not episodes:
        print(f"❌ No episodes to save")
        return False

    # Save to JSON
    json_file = data_dir / 'episodes.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)

    # Save metadata
    metadata_file = data_dir / 'metadata.txt'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(f"Show: {show_name}\n")
        f.write(f"Total Episodes: {len(episodes)}\n")
        f.write(f"Scraped: {datetime.now().isoformat()}\n")

    return True

def main():
    if len(sys.argv) > 1:
        # Specific show requested
        show_names = [sys.argv[1]]
    else:
        # Process all shows
        show_names = list(RSS_FEEDS.keys())

    print("\n" + "="*70)
    print("🎙️  Democracy at Work RSS Scraper")
    print("="*70)

    for show_name in show_names:
        if show_name not in RSS_FEEDS:
            print(f"\n❌ Unknown show: {show_name}")
            print(f"   Available: {', '.join(RSS_FEEDS.keys())}")
            continue

        print(f"\n📺 Processing: {show_name}")

        # Download fresh RSS feed
        if not download_rss(show_name):
            print(f"   ❌ Skipping (no RSS data)")
            continue

        rss_path = Path(LOCAL_RSS[show_name])
        episodes = parse_rss(rss_path)

        if episodes:
            # Merge with existing data to preserve YouTube links
            existing = load_existing_episodes(show_name)
            episodes, new_count = merge_episodes(episodes, existing)
            print(f"   ✓ Parsed {len(episodes)} episodes ({new_count} new)")
            if save_episodes(show_name, episodes):
                print(f"   ✓ Saved to shows/{show_name}/data/")
        else:
            print(f"   ❌ No episodes found")

    print("\n" + "="*70)
    print("✓ Done!")

if __name__ == '__main__':
    main()
