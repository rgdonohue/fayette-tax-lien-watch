"""
Fayette County Delinquent Tax Bill Scraper
==========================================
Scrapes the delinquent tax bill search at fayettedeeds.com.

Usage:
    python scripts/scrape_delinquent_bills.py --years 2020 2021 2022
    python scripts/scrape_delinquent_bills.py --years 2016 2017 2018 2019 2020 2021 2022 2023 2024
    python scripts/scrape_delinquent_bills.py --years 2024 --dry-run

Outputs:
    data/raw/delinquent/<year>/list_<year>.html     - raw list page HTML
    data/raw/delinquent/<year>/detail_<instnum>.html - raw detail page HTML
    data/interim/delinquent_bills_<year>.csv         - parsed bills for that year
    data/interim/delinquent_bills_all.csv            - combined across all scraped years
    data/interim/scrape_log.jsonl                    - structured log of every request
"""

import argparse
import csv
import hashlib
import json
import logging
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "delinquent"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
LOG_FILE = INTERIM_DIR / "scrape_log.jsonl"

RAW_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://www.fayettedeeds.com/delinquent"
LIST_URL = f"{BASE_URL}/index.php"
DETAIL_URL = f"{BASE_URL}/details.php"
THROTTLE_SECONDS = 2.5  # between each request

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# Fields emitted per record
BILL_FIELDS = [
    "inst_num",
    "bill_number",
    "tax_year",
    "status",
    "property_address",
    "purchaser_list",      # from list page (may be abbreviated)
    "owner_name",
    # -- from detail page --
    "face_value",
    "amount_paid",
    "parcel_num",
    "assigned",
    "purchaser_detail",
    "purchaser_address",
    "district",
    "date_paid",
    "paid_by",
    "assessment",
    "owed_at_sale",
    "amount_due",
    "bankruptcy",
    "exonerated",
    "date_exonerated",
    "released",
    "date_released",
    "sold",
    # -- metadata --
    "detail_url",
    "scrape_date",
    "detail_fetched",
    "notes",
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


def log_request(event: str, url: str, status: int, elapsed: float, extra: dict = None):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "event": event,
        "url": url,
        "status": status,
        "elapsed_ms": round(elapsed * 1000),
        **(extra or {}),
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def fetch(client: httpx.Client, url: str, params: dict = None, retries: int = 3) -> httpx.Response:
    for attempt in range(1, retries + 1):
        try:
            r = client.get(url, params=params, timeout=30)
            log_request("fetch", str(r.url), r.status_code, r.elapsed.total_seconds())
            r.raise_for_status()
            return r
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            wait = 30 * attempt
            log.warning(f"Attempt {attempt}/{retries} failed for {url}: {e}. Waiting {wait}s.")
            if attempt == retries:
                raise
            time.sleep(wait)


def save_html(html: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    sha = hashlib.sha256(html.encode()).hexdigest()[:12]
    log.debug(f"Saved {path.name} (sha256:{sha})")


# ---------------------------------------------------------------------------
# Parsing: list page
# ---------------------------------------------------------------------------
def parse_list_page(html: str, tax_year: int) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    # BeautifulSoup lowercases attribute names; the site uses InstNum="..." in HTML
    rows = soup.select("table tr[instnum]")

    if not rows:
        # Check for "no records" message
        if "no results" in html.lower() or "no records" in html.lower():
            log.info(f"  No records found for {tax_year}")
            return []
        log.warning(f"  No <tr instnum=...> rows found for {tax_year}. Page may have changed.")
        return []

    records = []
    for row in rows:
        inst_num = row.get("instnum", "").strip()  # lowercase after BS4 normalization
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        bill_number = cells[0].get_text(strip=True)
        year = cells[1].get_text(strip=True)
        status = cells[2].get_text(strip=True)
        description = cells[3].get_text(strip=True)

        # Purchaser cell may contain phone/email links
        purch_cell = cells[4]
        purchaser_text = purch_cell.get_text(" ", strip=True).strip()

        owner = cells[5].get_text(strip=True)

        records.append({
            "inst_num": inst_num,
            "bill_number": bill_number,
            "tax_year": year or str(tax_year),
            "status": status,
            "property_address": description,
            "purchaser_list": purchaser_text,
            "owner_name": owner,
        })

    log.info(f"  Parsed {len(records)} records from list page.")

    # The delinquent tax search has no confirmed hard cap (2023 returned 2166+ records).
    # The land records search caps at ~999. Flag anything at exactly 999 for manual review.
    if len(records) == 999:
        log.warning(
            f"  *** POSSIBLE TRUNCATION: {tax_year} returned exactly 999 records. "
            "This may be a site-imposed cap. Cross-check against DOR county totals."
        )

    return records


# ---------------------------------------------------------------------------
# Parsing: detail page
# ---------------------------------------------------------------------------
def parse_detail_page(html: str, inst_num: str) -> dict:
    """
    Detail page structure: three tables, each with a header row (th or td) and
    a single data row beneath it. Parse by zipping headers to values by column index.
    """
    soup = BeautifulSoup(html, "lxml")
    detail = {"detail_fetched": "yes", "notes": ""}

    def table_to_dict(table) -> dict:
        rows = table.find_all("tr")
        if len(rows) < 2:
            return {}
        headers = [cell.get_text(strip=True).lower() for cell in rows[0].find_all(["th", "td"])]
        values = [cell.get_text(strip=True) for cell in rows[1].find_all(["th", "td"])]
        return dict(zip(headers, values))

    tables = soup.find_all("table")
    t1 = table_to_dict(tables[0]) if len(tables) > 0 else {}
    t2 = table_to_dict(tables[1]) if len(tables) > 1 else {}
    t3 = table_to_dict(tables[2]) if len(tables) > 2 else {}

    # Table 1 — Bill Summary
    detail["face_value"] = t1.get("face value", "")
    detail["amount_paid"] = t1.get("amount paid", "")

    # Table 2 — Sale/Purchase Info
    detail["parcel_num"] = t2.get("account/parcel #", "")
    detail["assigned"] = t2.get("assigned", "")
    detail["purchaser_detail"] = t2.get("purchaser", "")
    detail["purchaser_address"] = t2.get("purchaser address", "")
    detail["date_paid"] = t2.get("date paid", "")
    detail["paid_by"] = t2.get("paid by", "")
    detail["district"] = t2.get("district", "")

    # Table 3 — Lien Status
    detail["assessment"] = t3.get("assessment", "")
    detail["owed_at_sale"] = t3.get("owed at sale", "")
    detail["amount_due"] = t3.get("amount due", "")
    detail["bankruptcy"] = t3.get("bankruptcy", "")
    detail["exonerated"] = t3.get("exonerated", "")
    detail["date_exonerated"] = t3.get("date exonerated", "")
    detail["released"] = t3.get("released", "")
    detail["date_released"] = t3.get("date released", "")
    detail["sold"] = t3.get("sold", "")

    # Sanity check
    filled = sum(1 for k, v in detail.items() if v and k not in ("detail_fetched", "notes"))
    if filled < 4:
        detail["notes"] = "WARNING: few fields parsed — page structure may have changed"
        log.warning(f"  {inst_num}: Only {filled} detail fields parsed.")

    return detail


# ---------------------------------------------------------------------------
# Checkpoint: load previously scraped inst_nums
# ---------------------------------------------------------------------------
def load_checkpoint(year: int) -> set[str]:
    path = INTERIM_DIR / f"delinquent_bills_{year}.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["inst_num"] for row in reader if row.get("detail_fetched") == "yes"}


def save_year_csv(records: list[dict], year: int):
    path = INTERIM_DIR / f"delinquent_bills_{year}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=BILL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    log.info(f"  Saved {len(records)} records → {path.name}")


def merge_all_years():
    paths = sorted(INTERIM_DIR.glob("delinquent_bills_20*.csv"))
    all_rows = []
    for p in paths:
        with p.open(encoding="utf-8") as f:
            all_rows.extend(list(csv.DictReader(f)))
    out = INTERIM_DIR / "delinquent_bills_all.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=BILL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    log.info(f"Merged {len(all_rows)} total records → {out.name}")


# ---------------------------------------------------------------------------
# Core scrape loop for one year
# ---------------------------------------------------------------------------
def scrape_year(client: httpx.Client, year: int, dry_run: bool = False):
    log.info(f"=== Scraping tax year {year} ===")
    year_dir = RAW_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    # --- Step 1: Fetch list page ---
    list_html_path = year_dir / f"list_{year}.html"

    if list_html_path.exists():
        log.info(f"  List page already cached: {list_html_path.name}")
        html = list_html_path.read_text(encoding="utf-8")
    else:
        if dry_run:
            log.info(f"  [DRY RUN] Would fetch list for {year}")
            return
        log.info(f"  Fetching list page for {year}...")
        r = fetch(client, LIST_URL, params={
            "taxYear": year,
            "delBills": "on",
            "executeSearch": "1",
            "lastName": "",
            "firstName": "",
            "billNumber": "",
            "accNum": "",
            "addr1": "",
        })
        html = r.text
        save_html(html, list_html_path)
        time.sleep(THROTTLE_SECONDS)

    # --- Step 2: Parse list ---
    records = parse_list_page(html, year)
    if not records:
        return

    # Initialize records with metadata defaults
    for rec in records:
        rec["detail_url"] = f"{DETAIL_URL}?InstNum={rec['inst_num']}"
        rec["scrape_date"] = today
        rec["detail_fetched"] = "no"
        for field in BILL_FIELDS:
            rec.setdefault(field, "")

    if dry_run:
        log.info(f"  [DRY RUN] Would fetch {len(records)} detail pages for {year}")
        return

    # --- Step 3: Fetch detail pages (with checkpoint) ---
    done = load_checkpoint(year)
    log.info(f"  {len(done)} detail pages already fetched (checkpoint).")

    records_by_inst = {r["inst_num"]: r for r in records}

    for i, inst_num in enumerate(records_by_inst.keys(), 1):
        if inst_num in done:
            records_by_inst[inst_num]["detail_fetched"] = "yes"
            continue

        detail_path = year_dir / f"detail_{inst_num}.html"

        if detail_path.exists():
            detail_html = detail_path.read_text(encoding="utf-8")
        else:
            log.info(f"  [{i}/{len(records)}] Fetching detail for {inst_num}...")
            try:
                r = fetch(client, DETAIL_URL, params={"InstNum": inst_num})
                detail_html = r.text
                save_html(detail_html, detail_path)
            except httpx.HTTPError as e:
                log.error(f"  Failed to fetch {inst_num}: {e}")
                records_by_inst[inst_num]["notes"] = f"fetch_error: {e}"
                continue
            finally:
                time.sleep(THROTTLE_SECONDS)

        detail_fields = parse_detail_page(detail_html, inst_num)
        records_by_inst[inst_num].update(detail_fields)
        records_by_inst[inst_num]["scrape_date"] = today

        # Save checkpoint after every 50 detail pages
        if i % 50 == 0:
            save_year_csv(list(records_by_inst.values()), year)
            log.info(f"  Checkpoint saved at {i}/{len(records)}.")

    # --- Step 4: Final save ---
    save_year_csv(list(records_by_inst.values()), year)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scrape Fayette County delinquent tax bills.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=list(range(2016, 2025)),
        help="Tax years to scrape (default: 2016-2024)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse list pages but do not fetch detail pages.",
    )
    args = parser.parse_args()

    log.info(f"Starting scrape for years: {args.years}")
    log.info(f"Raw HTML → {RAW_DIR}")
    log.info(f"Parsed CSV → {INTERIM_DIR}")

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        for year in sorted(args.years):
            try:
                scrape_year(client, year, dry_run=args.dry_run)
            except Exception as e:
                log.error(f"Failed on year {year}: {e}", exc_info=True)
                log.info("Continuing to next year...")

    if not args.dry_run:
        merge_all_years()

    log.info("Done.")


if __name__ == "__main__":
    main()
