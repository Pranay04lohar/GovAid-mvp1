Project Name: YojnaBuddy

YojnaBuddy is a web application that helps Indian citizens discover and access government welfare schemes and legal aid services. Many of these schemes are scattered across government portals, often without centralized access.


[Scraper]
    ↓
[schemes.json]
    ↓
[Frontend (React)]
    ↓
[Fuse.js client-side search]

Goal:
We are building a scraper to collect schemes listed on government websites (https://www.myscheme.gov.in/) into a structured JSON format. These will later be used in a searchable frontend app (using Fuse.js) to help users easily discover relevant schemes.

This scraper should:

- Extract scheme name, description, and URL
- Tag each scheme with "All India" as state (for now)
- Use simple HTML parsing (no JavaScript rendering for v1)
- Output data as `schemes.json`

The focus right now is **scraping and cleaning data** from https://www.myscheme.gov.in/.

Key URLs to Scrape

1. Main Search Page:
   https://www.myscheme.gov.in/search

- Contains paginated list of all 3,439+ schemes

  2.Category-specific Pages:
  https://www.myscheme.gov.in/find-scheme

- Access category-based scheme listings

3. State-specific Pages:
   https://www.myscheme.gov.in/search/state/{StateName}

- Example: https://www.myscheme.gov.in/search/state/Karnataka

4. Individual Scheme Pages:
   https://www.myscheme.gov.in/schemes/{scheme-id}

- Example: https://www.myscheme.gov.in/schemes/gshtn

Each page follows the structured format shown in search result

