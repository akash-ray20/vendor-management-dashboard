import streamlit as st
from data_manager import initialize_session_state, get_kpis
from styles import apply_custom_css

# 1. Page Configuration
st.set_page_config(
    page_title="VendorFlow | AI Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Apply the UI/UX Styles from styles.py
apply_custom_css()

# 3. Initialize Data into Session State
# This calls the logic we wrote in data_manager.py
initialize_session_state()

# 4. Sidebar Navigation
st.sidebar.title("🛠️ VendorFlow AI")
st.sidebar.markdown("---")

# Navigation Menu
menu = st.sidebar.radio(
    "Main Menu",
    ["Dashboard Home", "Onboarded Vendors", "Approached Leads"]
)

st.sidebar.markdown("---")
st.sidebar.info("v1.0.0 | System Active")

# 5. Routing Logic (Which "Page" to show)
if menu == "Dashboard Home":
    st.title("📈 Vendor Analytics Dashboard")
    
    # Get KPIs from our data manager
    metrics = get_kpis()
    
    # Display KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Onboarded", metrics["total_onboarded"])
    col2.metric("Total Approached", metrics["total_approached"])
    col3.metric("Active Vendors", metrics["active_vendors"])
    col4.metric("Conversion Rate", f"{(metrics['active_vendors']/(metrics['total_approached']+1)*100):.1f}%")

    st.markdown("### Quick View")
    if not st.session_state.onboarded_df.empty:
        st.dataframe(st.session_state.onboarded_df.head(10), use_container_width=True)
    else:
        st.warning("No data found in /data/onboarded/. Please check your CSV files.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.write("Full database of registered vendors and their contact details.")
    # We will build the CRUD table here in the next step
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.write("Overview of potential vendors currently in the pipeline.")
    # We will build the lead tracking charts here in the next step
    st.dataframe(st.session_state.approached_df, use_container_width=True)