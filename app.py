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
    st.title("📈 Vendor Pipeline Overview")
    
    # --- KPI SECTION ---
    metrics = get_kpis()
    conv_rate = (metrics['active_vendors'] / max(metrics['total_approached'], 1)) * 100
    
    st.markdown(f"""
    <div style="display: flex; gap: 20px; margin-bottom: 30px;">
        <div style="flex: 1; background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #6B7280; font-size: 14px; font-weight: 600;">📦 TOTAL ONBOARDED</p>
            <h2 style="margin: 5px 0 0 0; color: #111827;">{metrics['total_onboarded']}</h2>
        </div>
        <div style="flex: 1; background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #6B7280; font-size: 14px; font-weight: 600;">🎯 LEADS IN PIPELINE</p>
            <h2 style="margin: 5px 0 0 0; color: #111827;">{metrics['total_approached']}</h2>
        </div>
        <div style="flex: 1; background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #6B7280; font-size: 14px; font-weight: 600;">⚡ PIPELINE CONVERSION</p>
            <h2 style="margin: 5px 0 0 0; color: #111827;">{conv_rate:.1f}%</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- DONUT CHARTS SECTION ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🛍️ Top Product Categories")
        df_app = st.session_state.approached_df
        
        # Point specifically to the 'category' column in the approached leads
        if not df_app.empty and 'category' in df_app.columns:
            # Clean categories to group identical items (e.g., "beauty" and "Beauty")
            df_app['category_clean'] = df_app['category'].astype(str).str.title().str.strip()
            cat_data = df_app[df_app['category_clean'] != 'Nan']['category_clean'].value_counts().nlargest(10).reset_index()
            cat_data.columns = ['Product Category', 'Count']
            
            fig_cat = px.pie(
                cat_data, names='Product Category', values='Count', hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_cat.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Could not locate the 'Category' column.")

    with col_b:
        st.subheader("🏷️ Business Model Segments")
        df_onb = st.session_state.onboarded_df
        
        # Point to the 'vendor_type' column (Dropship, Wholesale, etc.)
        if not df_onb.empty and 'vendor_type' in df_onb.columns:
            seg_data = df_onb['vendor_type'].dropna().value_counts().reset_index()
            seg_data.columns = ['Segment', 'Count']
            
            fig_seg = px.pie(
                seg_data, names='Segment', values='Count', hole=0.5,
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_seg.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_seg, use_container_width=True)
        else:
            st.info("Could not locate the 'Vendor Type' column in the onboarded data.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
