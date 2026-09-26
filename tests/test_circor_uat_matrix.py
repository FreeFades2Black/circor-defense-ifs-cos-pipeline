"""
CIRCOR UAT Test Automation Suite
Validates that core business logic, defense compliance checks, and
operational variance flags execute properly under plant conditions.
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
        .appName("CIRCOR-UAT-Tests") \
        .master("local[2]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

def test_uat_heat_lot_and_scrap_triggers_hold(spark):
    """
    UAT Scenario 14.2:
    A high-pressure valve operation incurs scrap on an Inconel casting.
    Verify that the analytics engine flags the order for an immediate administrative hold.
    """
    test_data = [
        ("SO-UAT-001", 10, "WC-MILL-01", "HT-INC625-TEST", 10.0, 10.0, 50.0, 8.0, 8.0, 100.0, 5.0, 1.0, "Started")
    ]
    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]
    
    df = spark.createDataFrame(test_data, schema)
    result = calculate_cos_lean_kpis(spark, df).collect()[0]
    
    # Assertions validating business logic
    assert result["qty_scrapped"] == 1.0
    assert result["first_pass_yield"] == 80.0
    assert result["trigger_administrative_hold"] == True, "Scrap on severe-service part must trigger hold"

def test_uat_within_standard_cost_tolerance(spark):
    """
    UAT Scenario 14.3:
    Standard operation completes within standard variance bounds.
    Verify no administrative hold is placed.
    """
    test_data = [
        ("SO-UAT-002", 10, "WC-LATHE-01", "HT-MONEL-TEST", 10.0, 10.5, 50.0, 8.0, 8.2, 100.0, 5.0, 0.0, "Started")
    ]
    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]
    
    df = spark.createDataFrame(test_data, schema)
    result = calculate_cos_lean_kpis(spark, df).collect()[0]
    
    assert result["variance_percentage"] < 15.0
    assert result["trigger_administrative_hold"] == False
