"""
Fayette County Land Records Scraper (httpx session replay)
============================================================
Scrapes delinquent tax instruments from fayettedeeds.com/landrecords using
direct HTTP requests — no browser automation required.

Flow:
  1. GET index.php  → PHPSESSID
  2. POST davidson_form with party + instrument filters → pick list
  3. POST ajaxActions.php?action=storeEID  for each name in pick list
  4. POST ajaxActions.php?action=checkEID  to verify
  5. POST index.php with pickListForm data  → results table

Column order in results table (verified from live HTML):
  0: checkbox   1: Book/Page   2: Recording date   3: Grantor
  4: Grantee    5: Instrument type   6: Property description
  7: Cross-references   8: Consideration   9: Image links

Usage:
  python scripts/scrape_land_records.py --grantee "KY LIEN HOLDINGS"
  python scripts/scrape_land_records.py --grantor "KY LIEN HOLDINGS"
  python scripts/scrape_land_records.py --both "RAMEY"
  python scripts/scrape_land_records.py --grantee "KY LIEN HOLDINGS" --start 01/01/2016 --end 12/31/2018

Outputs:
  data/raw/land_records/<slug>/results_<slug>.html   — raw results HTML
  data/raw/land_records/<slug>/picklist_<slug>.html  — raw pick list HTML
  data/interim/land_records_<slug>.csv               — parsed instruments
  data/interim/land_records_all.csv                  — merged across all runs
"""

import argparse
import csv
import hashlib
import json
import logging
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "land_records"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
LOG_FILE = INTERIM_DIR / "land_records_log.jsonl"

RAW_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://www.fayettedeeds.com/landrecords"
THROTTLE = 2.5

# Verified instrument doc type codes (confirmed from live page HTML)
INSTRUMENT_CODES = {
    "CERT_DEL_ASSIGN":  "071",   # CERT DEL ASSIGN
    "REASSIGN":         "073",   # REASSIGN CERTIFICATE OF DEL
    "DEL_TAX_RELEASE":  "072",   # DEL TAX RELEASE
    "3RD_PTY_TAX_REL":  "056",   # 3RD PTY TAX REL
    "IN_HOUSE_REL":     "028",   # IN HOUSE REL
}
ALL_TYPES = list(INSTRUMENT_CODES.keys())

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
AJAX_HEADERS = {**HEADERS, "X-Requested-With": "XMLHttpRequest"}

FIELDS = [
    "instrument_number", "book_page", "recording_date",
    "grantor", "grantee", "instrument_type",
    "property_description", "cross_references", "consideration",
    "query_party", "query_name", "query_start", "query_end",
    "scrape_date", "source_url", "notes",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def log_event(event: str, **kwargs):
    entry = {"ts": datetime.utcnow().isoformat(), "event": event, **kwargs}
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def save_html(html: str, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    sha = hashlib.sha256(html.encode()).hexdigest()[:12]
    log.debug(f"Saved {path.name} ({len(html):,} bytes, sha:{sha})")
    return sha


# ---------------------------------------------------------------------------
# Parsing: pick list
# ---------------------------------------------------------------------------
def parse_pick_list(html: str) -> list[dict]:
    """Return list of {name, count} dicts from pick list table."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="plresults")
    if not table:
        return []
    entries = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue
        cb = row.find("input", type="checkbox")
        if not cb:
            continue
        value = cb.get("value", "")  # e.g. "KY LIEN HOLDINGS LLC:"
        # Count is in last cell
        text = row.get_text(" ", strip=True)
        count_match = re.search(r"(\d+)\s*$", text)
        count = int(count_match.group(1)) if count_match else 0
        # Split value on ":" — lastname:firstname
        parts = value.split(":", 1)
        lastname = parts[0].strip()
        firstname = parts[1].strip() if len(parts) > 1 else ""
        entries.append({"lastname": lastname, "firstname": firstname, "count": count})
    return entries


# ---------------------------------------------------------------------------
# Parsing: results table
# ---------------------------------------------------------------------------
def parse_results(html: str) -> list[dict]:
    """
    Parse the results table from the index list page.

    Verified column order (0-indexed):
      0=checkbox  1=Book/Page  2=Date  3=Grantor  4=Grantee
      5=InstType  6=PropDesc   7=CrossRef  8=Consideration  9=Image
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="results")
    if not table:
        log.warning("No #results table found in page")
        return []

    records = []
    rows = table.find_all("tr")
    # First row is usually the "limited to 1000 records" warning banner — skip non-data rows
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        book_page  = cells[1].get_text(strip=True)
        rec_date   = cells[2].get_text(strip=True)
        grantor    = cells[3].get_text(strip=True)
        grantee    = cells[4].get_text(strip=True)
        inst_type  = cells[5].get_text(strip=True)
        prop_desc  = cells[6].get_text(strip=True) if len(cells) > 6 else ""
        cross_ref  = cells[7].get_text(strip=True) if len(cells) > 7 else ""
        consider   = cells[8].get_text(strip=True) if len(cells) > 8 else ""

        # Skip header rows or empty rows
        if not rec_date or not grantor:
            continue

        # Extract instrument number from cross_ref if possible (format: "BOOK/PAGE-CODE")
        # Or derive from book/page
        inst_match = re.search(r"(\d{10,})", cross_ref)
        if inst_match:
            inst_num = inst_match.group(1)
        else:
            # Use book+page as surrogate key (not perfect but unique enough)
            bp = re.sub(r"\D+", "_", book_page).strip("_")
            inst_num = f"bp_{bp}"

        records.append({
            "instrument_number": inst_num,
            "book_page": book_page,
            "recording_date": rec_date,
            "grantor": grantor,
            "grantee": grantee,
            "instrument_type": inst_type,
            "property_description": prop_desc,
            "cross_references": cross_ref,
            "consideration": consider,
        })

    if len(records) >= 999:
        log.warning(f"*** NEAR LIMIT: {len(records)} records — results may be truncated. Narrow date range.")

    return records


# ---------------------------------------------------------------------------
# Core search function
# ---------------------------------------------------------------------------
def search(
    client: httpx.Client,
    name: str,
    party: str,           # "grantor" | "grantee" | "both"
    instrument_types: list[str],
    start_date: str = "",
    end_date: str = "",
    slug: str = "",
) -> list[dict]:
    """Execute one complete search and return parsed records."""

    raw_dir = RAW_DIR / (slug or slugify(f"{party}_{name}"))
    raw_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    # --- Step 1: GET to acquire session ---
    r = client.get(f"{BASE_URL}/index.php", timeout=30)
    r.raise_for_status()
    time.sleep(THROTTLE)

    # --- Step 2: POST davidson_form ---
    codes = [INSTRUMENT_CODES[t] for t in instrument_types if t in INSTRUMENT_CODES]

    if party == "grantor":
        search_type = "Specified"
        party_type = "0"
        form_name_fields = {
            "grantor_last_name": name, "grantor_first_name": "", "grantor_middle_initial": "",
            "grantee_last_name": "", "grantee_first_name": "", "grantee_middle_initial": "",
        }
    elif party == "grantee":
        search_type = "Specified"
        party_type = "1"
        form_name_fields = {
            "grantor_last_name": "", "grantor_first_name": "", "grantor_middle_initial": "",
            "grantee_last_name": name, "grantee_first_name": "", "grantee_middle_initial": "",
        }
    else:  # both
        search_type = "Both"
        party_type = ""
        form_name_fields = {
            "both_last_name": name, "both_first_name": "", "both_middle_initial": "",
            "grantor_last_name": "", "grantor_first_name": "", "grantor_middle_initial": "",
            "grantee_last_name": "", "grantee_first_name": "", "grantee_middle_initial": "",
        }

    doc_type_fields = {f"instDocType[$k][{c}]": c for c in codes}

    form = {
        "searchType": "davidson",
        "show_pick_list": "off",
        "party_type": party_type,
        "search_type": search_type,
        **form_name_fields,
        "start_date": start_date,
        "end_date": end_date,
        **doc_type_fields,
    }

    log.info(f"  Posting search: {party}={name!r}, types={instrument_types}, dates={start_date}–{end_date}")
    r2 = client.post(f"{BASE_URL}/index.php", data=form, timeout=60)
    r2.raise_for_status()
    save_html(r2.text, raw_dir / f"picklist_{slug}.html")
    time.sleep(THROTTLE)

    # --- Step 3: Parse pick list ---
    entries = parse_pick_list(r2.text)
    if not entries:
        log.info("  No pick list entries found — no matching names")
        return []

    log.info(f"  Pick list: {len(entries)} entries")
    for e in entries:
        log.info(f"    {e['lastname']!r} {e['firstname']!r} — {e['count']} records")

    # --- Step 4: storeEID for each name ---
    for e in entries:
        r3 = client.post(
            f"{BASE_URL}/ajaxActions.php",
            data={"action": "storeEID", "lastname": e["lastname"], "firstname": e["firstname"]},
            headers=AJAX_HEADERS,
            timeout=15,
        )
        log.debug(f"  storeEID {e['lastname']!r}: {r3.status_code} {r3.text[:50]!r}")
        time.sleep(0.5)

    # --- Step 5: checkEID ---
    r4 = client.post(
        f"{BASE_URL}/ajaxActions.php",
        data={"action": "checkEID"},
        headers=AJAX_HEADERS,
        timeout=15,
    )
    log.debug(f"  checkEID: {r4.status_code} {r4.text[:50]!r}")
    time.sleep(1)

    # --- Step 6: POST pickListForm to get results ---
    pick_form = {
        "searchType": "name",
        "start_date": start_date,
        "end_date": end_date,
        "sort_type": "",
        "search_type": search_type,
        "last_name": "",
        "party_type": party_type,
        "entity_type": "",
        "Unit": "",
        "Zip": "",
    }
    r5 = client.post(f"{BASE_URL}/index.php", data=pick_form, timeout=120)
    r5.raise_for_status()
    save_html(r5.text, raw_dir / f"results_{slug}.html")
    time.sleep(THROTTLE)

    # --- Step 7: Parse results ---
    records = parse_results(r5.text)
    log.info(f"  Parsed {len(records)} records")

    # Enrich with query metadata
    for rec in records:
        rec["query_party"] = party
        rec["query_name"] = name
        rec["query_start"] = start_date
        rec["query_end"] = end_date
        rec["scrape_date"] = today
        rec["source_url"] = f"{BASE_URL}/index.php"
        rec.setdefault("notes", "")
        for f in FIELDS:
            rec.setdefault(f, "")

    log_event("search_complete", party=party, name=name, count=len(records))
    return records


# ---------------------------------------------------------------------------
# Save / merge
# ---------------------------------------------------------------------------
def save_csv(records: list[dict], slug: str) -> Path:
    path = INTERIM_DIR / f"land_records_{slug}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    log.info(f"  Saved {len(records)} records → {path.name}")
    return path


def merge_all():
    paths = sorted(INTERIM_DIR.glob("land_records_*.csv"))
    # Exclude the merged file itself
    paths = [p for p in paths if p.name != "land_records_all.csv"]
    all_rows = []
    seen = set()
    for p in paths:
        with p.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = (row.get("book_page"), row.get("grantor"), row.get("grantee"), row.get("instrument_type"))
                if key not in seen:
                    seen.add(key)
                    all_rows.append(row)
    out = INTERIM_DIR / "land_records_all.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    log.info(f"Merged {len(all_rows)} unique records → {out.name}")
    return all_rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--grantee", help="Search as grantee (lien purchaser)")
    group.add_argument("--grantor", help="Search as grantor (assigning party)")
    group.add_argument("--both", help="Search both grantor and grantee")
    parser.add_argument("--start", default="", help="Start date MM/DD/YYYY")
    parser.add_argument("--end", default="", help="End date MM/DD/YYYY")
    parser.add_argument("--types", nargs="+", choices=ALL_TYPES, default=ALL_TYPES)
    args = parser.parse_args()

    if args.grantee:
        name, party = args.grantee, "grantee"
    elif args.grantor:
        name, party = args.grantor, "grantor"
    else:
        name, party = args.both, "both"

    slug = slugify(f"{party}_{name}_{args.start}_{args.end}")

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60) as client:
        records = search(
            client, name=name, party=party,
            instrument_types=args.types,
            start_date=args.start, end_date=args.end,
            slug=slug,
        )

    if records:
        save_csv(records, slug)
        from collections import Counter
        by_type = Counter(r["instrument_type"] for r in records)
        log.info("\nBy instrument type:")
        for t, n in by_type.most_common():
            log.info(f"  {n:4d}  {t}")

    merge_all()
    log.info("Done.")


if __name__ == "__main__":
    main()
