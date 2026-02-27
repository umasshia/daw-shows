#!/usr/bin/env python3
"""
YouTube Matcher for all Democracy at Work shows
Matches YouTube videos to episodes in the database for any show
"""

import json
import csv
import sys
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
import re

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

def setup_dependencies():
    """Install required packages"""
    try:
        import yt_dlp
    except ImportError:
        print("Installing yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])

def fetch_youtube_playlist(playlist_url):
    """Fetch all videos from YouTube playlist using yt-dlp"""
    import yt_dlp
    
    videos = []
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:  # Skip None entries
                        videos.append({
                            'title': entry.get('title', 'Unknown'),
                            'video_id': entry.get('id', ''),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}"
                        })
        
        return videos
    except Exception as e:
        print(f"   ⚠️  Error fetching playlist: {e}")
        return []

def search_youtube(query):
    """Search YouTube for a video"""
    import yt_dlp
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch1:{query}"
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                if entry:
                    return {
                        'title': entry.get('title', ''),
                        'video_id': entry.get('id', ''),
                        'url': f"https://www.youtube.com/watch?v={entry['id']}"
                    }
    except Exception as e:
        pass
    
    return None

def normalize_title(title):
    """Normalize title for comparison"""
    # Remove common prefixes
    title = re.sub(r'^(Economic Update|Capitalism Hits Home|Global Capitalism|Dialectic at Work|Ask Prof Wolff):\s*', '', title, flags=re.IGNORECASE)
    # Remove brackets and special markers
    title = re.sub(r'\[.*?\]', '', title)
    # Normalize whitespace
    title = ' '.join(title.split())
    # Remove special characters
    title = re.sub(r'[^\w\s]', '', title)
    return title.lower().strip()

def similarity_score(a, b):
    """Calculate similarity score between two strings (0-100)"""
    a_norm = normalize_title(a)
    b_norm = normalize_title(b)
    return int(SequenceMatcher(None, a_norm, b_norm).ratio() * 100)

def load_episodes(csv_file):
    """Load episodes from CSV"""
    episodes = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        episodes = list(reader)
    return episodes

def save_episodes(csv_file, episodes):
    """Save episodes back to CSV"""
    if not episodes:
        return
    
    fieldnames = list(episodes[0].keys())
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(episodes)

def match_videos_to_episodes(videos, episodes, show_name=None):
    """Match YouTube videos to episodes using playlist or search fallback"""
    
    SHOW_PREFIXES = {
        'economic-update': 'Economic Update:',
        'capitalism-hits-home': 'Capitalism Hits Home:',
        'global-capitalism': 'Global Capitalism:',
        'the-dialectic-at-work': 'The Dialectic at Work:',
        'ask-prof-wolff': 'Ask Prof Wolff:',
    }
    
    matched_indices = set()
    preserved_matches = 0
    new_matches = 0
    
    # First pass: count existing YouTube URLs
    for j, episode in enumerate(episodes):
        if episode.get('youtube_url') and episode.get('youtube_url').strip():
            matched_indices.add(j)
            preserved_matches += 1
    
    # If no videos provided, try to fetch from playlist
    if not videos:
        playlist_url = YOUTUBE_PLAYLISTS.get(show_name)
        if playlist_url:
            print(f"   ⏳ Fetching playlist videos...")
            videos = fetch_youtube_playlist(playlist_url)
            if videos:
                print(f"   ✓ Found {len(videos)} videos on playlist")
            else:
                print(f"   ⚠️  Playlist unavailable, will use search fallback")
    
    # Match using similarity if we have videos
    if videos:
        for i, episode in enumerate(episodes):
            # Skip already matched episodes
            if i in matched_indices:
                continue
            
            episode_title = episode.get('title', '').strip()
            
            if not episode_title:
                continue
            
            # Find best match among videos
            best_match = None
            best_score = 0
            
            for video in videos:
                score = similarity_score(episode_title, video['title'])
                if score > best_score:
                    best_match = video
                    best_score = score
            
            # Accept matches with sufficient similarity (>60%)
            if best_match and best_score > 60:
                episodes[i]['youtube_url'] = best_match['url']
                episodes[i]['youtube_id'] = best_match['video_id']
                episodes[i]['youtube_name'] = best_match['title']
                matched_indices.add(i)
                new_matches += 1
                if i < 5 or i % 50 == 0:
                    print(f"   ✓ Matched ({best_score}%): {episode_title[:50]}")
    
    # Fallback: search YouTube for unmatched episodes
    if matched_indices != set(range(len(episodes))):
        show_prefix = SHOW_PREFIXES.get(show_name, '')
        print(f"   ⏳ Searching YouTube for {len(episodes) - len(matched_indices)} remaining episodes...")
        
        for i, episode in enumerate(episodes):
            if i in matched_indices:
                continue
            
            episode_title = episode.get('title', '').strip()
            if not episode_title:
                continue
            
            # Try search with show prefix
            search_query = f"{show_prefix} {episode_title}".strip()
            result = search_youtube(search_query)
            
            if result and result.get('url'):
                episodes[i]['youtube_url'] = result['url']
                episodes[i]['youtube_id'] = result['video_id']
                episodes[i]['youtube_name'] = result['title']
                matched_indices.add(i)
                new_matches += 1
            else:
                # Try without prefix
                result = search_youtube(episode_title)
                if result and result.get('url'):
                    episodes[i]['youtube_url'] = result['url']
                    episodes[i]['youtube_id'] = result['video_id']
                    episodes[i]['youtube_name'] = result['title']
                    matched_indices.add(i)
                    new_matches += 1
    
    if new_matches > 0 or preserved_matches > 0:
        print(f"   ✓ Found {len(videos)} playlist videos" if videos else "   ✓ Used search fallback")
    
    return preserved_matches, new_matches

def main():
    if len(sys.argv) > 1:
        # Specific show requested
        show_names = [sys.argv[1]]
    else:
        # All shows
        show_names = SHOWS
    
    print("\n" + "="*70)
    print("🎥 YouTube Matcher - Democracy at Work")
    print("="*70)
    
    for show_name in show_names:
        if show_name not in YOUTUBE_PLAYLISTS:
            print(f"\n❌ Unknown show: {show_name}")
            continue
        
        show_dir = Path(f'shows/{show_name}')
        csv_file = show_dir / 'data' / 'episodes.csv'
        
        if not csv_file.exists():
            print(f"\n❌ {csv_file} not found")
            continue
        
        print(f"\n📺 Processing: {show_name}")
        
        episodes = load_episodes(csv_file)
        print(f"   ✓ Loaded {len(episodes)} episodes")
        
        preserved, matched = match_videos_to_episodes([], episodes, show_name)
        
        # Save results
        save_episodes(csv_file, episodes)
        
        # Update JSON files
        json_file = show_dir / 'data' / 'episodes.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(episodes, f, indent=2, ensure_ascii=False)
        
        jsonl_file = show_dir / 'data' / 'episodes.jsonl'
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for ep in episodes:
                f.write(json.dumps(ep, ensure_ascii=False) + '\n')
        
        total_with_youtube = preserved + matched
        coverage = int((total_with_youtube / len(episodes)) * 100)
        
        print(f"   ✓ Preserved: {preserved} existing URLs")
        print(f"   ✓ Matched: {matched} new videos")
        print(f"   ✓ Total: {total_with_youtube}/{len(episodes)} ({coverage}%)")
    
    print("\n" + "="*70)
    print("✓ Done!")

if __name__ == '__main__':
    setup_dependencies()
    main()
