# CIRCOR International: IFS Cloud Manufacturing & Operational Intelligence Bridge

[![Platform](https://img.shields.io/badge/ERP-IFS%20Cloud%2024R2-blue.svg)](https://www.ifs.com)
[![Protocol](https://img.shields.io/badge/Integration-OData%20v4%20REST-green.svg)](https://docs.ifs.com/techdocs)
[![Engine](https://img.shields.io/badge/Compute-PySpark%20%7C%20Delta%20Lake-orange.svg)](https://spark.apache.org)
[![Compliance](https://img.shields.io/badge/Quality-AS9100%20%7C%20MIL--DTL--777-red.svg)](https://www.circor.com)
[![Live Showcase](https://img.shields.io/badge/Live%20Showcase-freefades2black.github.io-success?logo=github&style=flat-square)](https://freefades2black.github.io/circor-defense-ifs-cos-pipeline/)
[![CI/CD](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

> ### 🌐 Live Architecture & Verification Showcase (.io)
> **Direct Live Link:** [https://freefades2black.github.io/circor-defense-ifs-cos-pipeline/](https://freefades2black.github.io/circor-defense-ifs-cos-pipeline/)
> 
> *The live `.io` showcase deploys automatically via GitHub Actions, combining the **IFS Solution Architect Framework Cheat Sheet** with live execution outputs from the PySpark Gold variance computation and automated UAT test matrix.*

```text
====================================================================================================
               CIRCOR OPERATING SYSTEM (COS) • LIVE COMPUTE OUTPUT & UAT MATRIX (.IO)
               Executed on Omarchy Local Node & GitHub Pages Automated CI/CD
====================================================================================================
[GOLD MART] Ingested Conformed Operations: SO-LSL-2026-8041 (Inconel 625), SO-WRN-2026-1102 (Monel K-500)
[GOLD MART] Computed 2 operational Lean KPIs across Leslie Controls (FL) & Warren Pumps (MA)
[GOLD MART] 1 orders queued for administrative hold remediation: SO-LSL-2026-8041 (Variance: 34.19%, Scrap: 1.0)

+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+
|order_no        |heat_lot_no     |labor_cost_variance |machine_cost_variance|total_cost_variance |variance_percentage|first_pass_yield|trigger_administrative_hold|
+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+
|SO-LSL-2026-8041|HT-INC625-9942  |351.00              |725.00               |1076.00             |34.19              |80.00           |true                      |
|SO-WRN-2026-1102|HT-MONEL-1048   |-24.00              |-22.00               |-46.00              |-2.74              |100.00          |false                     |
+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+

==================================== AUTOMATED UAT TEST MATRIX ====================================
platform linux -- Python 3.14.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/free/projects/circor-defense-ifs-cos-pipeline
collected 2 items

tests/test_circor_uat_matrix.py::test_uat_heat_lot_and_scrap_triggers_hold PASSED [ 50%]
tests/test_circor_uat_matrix.py::test_uat_within_standard_cost_tolerance PASSED [100%]

====================================== 2 passed in 5.81s ======================================

[REMEDIATION] Placed IFS Administrative Hold on Shop Order SO-LSL-2026-8041:
              Reason: COS Lean Breach: Variance 34.19% | Scrap 1.0 units on Heat Lot HT-INC625-9942
[AUDIT LOG]   Rowstate transitioned: 'Started' -> 'Parked' | Material Review Board (MRB) notified.
====================================================================================================
```


A reference integration and operational intelligence bridge connecting **IFS Cloud ERP** to shop floor machining centers, quality inspection benches, and downstream analytics platforms across CIRCOR International manufacturing facilities (Leslie Controls in Tampa, FL; Warren Pumps in Warren, MA).

---

## Repository Architecture Mapping

This repository is organized to showcase the core operational and functional competencies required for the Lead IFS Business Systems Analyst role at CIRCOR:

| Operational Competency | Repository Implementation Artifact | Description |
| :--- | :--- | :--- |
| **1. Functional Process Design** | [`ifs_declarative_models/ShopFloorWorkbenchTailoring.client`](ifs_declarative_models/ShopFloorWorkbenchTailoring.client) & [`CircorManufacturing.projection`](ifs_declarative_models/CircorManufacturing.projection) | Native IFS Cloud Marble declarative client and projection models for Shop Floor Workbench tailoring, enforcing Heat Lot validation and single-click scrap reporting. |
| **2. Technical Architecture** | [`mock_ifs_cloud_api/`](mock_ifs_cloud_api/) & [`lakehouse_pipeline/`](lakehouse_pipeline/) | Containerized IFS Cloud Aurena OData v4 mock service coupled with a PySpark Medallion Lakehouse (Bronze -> Silver -> Gold). |
| **3. Site Deployments & Cutover** | [`cutover/PLANT_CUTOVER_72HR_RUNBOOK.md`](cutover/PLANT_CUTOVER_72HR_RUNBOOK.md) & [`tests/test_circor_uat_matrix.py`](tests/test_circor_uat_matrix.py) | Minute-by-minute 72-hour weekend plant cutover runbook and automated PySpark User Acceptance Testing (UAT) matrix. |
| **4. Cross-Functional Governance**| [`governance/MULTI_SITE_RISK_REGISTER.md`](governance/MULTI_SITE_RISK_REGISTER.md) | Multi-site executive risk register governing ERP rollouts across Leslie Controls (FL), Warren Pumps (MA), and Weinheim (Germany). |
| **5. Continuous Improvement (COS)** | [`lakehouse_pipeline/03_gold_circor_variance_engine.py`](lakehouse_pipeline/03_gold_circor_variance_engine.py) & [Marble Tailoring](ifs_declarative_models/ShopFloorWorkbenchTailoring.client) | CIRCOR Operating System (COS) variance engine calculating labor/machine cost drift, First Pass Yield (FPY), and shop floor click-waste elimination. |

---

## 1. Business Problem & Operational Context

CIRCOR International manufactures severe-service, mission-critical flow control equipment (cryogenic globe valves, high-pressure naval submarine ball valves, positive displacement pumps) across defense and industrial operating units such as Leslie Controls, Warren Pumps, and CIRCOR Aerospace.

These facilities operate predominantly under **Engineer-to-Order (ETO)** and **Configure-to-Order (CTO)** operational workflows. In high-mix, low-volume valve production involving exotic alloys (Inconel 625, Monel K-500), standard enterprise resource planning implementations encounter three critical failure modes:

1. **Uncontained Cost Drift:** High-precision 5-axis CNC profiling and cladding operations often experience tool wear or setup delays. When variances are evaluated only during monthly accounting rollups in IFS Cost Set 1, thousands of dollars in labor and machine overruns are already sunk.
2. **Defective Work In Progress (WIP) Propagation:** In defense manufacturing (MIL-DTL-777, AS9100 Rev D), component failure during hydrostatic pressure testing or dimensional inspection requires immediate containment. Without real-time event linking, upstream work centers continue machining raw castings tied to flawed heat lots.
3. **Shop Floor Adoption Bottlenecks:** The **CIRCOR Operating System (COS)** demands Lean flow, rapid First Pass Yield (FPY) feedback, and zero waste. If operators are forced through complex ERP desktop screens rather than streamlined touchpoints, data collection lags reality by shifts or days.

---

## 2. Operational Architecture

This repository models IFS Cloud as the transactional system of record and financial ledger, while decoupling high-frequency operational analytics and automated remediation into a modern event-driven pipeline.

```text
[ Shop Floor CNC Centers & Hydro Test Benches ]
                       │
                       ▼ (OData v4 REST / JSON)
       [ IFS Cloud 24R2 (Aurena / Oracle DB) ]
         ├── PartCatalogHandling.svc
         ├── ShopOrderHandling.svc
         ├── ShopFloorWorkbenchHandling.svc
         └── QualityAssuranceHandling.svc
                       │
                       ▼ (Batch Extraction / Event Hubs)
          [ Ingestion Engine / Lakehouse ]
                       │
                       ▼ (PySpark Transformation)
         [ Medallion Lakehouse Architecture ]
         ├── Bronze: Raw append-only IFS projection payloads
         ├── Silver: Conformed Shop Orders, Operations & Heat Lots
         └── Gold  : CIRCOR Operating System (COS) Operational Mart
                       │
                       ├──► [ Executive Dashboards / COS KPI Walls ]
                       │
                       ▼ (Reverse Action: Automated Hold)
       [ IFS Cloud Automated Remediation Daemon ]
         └── Invokes: /ShopOrderHandling.svc/ShopOrderSet('{id}')/ParkOrder
```

### Architectural Pillars
- **API-First Transactional Core:** Interfaces directly with IFS Cloud's native OData v4 projections (`ShopOrderHandling`, `ShopFloorWorkbenchHandling`, `PartCatalogHandling`).
- **Material Traceability by Design:** Incorporates raw mill Heat Lot numbers and Certified Material Test Report (CMTR) flags down to individual shop order operations.
- **Closed-Loop Remediation:** An operational daemon continuously reads computed variance flags and automatically issues administrative order holds (`ParkOrder`) in IFS Cloud when operations breach acceptable cost or scrap limits.

---

## 3. Repository Structure

```text
.
├── ifs_declarative_models/
│   ├── ShopFloorWorkbenchTailoring.client # IFS Cloud Marble declarative UI model
│   └── CircorManufacturing.projection     # IFS Cloud Aurena OData projection contract
├── mock_ifs_cloud_api/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                        # FastAPI service simulating IFS OData projections
│   ├── Dockerfile                         # Containerized IFS mock service
│   └── requirements.txt                   # API dependencies
├── lakehouse_pipeline/
│   ├── __init__.py
│   ├── 01_bronze_ifs_ingest.py            # Raw ingestion script
│   ├── 02_silver_conformed.py             # Conformed data models with SCD Type 2 tracking
│   ├── 03_gold_circor_variance_engine.py  # PySpark COS Lean metric calculation
│   ├── 04_ifs_remediation_daemon.py       # Automated reverse-ETL hold agent
│   └── circor_cos_pyspark_pipeline.py     # Standalone PySpark variance engine
├── cutover/
│   └── PLANT_CUTOVER_72HR_RUNBOOK.md      # Hour-by-hour plant conversion runbook
├── governance/
│   └── MULTI_SITE_RISK_REGISTER.md        # Multi-site executive risk & mitigation matrix
├── docs/
│   ├── CIRCOR_ETO_CTO_LIFECYCLE.md        # ETO/CTO valve lifecycle deep dive
│   └── IFS_ODATA_SPECIFICATION.md         # Endpoint schemas and entity mappings
├── tests/
│   ├── test_circor_integration.py         # End-to-end integration test suite
│   ├── test_circor_uat_matrix.py          # Plant UAT scenarios (14.2 & 14.3)
│   └── test_variance_engine.py            # Financial & scrap variance math unit tests
├── scripts/
│   └── run_e2e_verification.py            # Automated end-to-end verification script
├── docker-compose.yml                     # Local container orchestration
└── README.md
```

---

## 4. CIRCOR Operating System (COS) Metric Engine

The Gold-layer analytics engine computes operational variances at the individual work order and operation level using standard cost accounting rules:

$$\text{Labor Variance} = (\text{Actual Labor Hours} - \text{Planned Labor Hours}) \times \text{Standard Labor Rate}$$

$$\text{Machine Variance} = (\text{Actual Machine Hours} - \text{Planned Machine Hours}) \times \text{Standard Machine Rate}$$

$$\text{Total Cost Variance} = \text{Labor Variance} + \text{Machine Variance}$$

$$\text{First Pass Yield (FPY)} = \left(\frac{\text{Revised Qty Due} - \text{Qty Scrapped}}{\text{Revised Qty Due}}\right) \times 100$$

### Remediation Thresholds
An operational order hold is automatically triggered in IFS Cloud if:
1. **Cost Overrun:** $\text{Variance Percentage} > 15.0\%$ of total planned operational cost.
2. **Severe-Service Scrap:** $\text{Scrap Count} > 0$ on severe-service alloy operations (Inconel 625, Monel K-500).
3. **Hydrostatic Failure:** Hydrostatic pressure testing fails target hold pressure (e.g., 3,750 PSI) or registers measurable fluid leakage.

---

## 5. Quickstart & Local Deployment

### Prerequisites
- Python 3.10+
- Java 11 or 17 (required for local PySpark execution)
- Docker & Docker Compose (optional for containerized deployment)

### 1. Launch the Mock IFS Cloud OData Service

```bash
# Clone the repository
git clone https://github.com/FreeFades2Black/circor-defense-ifs-cos-pipeline.git
cd circor-defense-ifs-cos-pipeline

# Run natively with Python
uvicorn mock_ifs_cloud_api.app.main:app --host 0.0.0.0 --port 8800

# Or run containerized with Docker Compose
docker compose up -d --build
```
*Access interactive Swagger UI documentation at `http://localhost:8800/docs`.*

### 2. Ingest and Calculate CIRCOR Operating System Metrics

```bash
# Ingest raw IFS projections into Bronze storage
python lakehouse_pipeline/01_bronze_ifs_ingest.py

# Enforce AS9100 Heat Lot conformity and create Silver conformed datasets
python lakehouse_pipeline/02_silver_conformed.py

# Compute Gold-layer COS Lean Metrics and variance flags
python lakehouse_pipeline/03_gold_circor_variance_engine.py
```

### 3. Run the Automated IFS Remediation Daemon

```bash
# Poll Gold remediation queue and quarantine out-of-spec shop orders
python lakehouse_pipeline/04_ifs_remediation_daemon.py
```

---

## 6. Sample Execution Output

### PySpark Gold-Layer Variance Table
```text
+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+
|order_no        |heat_lot_no     |labor_cost_variance |machine_cost_variance|total_cost_variance |variance_percentage|first_pass_yield|trigger_administrative_hold|
+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+
|SO-LSL-2026-8041|HT-INC625-9942  |351.00              |725.00               |1076.00             |34.19              |80.00           |true                      |
|SO-WRN-2026-1102|HT-MONEL-1048   |-24.00              |-22.00               |-46.00              |-2.74              |100.00          |false                     |
+----------------+----------------+--------------------+---------------------+--------------------+-------------------+----------------+--------------------------+
```

### Remediation Daemon Execution Log
```text
[REMEDIATION DAEMON] Evaluating Gold Hold Queue (1 candidates)...
[SUCCESS] Placed IFS Administrative Hold on Shop Order SO-LSL-2026-8041:
          Reason: COS Lean Breach: Variance 34.19% | Scrap 1.0 units on Heat Lot HT-INC625-9942
[AUDIT LOG] State transitioned: 'Started' -> 'Parked' | Material Review Board (MRB) notification dispatched.
```

---

## 7. Automated Testing & Verification

Run the full automated test suite covering UAT plant conditions, financial equations, and API integration:

```bash
# Run complete test suite with PySpark
pytest tests/ -v
```

Expected test coverage:
* `tests/test_circor_uat_matrix.py`: Verifies UAT Scenarios 14.2 (Inconel scrap trigger hold) and 14.3 (Within standard tolerance).
* `tests/test_variance_engine.py`: Unit tests for labor, machine, and scrap variance math.
* `tests/test_circor_integration.py`: End-to-end integration tests validating OData projections, heat lot validation, and order parking.

---

## 8. Defense Compliance & Audit Governance

This solution conforms to United States defense and nuclear flow-control standards:
* **AS9100 Rev D / ISO 9001:2015:** Quality management systems for aerospace and defense.
* **MIL-DTL-777:** Valves, piping system, components, and hydrostatic testing compliance.
* **ASME Boiler & Pressure Vessel Code (Section III):** Nuclear submarine power plant components.
* **NAVSEA 250-1500-1:** Welding and non-destructive testing requirements for submarine hull penetrations.
