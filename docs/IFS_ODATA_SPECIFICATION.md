# CIRCOR International: IFS Cloud OData v4 Integration Specification

## 1. Protocol Architecture & Standards
The CIRCOR manufacturing intelligence pipeline interfaces directly with **IFS Cloud 24R2** native Aurena OData v4 REST endpoints.

* **Protocol Version:** OData v4.01 JSON format.
* **Base URL:** `https://<ifs-host>/main/ifsapplications/projection/v1/` (Simulated in development as `http://localhost:8000/ifs/`).
* **Authentication:** OAuth 2.0 Client Credentials Grant (`Authorization: Bearer <JWT>`).
* **Concurrency Control:** Optimistic concurrency via HTTP `ETag` and `If-Match` headers.

---

## 2. Aurena Projections & Entity Sets

### 2.1 Part Catalog Projection
* **Service:** `PartCatalogHandling.svc`
* **Entity Set:** `PartMasterSet`
* **Entity Type:** `CircorPartMaster`
* **HTTP Methods:** `GET`, `POST`, `PATCH`

| Attribute | Type | Description | Compliance Requirement |
| :--- | :--- | :--- | :--- |
| `part_no` | String (Key) | Unique CIRCOR engineering part number | Primary Key |
| `description` | String | Assembly / valve description | AS9100 Master Record |
| `contract` | String | Manufacturing Site ID (`US10-WARREN`, `US20-LESLIE`) | Multi-site partition |
| `cost_set` | Integer | Standard cost set (Default: `1` Frozen Standard) | Cost Accounting |
| `material_alloy` | String | Exotic alloy specification (`Inconel 625`, `Monel K-500`) | MIL-DTL-777 |
| `std_material_cost` | Decimal | Frozen standard material cost ($) | Standard Costing |
| `std_labor_cost` | Decimal | Frozen standard labor cost ($) | Standard Costing |
| `std_machine_cost` | Decimal | Frozen standard machine cost ($) | Standard Costing |
| `std_overhead_cost` | Decimal | Frozen standard overhead cost ($) | Standard Costing |
| `quality_spec` | String | Military or Aerospace standard (`MIL-SPEC-777`, `AS9100`) | Quality Certification |
| `requires_cmtr` | Boolean | Certified Material Test Report requirement flag | Defense Audit Trail |

---

### 2.2 Shop Order Handling Projection
* **Service:** `ShopOrderHandling.svc`
* **Entity Set:** `ShopOrderSet`
* **Entity Type:** `CircorShopOrderOperation`
* **HTTP Methods:** `GET`, `POST`, `PATCH`

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `order_no` | String (Key) | Unique shop order identifier |
| `operation_no` | Integer (Key) | Routing sequence number (10, 20, 30, ...) |
| `operation_description` | String | Machining or testing operation name |
| `work_center_no` | String | Machine center (`WC-5AXIS-MILL-02`, `WC-HYDRO-TEST`) |
| `labor_class_no` | String | Machinist grade code |
| `heat_lot_no` | String | Raw mill casting Heat Lot number for genealogy |
| `planned_labor_hours` | Decimal | Engineered setup + run labor hours |
| `actual_labor_hours` | Decimal | Cumulative clocked labor hours |
| `standard_labor_rate` | Decimal | Hourly labor rate ($/hr) |
| `planned_machine_hours` | Decimal | Engineered machine spindle hours |
| `actual_machine_hours` | Decimal | Cumulative machine spindle hours |
| `standard_machine_rate` | Decimal | Hourly machine rate ($/hr) |
| `revised_qty_due` | Decimal | Batch quantity scheduled |
| `qty_complete` | Decimal | Finished conforming units |
| `qty_scrapped` | Decimal | Units scrapped at this operation |
| `rowstate` | String | Lifecycle state: `Planned`, `Released`, `Started`, `Parked`, `Closed` |

---

### 2.3 Shop Order Remediation Action (Order Hold)
* **Service:** `ShopOrderHandling.svc`
* **Target:** `ShopOrderSet('{order_no}')/ParkOrder`
* **HTTP Method:** `POST`
* **Payload:**
```json
{
  "order_no": "SO-LSL-2026-8041",
  "reason": "Automated COS Hold: Variance 32.1%, Scrap: 1.0 on Heat Lot HT-INC625-9942"
}
```
* **Response (200 OK):**
```json
{
  "status": "Order Parked",
  "order_no": "SO-LSL-2026-8041",
  "new_state": "Parked",
  "reason": "Automated COS Hold: Variance 32.1%, Scrap: 1.0 on Heat Lot HT-INC625-9942"
}
```

---

### 2.4 Quality Assurance Projection
* **Service:** `QualityAssuranceHandling.svc`
* **Entity Set:** `HydrostaticTestReportSet`
* **HTTP Methods:** `GET`, `POST`
* **Payload Structure:**
```json
{
  "test_id": "HT-2026-00412",
  "order_no": "SO-LSL-2026-8041",
  "operation_no": 40,
  "tested_by_badge": "QC-8812",
  "test_pressure_psi": 3750.0,
  "required_hold_minutes": 15,
  "actual_hold_minutes": 15,
  "pressure_drop_psi": 0.0,
  "passed": true,
  "timestamp": "2026-09-26T14:30:00Z"
}
```

---

## 3. Query Options & OData Filtering
The CIRCOR pipeline leverages standard OData query parameters to minimize lakehouse ingestion bandwidth:

* Filter released orders:
  `GET /ShopOrderHandling.svc/ShopOrderSet?$filter=rowstate eq 'Started'`
* Specific Heat Lot query:
  `GET /ShopOrderHandling.svc/ShopOrderSet?$filter=heat_lot_no eq 'HT-INC625-9942'`
* Projection of cost variance fields:
  `GET /ShopOrderHandling.svc/ShopOrderSet?$select=order_no,operation_no,actual_labor_hours,planned_labor_hours`

---

## 4. Error Codes & Fault Handling
All error payloads adhere to RFC 7807 Problem Details for HTTP APIs:

| HTTP Status | OData Error Code | CIRCOR Remediation Workflow |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_HEAT_LOT` | Abort ingestion; flag non-compliant defense casting in quarantine table. |
| `404 Not Found` | `ORDER_NOT_FOUND` | Verify shop order scheduling in IFS master planning. |
| `409 Conflict` | `ORDER_ALREADY_PARKED` | Log idempotency notice; order is already securely quarantined. |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Exponential backoff (initial retry: 250ms, max 5s). |
| `500 Server Error` | `ORACLE_TRANSACTION_ABORT` | Retry with backoff; alert on-call Enterprise BSA. |
