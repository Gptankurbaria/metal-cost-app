import streamlit as st
from utils.calculations import CostCalculator

def render_ingot_view():
    st.markdown("## 🏗️ Process 1: Ingot Casting")
    
    # Initialize separate params if not exist
    if 'p1_costs' not in st.session_state:
        st.session_state.p1_costs = {
            'elec': 8.0,
            'labor': 2.0,
            'consumables': 3.0,
            'overhead': 2.0
        }
    
    # 1. Inputs Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">🛠️ Production Parameters</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Alloy Mix")
        alloy_cu = st.session_state.process_params['alloy_cu']
        
        # Interactive Inputs
        new_cu = st.number_input("Copper %", value=alloy_cu, step=0.5, min_value=0.0, max_value=100.0)
        new_zn = 100.0 - new_cu
        st.caption(f"Zinc Balance: {new_zn:.1f}%")
        
        # Update State
        st.session_state.process_params['alloy_cu'] = new_cu
        st.session_state.process_params['alloy_zn'] = new_zn
        
        st.subheader("Process Efficiency")
        burning_loss = st.number_input("Burning Loss %", value=st.session_state.process_params['burning_loss'], step=0.1)
        st.session_state.process_params['burning_loss'] = burning_loss

    with col2:
        st.subheader("Conversion Costs (₹/kg)")
        elec = st.number_input("Electricity (Furnace)", value=st.session_state.p1_costs['elec'], step=0.5)
        labor = st.number_input("Labour Charges", value=st.session_state.p1_costs['labor'], step=0.5)
        cons = st.number_input("Furnace Consumables", value=st.session_state.p1_costs['consumables'], step=0.5)
        over = st.number_input("General Overhead", value=st.session_state.p1_costs['overhead'], step=0.5)
        
        # Verify Total
        total_conv = elec + labor + cons + over
        st.info(f"Total Conversion Cost: ₹{total_conv:.2f}/kg")
        
        # Save
        st.session_state.p1_costs.update({
            'elec': elec, 'labor': labor, 'consumables': cons, 'overhead': over
        })
        
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Calculation
    rates = st.session_state.rm_rates
    result = CostCalculator.calculate_ingot_cost(
        cu_price=rates['cu'],
        zn_price=rates['zn'],
        cu_pct=new_cu,
        zn_pct=new_zn,
        burning_loss_pct=burning_loss,
        elec_cost=elec,
        labor_cost=labor,
        consumable_cost=cons,
        overhead_cost=over
    )

    # Financials
    st.markdown("### 💰 Pricing")
    margin_pct = st.number_input("Profit Margin (%)", value=10.0, step=0.5, key='p1_margin')
    
    selling_price = result['final_cost_per_kg'] * (1 + margin_pct/100)
    
    # Store Result globally for next stages
    st.session_state.calculated_costs = st.session_state.get('calculated_costs', {})
    st.session_state.calculated_costs['ingot_per_kg'] = result['final_cost_per_kg']

    # 3. Results Display
    st.markdown("### 📊 Cost Analysis")
    
    r1, r2, r3 = st.columns(3)
    
    with r1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">Base Material Cost</div>
            <div class="metric-value">₹{result['rm_cost']:.2f}</div>
            <div class="metric-label">Weighted Avg Raw Material</div>
        </div>
        """, unsafe_allow_html=True)
        
    with r2:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">Loss Value</div>
            <div class="metric-value" style="color: #ff6b6b;">₹{result['burning_loss_value']:.2f}</div>
            <div class="metric-label">Per kg input ({(burning_loss):.1f}% Loss)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with r3:
        st.markdown(f"""
        <div class="card" style="border: 1px solid #4CAF50;">
            <div class="card-header" style="color: #4CAF50;">Final Ingot Cost</div>
            <div class="metric-value">₹{result['final_cost_per_kg']:.2f}</div>
            <div class="metric-label">Per Kg Output</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"""
    <div class="card" style="border: 1px solid #FFD700; margin-top: 10px;">
        <div class="card-header" style="color: #FFD700;">Selling Price (Ingot)</div>
        <div class="metric-value">₹{selling_price:.2f}</div>
        <div class="metric-label">Per Kg @ {margin_pct}% Margin</div>
    </div>
    """, unsafe_allow_html=True)
