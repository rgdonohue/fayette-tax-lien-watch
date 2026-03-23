---
name: qa-records
description: Quality-assurance check on scraped or processed records. Validates data completeness, field coverage, anomalies, and cross-references counts against expected totals.
argument-hint: <path-to-csv-or-parquet>
---

# QA Records

Run quality assurance on the dataset at the given path.

## Checks to perform

1. **Row count**: How many records? Compare against expected total if known.
2. **Field completeness**: For each column, what % of values are non-null? Flag columns below 80%.
3. **Uniqueness**: Is the primary key (instrument_number) actually unique? Report duplicates.
4. **Date sanity**: Are all recording_dates within expected range (2010-present)? Flag future dates or pre-2000 dates.
5. **Instrument type distribution**: Count by instrument_type. Flag unexpected types.
6. **Party name patterns**: Most frequent grantors and grantees. Flag blanks.
7. **Amount distribution**: Min, max, median, mean of face_amount. Flag negatives or implausible values (> $1M for tax liens).
8. **Parcel coverage**: What % of records have a parcel_id? What % have a property_address?
9. **Truncation check**: If any query partition returned exactly 1000 records, flag it as likely truncated.

## Output

Print a structured QA report to stdout. Flag issues with severity:
- **CRITICAL**: Data integrity problems (duplicates, impossible values)
- **WARNING**: Completeness gaps that affect analysis
- **INFO**: Observations worth noting

If the file is a parquet, use pandas. If CSV, use pandas with appropriate encoding detection.

Refer to `docs/data_dictionary.md` for expected field names and types.
