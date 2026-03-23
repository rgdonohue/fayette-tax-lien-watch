# Fayette Tax Lien Watch

## Project overview
Public-interest data investigation into third-party tax lien certificate purchasing in Fayette County, Kentucky. Primary research target: KY Lien Holdings, LLC and related entities linked to Justin H. Ramey / Ramey Law.

Goal: Build a forensic, reproducible dataset answering how prevalent, concentrated, and spatially patterned delinquent-tax certificate assignments are in Fayette County — and who holds them.

## Analytical guardrails (NON-NEGOTIABLE)
1. **Active vs historical**: An assignment record does NOT prove current ownership. Releases and reassignments must be tracked.
2. **Entity vs relationship**: "Same contact ecosystem" is NOT "same legal holder." Preserve the distinction with confidence tags.
3. **System vs harm**: Kentucky's third-party purchaser system is documented law. Separate factual documentation of the system from evidence of its effects.
4. **Claim provenance**: Every data point must trace to a source document or URL. No inferred facts presented as observed facts.

## Data sources
- **Fayette Land Records**: fayettedeeds.com/landrecords/ — Instrument types: CERT DEL ASSIGN, REASSIGN CERTIFICATE OF DEL, DEL TAX RELEASE, 3RD PTY TAX REL, IN HOUSE REL
- **Fayette Tax Bills**: fayettedeeds.com/delinquent/ — delinquent bill lookup
- **KY DOR**: revenue.ky.gov — third-party purchaser lists, clerk manual, county delinquency lists
- **Lexington GIS**: lexingtonky.gov/gis — parcel geometry and attributes
- **1000-record cap**: The Fayette web search returns max 1000 results. Queries must be partitioned (by year, instrument type, party name) to stay under this limit. Cross-reference totals against DOR county lists to detect truncation.

## Tech stack
- Python 3.11+
- httpx or requests for HTTP (prefer over Playwright unless JS-rendering required)
- pandas / polars for tabular work
- geopandas + shapely for spatial
- DuckDB for analytical queries if datasets grow
- Jupyter notebooks for exploratory analysis only; final logic goes in scripts

## Code conventions
- Scripts in `scripts/`, notebooks in `notebooks/`
- Raw data goes in `data/raw/` and is NEVER modified in place
- Interim/cleaned data in `data/interim/`, final outputs in `data/processed/`
- All scraper scripts must: throttle requests (min 2s between), checkpoint progress, save raw HTML alongside parsed output, log to stdout
- Use `data_dictionary.md` as the canonical field reference

## Key entities to track

### Confirmed Ramey-linked (DOR registration or land records)
- **KY Lien Holdings, LLC** — 705-D S 4th St, Murray KY 42071; DOR reg 2016-43 (confirmed), 2024-147, 2025-155; 176 cert assignments Fayette 2010-2022
- **Purchase Area Lien Holdings LLC** — 488 Turner Rd, Murray KY 42071; DOR reg 2025-156; NEW, triple-registered with KY Lien 4/28/2025
- **Five Four Lean, LLC** — 705-C S 4th St, Murray KY 42071; DOR reg 2025-157; NEW, triple-registered with KY Lien 4/28/2025
- **Justin H. Ramey** (principal contact), **Ramey Law, PLLC**

### Separate entities (appear in same land records ecosystem)
- **Kings Right LLC** — 4064 Robinwood Cove, Memphis TN 38111; DOR reg 2016-57 (confirmed), 2023-118; principal: Hugh Stephens (taxsalemgmt@yahoo.com); received 10 cert reassignments from KY Lien Holdings 2012-2013; NOT Ramey-linked
- **Cardinal Lien Serv LLC** — 54 certs purchased Fayette County; some transferred to PAM Institutional Tax Lien Fund LLC and KY Lien Holdings
- **Tax Lien Ptnr LLC** — 17 certs purchased Fayette County; sold 2 to KY Lien Holdings
- **PAM Institutional Tax Lien Fund LLC** — received 9+ certs from Cardinal Lien Serv

### Address of interest
- 2365 Harrodsburg Rd Ste A325, Lexington KY 40504 (original Ramey address — check other entities sharing it)
