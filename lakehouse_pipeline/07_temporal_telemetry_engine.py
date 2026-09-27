"""
CIRCOR Temporal Operations Engine
Ingests time-series operational telemetry, computing:
1. Spindle thermal accumulation and heat-driven tool degradation over time.
2. Cumulative labor and machine cost drift hour-by-hour against Cost Set 1.
3. Hydrostatic proof pressure decay curves across elapsed test seconds.
"""

from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

@dataclass
class TemporalSnapshot:
    elapsed_hour: int
    timestamp_utc: str
    order_no: str
    work_center: str
    alloy_grade: str
    cumulative_labor_cost: float
    cumulative_machine_cost: float
    cumulative_planned_cost: float
    cumulative_cost_drift: float
    spindle_temp_celsius: float
    thermal_status: str
    spindle_load_pct: float
    active_hold_triggered: bool

def generate_temporal_machining_profile():
    # Model 18-hour continuous 5-axis profile on Freez-SO-2026-8041 (Inconel 625)
    # Standard rates: Labor $54/hr, Machine $145/hr -> Total Planned $199/hr
    start_time = datetime(2026, 9, 26, 6, 0, 0)
    planned_hourly_rate = 199.00
    actual_labor_rate = 54.00
    actual_machine_rate = 145.00
    
    snapshots = []
    
    # Tool wear acceleration begins at Hour 12 due to thermal buildup
    for hour in range(1, 19):
        current_time = start_time + timedelta(hours=hour)
        
        # In early hours, machine runs nominal; after hour 12, chatter and tool wear increase machine runtime
        if hour <= 11:
            actual_machine_ratio = 1.0
            actual_labor_ratio = 1.0
            temp_c = round(42.0 + (hour * 1.8), 1)
        else:
            # Thermal accumulation causes tool wear, extending cut time per operational cycle
            actual_machine_ratio = 1.0 + ((hour - 11) * 0.12)
            actual_labor_ratio = 1.0 + ((hour - 11) * 0.08)
            temp_c = round(61.8 + ((hour - 11) * 4.2), 1)
            
        cum_planned = round(hour * planned_hourly_rate, 2)
        cum_labor = round(hour * actual_labor_ratio * actual_labor_rate, 2)
        cum_machine = round(hour * actual_machine_ratio * actual_machine_rate, 2)
        cum_actual = cum_labor + cum_machine
        drift = round(cum_actual - cum_planned, 2)
        
        # Thermal status
        if temp_c >= 80.0:
            thermal_state = "CRITICAL_HEAT_BREACH"
        elif temp_c >= 65.0:
            thermal_state = "ELEVATED_THERMAL_DRIFT"
        else:
            thermal_state = "NOMINAL_STABLE"
            
        # Hold trigger: If cumulative cost drift exceeds 15% of planned or thermal state is critical
        pct_drift = (drift / cum_planned) * 100.0 if cum_planned > 0 else 0.0
        hold_flag = pct_drift > 15.0 or thermal_state == "CRITICAL_HEAT_BREACH"
        
        load_pct = round(52.0 + (hour * 1.9), 1)
        
        snapshots.append(TemporalSnapshot(
            elapsed_hour=hour,
            timestamp_utc=current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            order_no="Freez-SO-2026-8041",
            work_center="Freez-WC-5AXIS-MILL-02",
            alloy_grade="Inconel 625",
            cumulative_labor_cost=cum_labor,
            cumulative_machine_cost=cum_machine,
            cumulative_planned_cost=cum_planned,
            cumulative_cost_drift=drift,
            spindle_temp_celsius=temp_c,
            thermal_status=thermal_state,
            spindle_load_pct=load_pct,
            active_hold_triggered=hold_flag
        ))
        
    return snapshots

def evaluate_hydro_pressure_curve():
    # 10-minute continuous proof curve (600 seconds) sampled at 60-second intervals
    # Target: 3,750 PSI, allowable drop = 0 PSI, leak rate = 0.0 SCFH
    curve = []
    base_pressure = 3755.0
    for minute in range(1, 11):
        # Nominal test profile holds pressure continuously
        pressure = base_pressure - (minute * 0.2)
        curve.append({
            "elapsed_minute": minute,
            "hold_seconds": minute * 60,
            "pressure_psi": round(pressure, 1),
            "leak_rate_scfh": 0.0,
            "verification_status": "PASS" if pressure >= 3750.0 else "FAIL"
        })
    return curve

if __name__ == "__main__":
    records = generate_temporal_machining_profile()
    hydro = evaluate_hydro_pressure_curve()
    
    print("====================================================================================================")
    print("        CIRCOR TEMPORAL TELEMETRY ENGINE • HOUR-BY-HOUR COST & HEAT DRIFT ANALYSIS")
    print("====================================================================================================")
    print(f"Target Work Order: Freez-SO-2026-8041 (Inconel 625 5-Axis Milling)")
    print(f"{'Hour':<6} | {'Timestamp UTC':<22} | {'Planned ($)':<12} | {'Actual ($)':<12} | {'Drift ($)':<10} | {'Temp (°C)':<9} | {'Hold Trigger':<12}")
    print("----------------------------------------------------------------------------------------------------")
    for r in records[::3]:  # Sample every 3 hours for terminal display
        print(f"H+{r.elapsed_hour:<4} | {r.timestamp_utc:<22} | ${r.cumulative_planned_cost:<11.2f} | ${(r.cumulative_labor_cost + r.cumulative_machine_cost):<11.2f} | +${r.cumulative_cost_drift:<9.2f} | {r.spindle_temp_celsius:<6}°C | {str(r.active_hold_triggered):<12}")
    print("====================================================================================================")
    print(f"Hydro Proof Verification Curve: 10.0-minute continuous hold at {hydro[-1]['pressure_psi']} PSI (0.0 SCFH leakage)")
    print("====================================================================================================")
