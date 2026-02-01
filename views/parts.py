import streamlit as st
from utils.calculations import CostCalculator

def render_parts_view():
    st.markdown("## ⚙️ Process 3: Parts Machining")
    
    # Retrieve Input Cost
    prev_cost = st.session_state.get('calculated_costs', {}).get('sheet_per_kg', 0.0)
    
    if prev_cost == 0:
        st.warning("⚠️ Sheet Cost not calculated yet. Using provisional market rate.")
        prev_cost = 650.0 
        
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header">INPUT: Sheet Cost @ ₹{prev_cost:.2f}/kg</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Part Specs (in KG)")
        # Example Part
        gross_w = st.number_input("Gross Weight (Input Sheet per part) [KG]", value=1.000, step=0.001, format="%.3f")
        
        # Default Net Weight based on Dashboard Yield if available
        p3_yield = st.session_state.process_params.get('p3_yield_pct', 65.0)
        default_net = gross_w * (p3_yield / 100.0)
        
        net_w = st.number_input("Net Weight (Finished Part) [KG]", value=default_net, step=0.001, format="%.3f")
        
        yield_calc = (net_w / gross_w * 100) if gross_w > 0 else 0
        st.caption(f"Material Yield: {yield_calc:.1f}%")

    with c2:
        st.subheader("Machining parameters")
        machining_cost = st.number_input("Machining/Labor Cost (₹/piece)", value=st.session_state.process_params['machining_cost'])
        
        default_scrap = st.session_state.get('indicative_scrap_rate', 350.0)
        scrap_rate = st.number_input("Scrap Recovery (₹/kg)", value=default_scrap, help=f"Auto-calculated: ₹{default_scrap:.2f}")
        
        if abs(scrap_rate - default_scrap) < 1.0:
            st.caption("🔗 Linked to Auto Rate")
        
        st.session_state.process_params['machining_cost'] = machining_cost
        st.session_state.process_params['p3_scrap_rate'] = scrap_rate

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Calculate
    result = CostCalculator.calculate_part_cost(
        sheet_cost_per_kg=prev_cost,
        part_weight_kg=net_w,
        gross_weight_kg=gross_w,
        scrap_recovery_price=scrap_rate,
        machining_cost_per_part=machining_cost
    )
    
    # Financials
    st.markdown("### 💰 Pricing")
    margin_pct = st.number_input("Profit Margin (%)", value=10.0, step=0.5, key='p3_margin')
    
    selling_price_part = result['total_cost_per_part'] * (1 + margin_pct/100)
    selling_price_kg = result['effective_cost_per_kg_finished'] * (1 + margin_pct/100)
    
    # Store
    st.session_state.calculated_costs['part_unit_cost'] = result['total_cost_per_part']
    
    # Results
    st.markdown("### 🏆 Final Product Pricing")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.markdown("**1. Net Material Cost**")
        st.write(f"Gross: {gross_w}kg x ₹{prev_cost:.2f} = ₹{result['material_cost']:.2f}")
        st.write(f"Scrap: -{gross_w - net_w:.3f}kg x ₹{scrap_rate:.2f} = -₹{result['scrap_credit']:.2f}")
        net_mat_cost = result['material_cost'] - result['scrap_credit']
        st.markdown(f"**= ₹{net_mat_cost:.2f}** (for {net_w:.3f} Kgs)")
        
        if net_w > 0:
            st.divider()
            st.caption("Rate per Kg Finished:")
            st.markdown(f"**{net_mat_cost:.2f} / {net_w:.3f} = ₹{net_mat_cost/net_w:.2f}/kg**")
        
    with kpi2:
        st.markdown("**2. Processing**")
        st.metric("Machining Overhead", f"₹{result['machining_cost']:.2f}")
        st.caption("Labor + Consumables")
        
    with kpi3:
        st.markdown(f"""
        <div class="card" style="border: 1px solid #1f77b4;">
            <div class="card-header" style="color: #1f77b4;">Unit Cost (Factory)</div>
            <div class="metric-value">₹{result['total_cost_per_part']:.2f}</div>
            <div class="metric-label">Per Piece</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card" style="border: 1px solid #FFD700; margin-top: 10px;">
        <div class="card-header" style="color: #FFD700;">Selling Price (Finished)</div>
        <div class="metric-value">₹{selling_price_kg:.2f}</div>
        <div class="metric-label">Per Kg @ {margin_pct}% Margin</div>
        <div class="metric-label" style="font-size: 0.8em; color: #666;">(₹{selling_price_part:.2f} / piece)</div>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown(f"**Effective Rate on Finished Weight:** ₹{result['effective_cost_per_kg_finished']:.2f} / kg")
