"""
CIRCOR Operating System (COS) Unit Test Suite: Variance Engine
Tests standard cost variance formulas, scrap containment logic, and First Pass Yield calculations.
"""

import os
import sys
import pytest
from pyspark.sql import SparkSession
from lakehouse_pipeline.circor_cos_pyspark_pipeline import calculate_cos_lean_kpis

@pytest.fixture(scope="session")
def spark():
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    return SparkSession.builder \
        .appName("CIRCOR-Unit-Variance-Tests") \
        .master("local[2]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

def test_cost_overrun_triggers_hold(spark):
    """Verify that an operation exceeding 15% cost overrun triggers an administrative hold even with zero scrap."""
    test_data = [
        ("SO-VAR-001", 10, "WC-5AXIS-01", "HT-ALLOY-1", 10.0, 13.0, 50.0, 10.0, 12.0, 100.0, 5.0, 0.0, "Started")
    ]
    # Planned cost: (10*50) + (10*100) = 500 + 1000 = $1500
    # Actual cost: (13*50) + (12*100) = 650 + 1200 = $1850
    # Variance: $350 (23.33% overrun > 15.0%)
    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]
    df = spark.createDataFrame(test_data, schema)
    result = calculate_cos_lean_kpis(spark, df).collect()[0]

    assert result["total_cost_variance"] == 350.0
    assert result["variance_percentage"] == 23.33
    assert result["first_pass_yield"] == 100.0
    assert result["trigger_administrative_hold"] == True

def test_favorable_variance_no_hold(spark):
    """Verify that operations running faster than standard (favorable variance) do not trigger hold."""
    test_data = [
        ("SO-VAR-002", 20, "WC-LATHE-02", "HT-ALLOY-2", 10.0, 8.0, 50.0, 10.0, 8.0, 100.0, 2.0, 0.0, "Started")
    ]
    # Planned: $1500, Actual: $1200, Variance: -$300 (-20.0%)
    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]
    df = spark.createDataFrame(test_data, schema)
    result = calculate_cos_lean_kpis(spark, df).collect()[0]

    assert result["total_cost_variance"] == -300.0
    assert result["variance_percentage"] == -20.0
    assert result["trigger_administrative_hold"] == False
