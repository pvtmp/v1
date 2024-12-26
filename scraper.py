# scraper.py
import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://receive-smss.com"

# We'll pretend we have a "zenrows_api_key" that might be updated by admin
zenrows_api_key = "YOUR_INITIAL_API_KEY"

def create_enhanced_scraper():
    """
    Create and return a Cloudscraper instance with any custom headers or logic.
    In a real scenario, you'd pass your zenrows_api_key if it changes the request URL or headers.
    """
    scraper = cloudscraper.create_scraper(
        # minimal config; in older versions you can't pass requestHeader or request_kwargs directly
        # We'll just return a base instance
    )
    return scraper

# Create a single, module-level scraper session
scraper = create_enhanced_scraper()

def scrape_all_numbers():
    """
    Scrape the homepage for all available phone numbers.
    Returns a list of dicts: [{phone_number, country, url}, ...]
    """
    resp = scraper.get(BASE_URL, timeout=20)
    if resp.status_code != 200:
        print(f"[scrape_all_numbers] Error: HTTP {resp.status_code}")
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")

    number_data = []
    # Each phone number block might be: <a href="/sms/13136399690/">
    # We'll also parse the country from .number-boxes-item-country or .number-boxess-item-country
    links = soup.select("a[href^='/sms/']")
    for link in links:
        href = link.get("href", "")
        if not href.startswith("/sms/"):
            continue
        
        phone_str = href.replace("/sms/", "").replace("/", "").strip()

        # Combine the two classes for country:
        country_span = link.select_one(".number-boxes-item-country, .number-boxess-item-country")
        if country_span:
            country_name = country_span.get_text(strip=True)
        else:
            country_name = "Unknown"
        
        number_data.append({
            "phone_number": phone_str,
            "country": country_name,
            "url": BASE_URL + href
        })

    # Optionally remove duplicates
    unique = {}
    for item in number_data:
        unique[item["phone_number"]] = item
    
    return list(unique.values())

def scrape_messages_for_number(phone_number: str):
    """
    Scrapes messages for a given phone_number (e.g. '13136399690').
    Returns a list of dicts: [{message, sender, time}, ...]
    """
    url = f"{BASE_URL}/sms/{phone_number}/"
    resp = scraper.get(url, timeout=20)
    if resp.status_code != 200:
        print(f"[scrape_messages_for_number] Error: HTTP {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select(".row.message_details")

    messages = []
    for row in rows:
        msg_div = row.select_one(".msgg")
        sender_div = row.select_one(".senderr")
        time_div   = row.select_one(".time")

        if not (msg_div and sender_div and time_div):
            continue
        
        message_text = msg_div.get_text(strip=True)
        sender_text  = sender_div.get_text(strip=True)
        time_text    = time_div.get_text(strip=True)

        # Remove "Message", "Sender", "Time" if present
        if message_text.startswith("Message"):
            message_text = message_text[len("Message"):].strip()
        if sender_text.startswith("Sender"):
            sender_text = sender_text[len("Sender"):].strip()
        if time_text.startswith("Time"):
            time_text = time_text[len("Time"):].strip()

        messages.append({
            "message": message_text,
            "sender": sender_text,
            "time": time_text
        })

    return messages

def update_zenrows_key(new_key: str):
    """
    Example function: update the global zenrows_api_key.
    In real code, you'd re-initialize the scraper or store the key in a .env
    """
    global zenrows_api_key
    zenrows_api_key = new_key
    # you might also re-create the scraper if it depends on that key
    # scraper = create_enhanced_scraper()
