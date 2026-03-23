# Source Recon: fayettedeeds.com

**Date:** 2026-03-21
**Target URLs:**
- Land Records: `https://www.fayettedeeds.com/landrecords/index.php`
- Tax Bill / Delinquent: `https://www.fayettedeeds.com/delinquent/index.php`

**Platform vendor:** Business Information Systems (bisonline.com) -- PHP + jQuery + DataTables
**CDN:** `cdn.bisonline.com`

---

## 1. Anti-Bot / Access Controls

| Check | Finding |
|-------|---------|
| robots.txt | **404 -- does not exist.** No crawl restrictions declared. |
| CAPTCHA | None detected on any page. |
| CSRF tokens | **None.** No hidden CSRF/nonce fields in any form. |
| Rate limiting | No evidence of rate-limit headers (`X-RateLimit`, `Retry-After`, etc.). |
| WAF / Cloudflare | Not detected. Plain Apache server. |
| Login required | **No.** Public access; no auth wall. |
| Session management | PHP sessions (`PHPSESSID` cookie). Server sets it on first request. Required for land records multi-step flow. |
| JavaScript requirement | **Delinquent search: No JS needed.** Results are fully server-rendered HTML. **Land records: JS needed** for multi-step flow (pick list -> storeEID AJAX -> tab load). |

---

## 2. Recommended HTTP Approach

### Delinquent Tax Search (PRIMARY target for this project)

**Recommendation: httpx (plain HTTP, no browser needed)**

- Form uses `method="GET"` with simple query params
- Results are **fully server-rendered** in a single HTML table
- Detail pages load via simple GET to `details.php?InstNum={id}`
- No JavaScript execution required to retrieve data
- No CSRF tokens or complex session management needed

### Land Records Search

**Recommendation: Playwright (browser automation required)**

The land records search uses a complex multi-step flow:
1. POST the `davidson_form` to get a **Pick List** (list of matching names + counts)
2. User clicks checkboxes, which fire AJAX calls to `ajaxActions.php` with `action=storeEID` to store selected names in the server-side session
3. `submitPickList()` calls `ajaxActions.php` with `action=checkEID`, then dynamically adds a jQuery UI tab that POSTs to `index.php` with serialized form data via `storeDataString` AJAX
4. Results render in the new tab via server response

This flow depends on:
- jQuery UI tabs
- Multiple sequential AJAX calls to `ajaxActions.php`
- Session state (selected names stored server-side)
- Dynamic tab creation

A headless browser or very careful session replay with httpx (replicating the AJAX calls) would be needed.

---

## 3. Delinquent Tax Bill Search -- Form Inventory

**URL:** `https://www.fayettedeeds.com/delinquent/index.php`
**Method:** `GET`
**Action:** `index.php` (same page, self-submitting)

### Form Fields

| Field Name | Type | Label | Notes |
|------------|------|-------|-------|
| `lastName` | text | Last Name | Partial match (prefix). Case-insensitive. |
| `firstName` | text | First Name | |
| `billNumber` | text | Bill Number | Unique bill identifier |
| `taxYear` | text | Tax Year | 4-digit year (e.g., `2024`) |
| `accNum` | text | Account/Parcel Number | PVA parcel number |
| `addr1` | text | Address 1 | Property address |
| `delBills` | checkbox | Show Only Delinquent Bills | Value: `on` when checked |
| `executeSearch` | hidden | (trigger) | Value: `1` -- **required** to trigger search |

### Example Request

```
GET /delinquent/index.php?lastName=&firstName=&billNumber=&taxYear=2024&accNum=&addr1=&delBills=on&executeSearch=1
```

### Validation

- Client-side only (simple `validate()` that shows a loading animation)
- No server-side field requirements beyond `executeSearch=1`
- Empty search with just `executeSearch=1` returns results (all records)

---

## 4. Delinquent Tax Search -- Results Structure

Results are server-rendered in a single `<table class="table table-striped table-bordered table-hover">`.

### List View Columns

| Column | HTML Details |
|--------|-------------|
| Bill Number | `<a onclick="showDetails({InstNum})">` -- the InstNum is on the `<tr>` as attribute `InstNum="{id}"` |
| Year | Tax year of the bill |
| Status | `Delinquent` or `Paid` (has class `uppercase`) |
| Description | Property address / description |
| Purchaser | Tax lien purchaser info (may include phone/email links, often empty) |
| Owner | Property owner name |

### Key HTML Patterns for Parsing

```html
<tr bgcolor="#eaecef" InstNum="2025042390003">
    <td align="left">
        <a class="blueLink" onclick="showDetails(2025042390003);">345</a>
    </td>
    <td align="left">2024</td>
    <td align="left" class="uppercase">Delinquent</td>
    <td align="left">398 E FIFTH ST</td>
    <td align="left" class="purchaser">
        </br>
        <a class="blueLink" href="tel:"></a><br/>
        <a class="blueLink" href="mailto:"></a><br/>
    </td>
    <td align="left">Abe Properties Llc</td>
</tr>
```

### Detail Page

**URL:** `https://www.fayettedeeds.com/delinquent/details.php?InstNum={InstNum}`
**Method:** GET (no session required)

Returns three tables with rich detail:

**Table 1 -- Bill Summary:**

| Field | Example |
|-------|---------|
| Owner's Name | ABE PROPERTIES LLC |
| Property Address | 398 E FIFTH ST |
| Face Value | $1843.43 |
| Amount Paid | $0.00 |

**Table 2 -- Sale/Purchase Info:**

| Field | Example |
|-------|---------|
| Account/parcel # | 11886450 |
| Assigned | NO |
| Purchaser | (name, may be empty) |
| Purchaser Address | (address) |
| Tax Year | 2024 |
| Bill # | 345 |
| Amount Paid | $0.00 |
| Date Paid | (date or empty) |
| Paid By | (name or empty) |
| District | 1 |

**Table 3 -- Lien Status:**

| Field | Example |
|-------|---------|
| Assessment | 146500.00 |
| Owed At Sale | $2268.90 |
| Amount Due | $3248.43 |
| Bankruptcy | NO |
| Exonerated | NO |
| Date Exonerated | (date or empty) |
| Released | NO |
| Date Released | (date or empty) |
| Sold | NO |

**Additional APIs on detail page:**
- `taxComments.php` (POST, params: `instNum`, `billYear`) -- returns JSON array of comment strings
- `delinquentTaxCalculator.php` (POST, params: `futureDate`, `instNum`) -- returns JSON with `total` and `feeDetails`

---

## 5. Land Records Search -- Form Inventory

**URL:** `https://www.fayettedeeds.com/landrecords/index.php`
**Method:** `POST`
**Form ID:** `davidson_form`

### Hidden Fields

| Field | Value |
|-------|-------|
| `searchType` | `davidson` |
| `show_pick_list` | `off` |
| `party_type` | (empty) |

### Search Mode (radio: `search_type`)

| Value | Label | Behavior |
|-------|-------|----------|
| `Both` (default) | Search One Name for Both Parties | Shows `both_last_name`, `both_first_name`, `both_middle_initial` |
| `Specified` | Search One Name for Specified Party | Shows separate Grantor and Grantee name fields |
| `Common` | Search For Both Names With Common Specified Instruments | Shows separate Grantor and Grantee name fields |

### Name Fields

**"Both" mode:**
- `both_last_name` -- Last Name/Company
- `both_first_name` -- First Name
- `both_middle_initial` -- MI

**"Specified"/"Common" mode:**
- `grantor_last_name`, `grantor_first_name`, `grantor_middle_initial`
- `grantee_last_name`, `grantee_first_name`, `grantee_middle_initial`

### Property Fields

| Field | Label |
|-------|-------|
| `StreetNum` | Street # |
| `directional` | Directional |
| `streetName` | Street Name |
| `type` | Type |
| `SubName` | Subdivision |
| `lot` | Lot |
| `block` | Block |

### Recording Fields

| Field | Label |
|-------|-------|
| `inst_num` | Instrument # |
| `booknum` | Book # |
| `pagenum` | Page # |
| `suffix` | Suffix |
| `description` | Description |

### Date Range

| Field | Label | Format |
|-------|-------|--------|
| `start_date` | Begin Date | MM/DD/YYYY |
| `end_date` | End Date | MM/DD/YYYY |

### Consideration Range

| Field | Label |
|-------|-------|
| `startamt` | Start Amount |
| `endamt` | End Amount |

### Instrument Type Groups (checkboxes: `instType[{group}]`)

- ALL, ARTICLES, DEEDS, DELINQUENT TAX, FIXTURE FILING, LAND RECORDS, LEASES, LIENS, MISCELLANEOUS, MORTGAGES, PLAT, POWER OF ATTORNEY, RELEASE, WILLS

### Instrument Doc Types (checkboxes: `instDocType[ALL]` or individual `instDocType[$k][{code}]`)

90+ individual types. Key ones for this project:

| Code | Label |
|------|-------|
| 056 | 3RD PTY TAX REL |
| 071 | CERT DEL ASSIGN |
| DT | DELINQUENT TAX (group) |
| 010 | EASEMENT |
| 001 | DEED |
| 002 | DEED OF CORR |
| 009 | DEL TAX RELEASE |
| 011 | DISCLAIMER |
| 030 | FED LIEN |
| 031 | FED TAX RELEASE |
| 033 | JUDGEMENT LIEN |
| 036 | LIS PENDENS |
| 034 | LOCAL CTY LIEN |
| 048 | LOCAL CTY REL |
| 032 | MECHANICS LIEN |
| 020 | MORTGAGE |
| 070 | REASSIGN CERTIFICATE OF DEL |
| 022 | RELEASE |
| 037 | STATE TAX LIEN |
| 039 | STATE TAX REL |

### Land Records Results Columns

When records are displayed (in the Index List tab), the table `#results` has:

| Column ID | Header |
|-----------|--------|
| rc_verify | Record Info (instrument #, book/page) |
| rc_date | Rec. Date |
| rc_grantor | Grantor |
| rc_grantee | Grantee |
| rc_type | Instrument Type |
| rc_desc | Prop. Description |
| rc_xr | Cross-References |
| rc_con | Consideration |
| rc_image | Image? |

---

## 6. Pagination Strategy

### Delinquent Tax Search

- **No server-side pagination.** All results (up to 1000) are returned in a single HTML response.
- Client-side DataTables is initialized with `paging: false` and `searching: false`.
- The 1000-record hard limit is enforced server-side.
- **Strategy:** Use `taxYear` parameter to partition requests by year. A single year's delinquent bills for Fayette County should stay well under 1000 records.

### Land Records Search

- **No server-side pagination.** The Pick List and Index List are returned in full (up to 1000).
- DataTables is initialized with `bPaginate: false` (client-side only).
- The 1000-record limit is emphasized in a red warning banner.
- **Strategy:** Use date ranges (`start_date`/`end_date`) to partition into windows that stay under 1000 records. Narrow instrument type selections also help.

---

## 7. Session Management

### Delinquent Tax Search
- `PHPSESSID` cookie is set on first request
- Not strictly required for search (GET requests work without cookies in testing)
- **Recommendation:** Accept cookies but no special session handling needed

### Land Records Search
- `PHPSESSID` is **critical** -- the multi-step flow stores state server-side:
  - `storeEID` stores selected names
  - `storeDataString` stores serialized form data
  - `checkEID` verifies selections exist
- **Recommendation:** Use a session-aware HTTP client or Playwright. Maintain cookies across the multi-step flow.

---

## 8. Required Headers

Minimal headers work. The server does not enforce `Referer`, `Origin`, or specific `User-Agent`.

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
```

For AJAX calls to `ajaxActions.php`:
```
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
```

---

## 9. Throttling Recommendations

| Parameter | Recommendation |
|-----------|---------------|
| Request delay | 2-3 seconds between requests |
| Concurrency | 1 (single thread) |
| Session reuse | Reuse PHPSESSID across requests in a batch |
| Batch size | One tax year per batch for delinquent search |
| Time of day | Off-peak hours (evenings/weekends) |
| Back-off | If HTTP 429 or 503, exponential back-off starting at 30s |
| Daily limit | ~500 detail page fetches per session; rotate sessions if more needed |

No explicit rate limiting was detected, but the server runs on Apache without visible caching infrastructure. Be respectful of load.

---

## 10. Scraping Strategy Summary

### Priority 1: Delinquent Tax Bills (httpx)

This is the simplest and most valuable target:

1. **List scrape:** `GET /delinquent/index.php?taxYear={year}&delBills=on&executeSearch=1`
   - Parse the HTML table for Bill Number, Year, Status, Description, Purchaser, Owner
   - Extract `InstNum` from `<tr>` attributes
2. **Detail scrape:** `GET /delinquent/details.php?InstNum={id}`
   - Parse three HTML tables for full record detail
   - Key fields: Account/parcel #, Assessment, Owed At Sale, Amount Due, Face Value, Assigned status, Purchaser info, Bankruptcy/Exonerated/Released/Sold flags
3. **Partition by year** to stay under 1000-record limit

### Priority 2: Land Records -- Delinquent Tax Instruments (httpx with session replay OR Playwright)

To search land records for delinquent tax instruments specifically:

**Option A (httpx, session replay):**
1. GET the search page to obtain PHPSESSID
2. POST the `davidson_form` with `instType[DELINQUENT TAX]=DELINQUENT TAX` and date range
3. Parse the Pick List response
4. For each name, POST to `ajaxActions.php` with `action=storeEID`
5. POST to `ajaxActions.php` with `action=storeDataString`
6. GET `index.php?embedded=1` to retrieve the results table

**Option B (Playwright):**
1. Navigate to search page
2. Fill form, select instrument type checkboxes
3. Click Search
4. Select all names in Pick List
5. Click "Show Records"
6. Scrape the results table

---

## 11. Data Freshness

- Land records: "Instruments Verified Through: 3:24 pm on 03/20/2026" (near real-time, same-day)
- Delinquent tax data: Appears to lag slightly; most recent bills observed are 2024 tax year with 2025 instrument numbers

---

## 12. Additional Endpoints Discovered

| Endpoint | Purpose |
|----------|---------|
| `/delinquent/details.php?InstNum={id}` | Full tax bill detail |
| `/delinquent/taxComments.php` | Comments for a bill (POST, JSON response) |
| `/delinquent/delinquentTaxCalculator.php` | Future amount-due calculator (POST, JSON response) |
| `/landrecords/ajaxActions.php` | Session state management for land records (storeEID, clearEID, checkEID, storeDataString, summaryInfo, removeRow) |
| `/landrecords/index.php?searchType=details&inst_num={num}` | Land record instrument detail |
| `/nonIndexed/index.php` | Non-indexed documents |
| `/nontemp.php` | Daily notebook |
| `/marriage/index.php` | Marriage search |
| `/marriageform/index.php` | Marriage license form |
| `/request/` | Session verification endpoint (POST JSON: `action: verifySession`) |
| `/exit.php` | Session termination |
