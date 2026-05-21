import streamlit as st
import plotly.express as px
from data_manager import initialize_session_state, get_kpis
from styles import apply_custom_css

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="VendorFlow | AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply the UI/UX Styles from styles.py
apply_custom_css()

# 3. Initialize Data into Session State
# This ensures data is loaded once and persists without reloading the CSVs every click
initialize_session_state()

# 4. Sidebar Navigation
st.sidebar.title("🛠️ VendorFlow AI")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Main Menu",
    ["Dashboard Home", "Onboarded Vendors", "Approached Leads"]
)

st.sidebar.markdown("---")
st.sidebar.info("v1.1.0 | Dashboard Active")

# 5. Routing Logic
if menu == "Dashboard Home":
    st.title("📈 Vendor Analytics Dashboard")
    
    # --- KPI SECTION ---
    metrics = get_kpis()
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Onboarded", metrics["total_onboarded"])
    col2.metric("Total Approached", metrics["total_approached"])
    col3.metric("Active Vendors", metrics["active_vendors"])
    
    # Safe calculation for Conversion Rate to avoid dividing by zero
    conversion_rate = 0
    if metrics['total_approached'] > 0:
        conversion_rate = (metrics['active_vendors'] / metrics['total_approached']) * 100
    col4.metric("Conversion Rate", f"{conversion_rate:.1f}%")

    st.markdown("---")

    # --- CHARTS SECTION ---
    st.markdown("### 📊 Market Insights")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        df_onb = st.session_state.onboarded_df
        if not df_onb.empty and 'Vendor Type' in df_onb.columns:
            fig1 = px.pie(
                df_onb, 
                names='Vendor Type', 
                title='Onboarded: Vendors by Type', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig1.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Awaiting 'Vendor Type' data for chart generation.")

    with col_chart2:
        df_app = st.session_state.approached_df
        if not df_app.empty and 'source_file' in df_app.columns:
            # Clean up the filename for a prettier chart
            df_app['clean_source'] = df_app['source_file'].str.replace('.csv', '', regex=False).str.replace('Vendor Onboard Track Master File- Do not use.xlsx - ', '', regex=False)
            source_counts = df_app['clean_source'].value_counts().reset_index()
            source_counts.columns = ['Lead Stage', 'Count']
            
            fig2 = px.bar(
                source_counts, 
                x='Lead Stage', 
                y='Count', 
                title='Approached: Leads by Stage',
                color='Lead Stage',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Awaiting pipeline data for chart generation.")

    st.markdown("---")

    # --- QUICK VIEW TABLE ---
    st.markdown("### 📋 Quick View (Top 10 Onboarded)")
    if not st.session_state.onboarded_df.empty:
        st.dataframe(st.session_state.onboarded_df.head(10), use_container_width=True)
    else:
        st.warning("No data found. Please check your CSV files in the data/ folder.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.write("Full database of registered vendors and their contact details.")
    
    if not st.session_state.onboarded_df.empty:
        # Use st.dataframe for a nice, scrollable, sortable table
        st.dataframe(st.session_state.onboarded_df, use_container_width=True, height=600)
    else:
        st.info("No onboarded vendors found.")

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.write("Overview of potential vendors currently in the pipeline.")
    
    if not st.session_state.approached_df.empty:
        st.dataframe(st.session_state.approached_df, use_container_width=True, height=600)
    else:
        st.info("No approached leads found.")
