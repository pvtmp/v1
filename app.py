# app.py
from fastapi import FastAPI
from scraper import scrape_all_numbers, scrape_messages_for_number

app = FastAPI(title="Receive-SMSS Real-Time API (Cloudscraper, Older Version Compatible)")

@app.get("/")
def read_root():
    return {"message": "Cloudscraper-based real-time API is running."}

@app.get("/numbers")
def get_numbers():
    """
    Scrapes all phone numbers from the homepage and returns them in JSON format.
    """
    data = scrape_all_numbers()
    return {
        "count": len(data),
        "numbers": data
    }

@app.get("/numbers/{phone_number}")
def get_messages_by_phone(phone_number: str):
    """
    Scrapes messages for the given phone_number and returns them in JSON format.
    """
    msgs = scrape_messages_for_number(phone_number)
    return {
        "phone_number": phone_number,
        "message_count": len(msgs),
        "messages": msgs
    }
