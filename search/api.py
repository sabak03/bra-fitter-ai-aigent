"""
Bra Fit Search AI Agent - Search API

This module provides a FastAPI backend service for retrieving bra products
from trusted retailers based on user selected size and style.

Key features:
- Accepts size and optional style parameters via HTTP requests
- Scrapes or queries trusted retailer websites (Bravissimo)
- Normalises product data into a consistent format
- Returns structured JSON responses for the frontend
- Intergrated with Streamlit frontend search.py (user interface)

Technologies:
- FastAPI (API layer)
- Requests + BeautifulSoup (data extraction)
"""

from fastapi import FastAPI, Query 
from pydantic import BaseModel 
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

class Product(BaseModel):
    retailer: str
    title: str
    size: str
    style: Optional[str] = None
    price: Optional[str] = None
    url: str
    image: Optional[str] = None
    rating: Optional[str] = None

STYLE_URLS = {
    "any": "https://www.bravissimo.com/shop-by/size/{sizeSlug}/",
    "plunge": "https://www.bravissimo.com/shop-by/size/{sizeSlug}?limit=48&page=1&sortBy=default&f_type[]=Plunge%20Bra",
    "full cup": "https://www.bravissimo.com/shop-by/size/{sizeSlug}?limit=48&page=1&sortBy=default&f_type[]=Full%20Cup%20Bra",
    "non-wired": "https://www.bravissimo.com/shop-by/size/{sizeSlug}?limit=48&page=1&sortBy=default&f_type[]=Non%20Wired%20Bra",
    "balconette": "https://www.bravissimo.com/shop-by/size/{sizeSlug}?limit=48&page=1&sortBy=default&f_type[]=Balconette%20Bra",
    "comfort": "https://www.bravissimo.com/collections/ultimate-comfort-collection/{sizeSlug}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def size_to_slug(size: str) -> str:
    return f"{size.lower()}-bras"

def pick_url(size: str, style: Optional[str]) -> str:
    sizeSlug = size_to_slug(size)
    if not style:
        style = "Any"
    styleKey = style.strip().lower()
    template = STYLE_URLS.get(styleKey, STYLE_URLS["any"])
    return template.format(sizeSlug=sizeSlug)

def text_mentions_size(text: str, size: str) -> bool:
    return size.lower() in text.lower()

def search_bravissimo(size: str, style: Optional[str] = None) -> List[dict]:
    """
    Scrape Bravissimo website for products matching size and style. (BeautifulSoup)

    Builds a search URL based on user input, extracts product links,
    and returns cleaned product data.

    - Only trusted product URLs are included
    - Results are deduplicated and limited
    """
    url = pick_url(size, style)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Request failed:", e)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        if "/products/" not in href:
            continue
        if not text:
            continue
        product_url = href if href.startswith("http") else f"https://www.bravissimo.com{href}"

        results.append({
            "retailer": "Bravissimo",
            "title": text[9:120],
            "size": size,
            "style": style,
            "price": None,
            "url": product_url,
        })
    seen = set()
    unique = []
    for item in results:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique[:12]

@app.get("/search-bras", response_model=List[Product])
def search_bras(size: str = Query(..., description="Bra size like 30KK"), style: Optional[str] = Query(None, description="Style like Full cup")):
    """
    Search for bras based on size and optional style.

    This endpoint retrieves products from trusted retailer,
    filters relevant results, and returns a standardised list
    of product data.

    Args:
        size (str): Bra size (e.g. "30KK")
        style (Optional[str]): Style preference (e.g. "Full cup")

    Returns:
        List[Product]: A list of matching bra products with
                       retailer, title, price, and URL
    """
    try:
        return search_bravissimo(size, style)
    except Exception as e:
        print("ERROR:", e)
        return []
    
@app.get("/")
def root():
    return {"status": "ok"}