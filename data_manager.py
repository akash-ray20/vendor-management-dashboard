import streamlit as st
import pandas as pd
import os
import re

# --- CONFIGURATION ---
DATA_DIR = "data"

@st.cache_data(show_spinner="Running Data Pipeline...")
def clean_and_load_data():
    """
    Core data pipeline: Loads, cleans, standardizes, and routes data.
    """
    pipeline_frames = []
    master_frames = []
    
    if not os.path.exists(DATA_DIR):
        st.error(f"Directory '{DATA_DIR}' not found. Please create it and add your files.")
        return pd.DataFrame(), pd.DataFrame()

    all_files = os.listdir(DATA_DIR)
    if len(all_files) == 0:
        st.warning(f"The '{DATA_DIR}' folder is empty.")
        return pd.DataFrame(), pd.DataFrame()

    for filename in all_files:
        file_path = os.path.join(DATA_DIR, filename)
        
        try:
            # 1. LOAD & HANDLE STRUCTURAL ANOMALIES
            if filename.lower().endswith('.csv'):
                # The Shopperbeats file has 5 rows of garbage at the top
                if "shopperbeats" in filename.lower():
                    df = pd.read_csv(file_path, skiprows=5, low_memory=False)
                else:
                    df = pd.read_csv(file_path, low_memory=False)
            elif filename.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                continue  # Skip non-data files

            # 2. CLEAN UP EMPTY SPACE
            # Drop rows/columns that are 100% empty
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            # Strip accidental spaces from text (e.g. " Active " -> "Active")
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

            # 3. STANDARDIZE HEADERS
            # Converts 'Vendor Onboard Date' to 'vendor_onboard_date'
            df.columns = [str(c).strip().lower().replace(' ', '_').replace('/', '_') for c in df.columns]

            # 4. EXTRACT IMPLICIT DATA FROM FILENAME
            # Extracts the status word after the last dash (e.g., "... - Reject.csv" -> "Reject")
            extracted_status = filename.split('-')[-1].replace('.csv', '').replace('.xlsx', '').strip()
            df['file_status'] = extracted_status
            df['source_file'] = filename

            # 5. ROUTE TO THE CORRECT DATAFRAME
            fn_lower = filename.lower()
            if "track master" in fn_lower:
                pipeline_frames.append(df)
            elif "master au" in fn_lower or "onboard" in fn_lower:
                # Convert dates safely for the master file
                if 'vendor_onboard_date' in df.columns:
                    df['vendor_onboard_date'] = pd.to_datetime(df['vendor_onboard_date'], errors='coerce')
                master_frames.append(df)

        except Exception as e:
            st.error(f"Failed to process {filename}: {e}")

    # Combine into unified master dataframes
    df_pipeline = pd.concat(pipeline_frames, ignore_index=True) if pipeline_frames else pd.DataFrame()
    df_master = pd.concat(master_frames, ignore_index=True) if master_frames else pd.DataFrame()
    
    return df_master, df_pipeline

def initialize_session_state():
    """
    Initializes the session state using the cleaned data pipeline.
    """
    if 'onboarded_df' not in st.session_state or 'approached_df' not in st.session_state:
        onboarded, approached = clean_and_load_data()
        st.session_state.onboarded_df = onboarded.reset_index(drop=True)
        st.session_state.approached_df = approached.reset_index(drop=True)

def get_kpis():
    """
    Calculates metrics securely based on the standardized 'file_status' column.
    """
    onboarded = st.session_state.get('onboarded_df', pd.DataFrame())
    approached = st.session_state.get('approached_df', pd.DataFrame())
    
    active_count = 0
    if not onboarded.empty and 'file_status' in onboarded.columns:
        # Check if the extracted filename status was "Active"
        active_count = len(onboarded[onboarded['file_status'].str.lower() == 'active'])

    return {
        "total_onboarded": len(onboarded),
        "total_approached": len(approached),
        "active_vendors": active_count,
    }
