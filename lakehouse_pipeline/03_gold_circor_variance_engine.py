"""
CIRCOR Lakehouse Pipeline - Step 03: Gold CIRCOR Variance & Lean Mart Engine
Computes CIRCOR Operating System (COS) metrics from conformed Silver records:
- Labor & Machine Variance ($)
- Total Cost Variance (%)
- First Pass Yield (FPY %)
- Hold Flag generation for containment daemon
"""

import os
import sys
import json

# Add parent directory to sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from lakehouse_pipeline.circor_cos_pyspark_pipeline import calculate_cos_lean_kpis
except ImportError:
    from circor_cos_pyspark_pipeline import calculate_cos_lean_kpis

from pyspark.sql import SparkSession

def run_gold_variance_engine(
    silver_dir: str = "data/silver",
    gold_dir: str = "data/gold"
):
    os.makedirs(gold_dir, exist_ok=True)
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    silver_ops_file = os.path.join(silver_dir, "conformed_shop_order_operations.json")
    if os.path.exists(silver_ops_file):
        with open(silver_ops_file, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = [
            {
                "order_no": "Freez-SO-2026-8041",
                "operation_no": 20,
                "work_center_no": "Freez-WC-5AXIS-MILL-02",
                "heat_lot_no": "Freez-HEAT-INC625-9942",
                "planned_labor_hours": 18.0,
                "actual_labor_hours": 24.5,
                "standard_labor_rate": 54.0,
                "planned_machine_hours": 15.0,
                "actual_machine_hours": 20.0,
                "standard_machine_rate": 145.0,
                "revised_qty_due": 5.0,
                "qty_scrapped": 1.0,
                "rowstate": "Started"
            },
            {
                "order_no": "Freez-SO-2026-1102",
                "operation_no": 10,
                "work_center_no": "Freez-WC-LATHE-01",
                "heat_lot_no": "Freez-HEAT-MNL-1048",
                "planned_labor_hours": 12.0,
                "actual_labor_hours": 11.5,
                "standard_labor_rate": 48.0,
                "planned_machine_hours": 10.0,
                "actual_machine_hours": 9.8,
                "standard_machine_rate": 110.0,
                "revised_qty_due": 3.0,
                "qty_scrapped": 0.0,
                "rowstate": "Started"
            }
        ]

    spark = SparkSession.builder \
        .appName("Frees-COS-LeanVarianceEngine") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()


    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]

    clean_tuples = [
        (
            r["order_no"], int(r["operation_no"]), r["work_center_no"], r["heat_lot_no"],
            float(r["planned_labor_hours"]), float(r["actual_labor_hours"]), float(r["standard_labor_rate"]),
            float(r["planned_machine_hours"]), float(r["actual_machine_hours"]), float(r["standard_machine_rate"]),
            float(r["revised_qty_due"]), float(r["qty_scrapped"]), r["rowstate"]
        )
        for r in records
    ]

    df = spark.createDataFrame(clean_tuples, schema)
    gold_kpis_df = calculate_cos_lean_kpis(spark, df)

    gold_results = [row.asDict() for row in gold_kpis_df.collect()]

    # Save to gold operational mart
    gold_mart_path = os.path.join(gold_dir, "cos_operational_variance_mart.json")
    with open(gold_mart_path, "w", encoding="utf-8") as f:
        json.dump(gold_results, f, indent=2)

    # Filter hold candidates
    hold_candidates = [r for r in gold_results if r.get("trigger_administrative_hold")]
    hold_queue_path = os.path.join(gold_dir, "remediation_hold_queue.json")
    with open(hold_queue_path, "w", encoding="utf-8") as f:
        json.dump(hold_candidates, f, indent=2)

    print(f"[GOLD MART] Computed {len(gold_results)} operational KPIs.")
    print(f"[GOLD MART] {len(hold_candidates)} orders queued for administrative hold remediation.")

    print("\nPySpark Variance Table:")
    gold_kpis_df.select(
        "order_no", "heat_lot_no", "labor_cost_variance",
        "machine_cost_variance", "total_cost_variance",
        "variance_percentage", "first_pass_yield", "trigger_administrative_hold"
    ).show(truncate=False)

    return gold_results


if __name__ == "__main__":
    run_gold_variance_engine()
