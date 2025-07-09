
# 🤖 Gemini MCP Streamlit Chatbot

A powerful Streamlit web application that combines Google's Gemini AI with Apify web scraping actors and Google Sheets integration. This chatbot can scrape real-time data from various sources and provide intelligent responses using Gemini's AI capabilities.

## ✨ Features

- **🤖 AI-Powered Chat**: Chat with Google's Gemini 1.5 Pro model
- **🌐 Web Scraping**: Integrate with Apify actors for real-time data extraction
- **📊 Google Sheets Integration**: Automatically save scraped data to Google Sheets
- **🎯 Multiple Data Sources**: Support for Instagram, Booking.com, Tripadvisor, and Google Maps
- **💬 Interactive Interface**: Clean Streamlit-based chat interface
- **📈 Data Export**: Easy export of scraped data to Google Sheets

## 🚀 Supported Scraping Sources

| Source | Command | Description |
|--------|---------|-------------|
| **Instagram** | `scrape instagram #hashtag` | Scrape Instagram posts by hashtag |
| **Booking.com** | `scrape booking for [location]` | Find hotel deals and prices |
| **Tripadvisor** | `scrape tripadvisor for [location]` | Get restaurant/hotel reviews |
| **Google Maps** | `scrape googlemaps for [place]` | Extract Google Maps reviews |

## 📋 Prerequisites

- Python 3.13 or higher
- Google Gemini API key
- Apify API token
- Google Sheets service account credentials (optional)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gemini-mcp-streamlit.git
   cd gemini-mcp-streamlit
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   APIFY_API_TOKEN=your_apify_token_here
   GOOGLE_SHEETS_CREDENTIALS=your_google_sheets_json_credentials
   ```

## 🔑 API Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Apify API
1. Sign up at [Apify](https://apify.com/)
2. Go to Account Settings → Integrations → API tokens
3. Create a new token
4. Add it to your `.env` file as `APIFY_API_TOKEN`

### Google Sheets (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create a service account and download JSON credentials
5. Add the JSON content to your `.env` file as `GOOGLE_SHEETS_CREDENTIALS`

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8501`

3. **Start chatting!**
   - Ask general questions to Gemini
   - Use scraping commands to get real-time data
   - Export data to Google Sheets

## 💬 Example Commands

### General Chat
```
What's the weather like today?
Tell me a joke
Explain quantum computing
```

### Web Scraping
```
scrape instagram #travel
scrape booking for Paris
scrape tripadvisor for Italian restaurants in New York
scrape googlemaps for coffee shops in San Francisco
```

### Data Export
```
create google sheet named "Travel Data"
save to google sheets for my vacation research
```

## 📊 Data Format

The application automatically formats scraped data for easy reading:

- **Instagram**: Posts with captions, likes, comments, and URLs
- **Booking.com**: Hotels with ratings, prices, addresses, and booking links
- **Tripadvisor**: Places with ratings, reviews, addresses, and links
- **Google Maps**: Reviews with ratings, reviewer names, dates, and full review text

## 🔧 Configuration

You can customize the scraping behavior by modifying the `MCP_CONFIG` in `main.py`:

```python
MCP_CONFIG = {
    "instagram": {
        "actor_id": "apify/instagram-hashtag-scraper",
        "build_input": lambda query: {
            "hashtags": [query.split("#")[-1].strip()],
            "resultsLimit": 5  # Adjust number of results
        }
    },
    # ... other configurations
}
```

## 📁 Project Structure

```
gemini-mcp-streamlit/
├── main.py              # Main Streamlit application
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── README.md           # This file
├── .env               # Environment variables (create this)
└── .gitignore         # Git ignore rules
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for the AI capabilities
- [Apify](https://apify.com/) for web scraping actors
- [Streamlit](https://streamlit.io/) for the web interface
- [Google Sheets API](https://developers.google.com/sheets/api) for data export

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set in `.env`
2. **Google Sheets Error**: Check that your service account has proper permissions
3. **Apify Actor Failures**: Verify your Apify token and check actor availability
4. **Python Version**: Make sure you're using Python 3.13 or higher

### Getting Help

If you encounter any issues:
1. Check the console output for error messages
2. Verify your API keys and credentials
3. Ensure all dependencies are installed correctly
4. Open an issue on GitHub with detailed error information

---

**Happy Scraping! 🚀**
