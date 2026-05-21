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
    st.markdown("Overview of vendor network health and pipeline performance.")
    
    # --- KPI SECTION ---
    metrics = get_kpis()
    c1, c2, c3 = st.columns(3)
    
    # Safe metric calculations with explicit labeling
    c1.metric(label="📦 Total Onboarded", value=metrics["total_onboarded"])
    c2.metric(label="🎯 Leads in Pipeline", value=metrics["total_approached"])
    
    conv_rate = (metrics['active_vendors'] / max(metrics['total_approached'], 1)) * 100
    c3.metric(label="⚡ Activation Efficiency", value=f"{conv_rate:.1f}%")

    st.markdown("---")

    # --- ADVANCED ANALYTICS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📅 Onboarding Velocity")
        df_onb = st.session_state.onboarded_df.copy()
        
        # Pointing to the new standardized column: 'vendor_onboard_date'
        if not df_onb.empty and 'vendor_onboard_date' in df_onb.columns:
            time_df = df_onb.dropna(subset=['vendor_onboard_date']).copy()
            if not time_df.empty:
                time_df = time_df.sort_values('vendor_onboard_date')
                time_df['Cumulative Vendors'] = range(1, len(time_df) + 1)
                
                fig_time = px.line(
                    time_df, x='vendor_onboard_date', y='Cumulative Vendors', 
                    title='Vendor Acquisition Over Time',
                    color_discrete_sequence=['#2563EB']
                )
                fig_time.update_layout(xaxis_title="Date", yaxis_title="Total Vendors")
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("No valid dates found in 'Vendor Onboard Date' column.")
        else:
            st.info("Awaiting 'Vendor Onboard Date' data.")

    with col_b:
        st.subheader("📊 Pipeline Breakdown")
        df_app = st.session_state.approached_df.copy()
        
        # Pointing to the new auto-extracted column: 'file_status'
        if not df_app.empty and 'file_status' in df_app.columns:
            stage_counts = df_app['file_status'].value_counts().reset_index()
            stage_counts.columns = ['Pipeline Stage', 'Number of Leads']
            
            fig_bar = px.bar(
                stage_counts, x='Number of Leads', y='Pipeline Stage', orientation='h', 
                title='Leads by Current Status', color='Number of Leads', 
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No pipeline status data available.")

    st.markdown("---")
    
    # --- GEOGRAPHIC & CATEGORY DISTRIBUTION ---
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🌎 Global Footprint")
        if not df_onb.empty and 'country' in df_onb.columns:
            geo_data = df_onb['country'].dropna().value_counts().reset_index()
            geo_data.columns = ['Country', 'Vendor Count']
            
            fig_geo = px.choropleth(
                geo_data, locations="Country", locationmode='country names', 
                color="Vendor Count", title="Vendors by Country", 
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_geo, use_container_width=True)
        else:
            st.info("Awaiting 'Country' data.")

    with c4:
        st.subheader("🏷️ Top Categories")
        # The standardized column might be 'vendor_type' or 'category' depending on the file
        cat_col = 'vendor_type' if 'vendor_type' in df_onb.columns else ('category' if 'category' in df_onb.columns else None)
        
        if cat_col and not df_onb.empty:
            cat_data = df_onb[cat_col].dropna().value_counts().nlargest(10).reset_index()
            cat_data.columns = ['Business Segment', 'Count']
            
            fig_cat = px.treemap(
                cat_data, path=['Business Segment'], values='Count', 
                title='Top 10 Business Segments',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Awaiting 'Vendor Type' or 'Category' data.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
