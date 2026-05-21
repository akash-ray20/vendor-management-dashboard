import streamlit as st
import pandas as pd
import plotly.express as px
from data_manager import initialize_session_state, get_kpis
from styles import apply_custom_css

# 1. Page Configuration
st.set_page_config(page_title="VendorFlow AI", page_icon="📊", layout="wide")
apply_custom_css()
initialize_session_state()

# 2. Sidebar Navigation
st.sidebar.title("🛠️ VendorFlow AI")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Main Menu", ["Dashboard Home", "Onboarded Vendors", "Approached Leads"])
st.sidebar.markdown("---")

# 3. View Logic
if menu == "Dashboard Home":
    st.title("📈 Executive Vendor Insights")
    
    # --- KPI SECTION ---
    metrics = get_kpis()
    c1, c2, c3 = st.columns(3)
    
    # Explicit Labels for the cards
    c1.metric("📦 Total Onboarded", metrics["total_onboarded"], help="Vendors fully registered in our system")
    c2.metric("🎯 Leads in Pipeline", metrics["total_approached"], help="Potential vendors contacted but not yet fully onboarded")
    
    # Safe Activation Rate calculation
    conv = (metrics['active_vendors'] / max(metrics['total_approached'], 1) * 100) if metrics['total_approached'] > 0 else 0
    c3.metric("⚡ Activation Efficiency", f"{conv:.1f}%")

    st.markdown("---")

    # --- ADVANCED ANALYTICS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📅 Onboarding Growth")
        df_onb = st.session_state.onboarded_df.copy()
        
        # Check for the standardized 'date' column
        if not df_onb.empty and 'date' in df_onb.columns:
            df_onb['date'] = pd.to_datetime(df_onb['date'], errors='coerce')
            df_onb = df_onb.dropna(subset=['date']).sort_values('date')
            df_onb['Cumulative Count'] = range(1, len(df_onb) + 1)
            
            fig_time = px.line(df_onb, x='date', y='Cumulative Count', 
                              title='Vendor Acquisition Over Time', color_discrete_sequence=['#2563EB'])
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No valid 'Vendor Onboard Date' found to track velocity.")

    with col_b:
        st.subheader("📊 Pipeline Breakdown")
        df_app = st.session_state.approached_df.copy()
        if not df_app.empty and 'source_file' in df_app.columns:
            # Clean names for Lead Stages
            df_app['Stage'] = df_app['source_file'].str.extract(r'-\s*(.*)\.csv')[0].fillna('Unknown')
            stage_counts = df_app['Stage'].value_counts().reset_index()
            stage_counts.columns = ['Stage', 'Count']
            
            fig_bar = px.bar(stage_counts, x='Count', y='Stage', orientation='h', 
                            title='Leads by Current Status', color='Count', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No pipeline data available.")

    st.markdown("---")
    
    # --- GEOGRAPHIC & CATEGORY DISTRIBUTION ---
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🌎 Global Footprint")
        if not df_onb.empty and 'country' in df_onb.columns:
            geo_data = df_onb['country'].str.strip().value_counts().reset_index()
            geo_data.columns = ['country', 'Vendors']
            fig_geo = px.choropleth(geo_data, locations="country", locationmode='country names', 
                                    color="Vendors", title="Vendors by Country", color_continuous_scale='Blues')
            st.plotly_chart(fig_geo, use_container_width=True)
        else:
            st.info("Add a 'Country' column to see the map.")

    with c4:
        st.subheader("🏷️ Top Categories")
        # Check the standardized 'category' column
        if not df_onb.empty and 'category' in df_onb.columns:
            cat_data = df_onb['category'].value_counts().nlargest(10).reset_index()
            cat_data.columns = ['category', 'Count']
            fig_cat = px.treemap(cat_data, path=['category'], values='Count', title='Top 10 Business Segments')
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No 'Vendor Type' or 'Category' found.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
