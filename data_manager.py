import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DATA_DIR = "data"

@st.cache_data(show_spinner="Standardizing Data...")
def load_and_sort_data():
    """
    Scans the /data folder, loads CSV/Excel files, standardizes key columns,
    and separates files into 'Onboarded' and 'Approached'.
    """
    onboarded_frames = []
    approached_frames = []
    
    if not os.path.exists(DATA_DIR):
        st.error(f"Directory '{DATA_DIR}' not found. Please ensure your folder is named 'data' (lowercase).")
        return pd.DataFrame(), pd.DataFrame()

    all_files = os.listdir(DATA_DIR)
    
    if len(all_files) == 0:
        st.warning(f"The '{DATA_DIR}' folder exists, but no files were found inside it.")
        return pd.DataFrame(), pd.DataFrame()

    for filename in all_files:
        file_path = os.path.join(DATA_DIR, filename)
        
        try:
            # 1. Handle BOTH CSV and Excel files smoothly
            if filename.lower().endswith('.csv'):
                # Special handling for Shopperbeats file which has rows above the header
                if "shopperbeats" in filename.lower():
                    df = pd.read_csv(file_path, skiprows=5, low_memory=False)
                else:
                    df = pd.read_csv(file_path, low_memory=False)
                    
            elif filename.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                continue # Skip non-data files
                
            # Clean up completely blank rows
            df = df.dropna(how='all')

            # --- THE FIX: COLUMN NORMALIZATION ---
            # Standardize column names so the app knows where to look for charts
            rename_map = {
                'Vendor Onboard Date': 'date', 'Onboard Date': 'date',
                'Country': 'country', 'Nation': 'country',
                'Vendor Type': 'category', 'Category': 'category',
                'Vendor Status': 'status', 'Status': 'status'
            }
            df = df.rename(columns=lambda x: rename_map.get(x, x))
            
            # Add the tracking column
            df['source_file'] = filename
            
            # 2. Smart Keyword Routing (Case-Insensitive)
            fn_lower = filename.lower()
            if "master au" in fn_lower or "onboard" in fn_lower:
                onboarded_frames.append(df)
            elif "track master" in fn_lower or "approach" in fn_lower or "lead" in fn_lower:
                approached_frames.append(df)
                
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")

    # Combine lists into master DataFrames
    final_onboarded = pd.concat(onboarded_frames, ignore_index=True) if onboarded_frames else pd.DataFrame()
    final_approached = pd.concat(approached_frames, ignore_index=True) if approached_frames else pd.DataFrame()
    
    return final_onboarded, final_approached

def initialize_session_state():
    """
    Initializes the session state using the updated loading logic.
    """
    if 'onboarded_df' not in st.session_state or 'approached_df' not in st.session_state:
        onboarded, approached = load_and_sort_data()
        st.session_state.onboarded_df = onboarded.reset_index(drop=True)
        st.session_state.approached_df = approached.reset_index(drop=True)

def get_kpis():
    """
    Calculates metrics based on the combined data.
    """
    onboarded = st.session_state.get('onboarded_df', pd.DataFrame())
    approached = st.session_state.get('approached_df', pd.DataFrame())
    
    # Identify Active vendors based on the 'source_file' name
    active_count = 0
    if not onboarded.empty and 'source_file' in onboarded.columns:
        # Check if the row came specifically from the 'Active.csv' onboarded file
        active_count = len(onboarded[onboarded['source_file'].str.contains('Active', case=False, na=False)])

    return {
        "total_onboarded": len(onboarded),
        "total_approached": len(approached),
        "active_vendors": active_count,
    }
