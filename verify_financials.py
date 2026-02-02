import sys
import os

sys.path.append(os.getcwd())
from utils.calculations import CostCalculator

def test_financials():
    print("--- Testing Financial Logic ---")
    
    # 1. Base Cost
    base_cost = 600.0
    print(f"Base Cost: Rs {base_cost}")
    
    # 2. Financials
    # Interest: 12% for 30 days
    # Margin: 10%
    fin = CostCalculator.calculate_financials(
        base_cost=base_cost,
        interest_rate_pa=12.0,
        holding_days=30,
        margin_pct=10.0
    )
    
    expected_interest = 600 * 0.12 * (30/365) # ~5.91
    print(f"Interest Cost: Rs {fin['interest_cost']:.2f} (Exp: ~{expected_interest:.2f})")
    print(f"Total Cost: Rs {fin['total_cost']:.2f}")
    
    expected_profit = fin['total_cost'] * 0.10
    print(f"Profit: Rs {fin['profit_margin']:.2f} (Exp: ~{expected_profit:.2f})")
    print(f"Selling Price: Rs {fin['selling_price']:.2f}")
    
    # 3. Scrap Estimation
    scrap = CostCalculator.estimate_scrap_rate(750.0, 100, 0.95)
    print(f"Est Copper Scrap: Rs {scrap:.2f} (95% of 750)")
    
    print("--- Test Complete ---")

if __name__ == "__main__":
    test_financials()
