import streamlit as st
import pandas as pd
import plotly.express as px
from data_manager import initialize_session_state, get_kpis
from styles import apply_custom_css

# 1. Page Configuration
st.set_page_config(page_title="VendorFlow AI", page_icon="📊", layout="wide")
apply_custom_css()

# CSS Hotfix for the "White Text on White Background" input bug
st.markdown("""
    <style>
        div[data-baseweb="select"] > div, div[data-baseweb="select"] li, span, input {
            color: #111827 !important;
        }
        .stSelectbox label p, .stTextInput label p {
            color: #374151 !important;
            font-weight: 600 !important;
        }
    </style>
""", unsafe_allow_html=True)

initialize_session_state()

# 2. Sidebar Navigation
st.sidebar.title("🛠️ VendorFlow AI")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Main Menu", ["Dashboard Home", "Onboarded Vendors", "Approached Leads"])
st.sidebar.markdown("---")

# Helper to find column containing a keyword
def find_col(df, keywords):
    for col in df.columns:
        if any(k in str(col).lower() for k in keywords):
            return col
    return None

# --- VIEW 1: DASHBOARD HOME ---
if menu == "Dashboard Home":
    st.title("📈 Vendor Pipeline Overview")
    
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

    st.subheader("👥 Lead Sourcing by Team")
    df_app = st.session_state.approached_df.copy()

    if not df_app.empty:
        col1 = find_col(df_app, ['first_contacted_by', 'contacted'])
        col2 = find_col(df_app, ['data_got_from', 'got_from'])
        
        def get_team_member(row):
            val1 = str(row.get(col1, '')).strip() if col1 else ''
            if val1 and val1.lower() not in ['nan', 'none', 'null', '']: return val1
            val2 = str(row.get(col2, '')).strip() if col2 else ''
            if val2 and val2.lower() not in ['nan', 'none', 'null', '']: return val2
            return 'Unknown'

        df_app['team_member'] = df_app.apply(get_team_member, axis=1)
        df_app['team_member_clean'] = df_app['team_member'].astype(str).str.split('(').str[0].str.strip().str.title()
        
        bad_names = ['Unknown', 'Email And Form', 'Website', 'Google', 'Network', 'Applied Through Website', 'Email', 'Manual']
        team_data = df_app[~df_app['team_member_clean'].isin(bad_names)]
        team_counts = team_data['team_member_clean'].value_counts().reset_index()
        team_counts.columns = ['Team Member', 'Leads Generated']
        
        if not team_counts.empty:
            fig_team = px.bar(team_counts, x='Leads Generated', y='Team Member', orientation='h', color='Leads Generated', color_continuous_scale='Teal', text='Leads Generated')
            fig_team.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=300)
            st.plotly_chart(fig_team, use_container_width=True)
        else: st.info("No valid human team members found.")
    else: st.info("Team sourcing data is empty.")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🛍️ Top Product Categories")
        cat_col = find_col(df_app, ['category'])
        if cat_col and not df_app.empty:
            df_app['category_clean'] = df_app[cat_col].astype(str).str.title().str.strip()
            cat_data = df_app[df_app['category_clean'] != 'Nan']['category_clean'].value_counts().nlargest(10).reset_index()
            cat_data.columns = ['Product Category', 'Count']
            if not cat_data.empty:
                fig_cat = px.pie(cat_data, names='Product Category', values='Count', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_cat.update_layout(margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_cat, use_container_width=True)
        else: st.info("Could not locate the 'Category' column.")

    with col_b:
        st.subheader("🏷️ Business Model Segments")
        df_onb = st.session_state.onboarded_df
        type_col = find_col(df_onb, ['vendor_type', 'type'])
        if type_col and not df_onb.empty:
            seg_data = df_onb[type_col].dropna().value_counts().reset_index()
            seg_data.columns = ['Segment', 'Count']
            if not seg_data.empty:
                fig_seg = px.pie(seg_data, names='Segment', values='Count', hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
                fig_seg.update_layout(margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_seg, use_container_width=True)
        else: st.info("Could not locate the 'Vendor Type' column.")


# --- VIEW 2: ONBOARDED VENDORS ---
elif menu == "Onboarded Vendors":
    st.title("📂 Onboarded Vendor Directory")
    st.markdown("Manage, filter, and analyze your active operational partners.")

    df_onb = st.session_state.onboarded_df.copy()

    if not df_onb.empty:
        # 1. SMART SEARCH & FILTERS
        st.subheader("🔍 Smart Filter Engine")
        
        name_col = find_col(df_onb, ['name', 'company'])
        type_col = find_col(df_onb, ['vendor_type', 'type'])
        country_col = find_col(df_onb, ['country', 'nation'])
        pay_col = find_col(df_onb, ['payment', 'terms'])

        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            search_term = st.text_input("Search by Vendor/Company Name", "")
        with col_f2:
            types = ["All"] + list(df_onb[type_col].dropna().unique()) if type_col else ["All"]
            selected_type = st.selectbox("Vendor Type", types)
        with col_f3:
            countries = ["All"] + list(df_onb[country_col].dropna().unique()) if country_col else ["All"]
            selected_country = st.selectbox("Country/Region", countries)

        # Apply the filters dynamically
        filtered_df = df_onb.copy()
        if search_term and name_col:
            filtered_df = filtered_df[filtered_df[name_col].astype(str).str.contains(search_term, case=False, na=False)]
        if selected_type != "All" and type_col:
            filtered_df = filtered_df[filtered_df[type_col] == selected_type]
        if selected_country != "All" and country_col:
            filtered_df = filtered_df[filtered_df[country_col] == selected_country]

        st.markdown(f"**Currently showing {len(filtered_df)} of {len(df_onb)} total vendors.**")
        st.markdown("---")

        # 2. TABBED INTERFACE (SWAPPED ORDER)
        tab1, tab2 = st.tabs(["⚙️ Operational Insights", "📋 Directory Data"])

        with tab1:
            st.markdown("### Logistics & Financial Terms")
            st.write("*Note: These charts update automatically based on your search filters above.*")
            
            c1, c2 = st.columns(2)
            
            with c1:
                if pay_col and not filtered_df.empty:
                    pay_data = filtered_df[pay_col].dropna().value_counts().reset_index()
                    pay_data.columns = ['Payment Terms', 'Count']
                    fig_pay = px.pie(pay_data, names='Payment Terms', values='Count', hole=0.4, 
                                     title="Financial Exposure (Payment Terms)", 
                                     color_discrete_sequence=px.colors.sequential.YlOrBr)
                    st.plotly_chart(fig_pay, use_container_width=True)
                else:
                    st.info("Payment terms data not available for this selection.")
                    
            with c2:
                integ_col = find_col(filtered_df, ['integration', 'po_integration', 'invoice'])
                if integ_col and not filtered_df.empty:
                    integ_data = filtered_df[integ_col].dropna().value_counts().reset_index()
                    integ_data.columns = ['Method', 'Count']
                    fig_integ = px.bar(integ_data, x='Count', y='Method', orientation='h', 
                                       title="Operational Methods", 
                                       color='Count', color_continuous_scale='Blues')
                    fig_integ.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                    st.plotly_chart(fig_integ, use_container_width=True)
                else:
                    st.info("Operational methodology data not available for this selection.")

        with tab2:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Current View to CSV",
                data=csv_data,
                file_name='vendor_report.csv',
                mime='text/csv',
            )
            st.dataframe(filtered_df, use_container_width=True, height=500)

    else:
        st.info("No onboarded vendor data available. Please check the data folder.")

# --- VIEW 3: APPROACHED LEADS ---
elif menu == "Approached Leads":
    st.title("🎯 Approached Leads & Tracking")
    st.dataframe(st.session_state.approached_df, use_container_width=True)
