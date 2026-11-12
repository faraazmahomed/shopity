import xml.etree.ElementTree as ET
import requests

def fetch_subreddit_posts(subreddit_name="django", limit=10):
    url = f"https://www.reddit.com/r/{subreddit_name}.rss"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)[:limit]
        
        posts = []
        for entry in entries:
            title = entry.find('atom:title', ns).text
            link_elem = entry.find('atom:link', ns)
            link = link_elem.attrib.get('href') if link_elem is not None else '#'
            
            author_elem = entry.find('atom:author/atom:name', ns)
            author = author_elem.text if author_elem is not None else 'Unknown'
            if author.startswith('/u/'):
                author = author[3:]
                
            posts.append({
                'title': title,
                'author': author,
                'permalink': link,
                'score': 'N/A'
            })
            
        return posts
    except Exception as e:
        print(f"Reddit RSS Error: {e}")
        return []
