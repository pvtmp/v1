# scraper.py
import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://receive-smss.com"

def create_enhanced_scraper():
    # Create a basic cloudscraper instance
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False},
    )
    # Then manually update headers
    custom_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://www.google.com/"
    }
    # Update the session headers
    scraper.headers.update(custom_headers)
    return scraper

# Create a single scraper session at the module level
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
    
    # <a href="/sms/13136399690/"> ...
    links = soup.select("a[href^='/sms/']")
    for link in links:
        href = link.get("href", "")
        if href.startswith("/sms/"):
            phone_str = href.replace("/sms/", "").replace("/", "").strip()
            # e.g., "13136399690"

            country_span = link.select_one(".number-boxes-item-country")
            country = country_span.get_text(strip=True) if country_span else "Unknown"
            
            number_data.append({
                "phone_number": phone_str,
                "country": country,
                "url": BASE_URL + href
            })
    
    # Remove duplicates if needed
    unique_numbers = {}
    for item in number_data:
        unique_numbers[item["phone_number"]] = item
    
    return list(unique_numbers.values())

def scrape_messages_for_number(phone_number: str):
    """
    Scrapes messages for /sms/<phone_number>/.
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
        time_div = row.select_one(".time")

        if not (msg_div and sender_div and time_div):
            continue

        message_text = msg_div.get_text(strip=True)
        sender_text  = sender_div.get_text(strip=True)
        time_text    = time_div.get_text(strip=True)

        # Remove "Message", "Sender", "Time" prefixes if they exist
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
