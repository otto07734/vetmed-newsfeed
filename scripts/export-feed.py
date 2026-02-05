#!/usr/bin/env python3
"""
Export blogwatcher articles to news.json for the VetMed News Feed widget.
Filters junk articles, assigns emojis, and formats for the widget.
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

# Emoji mapping based on keywords
EMOJI_MAP = [
    (r'gift|donat|fund|million|\$\d+|endow|philanthrop', '💰'),
    (r'fellowship|scholar|student|graduat|degree|class', '🎓'),
    (r'research|study|discover|scientist|lab\b|investig', '🔬'),
    (r'hospital|clinic|facility|center|treatment|surgery', '🏥'),
    (r'dog|canine|puppy|k-?9', '🐕'),
    (r'cat|feline|kitten', '🐱'),
    (r'horse|equine|equestrian', '🐴'),
    (r'cow|bovine|cattle|livestock|dairy', '🐄'),
    (r'pig|swine|porcine', '🐷'),
    (r'bird|avian|poultry|chicken', '🐦'),
    (r'zoo|wildlife|exotic|conservation', '🦁'),
    (r'cancer|tumor|oncolog', '🎗️'),
    (r'vaccine|immun|virus|disease|outbreak|pandemic', '💉'),
    (r'award|honor|recogni|winner|achievement', '🏆'),
    (r'conference|symposium|forum|event|workshop', '📅'),
    (r'one health|zoonotic|public health', '🌍'),
    (r'nutrition|diet|food|feed', '🥗'),
    (r'emergency|rescue|disaster', '🚨'),
    (r'technology|ai|artificial|digital|robot', '🤖'),
    (r'partnership|collaborat|agreement', '🤝'),
]

# Patterns to filter out junk articles
JUNK_PATTERNS = [
    r'^Read(\s+All)?(\s+News)?$',
    r'^EMAIL\s',
    r'^mailto:',
    r'^\d+$',  # Just numbers
    r'^Page \d+',
    r'^Next$|^Previous$',
    r'^Read more$',
    r'^See all$',
    r'^School of Veterinary Medicine$',
    r'^Veterinary Medicine$',
    r'^College of Veterinary Medicine$',
    r'^News$',
    r'^Events$',
    r'^Home$',
    r'^Contact',
    r'^About',
]

# Keywords that indicate vet/health relevance (at least one must match)
VET_HEALTH_KEYWORDS = [
    r'\bveterin', r'\banimal', r'\bpet\b', r'\bdog\b', r'\bcat\b', r'\bhorse', r'\bequine',
    r'\bbovine', r'\bcattle', r'\blivestock', r'\bpig\b', r'\bswine', r'\bpoultry', r'\bbird',
    r'\bwildlife', r'\bzoo\b', r'\bexotic', r'\bcanine', r'\bfeline', r'\bspecies',
    r'\bclinic', r'\bhospital', r'\bsurgery', r'\bdiagnos', r'\btreatment', r'\btherap',
    r'\bdisease', r'\bvirus', r'\bbacteri', r'\binfect', r'\bvaccine', r'\bimmun',
    r'\bpatholog', r'\boncolog', r'\bcancer', r'\btumor',
    r'\bresearch(?!.*magazine)', r'\bstudy\b', r'\bscientist', r'\blab\b',
    r'\bone health', r'\bzoonotic', r'\bpublic health', r'\bepidemiolog',
    r'\bnutrition', r'\bdiet\b', r'\bpharma', r'\bdrug\b', r'\bclinical',
    r'\banatomy', r'\bphysiology', r'\bgenetics', r'\bmolecular', r'\bcell\b',
    r'\bdvm\b', r'\bvet\b', r'\bveterinary', r'\bresidency\b', r'\bintern\b',
    r'\bshelter', r'\brescue\b', r'\bwelfare', r'\bhumane',
    r'\bbreeding', r'\breproduction', r'\bfertility', r'\btheriogenology',
    r'\bcardio', r'\bneuro', r'\bortho', r'\bderma', r'\bophthalm', r'\bdental',
    r'\bemergency', r'\bcritical care', r'\banesthes', r'\bradiology', r'\bimaging',
    r'\bnecropsy', r'\bautopsy', r'\bbiopsy', r'\bhistology',
    r'\bfellowship', r'\bscholarship',
    r'\baccredit', r'\bavma\b', r'\baaha\b',
]

# Keywords that indicate OFF-TOPIC content (exclude if these match without vet context)
EXCLUDE_KEYWORDS = [
    r'football', r'basketball', r'baseball', r'softball', r'soccer', r'hockey',
    r'lacrosse', r'volleyball', r'tennis', r'golf', r'track and field',
    r'athlete', r'championship', r'tournament', r'playoff', r'coach\b',
    r'shark[s]?\b(?!.*aquarium)', r'panther[s]?\b', r'tiger[s]?\b(?!.*zoo)', r'bear[s]?\b(?!.*wildlife)',
    r'ncaa', r'nec\b', r'conference\b(?!.*veterinary)',
    r'spirit squad', r'cheerleading', r'dance team',
    r'entrepreneur', r'business school', r'mba\b',
    r'law school', r'engineering(?!.*biomedical)', r'computer science',
    r'music\b', r'art\b(?!.*animals)', r'theater', r'film\b',
    r'political', r'election', r'president(?!.*university)',
    r'real estate', r'construction', r'architecture(?!.*hospital)',
]

# Schools we're tracking (for URL fixing)
SCHOOL_URLS = {
    'Western University': 'https://www.westernu.edu',
    'Lincoln Memorial University': '',  # Already full URLs
}

def get_emoji(title, summary=''):
    """Assign an emoji based on content keywords."""
    text = f"{title} {summary}".lower()
    for pattern, emoji in EMOJI_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return emoji
    return '📰'  # Default

def is_vet_health_related(title, source=''):
    """Check if article is related to veterinary medicine or health sciences.
    
    STRICT: Title must contain relevant keywords. Source name alone is not enough.
    This ensures we only surface truly relevant content.
    """
    title_lower = title.lower()
    
    # Check for vet/health keywords in TITLE specifically
    for pattern in VET_HEALTH_KEYWORDS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return True
    
    return False

def is_off_topic(title):
    """Check if article is clearly off-topic (sports, unrelated fields)."""
    text = title.lower()
    
    for pattern in EXCLUDE_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            # Double-check it's not actually vet-related
            if not is_vet_health_related(title):
                return True
    return False

def is_junk(title, url):
    """Check if article should be filtered out."""
    if len(title) < 10:
        return True
    for pattern in JUNK_PATTERNS:
        if re.match(pattern, title, re.IGNORECASE):
            return True
    if url.startswith('mailto:'):
        return True
    if '/page/' in url and url.endswith('/'):
        return True
    if '#footer' in url or '#header' in url or '#nav' in url:
        return True
    if url.endswith('/index.html') and len(title) < 20:
        return True
    return False

def fix_url(url, source):
    """Fix relative URLs."""
    if url.startswith('http'):
        return url
    if url.startswith('/'):
        base = SCHOOL_URLS.get(source, '')
        if base:
            return base + url
    return url

def parse_blogwatcher_output(output):
    """Parse blogwatcher articles output."""
    articles = []
    current = {}
    
    lines = output.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        # New article starts with [id]
        if re.match(r'\[\d+\]', line):
            if current and 'title' in current:
                articles.append(current)
            current = {}
            # Extract title
            match = re.match(r'\[\d+\]\s+\[(?:read|unread)\]\s+(.+)', line)
            if match:
                current['title'] = match.group(1).strip()
        elif line.startswith('Blog:'):
            current['source'] = line.replace('Blog:', '').strip()
        elif line.startswith('URL:'):
            current['url'] = line.replace('URL:', '').strip()
        elif line.startswith('Published:'):
            current['date'] = line.replace('Published:', '').strip()
    
    # Don't forget last article
    if current and 'title' in current:
        articles.append(current)
    
    return articles

def main():
    # Get articles from blogwatcher
    result = subprocess.run(
        ['blogwatcher', 'articles', '--all'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running blogwatcher: {result.stderr}")
        return
    
    articles = parse_blogwatcher_output(result.stdout)
    
    # Filter and process
    processed = []
    seen_titles = set()
    skipped_off_topic = 0
    skipped_not_relevant = 0
    
    for article in articles:
        title = article.get('title', '')
        url = article.get('url', '')
        source = article.get('source', 'Unknown')
        
        # Skip junk
        if is_junk(title, url):
            continue
        
        # Skip off-topic content (sports, unrelated fields)
        if is_off_topic(title):
            skipped_off_topic += 1
            continue
        
        # Must be vet/health related
        if not is_vet_health_related(title, source):
            skipped_not_relevant += 1
            continue
        
        # Skip duplicates
        title_key = title.lower()[:50]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        
        # Fix URL
        url = fix_url(url, source)
        
        # Create processed article
        processed.append({
            'emoji': get_emoji(title),
            'title': title[:100],  # Truncate long titles
            'summary': '',  # We don't have summaries from blogwatcher
            'url': url,
            'source': source,
            'date': article.get('date', '')
        })
    
    print(f"Filtered: {skipped_off_topic} off-topic, {skipped_not_relevant} not relevant")
    
    # Take most recent 100
    processed = processed[:100]
    
    # Create feed JSON
    feed = {
        'lastUpdated': datetime.now().astimezone().isoformat(),
        'items': processed
    }
    
    # Write to file
    output_path = Path(__file__).parent.parent / 'public' / 'news.json'
    with open(output_path, 'w') as f:
        json.dump(feed, f, indent=2)
    
    print(f"Exported {len(processed)} articles to {output_path}")

if __name__ == '__main__':
    main()
