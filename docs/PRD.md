# Product Requirements Document: Fayette Tax Lien Watch

## 1. Problem statement

Kentucky law allows county clerks to sell delinquent property tax certificates to third-party purchasers. Once sold, the original tax debt accrues 12% simple interest plus administrative fees, and the purchaser can pursue enforcement suits after a one-year tolling period. In Fayette County, the County Clerk has noted that approximately 1,500 delinquent bills were under $100 while only ~23 exceeded $1,000 (2024 data, WEKU). This raises the question of whether a small number of purchasers are systematically acquiring large portfolios of small-debt certificates, and what spatial and social patterns result.

No public dataset currently answers this question. The data exists across multiple government systems but has never been assembled, reconciled, or mapped.

## 2. Research questions

| # | Question | Evidence required |
|---|----------|-------------------|
| RQ1 | How many Fayette properties have had delinquent-tax certificates assigned to KY Lien Holdings, LLC? | Complete filing count from clerk records |
| RQ2 | How many appear still active vs released/reassigned? | Event-chain reconstruction per parcel |
| RQ3 | What is the original face-value debt, and where obtainable, the current payoff? | Bill amounts from filings or tax bill lookup |
| RQ4 | Where are these properties located, and what patterns emerge by neighborhood, land use, and debt size? | Spatial join to parcel geometry |
| RQ5 | What is the company/ecosystem around KY Lien Holdings and related Ramey-linked entities? | Purchaser lists, SOS filings, litigation records |

## 3. Users and stakeholders

- **Primary**: Christine, Director of Seedleaf — presenting to City Council, needs testimony-ready evidence
- **Secondary**: Journalists, legal aid organizations, neighborhood advocates
- **Tertiary**: Other Kentucky counties investigating similar patterns

## 4. Deliverables

### Data outputs (pipeline products)
| Deliverable | Format | Description |
|-------------|--------|-------------|
| Lien event table | CSV + Parquet | Every relevant filing as a timestamped event |
| Portfolio status table | CSV | Current status per parcel (active/released/reassigned) |
| Parcel-joined dataset | GeoJSON + CSV | Events joined to Fayette parcel geometry |
| Entity registry | CSV | Normalized entity records with confidence tags |

### Analytical outputs
| Deliverable | Format | Description |
|-------------|--------|-------------|
| Summary statistics | Markdown table | Counts, totals, breakdowns by status/year/area |
| Spatial maps | GeoJSON + PNG | Active and historical lien locations |
| Neighborhood/district rollups | CSV + charts | Counts and debt totals by geography |

### Communication outputs (built AFTER data work stabilizes)
| Deliverable | Format | Description |
|-------------|--------|-------------|
| Council brief (1-pager) | PDF/Markdown | Hard facts, process facts, impact evidence, policy argument — clearly separated |
| Methods and limitations | Markdown | Full methodology disclosure for credibility |

## 5. Data model

### Lien event record
```
parcel_id               -- Fayette PVA parcel identifier
bill_number             -- tax bill number if available
tax_year                -- year of the delinquent tax
property_address        -- address from filing
owner_name_at_event     -- property owner at time of filing
instrument_type         -- CERT DEL ASSIGN | REASSIGN CERTIFICATE OF DEL | DEL TAX RELEASE | 3RD PTY TAX REL | IN HOUSE REL
instrument_number       -- clerk filing number (unique key)
recording_date          -- date recorded
grantor                 -- party granting (typically county or prior holder)
grantee                 -- party receiving (typically purchaser or owner on release)
face_amount             -- dollar amount if present on filing
source_url              -- URL to source record
source_doc_id           -- document identifier in source system
notes                   -- free text for anything anomalous
```

### Entity record
```
entity_id               -- internal identifier
legal_entity_name       -- name as it appears in filings
normalized_name         -- cleaned/standardized name
entity_type             -- LLC | individual | law_firm | government
principal_contact       -- named individual if known
address                 -- registered or mailing address
phone                   -- if available
email                   -- if available
years_active            -- years appearing in purchaser lists or filings
source                  -- where this entity was found
related_entities        -- list of entity_ids believed related
confidence_same_family  -- high | medium | low
evidence_note           -- what supports the relationship claim
```

### Parcel status (derived)
```
parcel_id
property_address
current_holder          -- entity currently holding certificate, or NULL if released
current_status          -- active | released | reassigned | unknown
first_assignment_date
most_recent_event_date
most_recent_event_type
total_events
original_face_amount
tax_years_affected      -- list
```

## 6. Data acquisition strategy

### Phase 1: Web scraping (immediate)
Query Fayette Land Records for each instrument type, partitioned to stay under 1000-record cap:
- By instrument type (5 types)
- By year range if needed
- By party name (KY Lien Holdings, Ramey, etc.)

Validate completeness by comparing total counts across query strategies.

### Phase 2: Open records requests (file on Day 1)
1. **Fayette County Clerk**: All filings for delinquent-tax instrument types, 2016–present, in machine-readable format
2. **KY Department of Revenue**: Annual Fayette County certificate-of-delinquency lists (KRS 134.131), all available years
3. **Fayette County Clerk**: Certificates excluded from sale, delinquency notice logs

### Phase 3: Supplementary sources
- KY Secretary of State: LLC filings for KY Lien Holdings and related entities
- Fayette Circuit Court: litigation involving KY Lien Holdings
- DOR purchaser lists: 2016, 2023, 2024, 2025 (already identified)
- Lexington GIS open data: parcel boundaries and attributes

## 7. Technical approach

### Scraping
- Start with `httpx` + `BeautifulSoup` (the Fayette clerk site appears server-rendered)
- If JS rendering is required, escalate to Playwright
- Throttle: minimum 2 seconds between requests
- Checkpoint: save progress after each query batch; resume from checkpoint on restart
- Archive: save raw HTML alongside parsed CSV for auditability

### Reconstruction
- Model every filing as an event
- Sort events by parcel + date
- Apply state machine: ASSIGN → active, RELEASE → released, REASSIGN → holder change
- Flag ambiguous cases (e.g., assignment without matching parcel, duplicate instrument numbers)

### Spatial join
- Primary join key: parcel_id (when available in filing)
- Fallback: address geocoding against parcel centroids with confidence score
- Never auto-merge on fuzzy match alone; flag for manual review

### Validation
- Compare scraper record counts against DOR county-level totals
- Sample 20-30 records for manual QA against source documents
- Track known-missing records (truncation, parsing failures) in a gaps log

## 8. Constraints and risks

| Risk | Mitigation |
|------|------------|
| 1000-record web cap truncates results | Partition queries; file open-records requests for complete data |
| Address matching between clerk and GIS is noisy | Confidence scoring; manual review queue; prefer parcel_id when available |
| Entity relationships are inferred, not proven | Confidence tags; separate "same entity" from "related entity" |
| Data may be stale (records lag reality) | Date-stamp all observations; note data-as-of dates |
| Project could be used to harass individuals | Focus on institutional patterns, not individual property owners; aggregate where possible |
| Methodology challenged in public forum | Full methods disclosure; conservative claims; separate fact/inference/argument |

## 9. Sprint plan

### Sprint 0 (Days 1-3): Foundation
- [ ] Scaffold repo, initialize git, write CLAUDE.md
- [ ] Inventory all sources with URLs, field lists, access methods, and known limits
- [ ] Archive DOR purchaser lists and clerk manual
- [ ] Draft and file open-records requests
- [ ] Prototype scraper: single instrument type, single year, validate output
- [ ] First 20-record manual QA

### Sprint 1 (Days 4-7): Core data
- [ ] Complete scraping across all instrument types and years
- [ ] Build event table
- [ ] Build reconstruction logic (event → parcel status)
- [ ] Validate counts against available DOR totals
- [ ] Entity resolution pass

### Sprint 2 (Days 8-10): Spatial and summary
- [ ] Download and prep Fayette parcel layer
- [ ] Join events to parcels
- [ ] Generate maps and summary tables
- [ ] Identify and investigate anomalies

### Sprint 3 (Days 11-14): Communication
- [ ] Write methods and limitations document
- [ ] Draft council brief
- [ ] Peer review of methodology and claims
- [ ] Final deliverable package

## 10. Success criteria

The project succeeds if it can answer RQ1-RQ5 with:
- Verifiable source attribution for every claim
- Stated confidence levels and known gaps
- Reproducible pipeline (another analyst can re-run and get the same results)
- Clear separation of fact, inference, and argument in all outputs
