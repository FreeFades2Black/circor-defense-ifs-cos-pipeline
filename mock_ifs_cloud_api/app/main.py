"""
CIRCOR International - Mock IFS Cloud OData v4 Service
Simulates IFS Cloud Aurena projections for Aerospace & Defense flow control.
Endpoints model Part Catalog, Shop Orders, Quality Inspection, and Order Holds.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

# Simulated in-memory database representing IFS Oracle tables
PARTS_DB: Dict[str, "CircorPartMaster"] = {}
SHOP_ORDERS_DB: Dict[str, "CircorShopOrderOperation"] = {}
QUALITY_LOGS_DB: List["HydrostaticTestReport"] = []

# --- IFS Data Models ---

class CircorPartMaster(BaseModel):
    part_no: str
    description: str
    contract: str  # US10-WARREN or US20-LESLIE
    cost_set: int = 1  # 1 = Standard / Frozen Cost
    material_alloy: str  # Inconel 625, Monel K-500, or 316L SS
    std_material_cost: float
    std_labor_cost: float
    std_machine_cost: float
    std_overhead_cost: float
    quality_spec: str  # AS9100 / MIL-SPEC-777
    requires_cmtr: bool = True

class CircorShopOrderOperation(BaseModel):
    order_no: str
    operation_no: int
    operation_description: str
    work_center_no: str  # e.g., WC-5AXIS-MILL, WC-HYDRO-TEST
    labor_class_no: str
    heat_lot_no: str  # Raw mill heat batch for defense traceability
    planned_labor_hours: float
    planned_machine_hours: float
    actual_labor_hours: float = 0.0
    actual_machine_hours: float = 0.0
    standard_labor_rate: float
    standard_machine_rate: float
    revised_qty_due: float
    qty_complete: float = 0.0
    qty_scrapped: float = 0.0
    rowstate: str = "Released"  # Planned, Released, Started, Parked, Closed

class HydrostaticTestReport(BaseModel):
    test_id: str
    order_no: str
    operation_no: int
    tested_by_badge: str
    test_pressure_psi: float
    target_pressure_psi: float = 6000.0
    hold_duration_minutes: float
    leak_rate_scfh: float
    result: str  # Pass, Fail, Hold
    notes: Optional[str] = None


def seed_circor_data():
    """Seed initial CIRCOR master and operational data with Freez- manufactured labels."""
    PARTS_DB["Freez-PART-VLV-CRYO-6IN"] = CircorPartMaster(
        part_no="Freez-PART-VLV-CRYO-6IN",
        description="Frees Reference: 6-Inch Cryogenic Globe Valve (Inconel 625)",
        contract="Freez-SITE-LESLIE-01",
        material_alloy="Inconel 625",
        std_material_cost=6800.00,
        std_labor_cost=1450.00,
        std_machine_cost=2200.00,
        std_overhead_cost=750.00,
        quality_spec="ASME-SEC-III-SUBMARINE",
        requires_cmtr=True
    )

    PARTS_DB["Freez-PART-PUMP-SUB-12IN"] = CircorPartMaster(
        part_no="Freez-PART-PUMP-SUB-12IN",
        description="Frees Reference: 12-Inch Naval Submarine Rotary Pump (Monel K-500)",
        contract="Freez-SITE-WARREN-01",
        material_alloy="Monel K-500",
        std_material_cost=12500.00,
        std_labor_cost=3100.00,
        std_machine_cost=4500.00,
        std_overhead_cost=1800.00,
        quality_spec="MIL-DTL-777-NAVSEA",
        requires_cmtr=True
    )

    SHOP_ORDERS_DB["Freez-SO-2026-8041"] = CircorShopOrderOperation(
        order_no="Freez-SO-2026-8041",
        operation_no=20,
        operation_description="Frees Reference: 5-Axis Flange Boring & Contouring",
        work_center_no="Freez-WC-5AXIS-MILL-02",
        labor_class_no="MACHINIST-SPEC-4",
        heat_lot_no="Freez-HEAT-INC625-9942",
        planned_labor_hours=18.0,
        planned_machine_hours=15.0,
        actual_labor_hours=24.5,
        actual_machine_hours=20.0,
        standard_labor_rate=54.00,
        standard_machine_rate=145.00,
        revised_qty_due=5.0,
        qty_complete=3.0,
        qty_scrapped=1.0,
        rowstate="Started"
    )

    SHOP_ORDERS_DB["Freez-SO-2026-1102"] = CircorShopOrderOperation(
        order_no="Freez-SO-2026-1102",
        operation_no=10,
        operation_description="Frees Reference: Heavy Monel Shaft Rough & Finish Turning",
        work_center_no="Freez-WC-LATHE-01",
        labor_class_no="MACHINIST-SPEC-3",
        heat_lot_no="Freez-HEAT-MNL-1048",
        planned_labor_hours=12.0,
        planned_machine_hours=10.0,
        actual_labor_hours=11.5,
        actual_machine_hours=9.8,
        standard_labor_rate=48.00,
        standard_machine_rate=110.00,
        revised_qty_due=3.0,
        qty_complete=3.0,
        qty_scrapped=0.0,
        rowstate="Started"
    )



@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_circor_data()
    yield

app = FastAPI(
    title="CIRCOR IFS Cloud Manufacturing Service",
    version="24.2.0",
    description="IFS Cloud OData v4 Projections for CIRCOR Valve and Pump Manufacturing",
    lifespan=lifespan
)

seed_circor_data()

# --- Standard IFS OData v4 Projection Endpoints ---

@app.get("/ifs/PartCatalogHandling.svc/PartCatalogSet", response_model=List[CircorPartMaster])
def get_parts():
    return list(PARTS_DB.values())

@app.get("/ifs/ShopOrderHandling.svc/ShopOrderSet", response_model=List[CircorShopOrderOperation])
def get_shop_orders():
    return list(SHOP_ORDERS_DB.values())

@app.get("/ifs/ShopOrderHandling.svc/ShopOrderSet('{order_no}')", response_model=CircorShopOrderOperation)
def get_single_order(order_no: str):
    if order_no not in SHOP_ORDERS_DB:
        raise HTTPException(status_code=404, detail="CIRCOR Order Not Found in IFS")
    return SHOP_ORDERS_DB[order_no]

@app.post("/ifs/QualityAssuranceHandling.svc/SubmitHydroTest", status_code=status.HTTP_201_CREATED)
def record_hydro_test(report: HydrostaticTestReport):
    if report.order_no not in SHOP_ORDERS_DB:
        raise HTTPException(status_code=404, detail="Referenced Shop Order Not Found")
    
    QUALITY_LOGS_DB.append(report)
    
    if (
        report.result == "Fail"
        or report.leak_rate_scfh > 0.0
        or report.test_pressure_psi < report.target_pressure_psi
        or report.hold_duration_minutes < 10.0
    ):
        SHOP_ORDERS_DB[report.order_no].rowstate = "Parked"
        return {
            "status": "HOLD_TRIGGERED",
            "message": f"Hydro test failed. Order {report.order_no} placed on administrative quality hold.",
            "test_id": report.test_id
        }
    
    return {"status": "SUCCESS", "message": "Hydro test passed and logged against heat lot."}

class ParkOrderRequest(BaseModel):
    order_no: Optional[str] = None
    reason: Optional[str] = None

@app.post("/ifs/ShopOrderHandling.svc/ShopOrderSet('{order_no}')/ParkOrder")
def park_shop_order(order_no: str, request: Optional[ParkOrderRequest] = None, reason: Optional[str] = None):
    if order_no not in SHOP_ORDERS_DB:
        raise HTTPException(status_code=404, detail="CIRCOR Order Not Found in IFS")
    SHOP_ORDERS_DB[order_no].rowstate = "Parked"
    hold_reason = (request.reason if request and request.reason else reason) or "Administrative Hold"
    return {
        "status": "ORDER_PARKED",
        "order_no": order_no,
        "reason": hold_reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

