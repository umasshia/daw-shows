#!/usr/bin/env python3
"""
Fetch all playlists from Democracy at Work YouTube channel
and save their URLs for use in the YouTube matcher.
"""

import subprocess
import json
import re
from pathlib import Path

CHANNEL_URL = "https://www.youtube.com/@democracyatwrk"

def get_channel_playlists():
    """Extract all playlists from the channel using yt-dlp"""
    print("Fetching playlists from Democracy at Work channel...")
    
    try:
        result = subprocess.run(
            ['yt-dlp', '--flat-playlist', '-j', f'{CHANNEL_URL}/playlists'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return {}
        
        playlists = {}
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get('_type') == 'playlist':
                    playlist_id = data.get('id')
                    title = data.get('title', '')
                    url = f"https://www.youtube.com/playlist?list={playlist_id}"
                    playlists[title] = {
                        'url': url,
                        'id': playlist_id,
                        'title': title
                    }
                    print(f"  Found: {title}")
            except json.JSONDecodeError:
                continue
        
        return playlists
    
    except subprocess.TimeoutExpired:
        print("Timeout fetching channel playlists")
        return {}
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return {}

def match_playlists_to_shows(playlists):
    """Match YouTube playlists to our show IDs"""
    show_mappings = {
        'economic-update': ['Economic Update'],
        'capitalism-hits-home': ['Capitalism Hits Home'],
        'global-capitalism': ['Global Capitalism'],
        'the-dialectic-at-work': ['Dialectic', 'The Dialectic'],
        'ask-prof-wolff': ['Ask Prof', 'Ask Professor'],
    }
    
    matched = {}
    unmatched = []
    
    for yt_title, playlist_info in playlists.items():
        found = False
        for show_id, keywords in show_mappings.items():
            if any(keyword.lower() in yt_title.lower() for keyword in keywords):
                matched[show_id] = playlist_info
                print(f"✓ Matched '{yt_title}' -> {show_id}")
                found = True
                break
        if not found:
            unmatched.append(yt_title)
    
    if unmatched:
        print(f"\nUnmatched playlists:")
        for title in unmatched:
            print(f"  - {title}")
    
    return matched

def save_playlists(matched_playlists):
    """Save playlist URLs to JSON file"""
    output_file = Path('youtube_playlists.json')
    
    with open(output_file, 'w') as f:
        json.dump(matched_playlists, f, indent=2)
    
    print(f"\nSaved {len(matched_playlists)} playlists to {output_file}")
    return output_file

if __name__ == '__main__':
    print("Democracy at Work - Playlist Fetcher\n")
    
    playlists = get_channel_playlists()
    print(f"\nTotal playlists found: {len(playlists)}\n")
    
    if playlists:
        matched = match_playlists_to_shows(playlists)
        print(f"\nMatched playlists: {len(matched)}")
        
        if matched:
            save_playlists(matched)
            print("\nPlaylist URLs:")
            for show_id, info in matched.items():
                print(f"  {show_id}: {info['url']}")
    else:
        print("No playlists found. Make sure yt-dlp is installed and the channel is accessible.")
