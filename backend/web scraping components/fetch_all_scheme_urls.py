import httpx
import asyncio
import json
import os
from playwright.async_api import async_playwright
import re

API_URL = "https://api.myscheme.gov.in/search/v4/schemes"
CATEGORIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "categories.json")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

# Helper to clean category names for filenames
def clean_filename(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

async def get_x_api_key():
    api_key = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_request(request):
            nonlocal api_key
            headers = request.headers
            if "x-api-key" in headers:
                api_key = headers["x-api-key"]
                
        page.on("request", handle_request)
        await page.goto("https://www.myscheme.gov.in")
        await page.wait_for_timeout(2000)  # Wait for API calls
        await browser.close()
        
    if not api_key:
        raise Exception("Failed to extract x-api-key")
    return api_key

async def fetch_category_scheme_urls(category, num_schemes, output_file, api_key):
    all_urls = set()
    offset = 0
    size = 20  # Fetch 20 at a time for efficiency
    tried_alternate = False
    orig_category = category
    
    print(f"\nFetching schemes for category: {category} (up to {num_schemes})")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        while len(all_urls) < num_schemes:
            try:
                # Format query exactly as seen in browser
                query = [{"identifier": "schemeCategory", "value": category}]
                params = {
                    "lang": "en",
                    "q": json.dumps(query),
                    "keyword": "",
                    "sort": "",
                    "from": str(offset),
                    "size": str(size)
                }
                
                headers = {
                    "x-api-key": api_key,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/138.0",
                    "Origin": "https://www.myscheme.gov.in",
                    "Referer": "https://www.myscheme.gov.in/",
                    "Accept": "application/json, text/plain, */*"
                }
                
                print(f"\nMaking API request with params: {params}")
                resp = await client.get(API_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                # Check if we got a successful response
                if data.get("status") != "Success":
                    print(f"API returned error: {data.get('errorDescription')}")
                    break
                
                # Extract scheme URLs from the response
                if "data" in data and "hits" in data["data"] and "items" in data["data"]["hits"]:
                    items = data["data"]["hits"]["items"]
                    if not items:
                        if not tried_alternate and orig_category == "Agriculture, Rural & Environment":
                            print("No items found, trying alternate category name without space after comma...")
                            category = "Agriculture,Rural & Environment"
                            tried_alternate = True
                            offset = 0
                            continue
                        print("No more items found")
                        break
                        
                    for item in items:
                        if "fields" in item and "slug" in item["fields"]:
                            slug = item["fields"]["slug"]
                            url = f"https://www.myscheme.gov.in/schemes/{slug}"
                            all_urls.add(url)
                    
                    print(f"Fetched {len(items)} schemes at offset {offset} (total: {len(all_urls)})")
                    
                    if len(items) < size:
                        print("Received fewer items than requested, stopping pagination")
                        break
                        
                    offset += size
                else:
                    print("Unexpected API response structure. Keys found:", list(data.keys()))
                    print(json.dumps(data, indent=2)[:1000] + "...")
                    break
                    
            except Exception as e:
                print(f"Error fetching schemes: {e}")
                break
    
    # Save only up to num_schemes
    urls_to_save = list(all_urls)[:num_schemes]
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(urls_to_save, f, indent=2)
    
    print(f"Saved {len(urls_to_save)} scheme URLs to {output_file}")
    return urls_to_save

async def main():
    try:
        print("Extracting x-api-key...")
        api_key = await get_x_api_key()
        print(f"Extracted x-api-key: {api_key}")
        # Load categories
        with open(CATEGORIES_FILE, "r") as f:
            categories = json.load(f)
        for cat in categories:
            name = cat["name"]
            num = cat["num_schemes"]
            filename = os.path.join(OUTPUT_DIR, f"{clean_filename(name)}_urls.json")
            await fetch_category_scheme_urls(name, num, filename, api_key)
        
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 