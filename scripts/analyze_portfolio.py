"""
Portfolio Reconstruction and Analysis
======================================
Reconstructs KY Lien Holdings' per-property lien history from land records,
cross-references with delinquent bill data, and produces summary tables.

Outputs:
  data/processed/ky_lien_holdings_portfolio.csv   — per-property status
  data/processed/lien_events_all.csv              — all events sorted by property
  data/processed/summary_stats.json               — headline numbers
  outputs/tables/portfolio_summary.md             — human-readable summary
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_land_records():
    path = INTERIM_DIR / "land_records_all.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_delinquent_bills():
    path = INTERIM_DIR / "delinquent_bills_all.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
def normalize_name(s):
    s = re.sub(r"\s+", " ", s.strip().upper())
    # Remove trailing punctuation variants (comma before LLC, trailing period)
    s = re.sub(r",\s*(LLC|INC|LTD|CORP)\b", r" \1", s)
    s = s.rstrip(".")
    return s


def is_ky_lien(name):
    n = normalize_name(name)
    return "KY LIEN HOLDINGS" in n


def parse_dollar(s):
    try:
        return float(s.replace("$", "").replace(",", "").strip())
    except Exception:
        return None


def parse_date(s):
    """Return YYYY-MM-DD or empty string."""
    if not s:
        return ""
    m = re.match(r"(\d{4})[/-](\d{2})[/-](\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m2 = re.match(r"(\d{2})[/-](\d{2})[/-](\d{4})", s)
    if m2:
        return f"{m2.group(3)}-{m2.group(1)}-{m2.group(2)}"
    return s


# ---------------------------------------------------------------------------
# Portfolio reconstruction from land records
# ---------------------------------------------------------------------------
def xref_book_page(xref: str) -> str:
    """
    Extract book/page from a cross_references value.
    Format is 'BOOK/PAGE-CODE' (e.g. '791/270-072') — return 'BOOK/PAGE'.
    Also handles plain 'BOOK/PAGE' with no code suffix.
    """
    m = re.match(r"^(\d+/\d+)(?:-\d+)?$", xref.strip())
    return m.group(1) if m else ""


def clean_prop_desc(desc: str) -> str:
    """Normalize messy property description strings to a clean address."""
    # Many entries are padded with large whitespace blocks; collapse them
    return re.sub(r"\s+", " ", desc.strip())


def extract_address(desc: str) -> str:
    """
    Best-effort address extraction from a cleaned property description.

    Formats seen in Fayette County land records:
      1. '264 E FOURTH ST 405080000ASSIGN CERTIFICATE OF DELINQUENCY (264 E FOURTH ST)'
         → extract parenthesized address at end
      2. '3575 CAULDER RD 405170000ASSIGN CERTIFICATE OF DELINQUENCY (3575 CAULDER DR0'
         → truncated parenthesized part; fall back to leading address before parcel number
      3. 'ASSIGN ENC BK 475 PG 280 C. BURCHELL'
         → REASSIGN record, no address available
    """
    # Prefer complete parenthesized address at end
    m = re.search(r"\(([^)]+)\)\s*$", desc)
    if m:
        return m.group(1).strip()
    # Fall back: extract leading address before 9-digit parcel block
    m2 = re.match(r"^([A-Z0-9].+?)\s+\d{9}", desc)
    if m2:
        return m2.group(1).strip()
    return ""


def reconstruct_portfolio(land_records):
    """
    Reconstruct per-cert lien history using book/page cross-references.

    Matching strategy:
      - Each CERT DEL ASSIGN record (KY Lien as grantee) is identified by its book_page.
      - Each release (KY Lien as grantor) links back to the cert via cross_references:
          release.cross_references = 'CERT_BOOK/PAGE-CODE'
      - Primary match: release's cross_ref book/page == assignment's book_page (165/169)
      - Fallback match: release's cross_ref book/page == assignment's own cross_ref book/page
        (handles 4 cases where the release references the original pre-reassignment cert)

    Per-cert status:
      - No matching release → active
      - Has release → check instrument type:
          DEL TAX RELEASE / 3RD PTY TAX REL / IN HOUSE REL → released (owner paid / 3rd party)
          REASSIGN to non-KY-Lien grantee → reassigned

    Properties are then grouped by cleaned property_description from the assignment record.
    """

    # Separate by role
    assignments = []   # KY Lien Holdings is grantee (receiving cert)
    releases = []      # KY Lien Holdings is grantor (releasing or reassigning cert)
    other = []

    for rec in land_records:
        grantee = normalize_name(rec.get("grantee", ""))
        grantor = normalize_name(rec.get("grantor", ""))
        if is_ky_lien(grantee):
            assignments.append(rec)
        elif is_ky_lien(grantor):
            releases.append(rec)
        else:
            other.append(rec)

    print(f"\nLand records breakdown:")
    print(f"  KY Lien Holdings as grantee (receiving): {len(assignments)}")
    print(f"  KY Lien Holdings as grantor (releasing): {len(releases)}")
    print(f"  Other records: {len(other)}")

    # Index assignments by their book_page (primary) and by their own cross_ref bp (fallback)
    assign_by_bp = {}       # assignment.book_page → rec
    assign_by_xref_bp = {}  # strip_code(assignment.cross_references) → rec
    for rec in assignments:
        bp = rec["book_page"].strip()
        if bp:
            assign_by_bp[bp] = rec
        xbp = xref_book_page(rec.get("cross_references", ""))
        if xbp and xbp not in assign_by_xref_bp:
            assign_by_xref_bp[xbp] = rec

    # Match each release to its corresponding assignment cert
    # release_map: assignment.book_page → list of release records
    release_map = defaultdict(list)
    unmatched_releases = []
    for rel in releases:
        xbp = xref_book_page(rel.get("cross_references", ""))
        if xbp in assign_by_bp:
            # Primary match: release → assignment by cert book/page
            cert_bp = xbp
        elif xbp in assign_by_xref_bp:
            # Fallback: release references original cert before reassignment chain
            cert_bp = assign_by_xref_bp[xbp]["book_page"].strip()
        else:
            cert_bp = None

        if cert_bp:
            release_map[cert_bp].append(rel)
        else:
            unmatched_releases.append(rel)

    if unmatched_releases:
        print(f"  WARNING: {len(unmatched_releases)} release records could not be matched to an assignment:")
        for r in unmatched_releases:
            print(f"    {r['book_page']} xref={r['cross_references']!r} inst={r['instrument_type']!r}")

    # --- Build per-cert status, then group by property ---
    # cert_records: list of dicts with one entry per CERT DEL ASSIGN
    cert_records = []
    for rec in assignments:
        bp = rec["book_page"].strip()
        matched_rels = release_map.get(bp, [])

        assign_date = parse_date(rec.get("recording_date", ""))
        inst = rec.get("instrument_type", "").upper()

        # Determine cert status
        if matched_rels:
            # Find the latest release
            last_rel = sorted(matched_rels, key=lambda r: parse_date(r.get("recording_date", "")))[-1]
            last_rel_inst = last_rel.get("instrument_type", "").upper()
            last_rel_grantee = normalize_name(last_rel.get("grantee", ""))
            rel_date = parse_date(last_rel.get("recording_date", ""))

            if "RELEASE" in last_rel_inst or last_rel_inst in ("3RD PTY TAX REL", "IN HOUSE REL"):
                cert_status = "released"
                cert_holder = ""
                reassigned_to = ""
            elif "ASSIGN" in last_rel_inst and last_rel_grantee and not is_ky_lien(last_rel_grantee):
                cert_status = "reassigned"
                cert_holder = last_rel_grantee
                reassigned_to = last_rel_grantee
            else:
                cert_status = "released"
                cert_holder = ""
                reassigned_to = ""
        else:
            rel_date = ""
            cert_status = "active"
            cert_holder = "KY LIEN HOLDINGS LLC"
            reassigned_to = ""

        cert_records.append({
            "_cert_bp": bp,
            "_cert_status": cert_status,
            "_cert_holder": cert_holder,
            "_reassigned_to": reassigned_to,
            "_assign_date": assign_date,
            "_rel_date": rel_date,
            "_n_releases": len(matched_rels),
            "_rel_inst_types": ", ".join(sorted(set(r.get("instrument_type", "") for r in matched_rels))),
            "raw_prop_desc": rec.get("property_description", ""),
            "recording_date": assign_date,
            "grantor": rec.get("grantor", ""),
            "instrument_type": rec.get("instrument_type", ""),
            "book_page": bp,
        })

    # --- Group certs by property (cleaned address from assignment) ---
    # Use the property_description from the assignment rec as the grouping key
    prop_certs = defaultdict(list)
    for cr in cert_records:
        desc = clean_prop_desc(cr["raw_prop_desc"])
        # Many property desc fields start with a messy address block; use it as-is
        prop_certs[desc].append(cr)

    portfolio = []
    for prop_key, certs in prop_certs.items():
        certs_sorted = sorted(certs, key=lambda c: c["_assign_date"])
        first = certs_sorted[0]
        last = certs_sorted[-1]

        n_active = sum(1 for c in certs if c["_cert_status"] == "active")
        n_released = sum(1 for c in certs if c["_cert_status"] == "released")
        n_reassigned = sum(1 for c in certs if c["_cert_status"] == "reassigned")

        # Overall property status: active if ANY cert is still active
        # reassigned if any cert was reassigned (and none active)
        # released only if all certs released
        if n_active > 0:
            status = "active"
            current_holder = "KY LIEN HOLDINGS LLC"
        elif n_reassigned > 0:
            status = "reassigned"
            current_holder = next(c["_cert_holder"] for c in certs if c["_cert_status"] == "reassigned")
        else:
            status = "released"
            current_holder = ""

        reassigned_to = next((c["_reassigned_to"] for c in certs if c["_reassigned_to"]), "")
        all_rel_dates = [c["_rel_date"] for c in certs if c["_rel_date"]]
        last_release_date = max(all_rel_dates) if all_rel_dates else ""

        portfolio.append({
            "property_description": prop_key,
            "property_address": extract_address(prop_key),
            "current_status": status,
            "current_holder": current_holder,
            "reassigned_to": reassigned_to,
            "first_assignment_date": first["_assign_date"],
            "last_assignment_date": last["_assign_date"],
            "last_release_date": last_release_date,
            "total_certs": len(certs),
            "active_certs": n_active,
            "released_certs": n_released,
            "reassigned_certs": n_reassigned,
            "grantor_at_first_assign": first["grantor"],
            "book_page_first": first["book_page"],
            "instrument_types": ", ".join(sorted(set(c["instrument_type"] for c in certs))),
            "years_active": ", ".join(sorted(set(
                c["_assign_date"][:4] for c in certs if c["_assign_date"]
            ))),
        })

    return portfolio


# ---------------------------------------------------------------------------
# Delinquent bills analysis
# ---------------------------------------------------------------------------
def analyze_delinquent_bills(bills):
    amounts = []
    for r in bills:
        v = parse_dollar(r.get("face_value", ""))
        if v is not None and v >= 0:
            amounts.append(v)
    amounts.sort()

    due_amounts = []
    multipliers = []
    for r in bills:
        fv = parse_dollar(r.get("face_value", ""))
        ad = parse_dollar(r.get("amount_due", ""))
        if fv and ad and fv > 0 and ad > 0:
            due_amounts.append(ad)
            multipliers.append(ad / fv)

    n = len(amounts)
    return {
        "total_bills": len(bills),
        "bills_with_amounts": n,
        "face_value_median": sorted(amounts)[n // 2] if amounts else 0,
        "face_value_mean": sum(amounts) / n if n else 0,
        "face_value_min": min(amounts) if amounts else 0,
        "face_value_max": max(amounts) if amounts else 0,
        "under_50": sum(1 for a in amounts if a < 50),
        "under_100": sum(1 for a in amounts if a < 100),
        "under_500": sum(1 for a in amounts if a < 500),
        "under_50_pct": round(100 * sum(1 for a in amounts if a < 50) / n, 1) if n else 0,
        "under_100_pct": round(100 * sum(1 for a in amounts if a < 100) / n, 1) if n else 0,
        "total_face_value": sum(amounts),
        "total_amount_due": sum(due_amounts),
        "median_multiplier": round(sorted(multipliers)[len(multipliers) // 2], 1) if multipliers else 0,
        "over_3x": sum(1 for m in multipliers if m > 3),
        "over_5x": sum(1 for m in multipliers if m > 5),
        "over_10x": sum(1 for m in multipliers if m > 10),
        "by_year": {yr: len(list(recs)) for yr, recs in
                    __import__("itertools").groupby(sorted(bills, key=lambda r: r.get("tax_year", "")),
                                                     key=lambda r: r.get("tax_year", ""))},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading data...")
    land_records = load_land_records()
    bills = load_delinquent_bills()
    print(f"  Land records: {len(land_records)}")
    print(f"  Delinquent bills: {len(bills)}")

    # ---- Portfolio reconstruction ----
    print("\n=== KY LIEN HOLDINGS PORTFOLIO ===")
    portfolio = reconstruct_portfolio(land_records)

    status_counts = Counter(p["current_status"] for p in portfolio)
    print(f"\nUnique properties with any KY Lien Holdings instrument: {len(portfolio)}")
    print("Status breakdown:")
    for s, n in status_counts.most_common():
        print(f"  {s}: {n}")

    active = [p for p in portfolio if p["current_status"] == "active"]
    released = [p for p in portfolio if p["current_status"] == "released"]
    reassigned = [p for p in portfolio if p["current_status"] == "reassigned"]

    print(f"\nActive (no release recorded): {len(active)}")
    print(f"Released (owner paid): {len(released)}")
    print(f"Reassigned to another holder: {len(reassigned)}")

    if reassigned:
        print("\nReassigned to:")
        for p in reassigned:
            print(f"  {p['property_description'][:50]} → {p['reassigned_to']}")

    # Years of activity
    all_years = set()
    for p in portfolio:
        for yr in p.get("years_active", "").split(", "):
            if yr.strip():
                all_years.add(yr.strip())
    print(f"\nActive years: {sorted(all_years)}")

    # Save portfolio CSV
    pf_path = PROCESSED_DIR / "ky_lien_holdings_portfolio.csv"
    pf_fields = [
        "property_description", "property_address", "current_status", "current_holder",
        "reassigned_to", "first_assignment_date", "last_assignment_date", "last_release_date",
        "total_certs", "active_certs", "released_certs", "reassigned_certs",
        "grantor_at_first_assign", "book_page_first", "instrument_types", "years_active",
    ]
    with pf_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=pf_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(portfolio)
    print(f"\nPortfolio saved → {pf_path.name}")

    # ---- Delinquent bills analysis ----
    print("\n=== DELINQUENT BILL LANDSCAPE (unpurchased bills, all years) ===")
    bill_stats = analyze_delinquent_bills(bills)
    print(f"Total bills in system: {bill_stats['total_bills']}")
    print(f"Median face value: ${bill_stats['face_value_median']:.2f}")
    print(f"Under $50: {bill_stats['under_50']} ({bill_stats['under_50_pct']}%)")
    print(f"Under $100: {bill_stats['under_100']} ({bill_stats['under_100_pct']}%)")
    print(f"Total face value: ${bill_stats['total_face_value']:,.2f}")
    print(f"Total currently due: ${bill_stats['total_amount_due']:,.2f}")
    print(f"Median debt multiplier (current due / original): {bill_stats['median_multiplier']}x")
    print(f"Bills over 3x: {bill_stats['over_3x']} | over 5x: {bill_stats['over_5x']} | over 10x: {bill_stats['over_10x']}")

    # ---- Related entities from land records ----
    print("\n=== RELATED ENTITIES ===")
    all_grantors = Counter(normalize_name(r.get("grantor", "")) for r in land_records if r.get("grantor"))
    all_grantees = Counter(normalize_name(r.get("grantee", "")) for r in land_records if r.get("grantee"))
    print("Top grantors (in our delinquent tax land records):")
    for name, n in all_grantors.most_common(15):
        print(f"  {n:4d}  {name}")
    print("Top grantees:")
    for name, n in all_grantees.most_common(15):
        print(f"  {n:4d}  {name}")

    # Build entity summary: for each entity, count certs as purchaser (grantee) and as assignor (grantor)
    entity_stats = {}
    for rec in land_records:
        for role, field in [("as_grantee", "grantee"), ("as_grantor", "grantor")]:
            name = normalize_name(rec.get(field, ""))
            if not name:
                continue
            if name not in entity_stats:
                entity_stats[name] = {"as_grantee": 0, "as_grantor": 0}
            entity_stats[name][role] += 1
    # Sort by total activity
    entity_list = [
        {"entity": k, "certs_purchased": v["as_grantee"], "certs_transferred_out": v["as_grantor"]}
        for k, v in entity_stats.items()
        if v["as_grantee"] >= 3 or v["as_grantor"] >= 3
    ]
    entity_list.sort(key=lambda x: x["certs_purchased"] + x["certs_transferred_out"], reverse=True)

    # ---- Summary JSON ----
    summary = {
        "as_of": __import__("datetime").date.today().isoformat(),
        "ky_lien_holdings": {
            "total_properties": len(portfolio),
            "active": len(active),
            "released": len(released),
            "reassigned": len(reassigned),
            "years_active": sorted(all_years),
            "total_cert_instruments": sum(p["total_certs"] for p in portfolio),
            "total_active_certs": sum(p["active_certs"] for p in portfolio),
            "total_released_certs": sum(p["released_certs"] for p in portfolio),
            "total_reassigned_certs": sum(p["reassigned_certs"] for p in portfolio),
        },
        "delinquent_bill_landscape": bill_stats,
        "land_records_total": len(land_records),
        "entity_activity": entity_list,
    }
    summary_path = PROCESSED_DIR / "summary_stats.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary saved → {summary_path.name}")

    # ---- Markdown summary ----
    md = f"""# Portfolio Analysis: KY Lien Holdings LLC in Fayette County
*As of {summary['as_of']}*

## KY Lien Holdings — Certificate of Delinquency Portfolio

| Metric | Value |
|--------|-------|
| Unique properties with any instrument | **{len(portfolio)}** |
| Currently active (no release on record) | **{len(active)}** |
| Released (owner paid) | **{len(released)}** |
| Reassigned to another holder | **{len(reassigned)}** |
| Years of activity in Fayette County | {', '.join(sorted(all_years))} |
| Total cert instruments recorded | {sum(p['total_certs'] for p in portfolio)} |
| Certs currently active | {sum(p['active_certs'] for p in portfolio)} |
| Certs released | {sum(p['released_certs'] for p in portfolio)} |
| Certs reassigned | {sum(p['reassigned_certs'] for p in portfolio)} |

> **Methodology note**: "Active" means no release instrument has been found in the clerk's land records. It does not rule out resolutions filed but not yet indexed, or informal resolutions not reflected in public records.

## Active Properties (no release on record)

| Property | First Assigned | Last Assigned | Assignment Count |
|----------|---------------|---------------|-----------------|
"""
    for p in sorted(active, key=lambda x: x["first_assignment_date"]):
        addr = p["property_address"] or p["property_description"][:50]
        md += f"| {addr} | {p['first_assignment_date']} | {p['last_assignment_date']} | {p['total_certs']} |\n"

    md += f"""
## Delinquent Bill Landscape (unpurchased bills, 2016–2024)

These are bills that were **not** purchased by any third party — the leftovers.
KY Lien Holdings' actual purchases are documented separately in the land records above.

| Metric | Value |
|--------|-------|
| Total unresolved bills in system | {bill_stats['total_bills']:,} |
| Median original tax debt | ${bill_stats['face_value_median']:.2f} |
| Bills under $50 (original) | {bill_stats['under_50']:,} ({bill_stats['under_50_pct']}%) |
| Bills under $100 (original) | {bill_stats['under_100']:,} ({bill_stats['under_100_pct']}%) |
| Total original face value | ${bill_stats['total_face_value']:,.2f} |
| Total currently owed | ${bill_stats['total_amount_due']:,.2f} |
| Median multiplier (owed ÷ original) | {bill_stats['median_multiplier']}× |
| Bills now >3× original amount | {bill_stats['over_3x']:,} |
| Bills now >10× original amount | {bill_stats['over_10x']:,} |

## Certificate Purchaser Ecosystem (all entities in land records)

| Entity | Certs Purchased (grantee) | Certs Transferred Out (grantor) |
|--------|--------------------------|--------------------------------|
"""
    for e in entity_list:
        md += f"| {e['entity']} | {e['certs_purchased']} | {e['certs_transferred_out']} |\n"

    md += f"""
## Reassigned Certificates (KY Lien Holdings → Kings Right LLC)

| Property | First Assigned | Reassigned |
|----------|---------------|-----------|
"""
    for p in sorted(reassigned, key=lambda x: x["first_assignment_date"]):
        addr = p["property_address"] or p["property_description"][:50]
        md += f"| {addr} | {p['first_assignment_date']} | {p['last_release_date']} |\n"

    md += f"""
## Data Sources
- Fayette County Land Records Search (fayettedeeds.com) — scraped {summary['as_of']}
- Fayette County Delinquent Tax Bill Search — scraped {summary['as_of']}
- See docs/methodology.md for full methods and limitations
"""
    md_path = TABLES_DIR / "portfolio_summary.md"
    md_path.write_text(md)
    print(f"Markdown summary → {md_path.name}")


if __name__ == "__main__":
    main()
