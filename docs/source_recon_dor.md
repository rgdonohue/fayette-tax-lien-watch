# Kentucky Department of Revenue -- Source Reconnaissance

Last updated: 2026-03-21

## 1. Primary DOR Pages

### 1.1 Third-Party Purchaser Page

- **URL:** <https://revenue.ky.gov/Property/Pages/Third-Party-Purchaser.aspx>
- **Format:** HTML (SharePoint-hosted; returns HTTP 403 to non-browser user-agents but loads in a standard browser)
- **Content:** Central hub for third-party purchaser registration. Links to:
  - Purchaser registration lists (PDF spreadsheets, updated periodically)
  - Application form (PDF)
  - Instructional materials for prospective purchasers
  - Delinquent tax sale date schedules per county

### 1.2 Delinquent Property Tax Page

- **URL:** <https://revenue.ky.gov/Property/Pages/Delinquent-Property-Tax.aspx>
- **Format:** HTML
- **Content:** Overview of the delinquent property tax process. Describes:
  - Certificate of delinquency as a lien against property
  - Interest at 1% per month, 10% county clerk fee, 20% county attorney fee
  - Newspaper advertisement requirement (30+ days before sale)
  - County clerk website listing requirement (30+ days before sale)
  - County lists posted to DOR website by June 1 each year

### 1.3 The Collection Process for Property Tax Bills

- **URL:** <https://revenue.ky.gov/Property/Pages/TheCollectionProcessforPropertyTaxBills.aspx>
- **Format:** HTML
- **Content:** End-to-end timeline:
  - By Oct 1: tax bills mailed; 2% discount if paid by Nov 1
  - Nov 2 -- Dec 31: face amount due
  - January: 5% penalty added
  - Feb 1: penalty increases to 21%
  - After Apr 15 close of business: unpaid bills transfer from sheriff to county clerk
  - At least 90 days after transfer: county clerk conducts tax sale
  - Mid-July through late October: tax sales (majority mid-July through end of August)

### 1.4 Clerk Network Page

- **URL:** <https://revenue.ky.gov/ClerkNetwork/Pages/default.aspx>
- **Format:** HTML
- **Content:** Central hub for county clerk resources. Links to manuals, tax sale date schedules, and third-party purchaser spreadsheets.

---

## 2. Third-Party Purchaser Registration Lists

All lists below are PDF files, directly downloadable. Each lists registered purchasers for a given tax year's delinquent bills.

### 2.1 2016 List

| Field | Description |
|---|---|
| **URL** | <https://revenue.ky.gov/Property/Documents/Thrid%20Party%20Purchasers%20Registered%202016.pdf> |
| **Alt URL** | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/Third%20Party%20Purchasers%20Registered%202016.pdf> |
| **Format** | PDF (91 KB) |
| **Dated** | 07/12/2016 (first URL); 08/18/2016 (alt URL -- likely a later update) |
| **Accessible** | Yes (HTTP 200) |

**Fields (2016 format -- simpler than later years):**
- Name of Third Party
- Principal Address
- Date Eligible to Begin Purchases
- Registration #

### 2.2 2023 List (covers 2022 delinquent tax bills)

| Field | Description |
|---|---|
| **URL** | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/2023-%20Third%20Party%20Purchaser%20Spread%20Sheet%20UPDATED%204-13-23.pdf> |
| **Format** | PDF (275 KB) |
| **Dated** | Updated 4/13/2023 |
| **Accessible** | Yes (HTTP 200) |

**Fields (2023+ expanded format):**
- Date (application received)
- Related Party (YES/NO flag; related-party names noted with asterisks)
- Name of Business
- Principal Contact
- Principal Address
- Email
- Phone
- Registration #
- Purchase Eligibility Date

**Additional 2023 variant:** An earlier snapshot at a different path:
- <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/2023%20-%20Third%20Party%20Purchaser%20Spread%20Sheet%20UPDATED%202-23-23.pdf>

### 2.3 2024 List (covers 2023 delinquent tax bills)

| Field | Description |
|---|---|
| **URL** | <https://revenue.ky.gov/Property/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%202-28-2024.pdf> |
| **Format** | PDF |
| **Dated** | Updated 2/28/2024 |
| **Accessible** | Likely yes (found via search results) |

**Fields:** Same expanded format as 2023 (Date, Related Party, Name of Business, Principal Contact, Principal Address, Email, Phone, Registration #, Purchase Eligibility Date).

### 2.4 2025 Lists (covers 2024 delinquent tax bills)

Multiple snapshots published over time, all PDF:

| Snapshot | URL | Size | Accessible |
|---|---|---|---|
| 1/8/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%201-8-2025.pdf> | -- | Yes |
| 3/28/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%203.28.2025.pdf> | -- | Yes |
| 5/12/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%205.12.2025.pdf> | 342 KB | Yes (HTTP 200) |
| 6/27/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%206.27.2025.pdf> | -- | Yes |
| 7/8/2025 (latest for 2024 bills) | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchaser%20Spreadsheet%20UPDATED%207.8.2025.pdf> | 408 KB | Yes (HTTP 200) |

**Fields:** Same expanded format (Date, Related Party, Name of Business, Principal Contact, Principal Address, Email, Phone, Registration #, Purchase Eligibility Date).

### 2.5 2026 List (covers 2025 delinquent tax bills)

| Field | Description |
|---|---|
| **URL** | <https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%20February%2013,%202026.pdf> |
| **Format** | PDF (283 KB) |
| **Dated** | 2/13/2026 (created); 2/16/2026 (last modified) |
| **Author** | Moore, Luka (DOR) |
| **Accessible** | Yes (HTTP 200) |

**Fields:** Same expanded format:
- Date (application received)
- Related Party (YES/NO)
- Name of Business
- Principal Contact
- Principal Address
- Email
- Phone
- Registration # (format: 2026-NN)
- Purchase Eligibility Date

**Note:** The DOR third-party purchaser page references an even more recent update dated 3/16/2026, but the exact URL for that version was not confirmed. The naming pattern suggests it may be at:
`https://revenue.ky.gov/ClerkNetwork/Documents/Third%20Party%20Purchase%20Spread%20Sheet%20UPDATED%20March%2016,%202026.pdf`
or a date-formatted variant. This should be checked periodically.

---

## 3. URL Pattern Analysis

DOR has migrated file hosting over the years:

| Era | Base Path |
|---|---|
| 2016--2023 | `revenue.ky.gov/Property/Documents/` or `revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/` |
| 2023--present | `revenue.ky.gov/ClerkNetwork/Documents/` (primary) and occasionally `ClerkNetwork/PublishingImages/Pages/default/` |

File naming is inconsistent (spaces, date formats vary: `M.D.YYYY`, `M-D-YYYY`, `Month D, YYYY`). Automated scraping should account for this.

---

## 4. County Clerk Delinquent Tax Sale Date Schedules

All-county schedules showing each county's tax sale date plus whether the DOR approval letter has been sent.

### 2025 Schedule (for 2024 delinquent bills)

| Snapshot | URL | Size | Accessible |
|---|---|---|---|
| 1/8/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Tax%20Sales%20Updates%201-8-2025.pdf> | -- | Yes |
| 1/23/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Tax%20Sales%20Updates%201-23-2025.pdf> | -- | Yes |
| 4/11/2025 | <https://revenue.ky.gov/ClerkNetwork/Documents/Tax%20Sales%20Updated%204.11.2025.pdf> | -- | Yes |
| 7/1/2025 (latest) | <https://revenue.ky.gov/ClerkNetwork/Documents/2025%20County%20Clerk%20Delinquent%20Tax%20Sale%20Updated%207.1.2025.pdf> | 56 KB | Yes (HTTP 200) |

**Fields:**
- COUNTY
- TAX SALE DATE
- App. Letter (checkmark if DOR approval letter sent)

**Fayette County 2025 sale date:** 7/18/2025

### 2024 Schedule (for 2023 delinquent bills)

| Snapshot | URL |
|---|---|
| 2/14/2024 | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/2024%20Delinquent%20Tax%20Sale%20Dates%20UPDATED%20%202-14-2024.pdf> |
| 2/22/2024 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/2024%20Delinquent%20tax%20sale%20dates%202-22-2024.pdf> |
| 8/27/2024 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/2024%20Delinquent%20Tax%20Sale%20Dates%20Updated%208-27-2024.pdf> |

### Historical Schedules

| Year | URL |
|---|---|
| 2023 | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/2023%20Delinquent%20Tax%20Sale%20Dates%20Updated%202-3-23.pdf> |
| 2022 | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/County%20Clerk%202022%20Delinquent%20Property%20%20Tax%20Sale%20Dates%20UPDATED%205-11-22.pdf> |
| 2021 | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/County%20Clerk%202021%20Delinquent%20Property%20%20Tax%20Sale%20Dates%20update%209-1-21.pdf> |

---

## 5. Clerk Manual (Real Property Tax Duties)

| Field | Description |
|---|---|
| **URL** | <https://revenue.ky.gov/ClerkNetwork/Documents/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk's%20Office%20Manual%202025.pdf> |
| **Format** | PDF |
| **Size** | 4,181,903 bytes (~3.99 MB) |
| **Accessible** | Yes (HTTP 200) |
| **Last manual update** | 6/26/2025 per Clerk Network page |

**Note on requested URL:** The originally requested URL using `%27` (URL-encoded straight apostrophe) also resolves correctly:
`https://revenue.ky.gov/ClerkNetwork/Documents/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk%27s%20Office%20Manual%202025.pdf`

### Historical Clerk Manuals

| Edition | URL |
|---|---|
| 2023-2024 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk's%20Office%20Manual%20Dec%202023-2024.pdf> |
| 2022 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk's%20Office%20Manual%202022.pdf> |
| 2021 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk's%20Office%20Manual%202021.pdf> |
| 2018 | <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/Real%20Property%20Tax%20Duties%20of%20the%20County%20Clerk's%20Office%20Manual%202018.pdf> |

---

## 6. Application and Instructional Documents

### 6.1 Application for Certificate of Registration

- **URL:** <https://revenue.ky.gov/Documents/ApplicationForCertificateofRegistrationtoPurchaseCertificatesofDelinquency.pdf>
- **Format:** PDF (65 KB)
- **Accessible:** Yes (HTTP 200)

### 6.2 Application Form 62A370A

| Version | URL |
|---|---|
| 10-18 (current) | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/62A370A%20(10-18).pdf> |
| 10-17 | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/62A370A%20(10-17).pdf> |

- **Format:** PDF (116 KB for 10-18 version)
- **Accessible:** Yes (HTTP 200)

### 6.3 Instructions for Third Party Purchaser

- **URL:** <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/INSTRUCTIONS%20FOR%20THIRD%20PARTY%20PURCHASER.pdf>
- **Format:** PDF
- **Accessible:** Yes

### 6.4 Basic Information for Potential Third Party Purchasers

| Version | URL | Size |
|---|---|---|
| Current (Property/Documents) | <https://revenue.ky.gov/Property/Documents/Basic%20Information%20About%20Buying%20And%20Collecting%20On%20Certificates%20Of%20Delinquency%20For%20Potential%20Third%20Party%20Purchasers.pdf> | 782 KB |
| Older (top-level Documents) | <https://revenue.ky.gov/Documents/PotentialThirdPartyPurchasersManual.pdf> | 102 KB |
| Oct 2022 updated | <https://revenue.ky.gov/Property/PublishingImages/Pages/Third-Party-Purchaser/Oct%202022-Potential%20Third%20Party%20Purchasers%20Manual%20UPDATED%2010-3-22.pdf> | -- |

- **Format:** PDF
- **Accessible:** Yes (HTTP 200)

### 6.5 Installment Payment Plan Calculator Instructions

- **URL:** <https://revenue.ky.gov/Documents/INSTRUCTIONSFORTHIRDPARTYPURCHASERINSTALLMENTPAYMENTPLANCALCULATOR.pdf>
- **Format:** PDF
- **Accessible:** Yes

---

## 7. Regulatory and Training Materials

### 7.1 Kentucky Administrative Regulations (KAR)

| Regulation | Subject | URL | Size | Accessible |
|---|---|---|---|---|
| 103 KAR 5:180 | Procedures for sale of certificates of delinquency by county clerks | <https://revenue.ky.gov/DOR%20Training%20Materials/103%20KAR%205.180.%20Procedures%20for%20sale%20of%20certificates%20of%20delinquincy%20by%20county%20clerks.pdf> | 140 KB | Yes |
| 103 KAR 5:190 | State registration requirements and application process for purchasing certificates of delinquency; fees | <https://revenue.ky.gov/DOR%20Training%20Materials/103%20KAR%205.190.%20State%20registration%20requirements%20and%20application%20process%20for%20purchasing%20certificates%20of%20delinquincy;%20fees.pdf> | 134 KB | Yes |
| 103 KAR 5:220 | Installment payment plan guidelines for third party purchasers of certificates of delinquency | <https://revenue.ky.gov/DOR%20Training%20Materials/103%20KAR%205.220.%20Installment%20payment%20plan%20guidelines%20for%20thrid%20party%20purchasers%20of%20certificates%20of%20delinquincy.pdf> | 303 KB | Yes |
| 103 KAR 5:230 | Information to be provided by the sheriff when transferring delinquent property tax bills to the county clerk | <https://revenue.ky.gov/DOR%20Training%20Materials/103%20KAR%205.230.%20Information%20to%20be%20provided%20by%20the%20sheriff%20when%20transferring%20delinquent%20property%20tax%20bills%20to%20the%20county%20clerk.pdf> | 281 KB | Yes |

**Note:** DOR URLs contain the original misspelling "delinquincy" (instead of "delinquency") and "thrid" (instead of "third"). These are the actual filenames on the server.

### 7.2 Delinquent Property Tax Collection Manual

- **URL:** <https://revenue.ky.gov/ClerkNetwork/Documents/DelinquentCollectionManual20062.pdf>
- **Format:** PDF (107 KB)
- **Accessible:** Yes (HTTP 200)

### 7.3 County Clerk's Monthly Report Form (62A369-A)

- **URL:** <https://revenue.ky.gov/ClerkNetwork/Documents/62a369A.pdf>
- **Format:** PDF
- **Accessible:** Yes

### 7.4 DOR Training Material (KY-RP-19-04)

- **URL:** <https://revenue.ky.gov/DOR%20Training%20Materials/KY-RP-19-04.pdf>
- **Format:** PDF
- **Accessible:** Yes

---

## 8. Related Resources

### 8.1 Sheriff Network Manual

- **URL:** <https://revenue.ky.gov/SheriffNetwork/PublishingImages/Pages/default/Sheriff's%20Office%20Manual%202017.pdf>
- **Format:** PDF
- **Content:** Property tax duties of the sheriff's office, including the collection timeline before delinquent transfer to county clerk.

### 8.2 County Clerk's Office Manual for Public Service & Centrally Assessed Companies

- **URL:** <https://revenue.ky.gov/ClerkNetwork/PublishingImages/Pages/default/County%20Clerks%20Office%20Manual%20for%20PS%20&%20CA%20Companies%20%20(03-25).pdf>
- **Format:** PDF
- **Content:** Manual for county clerks handling public service and centrally assessed company taxes.

### 8.3 DOR News: 2023 Application Announcement

- **URL:** <https://revenue.ky.gov/News/Pages/DOR-Now-Accepting-2023-Applications-for-Third-Party-Purchasers.aspx>
- **Format:** HTML
- **Content:** Announcement that DOR is accepting third-party purchaser applications for 2023.

### 8.4 DOR Forms Page

- **URL:** <https://revenue.ky.gov/Get-Help/Pages/Forms.aspx>
- **Format:** HTML
- **Content:** Central forms repository; includes property tax forms.

---

## 9. Key Findings Summary

1. **Purchaser lists exist for every year from 2016 to 2026**, all as downloadable PDFs. The 2016 list uses a simpler format (4 fields); 2023 onward uses an expanded 9-field format including Related Party flag, email, and phone.

2. **The 2026 list (covering 2025 delinquent tax bills)** was created 2/13/2026 and is accessible. The DOR page references a 3/16/2026 update that may exist at a slightly different filename.

3. **All PDFs tested returned HTTP 200** when fetched with a browser-like User-Agent header. The HTML pages on revenue.ky.gov return HTTP 403 to simple curl/bot user-agents (WAF protection) but the PDF document URLs are directly accessible.

4. **The 2025 Clerk Manual** is accessible at the confirmed URL, weighing 3.99 MB.

5. **County-level tax sale date schedules** are published as PDF and updated multiple times per year. Fayette County's 2025 sale date was 7/18/2025.

6. **DOR posts county delinquency lists to their website by June 1** each year, per the Delinquent Property Tax page. These are separate from the third-party purchaser lists and provide the actual certificates of delinquency (individual property-level data). The exact URL structure for these county-specific lists was not found in this reconnaissance and warrants further investigation.

7. **Registration threshold:** A purchaser must register with DOR if they plan to buy >3 certificates in a county, >5 statewide, or invest >$10,000 total. Applications should be received by May 15 to ensure participation in all county sales.

8. **URL naming is inconsistent.** File names include typos ("Thrid" for "Third," "delinquincy" for "delinquency"), varying date formats, and mixed use of spaces vs. dots. Any automated monitoring should search by pattern rather than constructing exact URLs.
