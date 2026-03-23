---
name: archive-source
description: Archive a web source to data/raw/ with metadata. Use when preserving DOR pages, clerk records, court cases, or any web source that might change or disappear.
argument-hint: <url> [optional-description]
---

# Archive Source

Fetch and archive a web page to `data/raw/` for reproducibility.

## Process

1. Create a filename from the URL domain + path + today's date (e.g., `revenue_ky_gov_purchaser_list_2026-03-21.html`)
2. Fetch the page content
3. Save the raw HTML to `data/raw/`
4. Create or append to `data/raw/source_manifest.csv` with these fields:
   - `url`: original URL
   - `filename`: local filename
   - `fetch_date`: ISO date
   - `description`: user-provided or inferred description
   - `sha256`: hash of the saved file
5. Print confirmation with the local path and hash

## Rules

- Never modify raw archived files after saving
- If the URL has already been archived today, skip and report the existing file
- If the page requires JavaScript to render, note this in the manifest and suggest using a browser-based approach
- Respect robots.txt — check before fetching
