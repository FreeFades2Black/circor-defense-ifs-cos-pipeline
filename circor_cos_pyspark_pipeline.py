"""
CIRCOR Operating System (COS) Operational Intelligence Engine
Transforms IFS Cloud Shop Floor and Quality logs into Gold-level Lean metrics.
"""

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, when, lit

def calculate_cos_lean_kpis(spark: SparkSession, orders_df):
    """
    Computes CIRCOR Operating System KPIs:
    1. Labor Cost Variance = (Actual Labor Hours - Planned Labor Hours) * Standard Rate
    2. Machine Cost Variance = (Actual Machine Hours - Planned Machine Hours) * Standard Rate
    3. Total Cost Variance ($)
    4. First Pass Yield (FPY) = (Revised Qty Due - Qty Scrapped) / Revised Qty Due
    5. Quality Flag: Flags operations where variance exceeds 15% or scrap exceeds 0 units.
    """

    cos_metrics_df = orders_df.withColumn(
        "planned_labor_cost",
        round(col("planned_labor_hours") * col("standard_labor_rate"), 2)
    ).withColumn(
        "actual_labor_cost",
        round(col("actual_labor_hours") * col("standard_labor_rate"), 2)
    ).withColumn(
        "labor_cost_variance",
        round(col("actual_labor_cost") - col("planned_labor_cost"), 2)
    ).withColumn(
        "planned_machine_cost",
        round(col("planned_machine_hours") * col("standard_machine_rate"), 2)
    ).withColumn(
        "actual_machine_cost",
        round(col("actual_machine_hours") * col("standard_machine_rate"), 2)
    ).withColumn(
        "machine_cost_variance",
        round(col("actual_machine_cost") - col("planned_machine_cost"), 2)
    ).withColumn(
        "total_cost_variance",
        round(col("labor_cost_variance") + col("machine_cost_variance"), 2)
    ).withColumn(
        "planned_total_cost",
        col("planned_labor_cost") + col("planned_machine_cost")
    ).withColumn(
        "variance_percentage",
        round((col("total_cost_variance") / col("planned_total_cost")) * 100, 2)
    ).withColumn(
        "first_pass_yield",
        round(((col("revised_qty_due") - col("qty_scrapped")) / col("revised_qty_due")) * 100, 2)
    ).withColumn(
        "trigger_administrative_hold",
        when((col("variance_percentage") > 15.0) | (col("qty_scrapped") > 0.0), lit(True)).otherwise(lit(False))
    )

    return cos_metrics_df

def run_pipeline(fetch_from_api: bool = False, api_endpoint: str = "http://localhost:8000/ifs"):
    """Initialize SparkSession and execute CIRCOR Lean Variance calculations."""
    import os
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    spark = SparkSession.builder \
        .appName("Frees-COS-LeanVarianceEngine") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

    raw_circor_records = []

    if fetch_from_api:
        try:
            import requests
            url = f"{api_endpoint}/ShopOrderHandling.svc/ShopOrderSet"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                orders = res.json()
                for o in orders:
                    raw_circor_records.append((
                        o["order_no"], o["operation_no"], o["work_center_no"], o["heat_lot_no"],
                        float(o["planned_labor_hours"]), float(o["actual_labor_hours"]), float(o["standard_labor_rate"]),
                        float(o["planned_machine_hours"]), float(o["actual_machine_hours"]), float(o["standard_machine_rate"]),
                        float(o["revised_qty_due"]), float(o["qty_scrapped"]), o["rowstate"]
                    ))
        except Exception as e:
            print(f"[WARN] Failed to fetch live from IFS API ({e}). Falling back to static batch.")

    if not raw_circor_records:
        # Default raw order records ingested from IFS Cloud ShopOrderSet with Freez- labeling
        raw_circor_records = [
            ("Freez-SO-2026-8041", 20, "Freez-WC-5AXIS-MILL-02", "Freez-HEAT-INC625-9942", 18.0, 24.5, 54.00, 15.0, 20.0, 145.00, 5.0, 1.0, "Started"),
            ("Freez-SO-2026-1102", 10, "Freez-WC-LATHE-01", "Freez-HEAT-MNL-1048", 12.0, 11.5, 48.00, 10.0, 9.8, 110.00, 3.0, 0.0, "Started")
        ]


    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]

    orders_df = spark.createDataFrame(raw_circor_records, schema)
    cos_results_df = calculate_cos_lean_kpis(spark, orders_df)

    print("\n" + "="*80)
    print("  CIRCOR OPERATING SYSTEM (COS) - LEAN VARIANCE & FIRST PASS YIELD MART")
    print("="*80)

    cos_results_df.select(
        "order_no", "heat_lot_no", "labor_cost_variance",
        "machine_cost_variance", "total_cost_variance",
        "variance_percentage", "first_pass_yield", "trigger_administrative_hold"
    ).show(truncate=False)

    return cos_results_df

if __name__ == "__main__":
    fetch_api = "--from-api" in sys.argv
    run_pipeline(fetch_from_api=fetch_api)
