class CostCalculator:
    @staticmethod
    def calculate_ingot_cost(
        cu_price, zn_price, 
        cu_pct, zn_pct, 
        burning_loss_pct, 
        elec_cost=0,
        labor_cost=0,
        consumable_cost=0,
        overhead_cost=0
    ):
        """
        Calculates the cost of 1 kg of Ingot.
        """
        total_input_weight = 1.0
        
        # Raw Material Cost
        rm_cost = (cu_price * (cu_pct/100)) + (zn_price * (zn_pct/100))
        
        # Total Conversion Cost (Input Basis)
        conversion_cost_input = elec_cost + labor_cost + consumable_cost + overhead_cost
        
        # Total cost before loss
        total_cost_input = rm_cost + conversion_cost_input
        
        # Output Weight after Burning Loss
        output_weight = total_input_weight * (1 - (burning_loss_pct/100))
        
        # Effective Cost per Kg of Output
        if output_weight > 0:
            final_cost_per_kg = total_cost_input / output_weight
        else:
            final_cost_per_kg = 0
            
        return {
            "rm_cost": rm_cost,
            "conversion_cost_total": conversion_cost_input,
            "breakdown": {
                "electricity": elec_cost,
                "labor": labor_cost,
                "consumables": consumable_cost,
                "overhead": overhead_cost
            },
            "burning_loss_weight": total_input_weight - output_weight,
            "burning_loss_value": (total_input_weight - output_weight) * rm_cost,
            "output_weight": output_weight,
            "final_cost_per_kg": final_cost_per_kg
        }

    @staticmethod
    def calculate_sheet_cost(ingot_cost_per_kg, yield_pct, scrap_recovery_price, process_cost_per_kg):
        """ Calculates Sheet Cost """
        input_weight = 1.0
        input_cost = ingot_cost_per_kg 
        
        total_input_cost = input_cost + process_cost_per_kg
        
        good_output_weight = input_weight * (yield_pct / 100)
        scrap_weight = input_weight - good_output_weight
        
        scrap_credit = scrap_weight * scrap_recovery_price
        net_cost = total_input_cost - scrap_credit
        
        if good_output_weight > 0:
            final_cost_per_kg = net_cost / good_output_weight
        else:
            final_cost_per_kg = 0
            
        return {
            "input_cost": input_cost,
            "processing_cost": process_cost_per_kg,
            "scrap_weight": scrap_weight,
            "scrap_credit": scrap_credit,
            "good_output_weight": good_output_weight,
            "final_cost_per_kg": final_cost_per_kg
        }

    @staticmethod
    def calculate_part_cost(sheet_cost_per_kg, part_weight_kg, gross_weight_kg, scrap_recovery_price, machining_cost_per_part):
        """ Calculates Part Cost (KG units) """
        material_cost = gross_weight_kg * sheet_cost_per_kg
        scrap_weight_kg = gross_weight_kg - part_weight_kg
        scrap_credit = scrap_weight_kg * scrap_recovery_price
        
        net_material_cost = material_cost - scrap_credit
        total_cost = net_material_cost + machining_cost_per_part
        
        return {
            "material_cost": material_cost,
            "scrap_credit": scrap_credit,
            "machining_cost": machining_cost_per_part,
            "total_cost_per_part": total_cost,
            "effective_cost_per_kg_finished": (total_cost / part_weight_kg) if part_weight_kg > 0 else 0
        }

    @staticmethod
    def calculate_financials(base_cost, interest_rate_pa, holding_days, margin_pct):
        """
        Adds Interest (Working Capital) and Profit Margin.
        """
        # Interest on Working Capital (Cost * Rate * Days/365)
        interest_cost = base_cost * (interest_rate_pa / 100) * (holding_days / 365)
        
        cost_with_interest = base_cost + interest_cost
        
        # Margin (Percentage of Selling Price or Cost? Usually Cost Plus is safer for simple apps)
        # "Cost + Profit = Selling Price" implies Cost + (Cost * Margin%) = Price
        profit_amount = cost_with_interest * (margin_pct / 100)
        
        selling_price = cost_with_interest + profit_amount
        
        return {
            "base_cost": base_cost,
            "interest_cost": interest_cost,
            "total_cost": cost_with_interest,
            "profit_margin": profit_amount,
            "selling_price": selling_price
        }

    @staticmethod
    def estimate_scrap_rate(metal_price, purity_pct=100, recovery_factor=0.9):
        """
        Auto-estimates scrap value typically lower than virgin metal.
        """
        return metal_price * (purity_pct/100) * recovery_factor
