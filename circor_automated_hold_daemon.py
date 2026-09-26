"""
CIRCOR Automated Quality & Variance Hold Daemon
Reads flagged non-conformances and executes automated order holds in IFS Cloud.
"""

import sys
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

IFS_ENDPOINT = "http://localhost:8000/ifs"

def execute_circor_order_holds(flagged_orders: list, endpoint: str = IFS_ENDPOINT) -> list:
    results = []
    for order in flagged_orders:
        order_no = order["order_no"]
        reason = (
            f"COS Hold: Cost drift reached {order['variance_percentage']}% "
            f"with FPY of {order['first_pass_yield']}%. Heat Lot: {order['heat_lot_no']}."
        )

        logging.warning(f"CIRCOR Policy Triggered: Placing Order {order_no} on hold in IFS...")

        url = f"{endpoint}/ShopOrderHandling.svc/ShopOrderSet('{order_no}')/ParkOrder"
        params = {"reason": reason}

        try:
            res = requests.post(url, params=params, timeout=5)
            if res.status_code == 200:
                payload = res.json()
                logging.info(f"IFS Order {order_no} successfully PARKED. Response: {payload}")
                results.append({"order_no": order_no, "status": "PARKED", "response": payload})
            else:
                logging.error(f"Failed to hold order {order_no}. HTTP code: {res.status_code}")
                results.append({"order_no": order_no, "status": "ERROR", "http_code": res.status_code})
        except Exception as exc:
            logging.error(f"Error reaching IFS Cloud endpoint: {str(exc)}")
            results.append({"order_no": order_no, "status": "UNREACHABLE", "error": str(exc)})
    return results

if __name__ == "__main__":
    sample_flagged_work = [
        {
            "order_no": "SO-LSL-2026-8041",
            "heat_lot_no": "HT-INC625-9942",
            "variance_percentage": 34.1,
            "first_pass_yield": 80.0
        }
    ]
    execute_circor_order_holds(sample_flagged_work)
