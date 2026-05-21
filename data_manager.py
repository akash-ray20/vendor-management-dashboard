import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DATA_DIR = "data"
ONBOARDED_DIR = os.path.join(DATA_DIR, "onboarded")
APPROACHED_DIR = os.path.join(DATA_DIR, "approached")

@st.cache_data(show_spinner="Fetching vendor records...")
def load_csv_files(directory):
    """
    Helper function to find and merge all CSVs in a specific directory.
    """
    if not os.path.exists(directory):
        return pd.DataFrame()
    
    all_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        try:
            # We use low_memory=False to handle mixed types in large excel-exported CSVs
            temp_df = pd.read_csv(file_path, low_memory=False)
            # Add a source column to track which file the data came from (useful for status)
            temp_df['source_file'] = filename
            df_list.append(temp_df)
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            
    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

def initialize_session_state():
    """
    Centralized logic to load data into the session state.
    This ensures data is loaded once and persists during user interactions.
    """
    # Initialize Onboarded Data
    if 'onboarded_df' not in st.session_state:
        df = load_csv_files(ONBOARDED_DIR)
        # Basic Clean: Drop completely empty rows/cols
        st.session_state.onboarded_df = df.dropna(how='all', axis=0).reset_index(drop=True)
        
    # Initialize Approached Data
    if 'approached_df' not in st.session_state:
        df = load_csv_files(APPROACHED_DIR)
        st.session_state.approached_df = df.dropna(how='all', axis=0).reset_index(drop=True)

def update_vendor(df_key, index, updated_row):
    """
    CRUD Helper: Updates a specific row in the session state dataframe.
    """
    st.session_state[df_key].iloc[index] = updated_row
    # Optional: Logic to save back to CSV could go here

def add_vendor(df_key, new_data_dict):
    """
    CRUD Helper: Appends a new vendor to the session state dataframe.
    """
    new_row = pd.DataFrame([new_data_dict])
    st.session_state[df_key] = pd.concat([st.session_state[df_key], new_row], ignore_index=True)

def get_kpis():
    """
    Returns a dictionary of key metrics for the dashboard.
    """
    onboarded = st.session_state.get('onboarded_df', pd.DataFrame())
    approached = st.session_state.get('approached_df', pd.DataFrame())
    
    metrics = {
        "total_onboarded": len(onboarded),
        "total_approached": len(approached),
        "active_vendors": 0,
        "pending_leads": 0
    }
    
    if not onboarded.empty and 'Vendor Status' in onboarded.columns:
        metrics["active_vendors"] = len(onboarded[onboarded['Vendor Status'] == 'Active'])
        
    return metrics