#!/usr/bin/env python3
"""
Generic RSS Scraper for Democracy at Work shows
Scrapes episodes from RSS feeds and saves to structured show directories
"""

import sys
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import re

SHOWS = {
    'economic-update': 'rss/economic update.xml',
    'capitalism-hits-home': 'rss/capitalism hits home.xml',
    'global-capitalism': 'rss/global capitalism.xml',
    'the-dialectic-at-work': 'rss/the dialectic at work.xml',
    'ask-prof-wolff': 'rss/ask prof wolff.xml',
}

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

def save_episodes(show_name, episodes):
    """Save episodes to CSV, JSON, and JSONL formats"""
    show_dir = Path(f'shows/{show_name}')
    data_dir = show_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    if not episodes:
        print(f"❌ No episodes to save")
        return False
    
    # Save to CSV
    csv_file = data_dir / 'episodes.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=episodes[0].keys())
        writer.writeheader()
        writer.writerows(episodes)
    print(f"✓ Saved {csv_file}")
    
    # Save to JSON
    json_file = data_dir / 'episodes.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {json_file}")
    
    # Save to JSONL
    jsonl_file = data_dir / 'episodes.jsonl'
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for ep in episodes:
            f.write(json.dumps(ep, ensure_ascii=False) + '\n')
    print(f"✓ Saved {jsonl_file}")
    
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
        show_names = list(SHOWS.keys())
    
    print("\n" + "="*70)
    print("🎙️  Democracy at Work RSS Scraper")
    print("="*70)
    
    for show_name in show_names:
        if show_name not in SHOWS:
            print(f"\n❌ Unknown show: {show_name}")
            print(f"   Available: {', '.join(SHOWS.keys())}")
            continue
        
        rss_file = SHOWS[show_name]
        rss_path = Path(rss_file)
        
        if not rss_path.exists():
            print(f"\n❌ RSS file not found: {rss_file}")
            continue
        
        print(f"\n📺 Processing: {show_name}")
        print(f"   RSS: {rss_file}")
        
        episodes = parse_rss(rss_path)
        
        if episodes:
            print(f"   ✓ Parsed {len(episodes)} episodes")
            if save_episodes(show_name, episodes):
                print(f"   ✓ Saved to shows/{show_name}/data/")
        else:
            print(f"   ❌ No episodes found")
    
    print("\n" + "="*70)
    print("✓ Done!")

if __name__ == '__main__':
    main()
