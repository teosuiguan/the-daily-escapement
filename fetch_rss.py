import feedparser
import datetime
import html
from bs4 import BeautifulSoup

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_feed(url, source_name):
    print(f"Fetching {source_name} from {url}...")
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        title = entry.get('title', 'No Title')
        link = entry.get('link', 'No URL')
        
        # Extract date
        published = entry.get('published_parsed') or entry.get('updated_parsed')
        date_str = ""
        if published:
            date_str = datetime.datetime(*published[:6]).strftime('%Y-%m-%d')
        
        # Extract content/summary
        content = ""
        if 'content' in entry:
            content = " ".join([c.value for c in entry.content])
        elif 'summary' in entry:
            content = entry.summary
        
        clean_content = clean_html(content)
        
        articles.append({
            'TITLE': title,
            'SOURCE': source_name,
            'URL': link,
            'DATE': date_str,
            'CONTENT': clean_content
        })
    return articles

def main():
    feeds = [
        ("https://www.hodinkee.com/articles/rss.xml", "Hodinkee"),
        ("https://watchesbysjx.com/feed", "SJX")
    ]
    
    all_articles = []
    for url, name in feeds:
        try:
            all_articles.extend(fetch_feed(url, name))
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    # Sort by date descending
    all_articles.sort(key=lambda x: x['DATE'], reverse=True)
    
    with open("/home/ubuntu/raw_articles.txt", "w") as f:
        for art in all_articles:
            f.write(f"TITLE: {art['TITLE']}\n")
            f.write(f"SOURCE: {art['SOURCE']}\n")
            f.write(f"URL: {art['URL']}\n")
            f.write(f"DATE: {art['DATE']}\n")
            f.write(f"CONTENT: {art['CONTENT'][:2000]}...\n") # Truncate content for the log but keep enough for LLM
            f.write("---\n")
    
    print(f"Successfully fetched {len(all_articles)} articles.")

if __name__ == "__main__":
    main()
