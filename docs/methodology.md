# Methodology

## Overview

This document describes the methods used to construct the Fayette County tax lien certificate dataset. It is intended for transparency and peer review. All claims derived from this dataset should cite this document.

## Data collection

### Fayette County Land Records
Records were collected from the Fayette County Clerk's online Land Records Search. The search interface limits results to 1,000 per query. To mitigate truncation:
- Queries were partitioned by instrument type and year
- Record counts per partition were compared against expected totals
- Any partition hitting the 1,000-record cap was further subdivided

**Known limitation**: If a partitioned query still exceeds 1,000 records, results are truncated without warning. Cross-referencing against open-records responses (when received) will identify gaps.

### KY Department of Revenue
Third-party purchaser registration lists were archived from the DOR website. County-level certificate-of-delinquency lists were requested via open-records request under KRS 134.131.

### Lexington GIS
Parcel boundary data was obtained from Lexington's open data portal. Parcel attributes include owner name, address, land use classification, and assessed value.

## Record linkage

### Parcel matching
The primary join key is `parcel_id` when present in the clerk filing. When parcel_id is absent, address-based matching is attempted:
- Address strings are normalized (directional abbreviations, unit/apt removal, suffix standardization)
- Normalized addresses are matched against the GIS parcel layer
- Each match receives a confidence score: exact (1.0), near (0.7-0.99), fuzzy (< 0.7)
- Fuzzy matches are flagged for manual review and excluded from aggregate statistics unless manually verified

### Entity resolution
Entity names are normalized by:
- Removing punctuation and standardizing LLC/Inc suffixes
- Matching against known-entity registry
- Grouping entities sharing registered addresses or principal contacts

Relationships between entities are tagged with confidence levels (high/medium/low) and evidence notes. Grouped entities are reported both individually and as a family, with the grouping logic disclosed.

## Portfolio reconstruction

Each filing is modeled as an event in a per-parcel timeline. The reconstruction logic applies these rules:

1. `CERT DEL ASSIGN` → sets parcel status to **active**, records holder as grantee
2. `REASSIGN CERTIFICATE OF DEL` → updates holder to new grantee, status remains **active**
3. `DEL TAX RELEASE` or `3RD PTY TAX REL` or `IN HOUSE REL` → sets status to **released**
4. A subsequent assignment after a release re-opens the parcel as **active**
5. If the event chain is ambiguous (e.g., release without prior assignment in our dataset), status is **unknown**

**Important**: "Active" means no release has been recorded in the data we collected. It does not rule out releases filed but not yet indexed, or resolutions through other mechanisms.

## Validation

- **Sample QA**: A random sample of 20-30 records was manually verified against source documents
- **Count cross-reference**: Total records per instrument type were compared against DOR county-level totals (when available)
- **Gap tracking**: Known truncations, parsing failures, and unmatched records are logged in `data/interim/gaps_log.csv`

## Limitations

1. **Web interface caps**: The 1,000-record limit means the web-scraped dataset may be incomplete. Open-records data, when received, will supersede.
2. **Temporal lag**: Records reflect filings as of the scrape date. Recent filings may not yet be indexed.
3. **Address matching noise**: Clerk records and GIS parcels use different address formats. Some joins will be wrong.
4. **No payoff data**: Face amounts on filings do not reflect accrued interest, fees, or partial payments. Actual current debt is not determinable from public records alone.
5. **Entity inference**: Grouping related entities involves judgment calls. The grouping logic is disclosed but may over- or under-group.
6. **Survivorship bias**: Only properties with recorded filings are captured. Properties where certificates were purchased but never recorded (if that occurs) would be invisible.

## Manual QA Results (2026-03-22)

**Automated count verification:**

| Query | HTML records | CSV records | Match |
|-------|-------------|-------------|-------|
| KY Lien Holdings (grantee) | 176 | 176 | ✓ |
| KY Lien Holdings (grantor) | 169 | 169 | ✓ |
| Five Four Lean (both) | 66 | 66 | ✓ |
| Purchase Area Lien Holdings (both) | 29 | 29 | ✓ |
| Kings Right LLC (both) | 361 | 361 | ✓ |

No duplicate book/page numbers in combined dataset. No records with empty book/page.

**Spot-check QA (3 records verified against source HTML):**

| Book/Page | Date | Grantee | Grantor | Address (from HTML) | Match |
|-----------|------|---------|---------|---------------------|-------|
| 475/541 | 2010/07/20 | KY Lien Holdings LLC | WITHERS BILLIE R | 1003 MARCELLUS DR | ✓ |
| 808/1 | 2023/07/24 | Five Four Lean LLC | DOUGLAS KAREN | 438 HAWKINS AVE 40508 | ✓ |
| 808/140 | 2023/07/24 | Purchase Area Lien Holdings LLC | DAUGHERTY JAMES W | 837 E SEVENTH ST 40505 | ✓ |

All verified instrument types, recording dates, party names, and property descriptions match source HTML exactly.
