"""
F-35 Joint Strike Fighter News Scraper

This script searches the web for news related to the F-35 Joint Strike Fighter
and captures the date, source, text, and AI-generated summary of each article.

Uses Google News RSS feed and web scraping - completely free with no API key required.
Includes automatic summarization using transformers library.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import json
import re
from urllib.parse import quote
from transformers import pipeline


# Initialize summarizer (loads model on first use)
summarizer = None


def get_summarizer():
    """Get or initialize the summarization pipeline."""
    global summarizer
    if summarizer is None:
        print("Loading summarization model (first time only)...\n")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer


def summarize_text(text, max_length=150, min_length=50):
    """
    Generate a summary of the given text using AI.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        min_length: Minimum length of summary
        
    Returns:
        Summary text
    """
    if not text or len(text.split()) < 15:
        return text  # Return original if too short to summarize
    
    try:
        summarizer_pipe = get_summarizer()
        
        # Truncate text if too long for the model
        words = text.split()
        if len(words) > 1024:
            text = ' '.join(words[:1024])
        
        summary = summarizer_pipe(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Warning: Summarization failed for this article: {e}")
        return text[:150] + "..." if len(text) > 150 else text


def search_google_news_rss(query="F-35 Joint Strike Fighter", max_articles=50):
    """
    Search using Google News RSS feed (free, no API key required).
    
    Args:
        query: Search query
        max_articles: Maximum number of articles to retrieve
        
    Returns:
        List of articles with date, source, and text
    """
    try:
        # Google News RSS feed URL
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}"
        
        print(f"Searching Google News RSS for: {query}\n")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:max_articles]
        
        articles = []
        for item in items:
            try:
                title = item.find('title')
                title_text = title.text if title else 'No title'
                
                pub_date = item.find('pubDate')
                pub_date_text = pub_date.text if pub_date else ''
                
                # Parse date from RSS format
                date_str = parse_rss_date(pub_date_text)
                
                description = item.find('description')
                desc_text = description.text if description else ''
                
                link = item.find('link')
                url = link.text if link else ''
                
                # Extract source from description or title
                source = extract_source(title_text)
                
                # Clean text
                clean_desc = clean_html(desc_text)
                
                # Generate summary based on description
                print(f"Processing: {title_text[:60]}...")
                summary = summarize_text(clean_desc)
                
                article = {
                    'date': date_str,
                    'source': source,
                    'title': clean_html(title_text),
                    'text': clean_desc,
                    'summary': summary,
                    'url': url
                }
                articles.append(article)
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        print(f"\nFound {len(articles)} articles\n")
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google News: {e}")
        return []


def search_bbc_news(max_articles=30):
    """
    Scrape BBC News for F-35 related articles (free, no API key required).
    
    Args:
        max_articles: Maximum number of articles to retrieve
        
    Returns:
        List of articles
    """
    try:
        print("Searching BBC News...\n")
        url = "https://www.bbc.com/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Find all article links
        for link in soup.find_all('a', href=re.compile('/news/article')):
            if len(articles) >= max_articles:
                break
            
            title = link.get_text(strip=True)
            
            # Filter for F-35 related articles
            if 'f-35' not in title.lower() and 'joint strike' not in title.lower():
                continue
            
            article = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'BBC News',
                'title': title,
                'text': title,
                'url': f"https://www.bbc.com{link.get('href')}"
            }
            articles.append(article)
        
        return articles
        
    except Exception as e:
        print(f"Error scraping BBC News: {e}")
        return []


def parse_rss_date(date_str):
    """Parse RSS date format to YYYY-MM-DD."""
    try:
        # RSS date format: Thu, 02 May 2024 10:30:15 GMT
        dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return dt.strftime('%Y-%m-%d')
    except:
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt.strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')


def clean_html(text):
    """Remove HTML tags and entities from text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text.strip()


def extract_source(title_text):
    """Extract source from title."""
    # Common news sources in Google News
    sources = ['BBC', 'Reuters', 'AP', 'CNN', 'Fox', 'NBC', 'ABC', 'CBS', 'NY Times', 'Washington Post', 'Bloomberg']
    for source in sources:
        if source.lower() in title_text.lower():
            return source
    return 'Google News'


def save_to_csv(articles, filename="f35_news.csv"):
    """Save articles to CSV file."""
    if not articles:
        print("No articles to save.")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'source', 'title', 'text', 'summary', 'url'])
            writer.writeheader()
            writer.writerows(articles)
        print(f"Saved {len(articles)} articles to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def save_to_json(articles, filename="f35_news.json"):
    """Save articles to JSON file."""
    if not articles:
        print("No articles to save.")
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(articles)} articles to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")


def print_summary(articles):
    """Print a summary of articles with AI-generated summaries."""
    if not articles:
        print("No articles found.")
        return
    
    print(f"{'='*80}")
    print(f"F-35 NEWS SUMMARY - {len(articles)} articles found")
    print(f"{'='*80}\n")
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article['date']}] {article['source']}")
        print(f"   Title: {article['title']}")
        print(f"   Summary: {article.get('summary', article['text'][:150])}")
        if article.get('url'):
            print(f"   URL: {article['url']}")
        print()


def main():
    """Main execution function."""
    print("="*80)
    print("F-35 Joint Strike Fighter News Scraper")
    print("(Free, No API Key Required)")
    print("="*80 + "\n")
    
    # Search Google News RSS (primary method - free, no limits)
    articles = search_google_news_rss(
        query="F-35 Joint Strike Fighter",
        max_articles=50
    )
    
    # Display results
    print_summary(articles)
    
    # Save results
    if articles:
        save_to_csv(articles, "f35_news.csv")
        save_to_json(articles, "f35_news.json")
        print(f"\n✓ Successfully scraped {len(articles)} articles")
    else:
        print("\n✗ No articles found.")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
