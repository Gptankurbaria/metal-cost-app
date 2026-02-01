import streamlit as st
import pandas as pd
from utils.calculations import CostCalculator

# Page Config
st.set_page_config(
    page_title="Executive Cost Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AUTHENTICATION ---
from utils.auth import check_password
if not check_password():
    st.stop()

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("assets/style.css")
except:
    pass

# --- NAVIGATION (Top) ---
st.sidebar.title("🏭 Shanghai Metals")
selection = st.sidebar.radio("Navigation", ["Executive Dashboard", "P1: Ingot", "P2: Sheet", "P3: Parts"])

st.sidebar.markdown("---")

# 1. Metal Rates & Scrap (Top Priority)
st.sidebar.subheader("🧱 Base Metal & Scrap Rates (₹/kg)")
col_rate1, col_rate2 = st.sidebar.columns(2)
with col_rate1:
    cu_rate = st.number_input("Copper Price", value=1000.0, step=1.0)
with col_rate2:
    zn_rate = st.number_input("Zinc Price", value=300.0, step=1.0)

# Store Global Params for Views (Initialize defaults EARLY)
if 'process_params' not in st.session_state or not st.session_state.process_params:
    st.session_state.process_params = {
        'alloy_cu': 100.0,
        'alloy_zn': 0.0,
        'burning_loss': 2.0,
        'furnace_cost': 15.0, 
        'rolling_yield': 98.0,
        'rolling_cost': 12.0,
        'p2_scrap_rate': 400.0,
        'machining_cost': 5.0,
        'p3_scrap_rate': 350.0,
        'p3_yield_pct': 70.0
    }

# Scrap Logic (Global)
st.sidebar.markdown("**Scrap Recovery Rates (Auto)**")
scrap_factor = st.sidebar.number_input("Scrap Recov % (Metal Base)", value=100.0, step=1.0) / 100.0

# Calculate specific scrap rate dynamically based on CURRENT Alloy Mix
current_cu_pct = st.session_state.process_params.get('alloy_cu', 100.0)
current_zn_pct = 100.0 - current_cu_pct

base_scrap_rate = (cu_rate * (current_cu_pct/100) + zn_rate * (current_zn_pct/100)) * scrap_factor
st.sidebar.info(f"Auto Scrap Rate: ~₹{base_scrap_rate:.2f}/kg")
st.session_state.indicative_scrap_rate = base_scrap_rate


# 2. Capacity & Expenses (Derived Costs)
st.sidebar.subheader("📊 Capacity & Budget (Monthly)")
capacity_kg = st.sidebar.number_input("Installed Capacity (kg/mo)", value=50000.0, step=1000.0)

st.sidebar.markdown("**Monthly Expenses (₹)**")
exp_power = st.sidebar.number_input("Electricity Bill", value=400000.0, step=10000.0)
exp_labor = st.sidebar.number_input("Total Labor Salary", value=150000.0, step=5000.0)
exp_cons = st.sidebar.number_input("Consumables (Furnace/Oil)", value=100000.0, step=5000.0)
exp_admin = st.sidebar.number_input("General/Admin/Rent", value=100000.0, step=5000.0)

# Derive Rates
if capacity_kg > 0:
    rate_elec = exp_power / capacity_kg
    rate_labor = exp_labor / capacity_kg
    rate_cons = exp_cons / capacity_kg
    rate_admin = exp_admin / capacity_kg
else:
    rate_elec = rate_labor = rate_cons = rate_admin = 0.0

st.sidebar.info(f"""
**Derived Rates (₹/kg):**
⚡ Elec: {rate_elec:.2f} | 👷 Lab: {rate_labor:.2f}
🔥 Cons: {rate_cons:.2f} | 🏢 O/H: {rate_admin:.2f}
**Total Conversion:** ₹{rate_elec+rate_labor+rate_cons+rate_admin:.2f}/kg
""")

# 3. Financials
st.sidebar.subheader("💰 Financial Targets")
interest_rate = st.sidebar.number_input("Interest Rate (% p.a.)", value=12.0)
margin_pct = st.sidebar.number_input("Desired Net Margin (%)", value=10.0)
holding_period = st.sidebar.number_input("Cycle Time (Days)", value=45)




# Sync Rates
if 'rm_rates' not in st.session_state:
    st.session_state.rm_rates = {}
st.session_state.rm_rates['cu'] = cu_rate
st.session_state.rm_rates['zn'] = zn_rate

# Update Derived Params to Session
st.session_state.derived_rates = {
    'elec': rate_elec,
    'labor': rate_labor,
    'cons': rate_cons,
    'overhead': rate_admin
}
st.session_state.p1_costs = { 
    'elec': rate_elec,
    'labor': rate_labor,
    'consumables': rate_cons,
    'overhead': rate_admin
}

# --- MAIN LOGIC ---

if selection == "Executive Dashboard":
    st.title("🏭 Shanghai Metals Cost Analysis")
    st.markdown("### 1. Product Composition")
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown("**Alloy Mix**")
        # Get default
        def_cu = st.session_state.process_params.get('alloy_cu', 63.0)
        cu_pct = st.number_input("Copper %", value=def_cu, step=0.5, min_value=0.0, max_value=100.0)
        st.session_state.process_params['alloy_cu'] = cu_pct
        
        zn_pct = 100.0 - cu_pct
        st.caption(f"Zinc Balance: {zn_pct:.1f}%")
        st.session_state.process_params['alloy_zn'] = zn_pct
        
    with col_in2:
        st.markdown("**Process Efficiency**")
        
        # P1 Loss
        burn_loss = st.number_input("P1: Burning Loss %", value=st.session_state.process_params.get('burning_loss', 1.5), step=0.1)
        st.session_state.process_params['burning_loss'] = burn_loss
        
        # P2 Yield
        # Get default from params
        def_sheet_yield = st.session_state.process_params.get('rolling_yield', 60.0)
        sheet_yield = st.number_input("P2: Sheet Yield %", value=def_sheet_yield, step=1.0)
        st.session_state.process_params['rolling_yield'] = sheet_yield
        
        # P3 Yield
        # Initialize if missing (default 65% based on 1.0/0.65 request)
        if 'p3_yield_pct' not in st.session_state.process_params:
            st.session_state.process_params['p3_yield_pct'] = 65.0
            
        def_parts_yield = st.session_state.process_params.get('p3_yield_pct', 65.0)
        parts_yield = st.number_input("P3: Parts Yield %", value=def_parts_yield, step=1.0)
        st.session_state.process_params['p3_yield_pct'] = parts_yield
        
    with col_in3:
        st.markdown("**Scrap Recovery**")
        # Auto Calculate Scrap specific to this alloy
        weighted_metal_cost = (cu_rate * cu_pct/100) + (zn_rate * zn_pct/100)
        auto_scrap_rate = weighted_metal_cost * scrap_factor
        
        st.metric("Auto Scrap Rate (₹/kg)", f"₹{auto_scrap_rate:.2f}", delta="Linked to Sidebar")


    # --- CALCULATIONS ---
    
    # STEP 1: Ingot
    ingot_res = CostCalculator.calculate_ingot_cost(
        cu_price=cu_rate, zn_price=zn_rate,
        cu_pct=cu_pct, zn_pct=zn_pct,
        burning_loss_pct=burn_loss,
        elec_cost=rate_elec,
        labor_cost=rate_labor,
        consumable_cost=rate_cons,
        overhead_cost=rate_admin
    )
    
    # STEP 2: Sheet
    # Use Process Params (Synced with View)
    sheet_process_cost = st.session_state.process_params.get('rolling_cost', 12.0)
    
    sheet_res = CostCalculator.calculate_sheet_cost(
        ingot_cost_per_kg=ingot_res['final_cost_per_kg'],
        yield_pct=sheet_yield,
        scrap_recovery_price=auto_scrap_rate,
        process_cost_per_kg=sheet_process_cost 
    )
    
    # STEP 3: Parts
    # Use 1.0 kg Gross Input to find Cost Per Kg Output (Effective Rate)
    parts_input_weight_kg = 1.0
    parts_output_weight_kg = parts_input_weight_kg * (parts_yield / 100.0)
    
    # Use Derived Process Cost from Params (Synced with View)
    # Note: View cost is per piece. Dashboard assumes 1kg piece for simplicity or treats this as 'Per Kg' parameter.
    # To match strictly: If View says "5.0/piece", and we treat piece as 1kg => 5.0/kg.
    p3_machining_cost = st.session_state.process_params.get('machining_cost', 5.0)
    
    parts_res = CostCalculator.calculate_part_cost(
        sheet_cost_per_kg=sheet_res['final_cost_per_kg'],
        part_weight_kg=parts_output_weight_kg, 
        gross_weight_kg=parts_input_weight_kg, 
        scrap_recovery_price=auto_scrap_rate, 
        machining_cost_per_part=p3_machining_cost
    )
    
    # Use Effective Cost per Kg Finished as key metric
    p3_final_cost_per_kg = parts_res['effective_cost_per_kg_finished']
    
    
    # Use Parts Cost for Final Selling Price
    final_base_cost = p3_final_cost_per_kg
    
    fin_res = CostCalculator.calculate_financials(
        base_cost=final_base_cost,
        interest_rate_pa=interest_rate,
        holding_days=holding_period,
        margin_pct=margin_pct
    )

    # --- DISPLAY ---
    
    st.markdown("### 2. Stage-wise Cost (Per Kg)")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # Calculate Financials for Ingot
        ingot_fin = CostCalculator.calculate_financials(
            base_cost=ingot_res['final_cost_per_kg'],
            interest_rate_pa=interest_rate,
            holding_days=holding_period,
            margin_pct=margin_pct
        )
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">1. Ingot Cost</div>
            <div class="metric-value">₹{ingot_res['final_cost_per_kg']:.2f}</div>
            <div class="metric-label">Loss: {burn_loss}%</div>
            <div style="border-top: 1px solid #eee; margin-top: 5px; padding-top: 5px;">
                <div style="font-size: 0.8em; color: #666;">+ Interest: ₹{ingot_fin['interest_cost']:.2f}</div>
                <div style="font-size: 0.9em; color: #666;">Selling Price</div>
                <div style="font-weight: bold; color: #2ecc71;">₹{ingot_fin['selling_price']:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Calculate Financials for Sheet
        sheet_fin = CostCalculator.calculate_financials(
            base_cost=sheet_res['final_cost_per_kg'],
            interest_rate_pa=interest_rate,
            holding_days=holding_period,
            margin_pct=margin_pct
        )
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">2. Sheet Cost</div>
            <div class="metric-value">₹{sheet_res['final_cost_per_kg']:.2f}</div>
            <div class="metric-label">Yield: {sheet_yield}%</div>
            <div style="border-top: 1px solid #eee; margin-top: 5px; padding-top: 5px;">
                <div style="font-size: 0.8em; color: #666;">+ Interest: ₹{sheet_fin['interest_cost']:.2f}</div>
                <div style="font-size: 0.9em; color: #666;">Selling Price</div>
                <div style="font-weight: bold; color: #2ecc71;">₹{sheet_fin['selling_price']:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        # Parts SP (already calc in fin_res)
        parts_sp = fin_res['selling_price']
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">3. Parts Cost</div>
            <div class="metric-value">₹{p3_final_cost_per_kg:.2f}</div>
            <div class="metric-label">Yield: {parts_yield}%</div>
            <div style="border-top: 1px solid #eee; margin-top: 5px; padding-top: 5px;">
                <div style="font-size: 0.8em; color: #666;">+ Interest: ₹{fin_res['interest_cost']:.2f}</div>
                <div style="font-size: 0.9em; color: #666;">Selling Price</div>
                <div style="font-weight: bold; color: #2ecc71;">₹{parts_sp:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="card" style="border: 2px solid #2980b9;">
            <div class="card-header" style="color: #2980b9;">Selling Price</div>
            <div class="metric-value">₹{fin_res['selling_price']:.2f}</div>
            <div class="metric-label">Margin: {margin_pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Cost Breakdown
    st.markdown("### 3. Financial Breakdown")
    
    st.table(pd.DataFrame({
        "Component": ["Net Mfg Cost (Parts)", "+ Interest Cost", "+ Profit Margin", "= Final Selling Price"],
        "Value (₹/kg)": [
            f"₹{final_base_cost:.2f}",
            f"₹{fin_res['interest_cost']:.2f}",
            f"₹{fin_res['profit_margin']:.2f}",
            f"**₹{fin_res['selling_price']:.2f}**"
        ]
    }))

elif selection == "P1: Ingot":
    from views.ingot import render_ingot_view
    render_ingot_view()

elif selection == "P2: Sheet":
    from views.sheet import render_sheet_view
    render_sheet_view()

elif selection == "P3: Parts":
    from views.parts import render_parts_view
    render_parts_view()

