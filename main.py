from dotenv import load_dotenv
import streamlit as st
import os
from apify_client import ApifyClient
import google.generativeai as genai
from datetime import datetime, timedelta
import re
import gspread
from google.oauth2.service_account import Credentials
import json

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
GOOGLE_SHEETS_CREDS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")  # JSON content or path to file

# Check env setup
if not GEMINI_API_KEY:
    st.error("Missing GEMINI_API_KEY in .env")
    st.stop()
if not APIFY_API_TOKEN:
    st.error("Missing APIFY_API_TOKEN in .env")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro"

# Initialize Google Sheets
def init_google_sheets():
    try:
        if not GOOGLE_SHEETS_CREDS:
            st.warning("Google Sheets credentials not found. Google Sheets functionality will be disabled.")
            return None
            
        if GOOGLE_SHEETS_CREDS.startswith('{'):
            # If credentials are provided as JSON string
            creds = Credentials.from_service_account_info(json.loads(GOOGLE_SHEETS_CREDS))
        else:
            # If credentials are provided as file path
            creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDS)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets initialization failed: {e}")
        return None

# Streamlit Page Setup
st.set_page_config(page_title="Gemini + Apify + Sheets Chatbot", page_icon="🤖")
st.title("🤖 Gemini + Apify + Sheets Chatbot")
st.caption("Chat with web-scraped data using Gemini and Apify MCP actors")

# Initialize Google Sheets client
sheets_client = init_google_sheets()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(MODEL_NAME)
    st.session_state.chat_session = model.start_chat(history=[])
if "last_scraped_data" not in st.session_state:
    st.session_state.last_scraped_data = None

# ---------------------------- Apify Configuration ---------------------------- #

MCP_CONFIG = {
    "instagram": {
        "actor_id": "apify/instagram-hashtag-scraper",
        "build_input": lambda query: {
            "hashtags": [query.split("#")[-1].strip()],
            "resultsLimit": 5
        }
    },
    "booking": {
        "actor_id": "voyager/booking-scraper",
        "build_input": lambda query: {
            "search": re.search(r'for\s+(.*)', query, re.IGNORECASE).group(1).strip() if re.search(r'for\s+', query) else "New York",
            "checkIn": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "checkOut": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "currency": "USD",
            "maxResults": 5
        }
    },
    "tripadvisor": {
        "actor_id": "curious_coder/tripadvisor-scraper",
        "build_input": lambda query: {
            "search": re.search(r'for\s+(.*)', query, re.IGNORECASE).group(1).strip() if re.search(r'for\s+', query) else "New York",
            "maxItems": 5,
            "category": "hotels",
            "language": "en",
            "currency": "USD"
        }
    },
    "googlemaps": {
        "actor_id": "compass/google-maps-reviews-scraper",
        "build_input": lambda query: {
            "startUrls": [{
                "url": f"https://www.google.com/maps/search/{re.search(r'for\s+(.*)', query, re.IGNORECASE).group(1).strip().replace(' ', '+') if re.search(r'for\s+', query) else 'New+York'}"
            }],
            "maxReviews": 10,
            "reviewerLanguage": "en",
            "region": "us",
            "includeHistogram": True,
            "includeReviewerName": True,
            "includeReviewerUrl": True,
            "includeReviewId": True,
            "includeReviewUrl": True,
            "includeResponseFromOwnerText": True,
            "includeReviewText": True,
            "includeReviewImages": False,
            "includeReviewRating": True
        }
    }
}

# ---------------------------- Functions ---------------------------- #

def run_apify_actor(actor_id, input_params):
    client = ApifyClient(APIFY_API_TOKEN)
    try:
        run = client.actor(actor_id).call(run_input=input_params)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        return dataset_items
    except Exception as e:
        st.error(f"Apify actor failed: {e}")
        return []

def format_data_general(data_items, max_items=5):
    """
    Generic formatter: creates structured text from a list of dicts
    """
    result = ""
    for idx, item in enumerate(data_items[:max_items]):
        result += f"\n🔹 **Item {idx + 1}:**\n"
        for key, value in item.items():
            if isinstance(value, (str, int, float)) and len(str(value)) < 500:
                result += f"• **{key}**: {value}\n"
        result += "\n"
    return result if result else "❌ No structured data found."

def format_booking_data(data_items, max_items=5):
    result = "🏨 **Hotel Results:**\n"
    for idx, item in enumerate(data_items[:max_items]):
        result += f"\n🔹 **{item.get('name', 'Unnamed Hotel')}**\n"
        rating = item.get('rating', {})
        if isinstance(rating, dict):
            rating_value = rating.get('value', 'N/A')
            rating_count = rating.get('reviewCount', 0)
        else:
            rating_value = rating
            rating_count = item.get('reviewCount', 0)
        result += f"• **Rating**: {rating_value}/10 ({rating_count} reviews)\n"
        price = item.get('price', {})
        if isinstance(price, dict):
            amount = price.get('amount', 'N/A')
            currency = price.get('currency', '')
        else:
            amount = price
            currency = ""
        result += f"• **Price**: {currency}{amount}\n"
        result += f"• **Address**: {item.get('address', 'N/A')}\n"
        result += f"• **URL**: [Booking Link]({item.get('url', '#')})\n"
    return result if result else "❌ No hotel data found."

def format_tripadvisor_data(data_items, max_items=5):
    result = "🗺️ **Tripadvisor Results:**\n"
    for idx, item in enumerate(data_items[:max_items]):
        result += f"\n🔹 **{item.get('title', 'Unnamed Place')}**\n"
        rating = item.get('rating', 'N/A')
        review_count = item.get('review_count', 0)
        result += f"• **Rating**: {rating}/5 ({review_count} reviews)\n"
        price = item.get('price', 'N/A')
        if price and isinstance(price, str):
            result += f"• **Price Level**: {price}\n"
        address = item.get('address', 'N/A')
        if isinstance(address, dict):
            address_str = ", ".join(filter(None, [
                address.get('street'),
                address.get('city'),
                address.get('state'),
                address.get('country')
            ]))
        else:
            address_str = str(address)
        result += f"• **Address**: {address_str}\n"
        url = item.get('url', '#')
        if url and not url.startswith('http'):
            url = f"https://www.tripadvisor.com{url}"
        result += f"• **URL**: [View on Tripadvisor]({url})\n"
    return result if result else "❌ No Tripadvisor data found."

def format_googlemaps_reviews(data_items, max_items=5):
    result = "📍 **Google Maps Reviews:**\n"
    if not data_items:
        return "❌ No reviews found."
    for idx, item in enumerate(data_items[:max_items]):
        if not isinstance(item, dict):
            continue
        result += f"\n🔹 **Review {idx + 1}**\n"
        place_name = item.get('placeName')
        result += f"• **Place**: {place_name if place_name else 'N/A'}\n"
        stars = item.get('stars')
        result += f"• **Rating**: {stars if stars is not None else 'N/A'}/5\n"
        reviewer = item.get('reviewerName')
        result += f"• **Reviewer**: {reviewer if reviewer else 'Anonymous'}\n"
        date = item.get('date')
        result += f"• **Date**: {date if date else 'N/A'}\n"
        review_text = item.get('text')
        if review_text:
            if len(review_text) > 200:
                review_text = review_text[:200] + "..."
            result += f"• **Review**: {review_text}\n"
        else:
            result += "• **Review**: No review text available\n"
        owner_response = item.get('responseFromOwnerText')
        if owner_response:
            if len(owner_response) > 150:
                owner_response = owner_response[:150] + "..."
            result += f"• **Owner Response**: {owner_response}\n"
        review_url = item.get('reviewUrl')
        if review_url:
            result += f"• **Full Review**: [View on Google Maps]({review_url})\n"
    return result if result.strip() != "📍 **Google Maps Reviews:**" else "❌ No valid reviews found."

def create_google_sheet(title, data):
    try:
        if not sheets_client:
            st.warning("Google Sheets client not initialized. Check your credentials.")
            return None
        if not data:
            st.warning("No data available to save to Google Sheets.")
            return None
        
        # Create a new spreadsheet
        spreadsheet = sheets_client.create(title)
        
        # Get the first worksheet
        worksheet = spreadsheet.get_worksheet(0)
        
        # Add headers from first data item's keys
        if data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            worksheet.append_row(headers)
        
        # Add data rows
        for item in data:
            if isinstance(item, dict):
                worksheet.append_row(list(item.values()))
        
        # Make the sheet publicly viewable (optional)
        spreadsheet.share(None, perm_type='anyone', role='reader')
        return spreadsheet.url
    except Exception as e:
        st.error(f"Failed to create Google Sheet: {e}")
        return None

def stream_handler(response_stream):
    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

# ---------------------------- Display Chat History ---------------------------- #

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ---------------------------- Chat Input ---------------------------- #

user_input = st.chat_input("💬 Ask or command...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    with st.chat_message("You"):
        st.markdown(user_input)

    # Check for Google Sheets creation command
    if "create google sheet" in user_input.lower() or "save to google sheets" in user_input.lower():
        if not st.session_state.last_scraped_data:
            result_text = "❌ No scraped data available to save. Please scrape data first."
        else:
            # Extract sheet title from command
            sheet_title = "Scraped Data"
            match = re.search(r'named\s+(.*)', user_input, re.IGNORECASE)
            if match:
                sheet_title = match.group(1).strip()
            elif "for" in user_input.lower():
                sheet_title = user_input.split("for")[-1].strip()
            
            sheet_url = create_google_sheet(sheet_title, st.session_state.last_scraped_data)
            if sheet_url:
                result_text = f"📊 **Google Sheet created**: [Open Sheet]({sheet_url})"
            else:
                result_text = "❌ Failed to create Google Sheet"
        
        with st.chat_message("Gemini"):
            st.markdown(result_text)
        st.session_state.chat_history.append(("Gemini", result_text))
    
    # Check for scraping commands
    else:
        matched_actor_key = None
        for key in MCP_CONFIG:
            if f"scrape {key}" in user_input.lower():
                matched_actor_key = key
                break

        if matched_actor_key:
            config = MCP_CONFIG[matched_actor_key]
            actor_id = config["actor_id"]
            input_builder = config["build_input"]
            input_data = input_builder(user_input)

            with st.spinner(f"🚀 Running {actor_id}..."):
                scraped_data = run_apify_actor(actor_id, input_data)
                st.session_state.last_scraped_data = scraped_data  # Store for Sheets
            
            if scraped_data:
                if matched_actor_key == "booking":
                    formatted_output = format_booking_data(scraped_data)
                elif matched_actor_key == "tripadvisor":
                    formatted_output = format_tripadvisor_data(scraped_data)
                elif matched_actor_key == "googlemaps":
                    formatted_output = format_googlemaps_reviews(scraped_data)
                else:
                    formatted_output = format_data_general(scraped_data)
                
                result_text = f"📊 **Results from {actor_id}:**\n{formatted_output}\n\n💡 You can now say 'create google sheet named [title]' to save this data"
            else:
                result_text = "❌ Could not fetch data."

            with st.chat_message("Gemini"):
                st.markdown(result_text)
            st.session_state.chat_history.append(("Gemini", result_text))
        
        # Regular Gemini chat
        else:
            with st.chat_message("Gemini"):
                with st.spinner("🤖 Thinking..."):
                    try:
                        response_stream = st.session_state.chat_session.send_message(user_input, stream=True)
                        full_response = st.write_stream(stream_handler(response_stream))
                        st.session_state.chat_history.append(("Gemini", full_response))
                    except Exception as e:
                        st.error(f"Gemini failed: {e}")