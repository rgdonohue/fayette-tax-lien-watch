# Source Reconnaissance: Lexington-Fayette County GIS & Parcel Data

**Date:** 2026-03-21
**Status:** Complete

---

## Summary

Lexington-Fayette Urban County Government (LFUCG) operates a well-maintained open data
program with 80+ GIS layers available at no cost. Parcel boundary polygons are freely
downloadable in multiple formats. However, the parcel layer contains **geometry and
address data only** -- it does **not** include owner name, assessed value, or tax
status. Those attributes live in the Fayette County PVA (qPublic) system, which must be
queried separately and joined via the `PVANUM` key.

---

## 1. Primary Portal: Lexington's Data Hub

| Item | Detail |
|------|--------|
| Portal URL | https://data.lexingtonky.gov |
| Alternate URL | https://data-lfucg.hub.arcgis.com |
| Platform | ArcGIS Hub (Esri) |
| Org ID | `Mg7DLdfYcSWIaDnu` |
| Owner account | `gis_lfucg` |
| Contact | gis@lexingtonky.gov |
| License | Public, "as-is" with LFUCG Terms of Use |

---

## 2. Parcel Boundary Layer (Primary Dataset)

### Metadata

| Item | Detail |
|------|--------|
| Title | Parcel |
| ArcGIS Item ID | `e4a525d8772741468205e82fc173db22` |
| Feature Count | **114,202 parcels** |
| Geometry Type | Polygon |
| Spatial Reference | WKID 2246 (NAD83 / Kentucky FIPS 1602, US Feet) |
| Last Data Edit | 2026-03-16 (epoch 1773849967374) |
| Max Record Count per query | 2,000 |
| Capabilities | Query, Extract |

### ArcGIS REST API Endpoint

```
https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Parcel/FeatureServer/0
```

### Bulk Download URLs

| Format | URL |
|--------|-----|
| **GeoJSON** | https://data.lexingtonky.gov/api/download/v1/items/e4a525d8772741468205e82fc173db22/geojson?layers=0 |
| **Shapefile** | https://data.lexingtonky.gov/api/download/v1/items/e4a525d8772741468205e82fc173db22/shapefile?layers=0 |
| **CSV** | https://data.lexingtonky.gov/api/download/v1/items/e4a525d8772741468205e82fc173db22/csv?layers=0 |
| **File GDB** | https://data.lexingtonky.gov/api/download/v1/items/e4a525d8772741468205e82fc173db22/filegdb?layers=0 |
| **KML** | https://data.lexingtonky.gov/api/download/v1/items/e4a525d8772741468205e82fc173db22/kml?layers=0 |

All supported export formats: csv, shapefile, sqlite, geoPackage, filegdb,
featureCollection, geojson, kml, excel.

> Download endpoints return HTTP 302 (redirect to file) or HTTP 202 (processing,
> retry shortly). Large files like Parcel GeoJSON may take a moment to generate.

### Hub Web UI

- Map view: https://data.lexingtonky.gov/maps/lfucg::parcel
- About page: https://data.lexingtonky.gov/datasets/lfucg::parcel/about
- Table explorer: https://data-lfucg.hub.arcgis.com/datasets/parcel/explore?showTable=true

### Fields / Attributes

| Field | Type | Description | Sample Value |
|-------|------|-------------|--------------|
| `PVANUM` | String(8) | **PVA parcel number -- join key to PVA records** | `10000030` |
| `NUM1` | String(5) | Street number (primary) | `3305` |
| `NUM2` | String(5) | Street number (secondary/range) | (often null) |
| `DIR` | String(2) | Street direction prefix | `S`, `W`, etc. |
| `NAME` | String(20) | Street name | `TAHOE` |
| `TYPE` | String(4) | Street suffix type | `RD`, `LN`, `DR` |
| `ADDRESS` | String(31) | Full concatenated address | `3305 TAHOE RD` |
| `UNIT` | String(20) | Unit/suite number | (often null) |
| `TAX` | String(2) | Tax district code | `01` |
| `CLASS` | String(1) | Property class (R=Residential, etc.) | `R` |
| `PVA_ACRE` | Double | Acreage per PVA records | `0.1148` |
| `CONDO` | String(10) | Condo identifier | (often null) |
| `CAB_SLIDE` | String(5) | Plat cabinet/slide reference | `D-240` |
| `DATEENTRD` | Date | Date parcel entered system | `2014-02-07` |
| `Shape__Area` | Double | Polygon area in sq feet (system) | `13660.69` |
| `Shape__Length` | Double | Polygon perimeter in feet (system) | `1769.24` |
| `OBJECTID` | OID | System row ID | `51156752` |

### Key Observations

- **`PVANUM` is the critical join key** to link parcels to PVA property records
  (owner, assessed value, sales). Some parcels (e.g., ROW, subdivisions in
  progress) have null `PVANUM`.
- **No owner name, assessed value, or tax amount** in this layer. Those must
  come from the PVA/qPublic system.
- The `TAX` field contains tax district codes (e.g., `01`), not dollar amounts.
- The `CLASS` field appears to encode land use type (`R` = Residential).
- Geometry is **not survey quality** -- intended for general reference only.

### Example Query (via REST API)

Query all parcels with a specific PVA number:
```
https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Parcel/FeatureServer/0/query?where=PVANUM%3D'10000030'&outFields=*&f=geojson
```

Query parcels by address name:
```
https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Parcel/FeatureServer/0/query?where=NAME%3D'MAIN'&outFields=PVANUM,ADDRESS,CLASS&f=json&resultRecordCount=100
```

Paginated bulk export (page through all records):
```
https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Parcel/FeatureServer/0/query?where=1%3D1&outFields=PVANUM,ADDRESS,CLASS,TAX,PVA_ACRE&returnGeometry=false&resultOffset=0&resultRecordCount=2000&f=json
```

---

## 3. Supplementary Boundary Layers

All layers below are hosted on the same ArcGIS Online org and support the same
export formats (shapefile, GeoJSON, CSV, GDB, KML, Excel, etc.).

### Council District

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `5bab826b97c84d229f7abf0bc947981c` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Council_District/FeatureServer |
| Hub page | https://data.lexingtonky.gov/maps/lfucg::council-district/about |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/5bab826b97c84d229f7abf0bc947981c/geojson?layers=0 |
| Key fields | `DISTRICT` (int), `REP` (council member name), `EMAIL`, `TELEPHONE`, `URL` |
| Description | 12 council districts based on 2020 Census, adopted Dec 7 2021 |

### Neighborhood Association

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `703c0fd5012c464da48207b8246840bc` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Neighborhood_Association/FeatureServer |
| Hub page | https://data.lexingtonky.gov/datasets/703c0fd5012c464da48207b8246840bc |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/703c0fd5012c464da48207b8246840bc/geojson?layers=0 |
| Key fields | `Assoc_Name`, `Council`, `Active`, `Census_Tract`, `Website`, contact info |
| Description | Neighborhood associations registered with LFUCG Division of Planning |

### Census Tract Boundaries 2020 (Current)

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `852f55ec57bc440fa86c7116dbf72dc2` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/CensusTractBoundaries/FeatureServer |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/852f55ec57bc440fa86c7116dbf72dc2/geojson?layers=0 |
| Key fields | `TRACT_FIPS`, `FIPS` (full GEOID), `POPULATION`, `POP_SQMI`, `SQMI`, `POPULATION_2020`, `POP20_SQMI` |

### Zoning

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `10d3e3cb91294dc090328231517d3b9a` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Zoning/FeatureServer |
| Hub page | https://data.lexingtonky.gov/datasets/zoning |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/10d3e3cb91294dc090328231517d3b9a/geojson?layers=0 |
| Key fields | `ZONING` (zone code), `DATE_ENTRD`, `LINK` |

### Urban Service Area

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `4c8db8e014cb49349fd430d96d8994b9` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Urban_Service_Area/FeatureServer |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/4c8db8e014cb49349fd430d96d8994b9/geojson?layers=0 |

### Voting Precinct

| Item | Detail |
|------|--------|
| ArcGIS Item ID | `0dd443e80af343d9aed2066fa77da9af` |
| FeatureServer | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Voting_Precinct/FeatureServer |
| Download GeoJSON | https://data.lexingtonky.gov/api/download/v1/items/0dd443e80af343d9aed2066fa77da9af/geojson?layers=0 |

### Additional Layers of Interest

| Layer | FeatureServer URL |
|-------|-------------------|
| Address Point | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Address_Point/FeatureServer |
| Street Centerline | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Street_Centerline/FeatureServer |
| Conditional Zoning Boundary | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Conditional_Zoning_Boundary/FeatureServer |
| Infill and Redevelopment Zone | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Infill_and_Redevelopment_Zone/FeatureServer |
| Development Plan | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Development_Plan/FeatureServer |
| National Register District | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/National_Register_District/FeatureServer |
| National Register Property | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/National_Register_Property/FeatureServer |
| Central Business District | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Central_Business_District/FeatureServer |
| School Board District | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/School_Board_District/FeatureServer |
| FEMA 2014 Floodplain | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Service_FEMA2014/FeatureServer |
| Census Tract 2010 | https://services1.arcgis.com/Mg7DLdfYcSWIaDnu/arcgis/rest/services/Census_Tract_2010/FeatureServer |

---

## 4. ArcGIS Server (maps.lexingtonky.gov)

LFUCG also runs a traditional ArcGIS Server at `maps.lexingtonky.gov/lfucggis/rest/services`.
These are MapServer services (read-only, no bulk download), but useful for tiled
map display and spatial queries.

### Available Map Services

| Service | URL |
|---------|-----|
| Property (Parcels + Address Points) | https://maps.lexingtonky.gov/lfucggis/rest/services/property/MapServer |
| Boundaries (Census Tracts, Zip Codes, Police Beats) | https://maps.lexingtonky.gov/lfucggis/rest/services/boundaries/MapServer |
| Political (Voting Precincts, Council Districts, CSEPP) | https://maps.lexingtonky.gov/lfucggis/rest/services/political/MapServer |
| Planning (Neighborhoods, Zoning, Overlays, PDR Farms) | https://maps.lexingtonky.gov/lfucggis/rest/services/planning/MapServer |
| Overlay (Incorporated Area, Regional County) | https://maps.lexingtonky.gov/lfucggis/rest/services/overlay/MapServer |
| Transportation | https://maps.lexingtonky.gov/lfucggis/rest/services/transportation/MapServer |
| Basemap | https://maps.lexingtonky.gov/lfucggis/rest/services/basemap/MapServer |
| Aerial (most recent) | https://maps.lexingtonky.gov/lfucggis/rest/services/aerial_mostrecent/MapServer |

### Geocoding Services

| Service | URL |
|---------|-----|
| Address Geocoder | https://maps.lexingtonky.gov/lfucggis/rest/services/locator/GeocodeServer |
| Address-only Geocoder | https://maps.lexingtonky.gov/lfucggis/rest/services/locator_address_only/GeocodeServer |
| Batch Geocoder | https://maps.lexingtonky.gov/lfucggis/rest/services/locator_batch/GeocodeServer |

The geocoder accepts a `Street` input field and returns match score, coordinates,
and address components.

### MapIt Web Application

Interactive map viewer combining the most-requested layers:
https://maps.lexingtonky.gov/mapit/

---

## 5. Property Valuation Data (PVA / qPublic)

The LFUCG parcel GIS layer does **not** contain owner names, assessed values, or
tax payment status. That data is maintained by the Fayette County Property
Valuation Administrator (PVA).

| Item | Detail |
|------|--------|
| PVA website | https://fayettepva.com/ |
| PVA (David O'Neill) | 101 E Vine St #600, Lexington, KY 40507 / (859) 246-2722 |
| Online property search | https://qpublic.schneidercorp.com/?county=ky_fayette |
| Search with map | https://qpublic.schneidercorp.com/Application.aspx?AppID=1019&LayerID=21445&PageTypeID=1&PageID=0 |
| Advanced search | https://qpublic.schneidercorp.com/Application.aspx?AppID=1019&LayerID=21445&PageTypeID=2&PageID=9141 |

### qPublic Data Available

Through the qPublic web interface, the following fields are searchable / viewable:

- Owner name
- Property address
- Parcel ID (PVANUM)
- Assessed value (land, improvements, total)
- Sales price and date
- Occupancy / style
- Tax district
- Legal description
- Deed book/page

### qPublic Access Limitations

- **No public bulk download or API** -- data is accessed record-by-record through
  the web UI.
- Commercial use or >50 records/month requires a paid subscription.
- Individual parcel KML files can be downloaded for map reference.
- The `PVANUM` field in the GIS parcel layer is the join key to qPublic records.

---

## 6. Tax Delinquency / Lien Data

Tax liens are handled by the **Fayette County Clerk**, not the PVA or Sheriff.

| Item | Detail |
|------|--------|
| Clerk delinquent taxes page | https://fayettecountyclerk.com/web/landrecords/delinquenttaxes |
| Tax sale procedures | https://fayettecountyclerk.com/web/landrecords/delinquenttaxes/taxsaleprocedures.htm |
| Tax sale procedures (PDF) | https://www.fayettecountyclerk.com/web/landrecords/delinquenttaxes/taxsaleprocedures.pdf |
| Sheriff property tax lookup | https://fayettesheriff.com/property_taxes_lookup.php |
| Delinquent tax collection | https://fayettecountyattorney.com/services/delinquent-tax-collection/ |
| KY DOR delinquent tax info | https://revenue.ky.gov/Property/Pages/Delinquent-Property-Tax.aspx |

### Tax Lien Sale Process

- The Sheriff collects current-year taxes; after a deadline they are transferred
  to the County Clerk.
- The Clerk conducts an annual certificate of delinquency sale each summer (90-135
  days after bills are turned over).
- Current-year bills: search at https://fayettesheriff.com/property_taxes_lookup.php
  (search by tax year, 2005-2025 available).
- Delinquent bills: search at https://fayettedeeds.com
- Sheriff lookup URL pattern: `property_taxes_lookup_[YEAR].php`

---

## 7. Statewide Kentucky GIS Resources

| Resource | URL |
|----------|-----|
| KyGovMaps Open Data Portal | https://opengisdata.ky.gov |
| KyGeoNet Clearinghouse | https://kygeonet.ky.gov |
| KY GIS Server REST root | https://kygisserver.ky.gov/arcgis/rest/services |
| Census Tracts 2020 (statewide) | https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Census_Tracts_2020_WGS84WM/MapServer |
| Census Block Groups 2020 | https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_Census_Block_Groups_2020_WGS84WM/MapServer |
| County boundaries | https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/Ky_CountyShading_WGS84WM/MapServer |

> Note: Kentucky does **not** maintain a statewide consolidated parcel layer on
> KyGovMaps. Only individual county PVA offices publish parcel data. For Fayette
> County, the LFUCG Hub is the authoritative source.

---

## 8. Integration Strategy for Tax Lien Project

### Recommended Data Pipeline

1. **Download parcel boundaries** from LFUCG Hub (GeoJSON or Shapefile via
   download URLs above).
2. **Overlay with council districts, neighborhoods, census tracts, zoning** using
   spatial joins for geographic enrichment.
3. **Join PVA property data** by `PVANUM` to attach owner name, assessed value,
   and property characteristics. This requires scraping qPublic or filing an open
   records request for bulk PVA data.
4. **Cross-reference with delinquent tax lists** obtained from the County Clerk
   (likely via open records request or scraping the Clerk's published lists).
5. **Use the geocoder** at maps.lexingtonky.gov for address standardization.

### Key Join Field

The `PVANUM` field (8-character string like `10000030`) is the universal parcel
identifier used across LFUCG GIS, PVA records, and tax billing systems. This is the
primary key for linking spatial data to property/tax records.

### API Rate Limits & Pagination

- ArcGIS FeatureServer queries return max **2,000 records per request**.
- Use `resultOffset` and `resultRecordCount` for pagination.
- The query endpoint supports JSON, GeoJSON, and PBF response formats.
- Spatial queries (intersects, contains, within) are fully supported.
- No authentication required for public layers.
