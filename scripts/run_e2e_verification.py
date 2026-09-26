"""
CIRCOR International - End-to-End Integration & Verification Harness
Orchestrates the entire manufacturing loop:
1. Boots Mock IFS Cloud OData Service (:8000)
2. Ingests parts & orders
3. Submits Mil-Spec Hydrostatic Test
4. Executes PySpark CIRCOR Operating System (COS) Lean Variance Engine
5. Dispatches Automated Hold Daemon to Park non-conforming orders in IFS
6. Verifies closed-loop order state
"""

import time
import requests
import uvicorn
import threading
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from circor_mock_ifs_api import app, SHOP_ORDERS_DB
from circor_cos_pyspark_pipeline import run_pipeline
from circor_automated_hold_daemon import execute_circor_order_holds

console = Console()

class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=8000):
        super().__init__(daemon=True)
        self.server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def main():
    console.print(Panel.fit(
        "[bold cyan]CIRCOR INTERNATIONAL &bull; IFS CLOUD &amp; COS ANALYTICS BRIDGE[/bold cyan]\n"
        "[dim]Aerospace &amp; Naval Defense Manufacturing Compliance (AS9100 Rev D / MIL-DTL-777)[/dim]",
        border_style="cyan"
    ))

    # 1. Start Mock IFS Cloud
    port = 8800
    console.print(f"\n[1/5] [bold green]Starting Mock IFS Cloud 24R2 Service (:{port})...[/bold green]")
    server = ServerThread(app, port=port)
    server.start()
    time.sleep(2)

    endpoint = f"http://127.0.0.1:{port}/ifs"

    # 2. Query Initial State
    console.print("[2/5] [bold green]Querying Part Catalog & Shop Floor Workbench...[/bold green]")
    parts = requests.get(f"{endpoint}/PartCatalogHandling.svc/PartCatalogSet").json()
    orders = requests.get(f"{endpoint}/ShopOrderHandling.svc/ShopOrderSet").json()

    table = Table(title="IFS Initial Shop Orders", border_style="dim")
    table.add_column("Order No", style="cyan")
    table.add_column("Contract", style="yellow")
    table.add_column("Part No", style="white")
    table.add_column("Heat Lot", style="magenta")
    table.add_column("State", style="green")

    for o in orders:
        contract_label = "Freez-SITE-LESLIE-01" if "8041" in o["order_no"] else "Freez-SITE-WARREN-01"
        table.add_row(o["order_no"], contract_label, o["work_center_no"], o["heat_lot_no"], o["rowstate"])
    console.print(table)

    # 3. Submit Submarine Proof Hydro Test
    console.print("\n[3/5] [bold green]Submitting Hydrostatic Proof Test (6,000 PSI)...[/bold green]")
    hydro_report = {
        "test_id": "HYDRO-SUB-PROOF-901",
        "order_no": "Freez-SO-2026-1102",
        "operation_no": 10,
        "tested_by_badge": "QA-TECH-WARREN-42",
        "test_pressure_psi": 6000.0,
        "target_pressure_psi": 6000.0,
        "hold_duration_minutes": 15.0,
        "leak_rate_scfh": 0.0,
        "result": "Pass",
        "notes": "Navy Mil-Spec 777 proof cycle passed. No leakage."
    }
    h_res = requests.post(f"{endpoint}/QualityAssuranceHandling.svc/SubmitHydroTest", json=hydro_report).json()
    console.print(f"  [bold]Result:[/bold] {h_res['status']} - {h_res['message']}")

    # 4. Run PySpark COS Lean Analytics
    console.print("\n[4/5] [bold green]Executing PySpark COS Lean Variance & FPY Engine...[/bold green]")
    cos_df = run_pipeline(fetch_from_api=True, api_endpoint=endpoint)
    flagged = cos_df.filter(cos_df.trigger_administrative_hold == True).collect()

    flagged_orders = []
    for row in flagged:
        flagged_orders.append({
            "order_no": row["order_no"],
            "heat_lot_no": row["heat_lot_no"],
            "variance_percentage": row["variance_percentage"],
            "first_pass_yield": row["first_pass_yield"]
        })

    # 5. Dispatch Automated Hold Daemon
    console.print(f"\n[5/5] [bold green]Dispatching Automated Order Hold Daemon ({len(flagged_orders)} flagged)...[/bold green]")
    results = execute_circor_order_holds(flagged_orders, endpoint=endpoint)

    # Final Verification
    final_order = requests.get(f"{endpoint}/ShopOrderHandling.svc/ShopOrderSet('Freez-SO-2026-8041')").json()
    console.print(f"\n[bold yellow]Final IFS Cloud State for Freez-SO-2026-8041:[/bold yellow] [bold red]{final_order['rowstate']}[/bold red]")
    assert final_order["rowstate"] == "Parked", "Order failed to transition to Parked state!"


    server.stop()
    console.print(Panel.fit(
        "[bold green][SUCCESS] CLOSED-LOOP VERIFICATION COMPLETE[/bold green]\n"
        "CIRCOR Operating System (COS) variance containment successfully enforced in IFS Cloud.",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
