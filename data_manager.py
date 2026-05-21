import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DATA_DIR = "data"

@st.cache_data(show_spinner="Syncing Vendor Database...")
def load_and_sort_data():
    """
    Scans the /data folder and separates files into 'Onboarded' and 'Approached'
    based on the keywords in their filenames.
    """
    onboarded_frames = []
    approached_frames = []
    
    if not os.path.exists(DATA_DIR):
        st.error(f"Directory '{DATA_DIR}' not found!")
        return pd.DataFrame(), pd.DataFrame()

    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    for filename in all_files:
        file_path = os.path.join(DATA_DIR, filename)
        try:
            df = pd.read_csv(file_path, low_memory=False)
            df['source_file'] = filename # Keeps track of which file the row came from
            
            # KEYWORD LOGIC:
            # Files with 'Master AU' are Onboarded
            # Files with 'Track Master' are Approached leads
            if "Master AU" in filename:
                onboarded_frames.append(df)
            elif "Track Master" in filename:
                approached_frames.append(df)
                
        except Exception as e:
            st.error(f"Skipping {filename}: {e}")

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
    
    # Identify Active vendors based on the 'source_file' name or a status column
    active_count = 0
    if not onboarded.empty:
        # Check if 'Active' is in the filename or a column
        active_count = len(onboarded[onboarded['source_file'].str.contains('Active', case=False)])

    return {
        "total_onboarded": len(onboarded),
        "total_approached": len(approached),
        "active_vendors": active_count,
    }
