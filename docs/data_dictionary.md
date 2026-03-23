# Data Dictionary

Canonical field reference for all datasets in this project. Any script or notebook that produces or consumes tabular data should conform to these definitions.

## Lien Event Table (`fayette_lien_events`)

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `instrument_number` | string | Unique filing number from clerk's office (primary key) | Fayette Land Records |
| `instrument_type` | enum | One of: CERT DEL ASSIGN, REASSIGN CERTIFICATE OF DEL, DEL TAX RELEASE, 3RD PTY TAX REL, IN HOUSE REL | Fayette Land Records |
| `recording_date` | date | Date the instrument was recorded | Fayette Land Records |
| `parcel_id` | string | Fayette PVA parcel identifier, if present in filing | Fayette Land Records |
| `bill_number` | string | Tax bill number, if present | Fayette Land Records / Tax Bill Search |
| `tax_year` | integer | Tax year of the delinquent bill | Fayette Land Records |
| `property_address` | string | Property address as listed in filing | Fayette Land Records |
| `owner_name_at_event` | string | Property owner name at time of filing | Fayette Land Records |
| `grantor` | string | Party granting the instrument | Fayette Land Records |
| `grantee` | string | Party receiving the instrument | Fayette Land Records |
| `face_amount` | decimal | Dollar amount on filing, if present | Fayette Land Records |
| `source_url` | string | Direct URL to source record | Fayette Land Records |
| `source_doc_id` | string | Document ID in source system | Fayette Land Records |
| `scrape_date` | date | Date this record was collected | Pipeline metadata |
| `notes` | string | Free text for anomalies or context | Manual annotation |

## Entity Registry (`entity_registry`)

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Internal unique identifier |
| `legal_entity_name` | string | Name exactly as it appears in source records |
| `normalized_name` | string | Cleaned, standardized name |
| `entity_type` | enum | LLC, individual, law_firm, government |
| `principal_contact` | string | Named individual if known |
| `address` | string | Registered or mailing address |
| `phone` | string | If available |
| `email` | string | If available |
| `years_active` | list[int] | Years appearing in purchaser lists or filings |
| `source` | string | Where this entity was identified |
| `related_entities` | list[string] | Entity IDs believed related |
| `confidence_same_family` | enum | high, medium, low |
| `evidence_note` | string | What supports the relationship claim |

## Parcel Status (derived: `parcel_lien_status`)

| Field | Type | Description |
|-------|------|-------------|
| `parcel_id` | string | Fayette PVA parcel identifier |
| `property_address` | string | Best-known address |
| `current_holder` | string | Entity currently holding certificate (NULL if released) |
| `current_status` | enum | active, released, reassigned, unknown |
| `first_assignment_date` | date | Earliest assignment event |
| `most_recent_event_date` | date | Latest event of any type |
| `most_recent_event_type` | string | Instrument type of latest event |
| `total_events` | integer | Count of all events for this parcel |
| `original_face_amount` | decimal | Face amount from first assignment |
| `tax_years_affected` | list[int] | All tax years with events |

## Enumerated Values

### instrument_type
| Value | Meaning |
|-------|---------|
| `CERT DEL ASSIGN` | Certificate of delinquency assigned to third-party purchaser |
| `REASSIGN CERTIFICATE OF DEL` | Certificate reassigned from one holder to another |
| `DEL TAX RELEASE` | Delinquent tax lien released (debt paid or resolved) |
| `3RD PTY TAX REL` | Third-party tax release |
| `IN HOUSE REL` | In-house release (county-initiated) |

### current_status
| Value | Meaning |
|-------|---------|
| `active` | Certificate currently held by a third party (no subsequent release/reassignment) |
| `released` | Most recent event is a release |
| `reassigned` | Most recent event is a reassignment to a different holder |
| `unknown` | Event chain is ambiguous or incomplete |
