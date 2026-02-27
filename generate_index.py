#!/usr/bin/env python3
"""
Generate index.html for a show by embedding its episodes.json data
"""

import sys
import json
from pathlib import Path

SHOWS = [
    'economic-update',
    'capitalism-hits-home',
    'global-capitalism',
    'the-dialectic-at-work',
    'ask-prof-wolff',
]

def generate_html_template():
    """Generate the HTML template"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Episodes</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: white;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        h1 {{
            font-size: 28px;
            color: #000;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .header-info {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 20px;
        }}
        .stats {{
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .stat {{
            font-size: 14px;
        }}
        .stat-number {{
            font-size: 20px;
            font-weight: bold;
            color: #000;
        }}
        .stat-label {{
            color: #999;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }}
        .search-box {{
            margin-bottom: 30px;
        }}
        input {{
            width: 100%;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
        }}
        input:focus {{
            outline: none;
            border-color: #999;
        }}
        .episode {{
            padding: 20px 0;
            border-bottom: 1px solid #ddd;
        }}
        .episode:last-child {{
            border-bottom: none;
        }}
        .episode-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
        }}
        .episode-number {{
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }}
        .episode-date {{
            font-size: 12px;
            color: #999;
        }}
        .episode-title {{
            font-size: 16px;
            color: #000;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .episode-meta {{
            font-size: 13px;
            color: #666;
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
        }}
        .episode-meta-item {{
            display: flex;
            gap: 6px;
        }}
        .episode-meta-label {{
            color: #999;
        }}
        .episode-link {{
            font-size: 13px;
        }}
        .episode-link a {{
            color: #000;
            text-decoration: none;
            border-bottom: 1px solid #000;
        }}
        .episode-link a:hover {{
            background: #f5f5f5;
        }}
        .no-link {{
            color: #ccc;
            text-decoration: line-through;
        }}
        .result-count {{
            font-size: 12px;
            color: #999;
            margin-bottom: 20px;
            padding-top: 10px;
        }}
        .no-results {{
            text-align: left;
            padding: 40px 20px;
            color: #999;
        }}
        .loading {{
            text-align: left;
            padding: 40px 20px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="header-info">
            <div class="stats">
                <div class="stat">
                    <div class="stat-number" id="statTotal">-</div>
                    <div class="stat-label">Total Episodes</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="statYoutube">-</div>
                    <div class="stat-label">With YouTube</div>
                </div>
            </div>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchBox" placeholder="Search episodes..." />
        </div>
        
        <div class="result-count">
            Showing <span id="resultCount">0</span> episodes
        </div>
        
        <div id="episodesList" class="loading">Loading episodes...</div>
        <div class="no-results" id="noResults" style="display: none;">
            No episodes found
        </div>
    </div>
    
    <script id="episodes-data" type="application/json"></script>
    <script>
        let episodes = [];
        
        // Try to load from embedded data first
        const embeddedData = document.getElementById('episodes-data').textContent;
        if (embeddedData.trim()) {{
            try {{
                episodes = JSON.parse(embeddedData);
                init();
            }} catch (e) {{
                console.error('Error parsing embedded data:', e);
                document.getElementById('episodesList').innerHTML = 
                    '<div class="no-results">Error loading episodes.</div>';
            }}
        }}
        
        function init() {{
            const total = episodes.length;
            const withYoutube = episodes.filter(e => e.youtube_url && e.youtube_url.trim()).length;
            
            document.getElementById('statTotal').textContent = total;
            document.getElementById('statYoutube').textContent = withYoutube;
            
            renderEpisodes('');
            
            document.getElementById('searchBox').addEventListener('input', (e) => {{
                renderEpisodes(e.target.value);
            }});
        }}
        
        function renderEpisodes(filter = '') {{
            const container = document.getElementById('episodesList');
            const noResults = document.getElementById('noResults');
            container.innerHTML = '';
            
            const filtered = episodes.filter(ep => {{
                if (!filter) return true;
                const search = filter.toLowerCase();
                return ep.title.toLowerCase().includes(search) ||
                       (ep.description || '').toLowerCase().includes(search) ||
                       (ep.author || '').toLowerCase().includes(search) ||
                       (ep.pub_date || '').includes(filter);
            }});
            
            document.getElementById('resultCount').textContent = filtered.length;
            
            if (filtered.length === 0) {{
                noResults.style.display = 'block';
                return;
            }}
            
            noResults.style.display = 'none';
            
            filtered.forEach((ep) => {{
                const hasYoutube = ep.youtube_url && ep.youtube_url.trim();
                const youtubeLink = hasYoutube 
                    ? `<a href="${{ep.youtube_url}}" target="_blank">Watch on YouTube →</a>`
                    : '<span class="no-link">No YouTube link</span>';
                
                const seasonNum = ep.season || '?';
                const episodeNum = ep.episode || '?';
                const date = ep.pub_date || 'Unknown';
                const duration = ep.duration || '-';
                const author = ep.author || '-';
                
                const div = document.createElement('div');
                div.className = 'episode';
                div.innerHTML = `
                    <div class="episode-header">
                        <div class="episode-number">S${{seasonNum}}E${{episodeNum}}</div>
                        <div class="episode-date">${{date}}</div>
                    </div>
                    <div class="episode-title">${{ep.title}}</div>
                    <div class="episode-meta">
                        <div class="episode-meta-item">
                            <span class="episode-meta-label">Duration:</span>
                            <span>${{duration}}</span>
                        </div>
                        <div class="episode-meta-item">
                            <span class="episode-meta-label">By:</span>
                            <span>${{author}}</span>
                        </div>
                    </div>
                    <div class="episode-link">
                        ${{youtubeLink}}
                    </div>
                `;
                
                container.appendChild(div);
            }});
        }}
    </script>
</body>
</html>
'''

def generate_for_show(show_name):
    """Generate index.html for a specific show"""
    show_dir = Path(f'shows/{show_name}')
    data_dir = show_dir / 'data'
    json_file = data_dir / 'episodes.json'
    
    if not json_file.exists():
        print(f"❌ {json_file} not found")
        return False
    
    # Read episodes
    with open(json_file, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    
    # Format title
    title = ' '.join(word.capitalize() for word in show_name.split('-'))
    
    # Generate HTML
    html = generate_html_template().format(title=title)
    
    # Embed episodes data
    episodes_json = json.dumps(episodes, ensure_ascii=False)
    html = html.replace(
        '<script id="episodes-data" type="application/json"></script>',
        f'<script id="episodes-data" type="application/json">{episodes_json}</script>'
    )
    
    # Write HTML
    html_file = show_dir / 'index.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    file_size = html_file.stat().st_size / 1024
    print(f"✓ {show_name}: {len(episodes)} episodes, {file_size:.1f} KB")
    return True

def main():
    if len(sys.argv) > 1:
        # Specific show
        shows = [sys.argv[1]]
    else:
        # All shows
        shows = SHOWS
    
    print(f"\n📄 Generating index.html files...\n")
    
    for show in shows:
        generate_for_show(show)
    
    print(f"\n✓ Done!")

if __name__ == '__main__':
    main()
