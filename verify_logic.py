import sys
import os

# Add local directory to path to allow imports
sys.path.append(os.getcwd())

from utils.calculations import CostCalculator

def test_logic():
    print("--- Starting Verification (Refined) ---")
    
    # Inputs
    cu_rate = 750.0
    zn_rate = 240.0
    
    # Process 1: Ingot
    print(f"\n[Process 1] Ingot (Cu {cu_rate}, Zn {zn_rate})")
    # Breakdown: Elec 8, Lab 2, Cons 3, Over 2 = Total 15
    p1 = CostCalculator.calculate_ingot_cost(
        cu_price=cu_rate, zn_price=zn_rate,
        cu_pct=63.0, zn_pct=37.0,
        burning_loss_pct=1.5,
        elec_cost=8.0, labor_cost=2.0, consumable_cost=3.0, overhead_cost=2.0
    )
    print(f"  > Raw Material Cost: {p1['rm_cost']:.2f}")
    print(f"  > Conversion Cost: {p1['conversion_cost_total']:.2f}")
    print(f"  > Final Ingot Cost: {p1['final_cost_per_kg']:.2f}")
    
    # Process 2: Sheet
    print(f"\n[Process 2] Sheet (Input: {p1['final_cost_per_kg']:.2f})")
    p2 = CostCalculator.calculate_sheet_cost(
        ingot_cost_per_kg=p1['final_cost_per_kg'],
        yield_pct=92.0,
        scrap_recovery_price=400.0,
        process_cost_per_kg=12.0
    )
    print(f"  > Sheet Cost: {p2['final_cost_per_kg']:.2f}")
    
    # Process 3: Parts (KG UNITS)
    print(f"\n[Process 3] Parts (Input: {p2['final_cost_per_kg']:.2f})")
    # 0.050 KG Gross, 0.035 KG Net
    p3 = CostCalculator.calculate_part_cost(
        sheet_cost_per_kg=p2['final_cost_per_kg'],
        part_weight_kg=0.035,
        gross_weight_kg=0.050,
        scrap_recovery_price=350.0,
        machining_cost_per_part=5.0
    )
    print(f"  > Unit Cost: {p3['total_cost_per_part']:.2f}")
    print(f"  > Effective / kg: {p3['effective_cost_per_kg_finished']:.2f}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_logic()
