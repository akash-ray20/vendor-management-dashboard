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

# Helper function to find columns regardless of exact name/casing
def find_column(df, keywords):
    for col in df.columns:
        if any(keyword in col.lower() for keyword in keywords):
            return col
    return None

# 3. View Logic
if menu == "Dashboard Home":
    st.title("📈 Vendor Pipeline Overview")
    
    # --- BULLETPROOF KPI SECTION ---
    # Bypassing st.metric to avoid CSS conflicts hiding the labels
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

    # --- RELEVANT ANALYTICS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Pipeline Status Breakdown")
        df_app = st.session_state.approached_df
        
        if not df_app.empty and 'file_status' in df_app.columns:
            stage_counts = df_app['file_status'].value_counts().reset_index()
            stage_counts.columns = ['Pipeline Stage', 'Count']
            
            fig_bar = px.bar(
                stage_counts, x='Count', y='Pipeline Stage', orientation='h', 
                color='Count', color_continuous_scale='Blues'
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Pipeline data is currently empty.")

    with col_b:
        st.subheader("🏷️ Business Segments")
        df_onb = st.session_state.onboarded_df
        
        # Smartly look for the category/type column
        cat_col = find_column(df_onb, ['category', 'type', 'segment'])
        
        if cat_col and not df_onb.empty:
            cat_data = df_onb[cat_col].dropna().value_counts().reset_index()
            cat_data.columns = ['Segment', 'Count']
            
            # Simple Donut chart for the 3 categories
            fig_pie = px.pie(
                cat_data, names='Segment', values='Count', hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Could not locate a 'Vendor Type' or 'Category' column in the onboarded data.")

elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.dataframe(st.session_state.onboarded_df, use_container_width=True)

elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
