# app.py
import os
from fastapi import FastAPI, Request, HTTPException, status, Depends
from usage_stats import record_usage, get_usage_stats
from scraper import scrape_all_numbers, scrape_messages_for_number, update_zenrows_key

app = FastAPI(title="Receive-SMSS Real-Time API (with Admin Panel)")

# A mock admin token
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "mySecret123")

def verify_admin_token(token: str):
    """
    A simple dependency function to verify the admin token
    """
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token"
        )
    return True

@app.get("/")
def home():
    return {"message": "Welcome to the real-time scraping API!"}

@app.get("/numbers")
def get_numbers(request: Request):
    # Log usage
    record_usage(f"{request.method} {request.url.path}")
    data = scrape_all_numbers()
    return {"count": len(data), "numbers": data}

@app.get("/numbers/{phone_number}")
def get_messages_by_phone(phone_number: str, request: Request):
    record_usage(f"{request.method} {request.url.path}")
    msgs = scrape_messages_for_number(phone_number)
    return {
        "phone_number": phone_number,
        "message_count": len(msgs),
        "messages": msgs
    }

# ----------------
#  ADMIN ROUTES
# ----------------

@app.get("/admin", tags=["admin"])
def admin_panel(token: str, verified: bool = Depends(verify_admin_token)):
    """
    Basic admin endpoint to show usage.
    Access example: GET /admin?token=mySecret123
    """
    usage = get_usage_stats()
    return {
        "message": "Admin Panel",
        "usage_stats": usage
    }

@app.post("/admin/set-zenrows-key", tags=["admin"])
def admin_set_zenrows_key(new_key: str, token: str = "", verified: bool = Depends(verify_admin_token)):
    """
    Let the admin update the ZenRows key at runtime
    e.g. POST /admin/set-zenrows-key?token=mySecret123 with JSON body {"new_key": "abc123"}
    """
    update_zenrows_key(new_key)
    return {"message": "ZenRows API key updated", "new_key": new_key}
