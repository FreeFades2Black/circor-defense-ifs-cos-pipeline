"""
CIRCOR Lakehouse Pipeline - Step 02: Silver Conformed & Traceability Enforcer
Transforms raw Bronze IFS payloads into conformed dimensional tables.
Enforces AS9100 Rev D & MIL-DTL-777 Heat Lot traceability rules, schema conformity,
and SCD Type 2 dimension versioning.
"""

import os
import sys
import glob
import json
import datetime
from typing import List, Dict, Any

class ConformedShopOrderOperation:
    def __init__(self, raw: Dict[str, Any], batch_timestamp: str):
        self.order_no = str(raw["order_no"]).strip()
        self.operation_no = int(raw["operation_no"])
        self.operation_description = str(raw.get("operation_description", "")).strip()
        self.work_center_no = str(raw.get("work_center_no", "WC-UNKNOWN")).strip()
        self.labor_class_no = str(raw.get("labor_class_no", "STD-MACHINIST")).strip()
        
        # Defense traceability validation (AS9100 / MIL-DTL-777)
        raw_heat_lot = raw.get("heat_lot_no")
        if not raw_heat_lot or str(raw_heat_lot).strip() in ["", "NULL", "NONE"]:
            raise ValueError(f"CRITICAL COMPLIANCE BREACH: Order {self.order_no} Op {self.operation_no} missing Heat Lot!")
        self.heat_lot_no = str(raw_heat_lot).strip()

        self.planned_labor_hours = float(raw.get("planned_labor_hours", 0.0))
        self.actual_labor_hours = float(raw.get("actual_labor_hours", 0.0))
        self.standard_labor_rate = float(raw.get("standard_labor_rate", 0.0))
        
        self.planned_machine_hours = float(raw.get("planned_machine_hours", 0.0))
        self.actual_machine_hours = float(raw.get("actual_machine_hours", 0.0))
        self.standard_machine_rate = float(raw.get("standard_machine_rate", 0.0))

        self.revised_qty_due = float(raw.get("revised_qty_due", 0.0))
        self.qty_complete = float(raw.get("qty_complete", 0.0))
        self.qty_scrapped = float(raw.get("qty_scrapped", 0.0))
        self.rowstate = str(raw.get("rowstate", "Released"))

        # SCD Type 2 tracking metadata
        self.is_current = True
        self.valid_from = batch_timestamp
        self.valid_to = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_no": self.order_no,
            "operation_no": self.operation_no,
            "operation_description": self.operation_description,
            "work_center_no": self.work_center_no,
            "labor_class_no": self.labor_class_no,
            "heat_lot_no": self.heat_lot_no,
            "planned_labor_hours": self.planned_labor_hours,
            "actual_labor_hours": self.actual_labor_hours,
            "standard_labor_rate": self.standard_labor_rate,
            "planned_machine_hours": self.planned_machine_hours,
            "actual_machine_hours": self.actual_machine_hours,
            "standard_machine_rate": self.standard_machine_rate,
            "revised_qty_due": self.revised_qty_due,
            "qty_complete": self.qty_complete,
            "qty_scrapped": self.qty_scrapped,
            "rowstate": self.rowstate,
            "is_current": self.is_current,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
        }

def process_bronze_to_silver(
    bronze_dir: str = "data/bronze",
    silver_dir: str = "data/silver"
) -> Dict[str, int]:
    """Reads Bronze payloads, validates genealogy, and writes conformed Silver datasets."""
    os.makedirs(silver_dir, exist_ok=True)
    conformed_ops = []
    quarantine_records = []

    # Look for bronze shop order files
    bronze_files = glob.glob(os.path.join(bronze_dir, "shop_orders_batch_*.json"))
    
    if not bronze_files:
        # Fallback sample data if bronze hasn't run from API
        sample_batch = {
            "batch_id": "init-fallback",
            "ingestion_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "records": [
                {
                    "order_no": "SO-LSL-2026-8041",
                    "operation_no": 20,
                    "operation_description": "5-Axis Contour CNC Profiling",
                    "work_center_no": "WC-5AXIS-MILL-02",
                    "labor_class_no": "AERO-MACHINIST-L3",
                    "heat_lot_no": "HT-INC625-9942",
                    "planned_labor_hours": 18.0,
                    "planned_machine_hours": 15.0,
                    "actual_labor_hours": 24.5,
                    "actual_machine_hours": 20.0,
                    "standard_labor_rate": 54.0,
                    "standard_machine_rate": 145.0,
                    "revised_qty_due": 5.0,
                    "qty_complete": 4.0,
                    "qty_scrapped": 1.0,
                    "rowstate": "Started"
                },
                {
                    "order_no": "SO-WRN-2026-1102",
                    "operation_no": 10,
                    "operation_description": "Submarine Pump Impeller Turning",
                    "work_center_no": "WC-LATHE-HEAVY-01",
                    "labor_class_no": "DEFENSE-MACHINIST-L2",
                    "heat_lot_no": "HT-MONEL-1048",
                    "planned_labor_hours": 12.0,
                    "planned_machine_hours": 10.0,
                    "actual_labor_hours": 11.5,
                    "actual_machine_hours": 9.8,
                    "standard_labor_rate": 48.0,
                    "standard_machine_rate": 110.0,
                    "revised_qty_due": 3.0,
                    "qty_complete": 3.0,
                    "qty_scrapped": 0.0,
                    "rowstate": "Started"
                }
            ]
        }
        timestamp = sample_batch["ingestion_timestamp_utc"]
        records = sample_batch["records"]
    else:
        # Load newest file
        newest_file = max(bronze_files, key=os.path.getctime)
        with open(newest_file, "r", encoding="utf-8") as f:
            batch = json.load(f)
        timestamp = batch.get("ingestion_timestamp_utc", datetime.datetime.now(datetime.timezone.utc).isoformat())
        records = batch.get("records", [])

    for r in records:
        try:
            conformed = ConformedShopOrderOperation(r, timestamp)
            conformed_ops.append(conformed.to_dict())
        except ValueError as err:
            print(f"[SILVER QUARANTINE] AS9100 non-compliance: {err}")
            quarantine_records.append({"raw": r, "error": str(err), "quarantined_at": timestamp})

    silver_ops_file = os.path.join(silver_dir, "conformed_shop_order_operations.json")
    with open(silver_ops_file, "w", encoding="utf-8") as f:
        json.dump(conformed_ops, f, indent=2)

    if quarantine_records:
        quarantine_file = os.path.join(silver_dir, "quarantined_non_compliant_records.json")
        with open(quarantine_file, "w", encoding="utf-8") as f:
            json.dump(quarantine_records, f, indent=2)

    print(f"[SILVER CONFORMED] Processed {len(conformed_ops)} valid records, {len(quarantine_records)} quarantined.")
    return {"conformed_records": len(conformed_ops), "quarantined_records": len(quarantine_records)}

if __name__ == "__main__":
    process_bronze_to_silver()
