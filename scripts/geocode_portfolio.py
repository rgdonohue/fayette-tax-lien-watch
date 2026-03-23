"""
Spatial Join: Portfolio Addresses → Council Districts + Neighborhoods
=====================================================================
For each property address in the lien portfolio (all Ramey-linked entities),
geocodes the address using the LFUCG geocoder, then spatially joins to
council district and neighborhood association layers.

Inputs:
  data/processed/ky_lien_holdings_portfolio.csv
  data/interim/land_records_all.csv   (for Five Four Lean and Purchase Area Lien)

Outputs:
  data/processed/portfolio_geocoded.csv   — all portfolio properties with coords and geography
  data/processed/district_rollup.csv      — count of active/released/total by council district
  outputs/tables/spatial_summary.md       — human-readable spatial breakdown
"""

import csv
import json
import re
import sys
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

GEOCODER_URL = "https://maps.lexingtonky.gov/lfucggis/rest/services/locator/GeocodeServer/findAddressCandidates"
DISTRICT_URL = "https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Council_District/FeatureServer/0/query"
NEIGHBORHOOD_URL = "https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Neighborhood_Association/FeatureServer/0/query"
THROTTLE = 1.5  # seconds between requests


# ---------------------------------------------------------------------------
# Address cleaning and extraction
# ---------------------------------------------------------------------------
def extract_address(desc: str) -> str:
    """Extract clean address from raw property description."""
    desc = re.sub(r"\s+", " ", desc.strip())
    # Prefer parenthesized address at end
    m = re.search(r"\(([^)]+)\)\s*$", desc)
    if m:
        return m.group(1).strip()
    # Leading address before 9-digit parcel block
    m2 = re.match(r"^([A-Z0-9].+?)\s+\d{9}", desc)
    if m2:
        return m2.group(1).strip()
    return ""


# ---------------------------------------------------------------------------
# LFUCG Geocoder
# ---------------------------------------------------------------------------
def geocode(client: httpx.Client, address: str) -> dict:
    """
    Query LFUCG geocoder. Returns dict with keys:
      score, x, y, matched_address, pvanum (if available)
    """
    params = {
        "Street": address,
        "City": "Lexington",
        "State": "KY",
        "outFields": "*",
        "maxLocations": 1,
        "f": "json",
    }
    try:
        r = client.get(GEOCODER_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"score": 0, "x": None, "y": None, "matched_address": "", "pvanum": ""}
        best = candidates[0]
        attrs = best.get("attributes", {})
        return {
            "score": best.get("score", 0),
            "x": best.get("location", {}).get("x"),
            "y": best.get("location", {}).get("y"),
            "matched_address": best.get("address", ""),
            "pvanum": attrs.get("Ref_ID", "") or attrs.get("PVANUM", ""),
        }
    except Exception as e:
        print(f"  Geocode error for {address!r}: {e}", file=sys.stderr)
        return {"score": 0, "x": None, "y": None, "matched_address": "", "pvanum": ""}


# ---------------------------------------------------------------------------
# Point-in-polygon: council district
# ---------------------------------------------------------------------------
def get_council_district(client: httpx.Client, x: float, y: float) -> dict:
    """Query which council district a point falls in (using spatial rel intersects)."""
    params = {
        "geometry": f"{x},{y}",
        "geometryType": "esriGeometryPoint",
        "inSR": "2246",  # LFUCG geocoder returns WKID 2246 (KY State Plane North, US Feet)
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "DISTRICT,REP",
        "returnGeometry": "false",
        "f": "json",
    }
    try:
        r = client.get(DISTRICT_URL, params=params, timeout=15)
        r.raise_for_status()
        features = r.json().get("features", [])
        if features:
            attrs = features[0].get("attributes", {})
            return {
                "council_district": str(attrs.get("DISTRICT", "")),
                "council_rep": attrs.get("REP", ""),
            }
    except Exception as e:
        print(f"  District lookup error: {e}", file=sys.stderr)
    return {"council_district": "", "council_rep": ""}


# ---------------------------------------------------------------------------
# Point-in-polygon: neighborhood
# ---------------------------------------------------------------------------
def get_neighborhood(client: httpx.Client, x: float, y: float) -> dict:
    """Query which neighborhood association a point falls in."""
    params = {
        "geometry": f"{x},{y}",
        "geometryType": "esriGeometryPoint",
        "inSR": "2246",  # LFUCG geocoder returns WKID 2246 (KY State Plane North, US Feet)
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "Assoc_Name,Council",
        "returnGeometry": "false",
        "f": "json",
    }
    try:
        r = client.get(NEIGHBORHOOD_URL, params=params, timeout=15)
        r.raise_for_status()
        features = r.json().get("features", [])
        if features:
            attrs = features[0].get("attributes", {})
            return {
                "neighborhood": attrs.get("Assoc_Name", ""),
                "neighborhood_council": attrs.get("Council", ""),
            }
    except Exception as e:
        print(f"  Neighborhood lookup error: {e}", file=sys.stderr)
    return {"neighborhood": "", "neighborhood_council": ""}


# ---------------------------------------------------------------------------
# Build combined portfolio across entities
# ---------------------------------------------------------------------------
def normalize_name(s):
    s = re.sub(r"\s+", " ", s.strip().upper())
    s = re.sub(r",\s*(LLC|INC|LTD|CORP)\b", r" \1", s)
    return s.rstrip(".")


def load_entity_portfolio(land_records: list[dict], entity_substring: str) -> list[dict]:
    """Extract cert-level records for one entity as grantee."""
    def is_entity(name):
        return entity_substring in normalize_name(name)

    results = []
    seen_bp = set()
    for rec in land_records:
        if is_entity(rec.get("grantee", "")) and not is_entity(rec.get("grantor", "")):
            bp = rec.get("book_page", "").strip()
            if bp in seen_bp:
                continue
            seen_bp.add(bp)
            desc = re.sub(r"\s+", " ", rec.get("property_description", "").strip())
            addr = extract_address(desc)
            # Fallback: FFL/PAL records use plain "NUMBER STREET [ZIP]" format
            if not addr and re.match(r"^\d+\s+\S", desc):
                addr = re.sub(r"\s+\d{5}(?:-\d{4})?\s*$", "", desc).strip()
            results.append({
                "entity": entity_substring,
                "property_address": addr,
                "property_description": desc,
                "first_assignment_date": rec.get("recording_date", ""),
                "book_page": bp,
                "grantor": rec.get("grantor", ""),
            })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Load KY Lien Holdings portfolio (already reconstructed with status)
    print("Loading KY Lien Holdings portfolio...")
    ky_lien_props = []
    with open(PROCESSED_DIR / "ky_lien_holdings_portfolio.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            addr = row.get("property_address", "").strip()
            if not addr:
                addr = extract_address(row.get("property_description", ""))
            ky_lien_props.append({
                "entity": "KY LIEN HOLDINGS",
                "property_address": addr,
                "property_description": row.get("property_description", ""),
                "current_status": row.get("current_status", ""),
                "first_assignment_date": row.get("first_assignment_date", ""),
                "years_active": row.get("years_active", ""),
                "total_certs": row.get("total_certs", ""),
                "book_page": row.get("book_page_first", ""),
                "grantor": row.get("grantor_at_first_assign", ""),
            })
    print(f"  KY Lien Holdings: {len(ky_lien_props)} properties")

    # Load land records for Five Four Lean and Purchase Area Lien
    print("Loading related entity land records...")
    land_records = []
    with open(PROJECT_ROOT / "data" / "interim" / "land_records_all.csv", encoding="utf-8") as f:
        land_records = list(csv.DictReader(f))

    ffl_props = load_entity_portfolio(land_records, "FIVE FOUR LEAN")
    pal_props = load_entity_portfolio(land_records, "PURCHASE AREA LIEN")
    for p in ffl_props:
        p["entity"] = "FIVE FOUR LEAN"
        p["current_status"] = "unknown"  # status reconstruction done separately
    for p in pal_props:
        p["entity"] = "PURCHASE AREA LIEN"
        p["current_status"] = "unknown"
    print(f"  Five Four Lean: {len(ffl_props)} certs")
    print(f"  Purchase Area Lien: {len(pal_props)} certs")

    all_props = ky_lien_props + ffl_props + pal_props
    print(f"\nTotal records to geocode: {len(all_props)}")

    # Load existing geocode results to avoid re-geocoding
    geocode_cache = {}
    cache_path = PROCESSED_DIR / "portfolio_geocoded.csv"
    if cache_path.exists():
        with cache_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                addr = row.get("property_address", "")
                if addr and row.get("geocode_score"):
                    geocode_cache[addr] = row
        print(f"  Loaded {len(geocode_cache)} cached geocode results")

    # Geocode and spatial join
    output_rows = []
    out_fields = [
        "entity", "property_address", "current_status",
        "first_assignment_date", "years_active", "total_certs",
        "geocode_score", "geocode_x", "geocode_y", "matched_address", "pvanum",
        "council_district", "council_rep", "neighborhood",
        "property_description", "book_page", "grantor",
    ]

    with httpx.Client(
        headers={"User-Agent": "Fayette-TaxLien-Research/1.0 (public-interest-journalism)"},
        follow_redirects=True,
        timeout=30,
    ) as client:
        for i, prop in enumerate(all_props, 1):
            addr = prop.get("property_address", "").strip()
            if not addr:
                print(f"  [{i}/{len(all_props)}] SKIP (no address): {prop.get('property_description','')[:60]}")
                row = {**prop, "geocode_score": "", "geocode_x": "", "geocode_y": "",
                       "matched_address": "", "pvanum": "", "council_district": "",
                       "council_rep": "", "neighborhood": ""}
                for f in out_fields:
                    row.setdefault(f, "")
                output_rows.append(row)
                continue

            if addr in geocode_cache:
                cached = geocode_cache[addr]
                print(f"  [{i}/{len(all_props)}] CACHED: {addr!r} → district {cached.get('council_district','?')}")
                row = {**prop}
                row.update({k: cached.get(k, "") for k in
                            ["geocode_score", "geocode_x", "geocode_y", "matched_address",
                             "pvanum", "council_district", "council_rep", "neighborhood"]})
                for f in out_fields:
                    row.setdefault(f, "")
                output_rows.append(row)
                continue

            # Geocode
            print(f"  [{i}/{len(all_props)}] Geocoding: {addr!r}")
            geo = geocode(client, addr)
            time.sleep(THROTTLE)

            district = {"council_district": "", "council_rep": ""}
            neighborhood = {"neighborhood": "", "neighborhood_council": ""}

            if geo["x"] and geo["score"] >= 70:
                district = get_council_district(client, geo["x"], geo["y"])
                time.sleep(0.5)
                neighborhood = get_neighborhood(client, geo["x"], geo["y"])
                time.sleep(0.5)
                print(f"    score={geo['score']}, district={district['council_district']}, "
                      f"neighborhood={neighborhood['neighborhood']}")
            else:
                print(f"    LOW SCORE ({geo['score']}) — no spatial join")

            row = {**prop}
            row.update({
                "geocode_score": geo["score"],
                "geocode_x": geo["x"] or "",
                "geocode_y": geo["y"] or "",
                "matched_address": geo["matched_address"],
                "pvanum": geo["pvanum"],
                "council_district": district["council_district"],
                "council_rep": district["council_rep"],
                "neighborhood": neighborhood["neighborhood"],
            })
            for f in out_fields:
                row.setdefault(f, "")
            output_rows.append(row)

            # Save checkpoint every 20 records
            if i % 20 == 0:
                with cache_path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(output_rows)
                print(f"  Checkpoint saved at {i}/{len(all_props)}")

    # Final save
    with cache_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"\nGeocoded portfolio saved → {cache_path.name}")

    # --- District rollup ---
    from collections import defaultdict, Counter
    district_stats = defaultdict(lambda: {"entity_ky": 0, "entity_ffl": 0, "entity_pal": 0,
                                           "active": 0, "released": 0, "unknown": 0, "total": 0})
    for row in output_rows:
        d = row.get("council_district") or "Unknown"
        entity = row.get("entity", "")
        status = row.get("current_status", "unknown")
        if "KY LIEN" in entity:
            district_stats[d]["entity_ky"] += 1
        elif "FIVE FOUR" in entity:
            district_stats[d]["entity_ffl"] += 1
        elif "PURCHASE AREA" in entity:
            district_stats[d]["entity_pal"] += 1
        district_stats[d][status if status in ("active", "released") else "unknown"] += 1
        district_stats[d]["total"] += 1

    rollup_path = PROCESSED_DIR / "district_rollup.csv"
    with rollup_path.open("w", newline="", encoding="utf-8") as f:
        fields = ["council_district", "total", "active", "released", "unknown",
                  "ky_lien_holdings", "five_four_lean", "purchase_area_lien"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for district, stats in sorted(district_stats.items(),
                                       key=lambda x: (x[0] == "Unknown", x[0])):
            writer.writerow({
                "council_district": district,
                "total": stats["total"],
                "active": stats["active"],
                "released": stats["released"],
                "unknown": stats["unknown"],
                "ky_lien_holdings": stats["entity_ky"],
                "five_four_lean": stats["entity_ffl"],
                "purchase_area_lien": stats["entity_pal"],
            })
    print(f"District rollup saved → {rollup_path.name}")

    # --- Neighborhood rollup ---
    nbhd_stats = defaultdict(lambda: {"total": 0, "active": 0, "district": ""})
    for row in output_rows:
        nbhd = row.get("neighborhood") or "Unknown"
        status = row.get("current_status", "")
        nbhd_stats[nbhd]["total"] += 1
        if status == "active":
            nbhd_stats[nbhd]["active"] += 1
        if not nbhd_stats[nbhd]["district"]:
            nbhd_stats[nbhd]["district"] = row.get("council_district", "")

    # --- Markdown summary ---
    geocoded_count = sum(1 for r in output_rows if r.get("geocode_score") and float(r.get("geocode_score", 0) or 0) >= 70)
    total_count = len(output_rows)

    md = f"""# Spatial Analysis: Ramey-Linked Tax Lien Properties
*Fayette County, KY | Data as of 2026-03-22*

## Geocoding Summary

- Total properties in portfolio: **{total_count}**
- Successfully geocoded (score ≥ 70): **{geocoded_count}** ({round(100*geocoded_count/total_count)}%)
- Not geocoded (no address or low score): {total_count - geocoded_count}

## By Council District

| District | Total | Active | Released | KY Lien | Five Four Lean | Purchase Area Lien |
|----------|-------|--------|---------|---------|--------------|-------------------|
"""
    for district, stats in sorted(district_stats.items(),
                                   key=lambda x: (x[0] == "Unknown", x[0])):
        md += (f"| {district} | {stats['total']} | {stats['active']} | {stats['released']} | "
               f"{stats['entity_ky']} | {stats['entity_ffl']} | {stats['entity_pal']} |\n")

    md += f"""
## Top Neighborhoods by Activity

| Neighborhood | Total Certs | Active |
|-------------|------------|--------|
"""
    for nbhd, stats in sorted(nbhd_stats.items(), key=lambda x: -x[1]["total"])[:20]:
        if nbhd == "Unknown":
            continue
        md += f"| {nbhd} | {stats['total']} | {stats['active']} |\n"

    md += """
## Methodology Notes

- Addresses geocoded using LFUCG municipal geocoder (maps.lexingtonky.gov)
- Minimum confidence score of 70/100 required for spatial join
- Council district assignment via point-in-polygon query against LFUCG Council District layer (2020 Census boundaries)
- Properties with no extractable address or low geocode confidence appear in "Unknown" district
- "Active" status for Five Four Lean and Purchase Area Lien reflects individual cert-level analysis; 2025 purchases are within the 1-year tolling period
"""
    md_path = TABLES_DIR / "spatial_summary.md"
    md_path.write_text(md)
    print(f"Spatial summary → {md_path.name}")

    # Print district table to stdout
    print("\n=== DISTRICT ROLLUP ===")
    print(f"{'District':>10}  {'Total':>6}  {'Active':>7}  {'Released':>9}  {'KY Lien':>8}  {'FFL':>5}  {'PAL':>5}")
    for district, stats in sorted(district_stats.items(),
                                   key=lambda x: (x[0] == "Unknown", x[0])):
        print(f"{district:>10}  {stats['total']:>6}  {stats['active']:>7}  {stats['released']:>9}  "
              f"{stats['entity_ky']:>8}  {stats['entity_ffl']:>5}  {stats['entity_pal']:>5}")


if __name__ == "__main__":
    main()
