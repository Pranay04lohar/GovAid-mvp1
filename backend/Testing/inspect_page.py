import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint

def inspect_page(url: str):
    """Inspect the HTML structure of a scheme page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print the page title to verify we got the right page
        print("\nPage Title:", soup.title.string if soup.title else "No title found")
        
        # Find all main sections
        print("\nMain Sections:")
        for section in soup.find_all(['section', 'div'], class_=True):
            print(f"\nSection: {section.get('class', ['No class'])[0]}")
            print("Content preview:", section.text[:100].strip())
        
        # Find all headings
        print("\nHeadings Structure:")
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            print(f"{heading.name}: {heading.text.strip()}")
        
        # Find all lists
        print("\nLists:")
        for lst in soup.find_all(['ul', 'ol']):
            print(f"\nList class: {lst.get('class', ['No class'])[0]}")
            print("First few items:")
            for item in lst.find_all('li')[:3]:
                print(f"- {item.text.strip()}")
        
        # Save the HTML structure to a file for detailed inspection
        with open('page_structure.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\nFull HTML structure saved to page_structure.html")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Example scheme URL - replace with an actual scheme URL from myscheme.gov.in
    test_url = "https://www.myscheme.gov.in/schemes/gshtn"  # This is an example URL
    inspect_page(test_url) 