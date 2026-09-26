# CIRCOR Multi-Site IFS Cloud Transformation Risk Register

| Risk ID | Risk Category | Specific Operational Scenario | Impact | Severity | Mitigation Strategy & Architectural Control |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Data Quality | Legacy ERP contains inaccurate manufacturing lead times (e.g., 2 weeks listed vs. 6 weeks actual for valve castings). | High | Critical | Execute pre-cutover lead time audit using historical PO receipts. Implement IFS MRP lead time buffers before production planning goes live. |
| **RSK-02** | Compliance | Machinists fail to log raw mill Heat Lot numbers during time clocking, invalidating AS9100 defense traceability. | High | High | Tailor Aurena Shop Floor Workbench with mandatory field validation. Block `Start Operation` commands until valid Heat Lot format is verified. |
| **RSK-03** | Plant Adoption | Machine operators resist web-based Aurena interfaces due to perceived input latency compared to legacy green-screens. | Medium | High | Strip out 70% of non-essential form fields using Marble page tailoring. Deploy rugged barcode scanners so clocking is executed via physical scans. |
| **RSK-04** | Integration | High-frequency IoT machine feeds overload the IFS Cloud OData layer during peak shifts, causing database locks. | High | Medium | Decouple telemetry using Azure Event Hubs and a PySpark buffer. Batch summarized machine runtime hours into IFS on 15-minute intervals. |
| **RSK-05** | Standardization | Individual plant managers request custom database fields that diverge from the corporate template, breaking updates. | Medium | Critical | Enforce a strict Solution Governance Board. Authorize zero core database changes; mandate all local requirements use low-code custom attributes. |
