"""
Streamlit News Scraper and Summarizer Web App

Search the web for news articles, automatically summarize them,
and display results in an interactive table.
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
from urllib.parse import quote
from transformers import pipeline

# Page configuration
st.set_page_config(
    page_title="News Scraper & Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main-header {
            color: #1f77b4;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 0.5em;
        }
        .metric-card {
            background-color: white;
            padding: 1em;
            border-radius: 0.5em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'summarizer' not in st.session_state:
    st.session_state.summarizer = None


@st.cache_resource
def get_summarizer():
    """Get or initialize the summarization pipeline (cached)."""
    st.info("⏳ Loading AI summarization model (first time only)...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    st.success("✓ Model loaded!")
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
        return text
    
    try:
        summarizer = get_summarizer()
        
        # Truncate text if too long for the model
        words = text.split()
        if len(words) > 1024:
            text = ' '.join(words[:1024])
        
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        st.warning(f"Could not summarize: {str(e)[:50]}")
        return text[:150] + "..." if len(text) > 150 else text


def parse_rss_date(date_str):
    """Parse RSS date format to YYYY-MM-DD."""
    try:
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
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text.strip()


def extract_source(title_text, guid_text='', link_url=''):
    """
    Extract source from title, guid, or URL.
    
    Args:
        title_text: Article title
        guid_text: RSS guid (often contains source info)
        link_url: Article URL
        
    Returns:
        Source name
    """
    # Try to extract from title (format: "Title - Source Name")
    if ' - ' in title_text:
        parts = title_text.split(' - ')
        if len(parts) >= 2:
            potential_source = parts[-1].strip()
            # Remove domain extensions if present
            potential_source = potential_source.replace('.com', '').replace('.co.uk', '').replace('.org', '')
            if len(potential_source) < 50:  # Reasonable source name length
                return potential_source
    
    # Try common sources list
    sources = ['BBC', 'Reuters', 'AP', 'CNN', 'Fox', 'NBC', 'ABC', 'CBS', 'NY Times', 'Washington Post', 'Bloomberg', 'CNBC', 'MSNBC', 'The Guardian', 'Financial Times', 'WSJ']
    for source in sources:
        if source.lower() in title_text.lower():
            return source
    
    # Try to extract from URL domain
    if link_url:
        try:
            from urllib.parse import urlparse
            domain = urlparse(link_url).netloc
            domain = domain.replace('www.', '').split('.')[0]
            if domain and len(domain) > 2:
                return domain.capitalize()
        except:
            pass
    
    # Try to extract from guid (Google News format often has source info)
    if guid_text and 'source=' in guid_text:
        try:
            source_part = guid_text.split('source=')[1].split('&')[0]
            if source_part:
                return source_part.replace('%20', ' ')
        except:
            pass
    
    return 'News'


def extract_author(title_text, description_text):
    """Extract author from title or description."""
    # Simple pattern to find "by Author Name"
    patterns = [
        r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Author:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title_text + ' ' + description_text)
        if match:
            return match.group(1)
    
    return 'Unknown'


def fetch_article_text(url):
    """
    Fetch the full article text from a URL.
    
    Args:
        url: Article URL
        
    Returns:
        Full article text or empty string if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "noscript"]):
            script.decompose()
        
        # Try multiple strategies to find article content
        article_text = ''
        
        # Strategy 1: Look for article/main/content tags with common patterns
        article_selectors = [
            ('article', {}),
            ('main', {}),
            ('div', {'class': re.compile(r'(article|content|post|story)', re.I)}),
            ('div', {'id': re.compile(r'(article|content|post|story|main)', re.I)}),
        ]
        
        for tag, attrs in article_selectors:
            try:
                element = soup.find(tag, attrs) if attrs else soup.find(tag)
                if element:
                    # Remove common junk from within
                    for junk in element.find_all(['script', 'style', 'nav', 'aside', 'footer']):
                        junk.decompose()
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > 300:  # Meaningful content
                        article_text = text
                        break
            except:
                continue
        
        # Strategy 2: If still empty, try paragraphs
        if not article_text or len(article_text) < 300:
            paragraphs = soup.find_all('p')
            if paragraphs:
                # Get all paragraph text but filter out navigation/ads
                texts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Skip very short paragraphs (likely navigation)
                    if len(text) > 20 and not any(skip in text.lower() for skip in ['subscribe', 'log in', 'sign up', 'advertisement', 'ad:']):
                        texts.append(text)
                if texts:
                    article_text = ' '.join(texts[:30])  # First 30 paragraphs
        
        # Strategy 3: Fallback to all text
        if not article_text or len(article_text) < 300:
            article_text = soup.get_text(separator=' ', strip=True)
        
        # Clean up multiple spaces
        article_text = ' '.join(article_text.split())
        
        # Limit to reasonable size for processing
        return article_text[:3500] if article_text else ''
        
    except Exception as e:
        return ''



def search_google_news_rss(query, max_articles=30):
    """
    Search using Google News RSS feed.
    
    Args:
        query: Search query
        max_articles: Maximum number of articles to retrieve
        
    Returns:
        List of articles with summaries
    """
    try:
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:max_articles]
        
        articles = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, item in enumerate(items):
            try:
                title = item.find('title')
                title_text = title.text if title else 'No title'
                
                pub_date = item.find('pubDate')
                pub_date_text = pub_date.text if pub_date else ''
                date_str = parse_rss_date(pub_date_text)
                
                description = item.find('description')
                desc_text = description.text if description else ''
                
                link = item.find('link')
                url = link.text if link else ''
                
                guid = item.find('guid')
                guid_text = guid.text if guid else ''
                
                source = extract_source(title_text, guid_text, url)
                author = extract_author(title_text, desc_text)
                
                status_text.text(f"Fetching: {title_text[:60]}...")
                
                # Fetch full article text from URL - THIS IS THE PRIMARY SOURCE FOR SUMMARY
                full_text = fetch_article_text(url)
                
                # Clean description from RSS
                clean_desc = clean_html(desc_text)
                
                # ALWAYS prefer full article text for summarization
                # Only fallback to description if we couldn't fetch the article
                if full_text and len(full_text.split()) > 30:
                    # Use full article text as primary source
                    text_to_summarize = full_text
                elif clean_desc and len(clean_desc.split()) > 20:
                    # Fallback to RSS description
                    text_to_summarize = clean_desc
                else:
                    # Last resort: use title
                    text_to_summarize = title_text
                
                # Generate summary from the selected text
                if len(text_to_summarize.split()) > 20:
                    summary = summarize_text(text_to_summarize)
                else:
                    # Too short to summarize
                    summary = text_to_summarize
                
                article = {
                    'date': date_str,
                    'source': source,
                    'author': author,
                    'title': clean_html(title_text),
                    'summary': summary,
                    'text': full_text if full_text else clean_desc,
                    'link': url
                }
                articles.append(article)
                
                progress_bar.progress((idx + 1) / len(items))
                
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        return articles
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<h1 class="main-header">📰 News Scraper & Summarizer</h1>', unsafe_allow_html=True)
    st.markdown("Search the web for news articles, automatically summarize them, and view in an interactive table.")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Query input
        query = st.text_input(
            "Enter search query:",
            value="technology news",
            placeholder="e.g., F-35, AI, climate change"
        )
        
        # Max articles slider
        max_articles = st.slider(
            "Number of articles to fetch:",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        # Search button
        search_button = st.button("🔍 Search News", use_container_width=True, type="primary")
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    # Search execution
    if search_button and query:
        with st.spinner(f"🔍 Searching for '{query}'..."):
            articles = search_google_news_rss(query, max_articles)
            st.session_state.articles = articles
    
    # Display results
    if st.session_state.articles:
        articles_df = pd.DataFrame(st.session_state.articles)
        
        # Display metrics
        with col1:
            st.metric("📊 Articles Found", len(articles_df))
        with col2:
            st.metric("📅 Date Range", f"{articles_df['date'].min()} to {articles_df['date'].max()}")
        with col3:
            st.metric("📰 Sources", articles_df['source'].nunique())
        
        st.divider()
        
        # Display table
        st.subheader("📋 Article Results")
        
        # Ensure all required columns exist
        required_columns = ['date', 'source', 'author', 'title', 'text', 'summary', 'link']
        for col in required_columns:
            if col not in articles_df.columns:
                articles_df[col] = ''
        
        # Create display dataframe with formatted columns
        display_df = articles_df[['date', 'source', 'author', 'title', 'text', 'summary']].copy()
        
        # Add clickable link column
        display_df['link'] = articles_df['link'].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 Read</a>' if x else 'N/A'
        )
        
        # Display table
        st.dataframe(
            display_df,
            column_config={
                'date': st.column_config.TextColumn('📅 Date', width='small'),
                'source': st.column_config.TextColumn('📰 Source', width='small'),
                'author': st.column_config.TextColumn('✍️ Author', width='small'),
                'title': st.column_config.TextColumn('📝 Title', width='large'),
                'text': st.column_config.TextColumn('📄 Full Text', width='large'),
                'summary': st.column_config.TextColumn('📝 Summary', width='large'),
                'link': st.column_config.Column('🔗 Link', width='small')
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.divider()
        
        # Download options
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = articles_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"news_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_str = articles_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"news_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    else:
        if not search_button:
            st.info("👈 Enter a search query and click 'Search News' to get started!")
        else:
            st.warning("No articles found. Try a different search query.")


if __name__ == "__main__":
    main()
