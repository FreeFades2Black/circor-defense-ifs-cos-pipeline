# CIRCOR Multi-Site ERP Cutover Runbook: 72-Hour Plant Go-Live

* **Target Site:** Leslie Controls (Tampa, FL) / Warren Pumps (Warren, MA)
* **Transition:** Legacy ERP (Infor / AS400) to IFS Cloud 24R2
* **Command Lead:** IFS Solution Architect

---

## T-72 Hours (Friday, 12:00 PM) - Operational Freeze
* [ ] **12:00 PM:** Freeze engineering changes (ECOs) in PLM; lock Bill of Materials revisions.
* [ ] **02:00 PM:** Cease external Purchase Order receipts in legacy ERP.
* [ ] **04:00 PM:** Shift 1 ends; complete final legacy shop order time clockings.
* [ ] **05:00 PM:** Read-Only Lock placed on legacy ERP database instances.
* [ ] **06:00 PM:** Kick off legacy data extraction scripts (Parts, Open POs, Stock Balances, WIP).

---

## T-48 Hours (Saturday, 08:00 AM) - Reconciliation & Staging
* [ ] **08:00 AM:** Physical stockroom inventory reconciliation: Verify high-dollar alloy forgings (Inconel, Monel) match extracted counts.
* [ ] **10:00 AM:** Run IFS Data Migration Tool staging validation jobs.
* [ ] **12:00 PM:** Load Part Masters and Cost Set 1 standard cost trees.
* [ ] **02:00 PM:** Execute General Ledger balance validation with Corporate Controller.
* [ ] **04:00 PM:** Load Open Purchase Orders and link supplier acknowledgments.
* [ ] **06:00 PM:** Load open Shop Order headers and active operations.

---

## T-24 Hours (Sunday, 08:00 AM) - Trial Balance & Floor Prep
* [ ] **08:00 AM:** Run Trial Balance reconciliation in IFS Finance; compare against legacy closing extract.
* [ ] **10:00 AM:** Verify Aurena Shop Floor Workbench tablets and barcode scanners at all machine cells.
* [ ] **12:00 PM:** Sanity check: Run test clocking and test hydro inspection on a simulated order; verify OData listeners capture events.
* [ ] **02:00 PM:** Go/No-Go Decision Gate with Plant General Manager and VP of IT.
* [ ] **04:00 PM:** Unlock production IFS Cloud environment for plant supervisors.
* [ ] **06:00 PM:** Release shift 1 production shop orders to machine queues.

---

## Go-Live Day (Monday, 05:30 AM) - First Production Shift
* [ ] **05:30 AM:** Lead architect present on the shop floor for shift start.
* [ ] **06:00 AM:** Monitor first live clockings on Shop Floor Workbench.
* [ ] **08:00 AM:** Convene first hourly War Room checkpoint with cell leads.
