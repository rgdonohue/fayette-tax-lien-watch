# Fayette Tax Lien Watch

Public-interest data investigation into third-party tax lien certificate purchasing in Fayette County, Kentucky.

This repository assembles public records from the Fayette County Clerk, the Fayette delinquent-tax lookup, Kentucky Department of Revenue purchaser lists, and Lexington GIS. The goal is to reconstruct purchaser portfolios, estimate recorded lien status, and produce testimony-ready analytical outputs with transparent methods and limitations.

## What This Repository Contains

The current project focuses on six related questions:

1. How many Fayette properties have had certificates of delinquency assigned to identified purchasers?
2. How many appear released, reassigned, or still unreleased in the land records?
3. What do the underlying delinquent-tax bills look like by size and year?
4. Where are the affected properties located by council district and neighborhood?
5. What entity relationships can be documented from purchaser lists, SOS records, and land records?
6. What claims can be supported conservatively in a public-facing brief?

The repository is designed to support both analysis and external scrutiny. Derived claims should be traceable back to source files and to the methodology in [docs/methodology.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/methodology.md).

## Current Outputs

Primary public-facing deliverables:

- [outputs/reports/council_brief.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/outputs/reports/council_brief.md): council-oriented research brief.
- [docs/methodology.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/methodology.md): methods, validation, and limitations.
- [outputs/tables/portfolio_summary.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/outputs/tables/portfolio_summary.md): reconstructed portfolio summary.
- [outputs/tables/spatial_summary.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/outputs/tables/spatial_summary.md): district and neighborhood rollups.
- [outputs/maps/portfolio_map_all_entities.png](/Users/richard/Documents/projects/fayette-tax-lien-watch/outputs/maps/portfolio_map_all_entities.png): all-entity map.
- [outputs/maps/portfolio_by_district.png](/Users/richard/Documents/projects/fayette-tax-lien-watch/outputs/maps/portfolio_by_district.png): district map.

Key analytical datasets:

- [data/processed/entity_registry.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/entity_registry.csv)
- [data/processed/dor_purchasers_fayette.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/dor_purchasers_fayette.csv)
- [data/processed/ky_lien_holdings_portfolio.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/ky_lien_holdings_portfolio.csv)
- [data/processed/five_four_lean_portfolio.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/five_four_lean_portfolio.csv)
- [data/processed/purchase_area_lien_portfolio.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/purchase_area_lien_portfolio.csv)
- [data/processed/kings_right_portfolio.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/kings_right_portfolio.csv)
- [data/processed/portfolio_geocoded.csv](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/portfolio_geocoded.csv)
- [data/processed/summary_stats.json](/Users/richard/Documents/projects/fayette-tax-lien-watch/data/processed/summary_stats.json)

## Repository Layout

```text
.
├── LICENSE
├── README.md
├── requirements.txt
├── scripts/
│   ├── scrape_land_records.py
│   ├── scrape_delinquent_bills.py
│   ├── analyze_portfolio.py
│   └── geocode_portfolio.py
├── docs/
│   ├── PRD.md
│   ├── methodology.md
│   ├── data_dictionary.md
│   ├── open_records_requests.md
│   ├── source_recon_dor.md
│   ├── source_recon_fayettedeeds.md
│   └── source_recon_gis.md
├── data/
│   ├── raw/         # archived source files; ignored by git except placeholders
│   ├── interim/     # scraped and intermediate tables
│   └── processed/   # analytical outputs used by reports
└── outputs/
    ├── maps/
    ├── reports/
    └── tables/
```

## Data Sources

- Fayette County Land Records Search: recorded certificate assignments, releases, and reassignments.
- Fayette County Delinquent Tax Search: current bill-level delinquency records.
- Kentucky Department of Revenue purchaser lists: annual third-party purchaser registrations by county.
- Lexington-Fayette Urban County Government GIS: geocoding and district / neighborhood overlays.

Recon notes and URL inventory are kept in:

- [docs/source_recon_fayettedeeds.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/source_recon_fayettedeeds.md)
- [docs/source_recon_dor.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/source_recon_dor.md)
- [docs/source_recon_gis.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/source_recon_gis.md)

## Environment Setup

Use Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies include:

- `httpx`, `beautifulsoup4`, `lxml` for scraping and parsing
- `pandas` for tabular analysis
- `geopandas`, `shapely`, `matplotlib` for spatial processing and maps
- `jupyter` for exploration

## Workflow

The intended pipeline is:

1. Scrape source systems into `data/interim/`
2. Reconstruct portfolio status from land-record event chains
3. Build processed outputs in `data/processed/`
4. Produce markdown tables and maps in `outputs/`
5. Draft public-facing materials using only claims supported by the data and methods docs

Typical commands:

```bash
source .venv/bin/activate
python scripts/scrape_land_records.py
python scripts/scrape_delinquent_bills.py
python scripts/analyze_portfolio.py
python scripts/geocode_portfolio.py
```

The repo does not currently use a single orchestration entrypoint or Makefile. Scripts are intended to be run explicitly and inspected between stages.

## Script Responsibilities

- [scripts/scrape_land_records.py](/Users/richard/Documents/projects/fayette-tax-lien-watch/scripts/scrape_land_records.py): collects clerk land-record filings for targeted entities / instrument types.
- [scripts/scrape_delinquent_bills.py](/Users/richard/Documents/projects/fayette-tax-lien-watch/scripts/scrape_delinquent_bills.py): collects delinquent-tax bill records.
- [scripts/analyze_portfolio.py](/Users/richard/Documents/projects/fayette-tax-lien-watch/scripts/analyze_portfolio.py): reconstructs event chains and produces summary outputs.
- [scripts/geocode_portfolio.py](/Users/richard/Documents/projects/fayette-tax-lien-watch/scripts/geocode_portfolio.py): geocodes addresses and assigns council districts / neighborhoods.

## Data Model and Interpretation

Canonical field definitions are in [docs/data_dictionary.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/data_dictionary.md).

Two points matter for interpretation:

- `active` in portfolio outputs means no matching release was found in the collected land records. It does not, by itself, prove current legal enforceability.
- Entity-family groupings are analytical judgments based on documentary evidence. They should be described as documented relationships or high-confidence linkages, not as proven alter-ego findings.

## Methodological Guardrails

This project is conservative by design. It aims to separate:

- documented fact from inference
- land-record status from legal status
- entity identity from relationship evidence
- descriptive analysis from policy argument

Important limitations include:

- clerk search result caps and possible truncation
- index lag in public record systems
- imperfect address extraction and geocoding
- incomplete DOR registration snapshots for some years
- absence of court-docket outcomes in the current pipeline

Read [docs/methodology.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/methodology.md) before relying on headline counts or legal characterizations.

## Reproducibility Notes

- `data/raw/` is treated as archival source material and is ignored by git except for placeholders.
- `data/interim/` and `data/processed/` are tracked because they are compact enough to audit and are part of the analytical record.
- The repository is suitable for public review because the tracked Git history currently contains no large objects near common Git hosting limits.

## Open Records and Follow-Up Work

Open-records request drafts are in [docs/open_records_requests.md](/Users/richard/Documents/projects/fayette-tax-lien-watch/docs/open_records_requests.md).

High-value next steps include:

- obtaining complete clerk exports to eliminate web-cap uncertainty
- obtaining complete DOR purchaser lists for disputed years
- checking Fayette Circuit Court dockets for enforcement actions
- standardizing all spatial outputs to one unit of analysis

## License

This repository is licensed under the MIT License. See [LICENSE](/Users/richard/Documents/projects/fayette-tax-lien-watch/LICENSE).
