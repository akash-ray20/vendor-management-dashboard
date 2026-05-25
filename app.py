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

# Helper to find column containing a keyword (immune to spaces/casing)
def find_col(df, keywords):
    for col in df.columns:
        if any(k in str(col).lower() for k in keywords):
            return col
    return None

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

    # --- ROW 1: TEAM PERFORMANCE (FULL WIDTH) ---
    st.subheader("👥 Lead Sourcing by Team")
    df_app = st.session_state.approached_df.copy()

    if not df_app.empty:
        # Smartly find the columns regardless of exact naming
        col1 = find_col(df_app, ['first_contacted_by', 'contacted'])
        col2 = find_col(df_app, ['data_got_from', 'got_from'])
        
        # BULLETPROOF FALLBACK LOGIC
        def get_team_member(row):
            # Check First Contacted By (strip spaces to avoid false positives)
            val1 = str(row.get(col1, '')).strip() if col1 else ''
            if val1 and val1.lower() not in ['nan', 'none', 'null', '']:
                return val1
            
            # Check Data Got From
            val2 = str(row.get(col2, '')).strip() if col2 else ''
            if val2 and val2.lower() not in ['nan', 'none', 'null', '']:
                return val2
            
            return 'Unknown'

        # Apply the function row by row
        df_app['team_member'] = df_app.apply(get_team_member, axis=1)

        # Clean names: Remove dates and standardize casing
        df_app['team_member_clean'] = df_app['team_member'].astype(str).str.split('(').str[0].str.strip().str.title()
        
        # Filter out junk data (Added 'Unknown' so the 23 blank rows don't ruin the chart)
        bad_names = ['Unknown', 'Email And Form', 'Website', 'Google', 'Network', 'Applied Through Website', 'Email', 'Manual']
        team_data = df_app[~df_app['team_member_clean'].isin(bad_names)]
        
        team_counts = team_data['team_member_clean'].value_counts().reset_index()
        team_counts.columns = ['Team Member', 'Leads Generated']
        
        if not team_counts.empty:
            fig_team = px.bar(
                team_counts, x='Leads Generated', y='Team Member', orientation='h', 
                color='Leads Generated', color_continuous_scale='Teal',
                text='Leads Generated'
            )
            fig_team.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=300)
            st.plotly_chart(fig_team, use_container_width=True)
        else:
            st.info("No valid human team members found after filtering out websites/emails.")
    else:
        st.info("Team sourcing data is currently empty.")

    st.markdown("---")

    # --- ROW 2: DONUT CHARTS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🛍️ Top Product Categories")
        cat_col = find_col(df_app, ['category'])
        if cat_col and not df_app.empty:
            df_app['category_clean'] = df_app[cat_col].astype(str).str.title().str.strip()
            cat_data = df_app[df_app['category_clean'] != 'Nan']['category_clean'].value_counts().nlargest(10).reset_index()
            cat_data.columns = ['Product Category', 'Count']
            
            if not cat_data.empty:
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
        type_col = find_col(df_onb, ['vendor_type', 'type'])
        
        if type_col and not df_onb.empty:
            seg_data = df_onb[type_col].dropna().value_counts().reset_index()
            seg_data.columns = ['Segment', 'Count']
            
            if not seg_data.empty:
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
