# Spatial Analysis: Ramey-Linked Tax Lien Properties
*Fayette County, KY | Data as of 2026-03-22*

## Geocoding Summary

- Total rows in portfolio: **204** (146 KY Lien Holdings properties + 42 Five Four Lean certs + 16 Purchase Area Lien certs)
- Successfully geocoded (score ≥ 70): **179** (88%)
- Not geocoded (no address or low score): 25

*Note: KY Lien Holdings rows are property-level (one row per unique property); Five Four Lean
and Purchase Area Lien rows are cert-level (properties with multiple certs appear as separate rows).*

## By Council District

| District | Total | Active | Released | Reassigned | KY Lien | Five Four Lean | Purchase Area Lien |
|----------|-------|--------|---------|------------|---------|--------------|-------------------|
| 1 | 39 | 8 | 30 | 1 | 25 | 8 | 6 |
| 2 | 16 | 6 | 10 | 0 | 10 | 5 | 1 |
| 3 | 12 | 0 | 11 | 1 | 10 | 2 | 0 |
| 4 | 7 | 0 | 4 | 3 | 5 | 2 | 0 |
| 5 | 8 | 0 | 8 | 0 | 7 | 1 | 0 |
| 6 | 9 | 2 | 6 | 1 | 7 | 1 | 1 |
| 7 | 15 | 2 | 13 | 0 | 13 | 2 | 0 |
| 8 | 7 | 0 | 7 | 0 | 6 | 1 | 0 |
| 9 | 13 | 2 | 11 | 0 | 13 | 0 | 0 |
| 10 | 11 | 1 | 8 | 2 | 7 | 4 | 0 |
| 11 | 17 | 3 | 14 | 0 | 10 | 5 | 2 |
| 12 | 25 | 1 | 23 | 1 | 13 | 8 | 4 |
| Unknown | 25 | 1 | 22 | 2 | 20 | 3 | 2 |

## Top Neighborhoods by Activity

| Neighborhood | Total Certs | Active |
|-------------|------------|--------|
| William Wells Brown Neighborhood Assoc | 10 | 3 |
| Clays Ferry Nghd Assoc | 7 | 1 |
| Liberty Area Nghd Assoc | 4 | 1 |
| Melrose-Oak Park | 4 | 3 |
| Woodhill Neighborhood Organization | 4 | 0 |
| Castlewood Nghd Assoc | 3 | 0 |
| Deerfield Comm Assoc Inc | 3 | 0 |
| East End Community Development Corporation | 3 | 0 |
| Garden Springs Nghd Assoc | 3 | 0 |
| Joyland Neighborhood Association | 3 | 1 |
| Kenwick Nghd Assoc | 3 | 0 |
| Mcconnell's Trace Nghd Assoc Inc | 3 | 2 |
| Aylesford Place Neighborhood Association | 2 | 0 |
| Belleau Wood Nghd Assoc. | 2 | 0 |
| Calumet Area Nghd Assoc | 2 | 0 |
| Cardinal Valley Nghd Assoc | 2 | 0 |
| East Lake Nghd Assoc | 2 | 0 |
| North Pointe Neighborhood Association | 2 | 0 |
| Northside Nghd Assoc | 2 | 1 |
| Plantation Nghd Assoc | 2 | 0 |
| Southern Heights Nghd | 2 | 0 |

## Methodology Notes

- Addresses geocoded using LFUCG municipal geocoder (maps.lexingtonky.gov)
- Minimum confidence score of 70/100 required for spatial join
- Council district assignment via point-in-polygon query against LFUCG Council District layer (2020 Census boundaries)
- Properties with no extractable address or low geocode confidence appear in "Unknown" district
- "Active" means unreleased in land records — it does not mean currently enforceable (see KRS 134.546 re: 11-year limitation)
- Counts are row-level: KY Lien Holdings is property-level; FFL and PAL are cert-level
