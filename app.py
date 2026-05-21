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
    st.title("📈 Executive Insights")
    
    # --- KPI SECTION (Named and Styled) ---
    metrics = get_kpis()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Total Onboarded**")
        st.metric("", metrics["total_onboarded"])
    with col2:
        st.markdown("**Leads Approached**")
        st.metric("", metrics["total_approached"])
    with col3:
        st.markdown("**Active Partners**")
        st.metric("", metrics["active_vendors"])
    with col4:
        st.markdown("**Activation Rate**")
        conv = (metrics['active_vendors'] / metrics['total_approached'] * 100) if metrics['total_approached'] > 0 else 0
        st.metric("", f"{conv:.1f}%")

    st.markdown("---")

    # --- ADVANCED ANALYTICS ---
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📅 Onboarding Velocity")
        df_onb = st.session_state.onboarded_df.copy()
        if not df_onb.empty and 'Vendor Onboard Date' in df_onb.columns:
            # Convert to datetime and plot cumulative growth
            df_onb['Vendor Onboard Date'] = pd.to_datetime(df_onb['Vendor Onboard Date'], errors='coerce')
            df_onb = df_onb.dropna(subset=['Vendor Onboard Date']).sort_values('Vendor Onboard Date')
            df_onb['Cumulative Count'] = range(1, len(df_onb) + 1)
            
            fig_time = px.area(df_onb, x='Vendor Onboard Date', y='Cumulative Count', 
                              title='Growth of Vendor Network', color_discrete_sequence=['#2563EB'])
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Onboarding date data not available for timeline.")

    with c2:
        st.markdown("### 📊 Pipeline Breakdown")
        df_app = st.session_state.approached_df.copy()
        if not df_app.empty and 'source_file' in df_app.columns:
            # Clean names for Lead Stages
            df_app['Stage'] = df_app['source_file'].str.extract(r'-\s*(.*)\.csv')[0].fillna('Unknown')
            stage_counts = df_app['Stage'].value_counts().reset_index()
            stage_counts.columns = ['Stage', 'Count']
            
            fig_bar = px.bar(stage_counts, x='Count', y='Stage', orientation='h', 
                            title='Leads by Current Status', color='Count', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # --- GEOGRAPHIC & CATEGORY DISTRIBUTION ---
    c3, c4 = st.columns(2)
    
    with c3:
        st.markdown("### 🌍 Global Presence")
        if not df_onb.empty and 'Country' in df_onb.columns:
            geo_data = df_onb['Country'].value_counts().reset_index()
            geo_data.columns = ['Country', 'Vendors']
            fig_geo = px.choropleth(geo_data, locations="Country", locationmode='country names', 
                                    color="Vendors", title="Vendors by Country", color_continuous_scale='Blues')
            st.plotly_chart(fig_geo, use_container_width=True)

    with c4:
        st.markdown("### 🏷️ Top Categories")
        # Check both dataframes for a Category or Vendor Type column
        cat_col = 'Category' if 'Category' in df_app.columns else ('Vendor Type' if 'Vendor Type' in df_onb.columns else None)
        if cat_col:
            df_cat = df_app if cat_col == 'Category' else df_onb
            cat_data = df_cat[cat_col].value_counts().nlargest(10).reset_index()
            cat_data.columns = [cat_col, 'Count']
            fig_cat = px.treemap(cat_data, path=[cat_col], values='Count', title='Top 10 Business Segments')
            st.plotly_chart(fig_cat, use_container_width=True)

# (Rest of the code for Onboarded/Approached views remains same as before)
elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
