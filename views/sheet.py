import streamlit as st
from utils.calculations import CostCalculator

def render_sheet_view():
    st.markdown("## 📜 Process 2: Sheet Rolling")
    
    # Retrieve Input Cost
    prev_cost = st.session_state.get('calculated_costs', {}).get('ingot_per_kg', 0.0)
    
    if prev_cost == 0:
        st.warning("⚠️ Ingot Cost not calculated yet. Using provisional market rate.")
        prev_cost = 600.0 # Fallback
        
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header">INPUT: Ingot Cost @ ₹{prev_cost:.2f}/kg</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Rolling Efficiency")
        yield_pct = st.slider("Yield % (Good Sheet Output)", 50.0, 100.0, st.session_state.process_params['rolling_yield'])
        st.session_state.process_params['rolling_yield'] = yield_pct
        
        st.metric("Scrap Generation", f"{100-yield_pct:.1f}%")
        
    with col2:
        st.subheader("Costs & Recovery")
        proc_cost = st.number_input("Rolling/Annealing Cost (₹/kg)", value=st.session_state.process_params['rolling_cost'])
        
        # Use Indicative Rate from Sidebar
        default_scrap = st.session_state.get('indicative_scrap_rate', 400.0)
        
        # Display as default, but allow override
        scrap_rate = st.number_input("Scrap Recovery (₹/kg)", value=default_scrap, help=f"Auto-calculated: ₹{default_scrap:.2f}")
        
        if abs(scrap_rate - default_scrap) < 1.0:
            st.caption("🔗 Linked to Auto Rate")
        else:
            st.caption("✏️ Custom Override")
        
        st.session_state.process_params['rolling_cost'] = proc_cost
        st.session_state.process_params['p2_scrap_rate'] = scrap_rate
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Calculate
    result = CostCalculator.calculate_sheet_cost(
        ingot_cost_per_kg=prev_cost,
        yield_pct=yield_pct,
        scrap_recovery_price=scrap_rate,
        process_cost_per_kg=proc_cost
    )

    # Financials
    st.markdown("### 💰 Pricing")
    margin_pct = st.number_input("Profit Margin (%)", value=10.0, step=0.5, key='p2_margin')
    
    selling_price = result['final_cost_per_kg'] * (1 + margin_pct/100)
    
    # Store
    st.session_state.calculated_costs['sheet_per_kg'] = result['final_cost_per_kg']
    
    # Display
    st.markdown("### 📊 Cost Analysis")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(f"Gross Input Cost: ₹{result['input_cost'] + result['processing_cost']:.2f}")
    with c2:
        st.success(f"Scrap Credit: -₹{result['scrap_credit']:.2f} (for {result['scrap_weight']*1000:.0f}g)")
    with c3:
        st.markdown(f"""
        <div class="card" style="border: 1px solid #4CAF50;">
            <div class="card-header" style="color: #4CAF50;">Final Sheet Cost</div>
            <div class="metric-value">₹{result['final_cost_per_kg']:.2f}</div>
            <div class="metric-label">Per Kg Sheet</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card" style="border: 1px solid #FFD700; margin-top: 10px;">
        <div class="card-header" style="color: #FFD700;">Selling Price (Sheet)</div>
        <div class="metric-value">₹{selling_price:.2f}</div>
        <div class="metric-label">Per Kg @ {margin_pct}% Margin</div>
    </div>
    """, unsafe_allow_html=True)
