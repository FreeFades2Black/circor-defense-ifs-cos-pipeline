"""
CIRCOR International - Actuarial Underwriting & Insurance Risk Engine
Models how automated sensor gates (DPM Barcode, XRF, WIKA Hydro PLC, NDT RFID)
affect commercial product liability, drydock warranty reserves, and insurance loss profiles.
"""

from dataclasses import dataclass, asdict
import json

@dataclass
class ComplianceRiskProfile:
    architecture_mode: str
    annual_defense_valve_volume: int
    uncontained_escape_rate: float        # Probability of an escape reaching fleet/shipyard
    avg_catastrophic_claim_cost: float     # Direct drydock de-installation + hull delay fees
    annual_expected_loss: float            # Annual Expected Loss (AEL)
    cgl_liability_premium_rate: float      # Premium rate per $1,000 gross output
    gross_annual_insurance_premium: float  # Annual commercial tower premium
    warranty_liability_reserve_pct: float  # US GAAP balance-sheet cash reserve required
    sequestered_working_capital: float     # Cash tied up in warranty reserves
    underwriting_tier: str                 # Insurer risk rating

def evaluate_circor_underwriting_models():
    # Baseline: 12,000 severe-service naval/industrial valves manufactured annually across Leslie & Warren
    annual_valves = 12000
    avg_valve_value = 8500.00
    gross_annual_production = annual_valves * avg_valve_value  # $102,000,000

    # Profile A: Traditional Manual Traveler / Paper Stamping Execution
    # Historical industry escape rate with manual travelers: ~0.42% (42 escapes per 10k valves)
    manual_escape_rate = 0.0042
    catastrophic_failure_cost = 1650000.00  # Average shipyard failure / NAVSEA corrective intervention
    manual_expected_loss = annual_valves * manual_escape_rate * catastrophic_failure_cost

    # Manual underwriting: Standard Standard Commercial Line ($18.50 per $1k output), 4.5% warranty reserve
    manual_profile = ComplianceRiskProfile(
        architecture_mode="Traditional Manual Inspection (Paper Stamped)",
        annual_defense_valve_volume=annual_valves,
        uncontained_escape_rate=manual_escape_rate,
        avg_catastrophic_claim_cost=catastrophic_failure_cost,
        annual_expected_loss=round(manual_expected_loss, 2),
        cgl_liability_premium_rate=18.50,
        gross_annual_insurance_premium=round((gross_annual_production / 1000.0) * 18.50, 2),
        warranty_liability_reserve_pct=4.5,
        sequestered_working_capital=round(gross_annual_production * 0.045, 2),
        underwriting_tier="Standard Industrial / Unmitigated Floor"
    )

    # Profile B: Sensor-Gated Closed-Loop IFS Cloud Execution
    # Optical DPM scanner + XRF chemistry check + S7-1500 Hydro PLC + NDT Badge locks
    # Reduces escape probability to edge sensor defect threshold: < 0.015%
    sensor_escape_rate = 0.00015
    sensor_expected_loss = annual_valves * sensor_escape_rate * catastrophic_failure_cost

    # Highly Protected Operations (HPO) status unlocks 22% insurance premium credit and lower warranty reserve (1.8%)
    sensor_profile = ComplianceRiskProfile(
        architecture_mode="Closed-Loop Sensor Gated (IFS Cloud 24R2 + Event Lakehouse)",
        annual_defense_valve_volume=annual_valves,
        uncontained_escape_rate=sensor_escape_rate,
        avg_catastrophic_claim_cost=catastrophic_failure_cost,
        annual_expected_loss=round(sensor_expected_loss, 2),
        cgl_liability_premium_rate=14.43,  # 22% underwriter credit
        gross_annual_insurance_premium=round((gross_annual_production / 1000.0) * 14.43, 2),
        warranty_liability_reserve_pct=1.8,
        sequestered_working_capital=round(gross_annual_production * 0.018, 2),
        underwriting_tier="Highly Protected Operations (HPO) / Tier-1 Defense Elite"
    )

    # Calculate Enterprise Financial Deltas
    premium_savings = manual_profile.gross_annual_insurance_premium - sensor_profile.gross_annual_insurance_premium
    working_capital_unlocked = manual_profile.sequestered_working_capital - sensor_profile.sequestered_working_capital
    annual_loss_avoidance = manual_profile.annual_expected_loss - sensor_profile.annual_expected_loss

    report = {
        "manual_profile": asdict(manual_profile),
        "sensor_profile": asdict(sensor_profile),
        "financial_advantages": {
            "annual_insurance_premium_savings": round(premium_savings, 2),
            "working_capital_freed_from_reserves": round(working_capital_unlocked, 2),
            "expected_annual_loss_reduction": round(annual_loss_avoidance, 2),
            "combined_annual_balance_sheet_impact": round(premium_savings + working_capital_unlocked, 2)
        }
    }
    return report

if __name__ == "__main__":
    result = evaluate_circor_underwriting_models()
    print("====================================================================================================")
    print("      CIRCOR ACTUARIAL RISK & COMMERCIAL INSURANCE UNDERWRITING MODEL (OMARCHY COMPUTE)")
    print("====================================================================================================")
    print(f"Annual Plant Production Benchmark: 12,000 Valves ($102,000,000 Gross Output)")
    print(f"Expected Annual Loss (Manual Traveler)     : ${result['manual_profile']['annual_expected_loss']:,.2f}")
    print(f"Expected Annual Loss (Sensor Gated)        : ${result['sensor_profile']['annual_expected_loss']:,.2f}")
    print(f"Direct Loss Exposure Avoided               : ${result['financial_advantages']['expected_annual_loss_reduction']:,.2f}")
    print("----------------------------------------------------------------------------------------------------")
    print(f"Commercial Liability Premium (Manual)      : ${result['manual_profile']['gross_annual_insurance_premium']:,.2f}/yr")
    print(f"Commercial Liability Premium (Sensor HPO)  : ${result['sensor_profile']['gross_annual_insurance_premium']:,.2f}/yr")
    print(f"Annual Insurance Premium Credit (22% HPO)  : ${result['financial_advantages']['annual_insurance_premium_savings']:,.2f}/yr")
    print("----------------------------------------------------------------------------------------------------")
    print(f"Sequestered Warranty Reserve (Manual 4.5%) : ${result['manual_profile']['sequestered_working_capital']:,.2f}")
    print(f"Sequestered Warranty Reserve (Sensor 1.8%) : ${result['sensor_profile']['sequestered_working_capital']:,.2f}")
    print(f"Working Capital Unlocked to Balance Sheet  : ${result['financial_advantages']['working_capital_freed_from_reserves']:,.2f}")
    print("====================================================================================================")
