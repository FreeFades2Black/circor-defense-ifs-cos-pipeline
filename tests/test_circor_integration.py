"""
Unit & Integration Test Suite for CIRCOR International IFS Cloud & COS Integration
Verifies OData endpoints, Hydrostatic QA gates, PySpark KPI calculations, and the Hold Daemon.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from pyspark.sql import SparkSession

# Ensure repository root is on sys.path for direct pytest invocation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from circor_mock_ifs_api import app, PARTS_DB, SHOP_ORDERS_DB, QUALITY_LOGS_DB, seed_circor_data

from circor_cos_pyspark_pipeline import calculate_cos_lean_kpis
from circor_automated_hold_daemon import execute_circor_order_holds

@pytest.fixture(autouse=True)
def reset_db():
    PARTS_DB.clear()
    SHOP_ORDERS_DB.clear()
    QUALITY_LOGS_DB.clear()
    seed_circor_data()

@pytest.fixture(scope="session")
def spark_session():
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    spark = SparkSession.builder \
        .appName("CIRCOR-TestSession") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()
    yield spark
    spark.stop()

def test_get_part_catalog():
    client = TestClient(app)
    res = client.get("/ifs/PartCatalogHandling.svc/PartCatalogSet")
    assert res.status_code == 200
    parts = res.json()
    assert len(parts) >= 2
    part_numbers = [p["part_no"] for p in parts]
    assert "Freez-PART-VLV-CRYO-6IN" in part_numbers
    assert "Freez-PART-PUMP-SUB-12IN" in part_numbers

def test_get_shop_orders():
    client = TestClient(app)
    res = client.get("/ifs/ShopOrderHandling.svc/ShopOrderSet")
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) >= 2
    so = client.get("/ifs/ShopOrderHandling.svc/ShopOrderSet('Freez-SO-2026-8041')")
    assert so.status_code == 200
    assert so.json()["heat_lot_no"] == "Freez-HEAT-INC625-9942"

def test_hydrostatic_testing_pass():
    client = TestClient(app)
    report = {
        "test_id": "HT-2026-001",
        "order_no": "Freez-SO-2026-1102",
        "operation_no": 10,
        "tested_by_badge": "QA-INSP-88",
        "test_pressure_psi": 6000.0,
        "target_pressure_psi": 6000.0,
        "hold_duration_minutes": 15.0,
        "leak_rate_scfh": 0.0,
        "result": "Pass",
        "notes": "Zero pressure drop observed across 15 minute soak."
    }
    res = client.post("/ifs/QualityAssuranceHandling.svc/SubmitHydroTest", json=report)
    assert res.status_code == 201
    assert res.json()["status"] == "SUCCESS"
    assert SHOP_ORDERS_DB["Freez-SO-2026-1102"].rowstate == "Started"

def test_hydrostatic_testing_fail_triggers_hold():
    client = TestClient(app)
    report = {
        "test_id": "HT-2026-002",
        "order_no": "Freez-SO-2026-1102",
        "operation_no": 10,
        "tested_by_badge": "QA-INSP-88",
        "test_pressure_psi": 5850.0,
        "target_pressure_psi": 6000.0,
        "hold_duration_minutes": 8.5,
        "leak_rate_scfh": 0.04,
        "result": "Fail",
        "notes": "Seat packing leak detected under ASME submarine proof cycle."
    }
    res = client.post("/ifs/QualityAssuranceHandling.svc/SubmitHydroTest", json=report)
    assert res.status_code == 201
    assert res.json()["status"] == "HOLD_TRIGGERED"
    # Order must automatically transition to Parked
    assert SHOP_ORDERS_DB["Freez-SO-2026-1102"].rowstate == "Parked"


def test_pyspark_cos_variance_engine(spark_session):
    raw_records = [
        ("SO-TEST-1", 10, "WC-1", "HT-1", 10.0, 15.0, 50.0, 10.0, 10.0, 100.0, 10.0, 2.0, "Started"),
        ("SO-TEST-2", 10, "WC-1", "HT-2", 10.0, 9.0, 50.0, 10.0, 10.0, 100.0, 10.0, 0.0, "Started")
    ]
    schema = [
        "order_no", "operation_no", "work_center_no", "heat_lot_no",
        "planned_labor_hours", "actual_labor_hours", "standard_labor_rate",
        "planned_machine_hours", "actual_machine_hours", "standard_machine_rate",
        "revised_qty_due", "qty_scrapped", "rowstate"
    ]
    df = spark_session.createDataFrame(raw_records, schema)
    results_df = calculate_cos_lean_kpis(spark_session, df)
    rows = {r["order_no"]: r for r in results_df.collect()}

    # SO-TEST-1: Labor exceeded (15 vs 10 hrs * $50 = +$250), Scrap = 2 units (FPY = 80%)
    assert rows["SO-TEST-1"]["labor_cost_variance"] == 250.0
    assert rows["SO-TEST-1"]["first_pass_yield"] == 80.0
    assert rows["SO-TEST-1"]["trigger_administrative_hold"] is True

    # SO-TEST-2: Under standard, 0 scrap (FPY = 100%)
    assert rows["SO-TEST-2"]["labor_cost_variance"] == -50.0
    assert rows["SO-TEST-2"]["first_pass_yield"] == 100.0
    assert rows["SO-TEST-2"]["trigger_administrative_hold"] is False


def test_actuarial_insurance_underwriting_model():
    import importlib
    m5 = importlib.import_module("lakehouse_pipeline.05_insurance_risk_actuarial_model")
    res = m5.evaluate_circor_underwriting_models()

    assert "manual_profile" in res
    assert "sensor_profile" in res
    assert "financial_advantages" in res

    # Verify HPO premium savings and working capital unlocked
    assert res["financial_advantages"]["annual_insurance_premium_savings"] == 415140.00
    assert res["financial_advantages"]["working_capital_freed_from_reserves"] == 2754000.00
    assert res["sensor_profile"]["underwriting_tier"] == "Highly Protected Operations (HPO) / Tier-1 Defense Elite"


def test_timesfm_predictive_spindle_forecast():
    import importlib
    m6 = importlib.import_module("lakehouse_pipeline.06_timesfm_predictive_spindle_forecast")
    res = m6.run_timesfm_spindle_inference()

    assert res["order_no"] == "Freez-SO-2026-8041"
    assert res["work_center"] == "Freez-WC-5AXIS-MILL-02"
    assert res["context_window_hours"] == 64
    assert res["forecast_horizon_hours"] == 12
    assert res["predictive_breach_detected"] is True
    assert res["estimated_prevented_scrap_cost"] == 24500.00
    assert "WorkOrderHandling.svc" in res["recommended_maintenance_action"]


def test_temporal_telemetry_engine():
    import importlib
    m7 = importlib.import_module("lakehouse_pipeline.07_temporal_telemetry_engine")
    snapshots = m7.generate_temporal_machining_profile()
    hydro = m7.evaluate_hydro_pressure_curve()

    assert len(snapshots) == 18
    # Early hours nominal
    assert snapshots[0].elapsed_hour == 1
    assert snapshots[0].cumulative_cost_drift == 0.0
    assert snapshots[0].active_hold_triggered is False

    # Hour 15 breaches >15% cost tolerance
    assert snapshots[14].elapsed_hour == 15
    assert snapshots[14].active_hold_triggered is True

    # Hydro curve verification
    assert len(hydro) == 10
    assert hydro[-1]["hold_seconds"] == 600
    assert hydro[-1]["pressure_psi"] >= 3750.0
    assert hydro[-1]["leak_rate_scfh"] == 0.0
    assert hydro[-1]["verification_status"] == "PASS"


