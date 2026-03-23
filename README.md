# Fayette Tax Lien Watch

Public-interest data investigation into third-party tax lien certificate purchasing in Fayette County, Kentucky.

## Research questions

1. How many Fayette properties have had delinquent-tax certificates assigned to KY Lien Holdings, LLC?
2. How many appear still active versus released/reassigned?
3. What is the original face-value debt?
4. Where are these properties located, and what spatial patterns emerge?
5. What is the entity ecosystem around KY Lien Holdings and related entities?

## Project structure

```
├── CLAUDE.md              # Project conventions and context for AI-assisted development
├── docs/
│   ├── PRD.md             # Product requirements document
│   ├── data_dictionary.md # Canonical field definitions
│   ├── methodology.md     # Methods, validation, limitations
│   └── open_records_requests.md  # Draft KORA requests
├── data/
│   ├── raw/               # Untouched source data (never modify)
│   ├── interim/           # Cleaned/intermediate data
│   └── processed/         # Final analytical outputs
├── notebooks/             # Exploratory Jupyter notebooks
├── scripts/               # Production data pipeline scripts
└── outputs/
    ├── figures/
    ├── tables/
    └── maps/
```

## Data sources

- [Fayette County Land Records](https://www.fayettedeeds.com/landrecords/index.php) — certificate assignments, releases, reassignments
- [Fayette County Tax Bills](https://www.fayettedeeds.com/delinquent/index.php) — delinquent bill lookup
- [KY DOR Third-Party Purchaser Lists](https://revenue.ky.gov/Property/pages/third-party-purchaser.aspx) — registered purchaser entities
- [Lexington GIS](https://www.lexingtonky.gov/government/departments-programs/chief-information-officer/geographic-information-services-gis) — parcel geometry

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Analytical guardrails

This project separates:
- **Active holdings** from historical appearances
- **Legal entity identity** from relationship inference
- **Evidence of a system** from evidence of harm

All claims trace to source documents. See `docs/methodology.md` for full methods disclosure.
