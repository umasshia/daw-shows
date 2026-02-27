#!/usr/bin/env python3
"""
Fast YouTube Matcher with Caching
Only fetches new videos and caches results
"""

import json
import csv
import sys
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
import re
from datetime import datetime, timedelta

SHOWS = [
    'economic-update',
    'capitalism-hits-home',
    'global-capitalism',
    'the-dialectic-at-work',
    'ask-prof-wolff',
]

YOUTUBE_PLAYLISTS = {
    'economic-update': 'https://www.youtube.com/playlist?list=PLPJpiw1WYdTMLIyASxEheOVjl1vKkajYj',
    'capitalism-hits-home': 'https://www.youtube.com/playlist?list=PLPJpiw1WYdTNYvke-gNRdml1Z2lwz0iEH',
    'global-capitalism': 'https://www.youtube.com/playlist?list=PLPJpiw1WYdTO6IoZ3VaDrQt-RJZsbG6nB',
    'the-dialectic-at-work': 'https://www.youtube.com/playlist?list=PLPJpiw1WYdTNjEmBz7JTKH9Dnfi3sWvfr',
    'ask-prof-wolff': 'https://www.youtube.com/playlist?list=PLPJpiw1WYdTPtnI9V-LaYVR97rmcCcFCQ',
}

def load_cache():
    """Load cached YouTube matches"""
    if Path(CACHE_FILE).exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save YouTube match cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_playlist_videos(playlist_url):
    """Fetch all videos from YouTube playlist"""
    try:
        import yt_dlp
    except ImportError:
        print("Installing yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
        import yt_dlp
    
    videos = []
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'socket_timeout': 10,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        videos.append({
                            'title': entry.get('title', ''),
                            'video_id': entry.get('id', ''),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}"
                        })
    except Exception as e:
        print(f"⚠️  Error fetching playlist: {e}")
    
    return videos

def normalize_title(title):
    """Normalize title for matching"""
    title = re.sub(r'^(Economic Update|Capitalism Hits Home|Global Capitalism|Dialectic at Work|Ask Prof Wolff):\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\[.*?\]', '', title)
    title = ' '.join(title.split())
    title = re.sub(r'[^\w\s]', '', title)
    return title.lower().strip()

def similarity_score(a, b):
    """Calculate similarity (0-100)"""
    a_norm = normalize_title(a)
    b_norm = normalize_title(b)
    if not a_norm or not b_norm:
        return 0
    return int(SequenceMatcher(None, a_norm, b_norm).ratio() * 100)

def process_show(show_name):
    """Process one show - match episodes from official playlist"""
    print(f"\nProcessing {show_name}...", end=" ", flush=True)
    
    data_dir = Path(f'shows/{show_name}/data')
    json_file = data_dir / 'episodes.json'
    
    if not json_file.exists():
        print(f"❌ File not found")
        return
    
    # Load episodes
    with open(json_file, 'r') as f:
        episodes = json.load(f)
    
    # Count missing YouTube URLs
    missing = [ep for ep in episodes if not ep.get('youtube_url')]
    
    if not missing:
        print(f"✓ All {len(episodes)} episodes have YouTube links")
        return
    
    print(f"Found {len(missing)} episodes without YouTube, fetching playlist...")
    
    # Fetch official playlist
    playlist_url = YOUTUBE_PLAYLISTS.get(show_name)
    if not playlist_url:
        print(f"❌ No playlist URL for {show_name}")
        return
    
    videos = fetch_playlist_videos(playlist_url)
    if not videos:
        print(f"❌ Could not fetch playlist videos")
        return
    
    print(f"\n  Fetched {len(videos)} videos from playlist")
    
    matched = 0
    # Match episodes to videos based on title similarity
    for ep in missing:
        ep_title = ep.get('title', '')
        
        # Find best matching video
        best_match = None
        best_score = 50  # Minimum threshold
        
        for video in videos:
            score = similarity_score(ep_title, video['title'])
            if score > best_score:
                best_score = score
                best_match = video
        
        if best_match:
            ep['youtube_url'] = best_match['url']
            ep['youtube_id'] = best_match['video_id']
            ep['youtube_name'] = best_match['title']
            matched += 1
            print(".", end="", flush=True)
        else:
            print("_", end="", flush=True)
    
    print(f"\n  ✓ Matched {matched}/{len(missing)}")
    
    # Save results
    with open(json_file, 'w') as f:
        json.dump(episodes, f, indent=2)

if __name__ == '__main__':
    print("=" * 50)
    print("Fast YouTube Matcher (with caching)")
    print("=" * 50)
    
    for show in SHOWS:
        process_show(show)
    
    print("\n" + "=" * 50)
    print("✓ Complete!")
    print("=" * 50)
