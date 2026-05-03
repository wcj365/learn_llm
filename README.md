# Learn LLM

## Setup Python Virtual Environment

Create a Python virtual environment named `.venv`.

- Make sure you are at the project root. 
- Run `python -m venv .venv` in a terminal

**Note:**

 in VS Code, open a new terminal will automatically activate this virtual environment. All the following commands will need to be run in the virutal environment. Always make sure the .venv is active before running any commands.

## Install the required Python packages

- Make sure the .venv is activated
- Run `pip install -r requirements.txt`

## Download pre-trained models from Huggingface
  - Create a local folder outside of the project root folder and name it `huggingface_models` 
  - Modify the download_models.py script to use the folder name
  - Run the download_models.py script

## Run sentiment analysis using the downloaded model

  - Modify sentiment_analysis.py to point to the folder
  - Run the script

## F-35 Joint Strike Fighter News Scraper

A Python script to search the web for F-35 related news and capture date, source, text, and AI-generated summary of each article.

### Features
- Uses **Google News RSS feed** (completely free, no API key required)
- **AI-powered article summarization** using transformers (BART model)
- Captures: date, source, title, full text, summary, and URL
- Exports results to CSV and JSON formats with summaries included
- No rate limits or subscription needed

### Setup

Install required packages (only needed once):
```bash
pip install -r requirements.txt
```

### Usage

Run the script from the project root:
```bash
python src/f35_news_scraper.py
```

The script will:
1. Fetch articles from Google News RSS feed
2. Generate AI summaries for each article (first run may take a minute while the model loads)
3. Display console summary with titles and summaries
4. Export to CSV and JSON files

### Output Files

- `f35_news.csv` - CSV file with date, source, title, original text, AI summary, and URL
- `f35_news.json` - JSON file with all article details including summaries

### Customization

Edit the script to modify:
- Search query (change "F-35 Joint Strike Fighter" in `main()`)
- Number of articles to retrieve (change `max_articles` parameter)
- Summary length (adjust `max_length` and `min_length` in `summarize_text()`)
- Output filename

---

## Streamlit News Scraper & Summarizer Web App

An interactive web application to search for any news topic, automatically summarize articles, and display results in an interactive table.

### Features
- 🔍 **Dynamic search** - Search for any topic
- 📊 **Interactive table** - View results with date, source, author, title, summary, and link
- 🤖 **AI summarization** - Automatic article summaries using BART model
- 📥 **Export options** - Download results as CSV or JSON
- ✨ **Beautiful UI** - Clean, responsive Streamlit interface

### Setup

Install required packages (if not already installed):
```bash
pip install -r requirements.txt
```

### Usage

Run the Streamlit app from the project root:
```bash
streamlit run src/streamlit_news_app.py
```

Then:
1. Enter your search query in the sidebar (e.g., "F-35", "AI news", "technology")
2. Adjust the number of articles to fetch (5-50)
3. Click "Search News" button
4. View results in the interactive table
5. Download results as CSV or JSON if needed

### Features in Detail

- **Search Sidebar**: Enter any search query and customize the number of articles
- **Results Metrics**: See the number of articles, date range, and number of sources
- **Interactive Table**: Displays:
  - 📅 Date - Publication date
  - 📰 Source - News outlet
  - ✍️ Author - Article author
  - 📝 Title - Article headline
  - 📄 Summary - AI-generated summary
  - 🔗 Link - Clickable link to full article
- **Export Options**: Download all results as CSV or JSON

### Tips

- First run will take longer (1-2 minutes) while the AI model loads
- Summaries are more effective for longer articles
- Try different queries to find the news you're interested in
- Use export feature to save articles for later analysis

