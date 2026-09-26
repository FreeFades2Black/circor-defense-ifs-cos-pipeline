# CIRCOR International: Defense Compliance, Risk Assessment & Financial Loss Matrix

## 1. Compliance Enforcement & Risk Architecture Overview
In naval submarine and aerospace flow-control manufacturing (Leslie Controls, Warren Pumps), quality and compliance failures are not minor rework events. A defective sea-chest valve or porous cryogenic casting compromises vessel survivability and carries severe regulatory, contractual, and financial penalties from NAVSEA, DCMA, and prime defense contractors (e.g., General Dynamics Electric Boat, Newport News Shipbuilding).

This matrix defines how the **IFS Cloud 24R2 + Event Lakehouse** reference architecture enforces standards at runtime, along with an impact assessment and financial loss model for non-compliance.

---

## 2. Compliance Risk Assessment & Loss Estimate Matrix

| Defense / Nuclear Standard | Operational Requirement | IFS Cloud & Pipeline Enforcement Mechanism | Failure Mode If Standards Fail | Risk Severity | Quantified Financial Loss Estimate (Per Incident / Batch) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AS9100 Rev D / ISO 9001:2015**<br>*(Clause 8.5.2 & 8.7)* | End-to-end raw mill Heat Lot traceability and immediate quarantine of nonconforming work in progress (WIP). | **UI & Event Enforcement:**<br>• `ShopFloorWorkbenchTailoring.client` mandates `HeatLotNo` input before spindle start.<br>• Automated hold daemon invokes `ShopOrderHandling.svc/ParkOrder` within 60s of scrap event. | **Uncontrolled WIP Propagation:**<br>Machinists run an entire shift of valve bodies from a rejected forging lot. Finished valves intermingle with certified stock. | **Critical**<br>(Likelihood: Med / Impact: High) | **$185,000 to $420,000**<br>• Scrap of 10-25 high-alloy castings ($8,500/ea raw).<br>• Wasted 5-axis machining time (80 hrs @ $145/hr).<br>• Quarantining and segregating warehouse stock.<br>• DCMA Corrective Action Request (CAR Level II/III) audit costs. |
| **MIL-DTL-777**<br>*(Naval Piping & Fluid Valves)* | Hydrostatic proof pressure testing (1.5× operating pressure, e.g., 3,750 to 6,000 PSI) with zero measurable fluid leakage. | **Data Contract & Gate Lock:**<br>• `QualityAssuranceHandling.svc` captures test pressure and leak rate.<br>• Automated hold parks order if `leak_rate_scfh > 0.0` or hold duration under target. Blocks shipping invoice. | **Escape to Fleet / Drydock Failure:**<br>Valve with hairline porosity bypasses hydro test due to paper traveler bypass and ships to shipyard. Fails pressure test during hull integration. | **Catastrophic**<br>(Likelihood: Low / Impact: Critical) | **$750,000 to $2,400,000**<br>• Emergency shipyard de-installation and drydock delay penalties ($25,000/day).<br>• Expedited replacement casting and 24/7 rush tooling.<br>• Potential liquidated damages and vendor debarment from naval contracts. |
| **ASME Section III**<br>*(Boiler & Pressure Vessel - Nuclear)* | Verified Certified Material Test Reports (CMTR) with mechanical and chemical certification prior to alloy cutting; zero-tolerance scrap baseline. | **Silver Schema Validation:**<br>• `02_silver_conformed.py` verifies CMTR heat chemistry against ASME Section III alloy bounds before operation release.<br>• Scrap count > 0 forces immediate administrative hold. | **Material Cross-Contamination:**<br>Machining standard 316L stainless steel using Inconel 625 tooling or drawings, resulting in uncertified alloy installed in nuclear coolant stream. | **Catastrophic**<br>(Likelihood: Low / Impact: Catastrophic) | **$1,200,000 to $5,000,000+**<br>• Complete recall and forensic destructive testing.<br>• Nuclear Regulatory Commission (NRC) / Naval Reactors inspection intervention.<br>• Direct contractual clawback and suspension of nuclear ASME N-Stamp certification. |
| **NAVSEA 250-1500-1**<br>*(Welding & NDT for Submarine Hulls)* | Qualified welder / inspector sign-offs and mandatory non-destructive testing (NDT) hold points before subsequent machining. | **Routing Predecessor Locks:**<br>• Predecessor rules in IFS routings lock Op 30 (Finish Machining) until Op 20 (NDT Liquid Penetrant) is signed off by a certified Level II/III inspector badge ID.<br>• Immutable UTC transition audit logging. | **Uninspected Weld Pass-Through:**<br>Machinist machines over an uninspected clad weld. Sub-surface weld cracking covered by final cosmetic finishing. | **Critical**<br>(Likelihood: Med / Impact: High) | **$340,000 to $920,000**<br>• Ultrasonic (UT) and radiographic (RT) field inspections.<br>• Gouging out flawed weld cladding, re-welding, and re-heat treating.<br>• Mandated 100% audit of all welds processed by the unverified operator. |

---

## 3. Financial Loss Quantification Methodology

Financial losses are modeled based on standard aerospace and defense cost structures across high-mix, low-volume flow control manufacturing:

$$\text{Total Cost of Quality Failure (COPQ)} = C_{\text{Material}} + C_{\text{Labor/Spindle}} + C_{\text{Containment}} + C_{\text{Regulatory/Penalties}}$$

Where:
* $C_{\text{Material}}$ = Cost of scrapped nickel-chromium superalloys (Inconel 625 @ ~$45-$65/lb raw forging; Monel K-500 @ ~$35-$50/lb).
* $C_{\text{Labor/Spindle}}$ = Sunk 5-axis CNC mill time ($145/hr) + Level 3/4 machinist wages ($54/hr fully burdened).
* $C_{\text{Containment}}$ = Material Review Board (MRB) engineering hours, forensic NDT scanning, warehouse segregation, and customer notifications.
* $C_{\text{Regulatory/Penalties}}$ = Shipyard delay fees ($10,000-$25,000/day), DCMA audit mitigation, and re-qualification testing.

---

## 4. Physical Shop Floor Checkpoints & Digital Enforcement Mechanisms

In defense and naval nuclear flow-control manufacturing, compliance is governed by hard physical checkpoints, strict testing parameters, and digital controls that stop the line automatically if a threshold is breached.

### 4.1 AS9100 Rev D / ISO 9001:2015: Raw Material Identification & Containment

* **Exact Technical Specifics:**
  * **Mandate:** Clauses 8.5.2 (Identification and Traceability) and 8.7 (Control of Nonconforming Outputs).
  * **Physical Requirement:** Every raw forging, bar stock billet, and sub-assembly casting must have its mill Heat Lot number permanently vibro-etched, dot-peened, or laser-marked on the part surface before any cutting begins. The chemical composition (e.g., Inconel 625: Ni 58% min, Cr 20–23%, Mo 8–10%) and mechanical elongation limits from the Certified Material Test Report (CMTR) must match the Part Master.

* **Shop Floor Monitoring & Enforcement:**
  * **Station Intake:** When raw Inconel 625 valve bodies arrive at the 5-axis CNC machining cell (e.g., `Freez-WC-5AXIS-MILL-02`), the machinist uses an optical 2D DataMatrix barcode scanner to scan both the physical valve body and traveler sheet.
  * **Interactive UI Lock:** The tailored Aurena client (`ShopFloorWorkbenchTailoring.client`) requires explicit field confirmation:
    * The *Start Operation* command remains disabled until the scanned `HeatLotNo` string matches the allocated inventory lot in IFS.
    * If an operator enters an unallocated heat number, the client blocks execution and prevents spindle run-time clocking.
  * **Automated Scrap Hold:** If an operator scraps a part during tool wear or casting porosity detection, the single-click `ReportScrap` command executes:
    * It immediately writes a scrap transaction to IFS Cloud with mandatory root-cause reason codes (`TOOL_BREAK`, `CASTING_VOID`).
    * The automated hold daemon calls `ShopOrderHandling.svc/ParkOrder`, shifting the state to *Parked* to prevent downstream shifts from running subsequent operations on the flawed lot.

---

### 4.2 MIL-DTL-777: High-Pressure Hydrostatic Testing

* **Exact Technical Specifics:**
  * **Mandate:** U.S. Navy specification for fluid system valves and piping components.
  * **Physical Requirement:** Hydrostatic proof shell test at 1.5× rated design pressure (e.g., a 2,500 Class valve is proof-tested at 3,750 PSI; severe-service valves at 6,000 PSI).
  * **Hold Duration & Acceptance Threshold:** Water pressure must be held continuously for a minimum of 10 minutes with zero observable drop in gauge pressure and zero allowable fluid leakage across the packing gland or casting body (0.0 SCFH / drops per minute).

* **Shop Floor Monitoring & Enforcement:**
  * **Automated Test Rig Data Capture:** At the hydrostatic test bench (e.g., `Freez-WC-HYDRO-01`), valves are clamped into an isolated hydraulic pressure test cell. Calibrated digital pressure transducers and mass flow leak detectors record pressure curves and elapsed hold times directly to a local test-bench PLC.
  * **Edge-to-ERP Telemetry Ingestion:** The test bench software sends a structured JSON payload directly to the IFS projection endpoint: `POST /ifs/QualityAssuranceHandling.svc/SubmitHydroTest`.
    * Payload captures: `order_no`, `test_pressure_psi`, `hold_duration_minutes`, and `leak_rate_scfh`.
  * **Automated Shipping Gate Lock:** If `test_pressure_psi < target_pressure_psi` or `leak_rate_scfh > 0.0` or `hold_duration_minutes < 10.0`, the API immediately updates the order state in IFS to *Parked*. The valve cannot be moved to the shipping dock or added to an outbound Bill of Lading because IFS blocks packing operations for any shop order in a *Parked* state.

---

### 4.3 ASME Section III (BPVC): Nuclear Power & Submarine Reactor Plant

* **Exact Technical Specifics:**
  * **Mandate:** ASME Boiler & Pressure Vessel Code, Section III, Division 1 (Rules for Construction of Nuclear Facility Components).
  * **Physical Requirement:** Zero tolerance for micro-voiding or uncertified chemical alloy substitutions in reactor coolant pressure boundaries. Superalloys like Inconel 625 and Monel K-500 must maintain unbroken mechanical property integrity (e.g., Charpy V-Notch impact testing requirements, yield strength verification).

* **Shop Floor Monitoring & Enforcement:**
  * **Silver-Layer Data Conformity Engine (`02_silver_conformed.py`):** Before machining orders are released from *Planned* to *Released*, the data pipeline validates the linked supplier CMTR values against ASME Section III chemistry boundary tables. If sulfur, carbon, or lead trace concentrations exceed specified fractions of a percent, the material is quarantined in IFS stock before the stockroom can issue the billet.
  * **First Pass Yield (FPY) Gating:** In a nuclear-grade cell, any scrap event represents potential structural integrity risk. The Gold-layer variance engine calculates FPY in real time:
    $$\text{FPY} = \left(\frac{\text{Revised Qty Due} - \text{Qty Scrapped}}{\text{Revised Qty Due}}\right) \times 100$$
    For ASME Section III orders, if $\text{Scrap Count} > 0$ or $\text{FPY} < 100\%$, an administrative alert is dispatched directly to the plant's Nuclear Quality Assurance Manager and the order is locked.

---

### 4.4 NAVSEA 250-1500-1: Welding & Non-Destructive Testing (NDT)

* **Exact Technical Specifics:**
  * **Mandate:** Naval Sea Systems Command Standard for welding and fabrication on submarine hull penetrations, sea chests, and reactor plants.
  * **Physical Requirement:** Mandatory non-destructive examination (NDE/NDT) hold points. 100% Visual Testing (VT) plus Liquid Penetrant Testing (PT), Magnetic Particle Testing (MT), or Ultrasonic Testing (UT) of all critical pressure boundary welds. Machinists are strictly prohibited from performing finish machining over a weld until inspection sign-off is logged.

* **Shop Floor Monitoring & Enforcement:**
  * **Predecessor Routing Enforcements:** The shop order routing defines explicit sequence dependencies:
    * Operation 10: Sub-arc cladding / hardfacing weld.
    * Operation 20: NDT Liquid Penetrant Inspection (Mandatory Quality Hold Point).
    * Operation 30: Finish CNC Milling of valve face and seat.
    * In IFS Cloud, Op 30 has a hard routing prerequisite on Op 20. The system rejects any clocking transaction on Op 30 until Op 20 reports Complete.
  * **Inspector Credential Verification:** Under NAVSEA S9074-AQ-GIB-010/248 and SNT-TC-1A, inspections must be signed off by a certified NDT Level II or Level III inspector. When closing Op 20, the inspector must scan their physical badge ID. The system validates the inspector's current certification record in the IFS Human Resources / Competency module. If their NDT certification has lapsed, the sign-off is rejected.
  * **Immutable Audit Trail:** Every inspection event, inspector badge ID, and status change is written to an immutable event log with millisecond UTC timestamps, ensuring complete compliance during annual DCMA and NAVSEA audits.

---

## 5. Floor Execution & Containment Matrix

| Defense Standard | Key Parameter Checked | Floor Detection Hardware | IFS Enforcement Point | What Happens If Breached |
| :--- | :--- | :--- | :--- | :--- |
| **AS9100 Rev D** | Heat Lot vs. Part Master matching | 2D DataMatrix scanner | `ShopFloorWorkbenchTailoring.client` | Spindle start disabled; order parked if scrap reported |
| **MIL-DTL-777** | Proof pressure hold (3,750 PSI / 10 min; 0.0 SCFH leak) | PLC digital pressure transducer + leak detector | `QualityAssuranceHandling.svc` | Auto-quarantine in ERP; blocks outbound shipping traveler |
| **ASME Sec III** | CMTR chemistry & zero scrap tolerance | Raw material laboratory CMTR records | `02_silver_conformed.py` | Order release blocked; scrap > 0 triggers administrative hold |
| **NAVSEA 250-1500-1** | Qualified NDT sign-off (PT/UT/VT) | Inspector badge scan + calibrated NDT gear | Routing Predecessor Locks | Next operation locked until certified inspector signs off |
