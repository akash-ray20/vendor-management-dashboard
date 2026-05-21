import streamlit as st

def apply_custom_css():
    """
    Injects custom CSS to transform the standard Streamlit look 
    into a modern, professional SaaS Dashboard.
    """
    st.markdown("""
        <style>
            /* Import a clean sans-serif font */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Main Background Layout */
            .stApp {
                background-color: #F9FAFB;
            }

            /* Sidebar Transformation */
            [data-testid="stSidebar"] {
                background-color: #111827; /* Dark Slate */
                border-right: 1px solid #E5E7EB;
            }
            
            [data-testid="stSidebar"] .stMarkdown p {
                color: #9CA3AF; /* Muted text for sidebar */
            }

            /* Metric Cards (KPIs) */
            div[data-testid="stMetric"] {
                background-color: white;
                border: 1px solid #F3F4F6;
                padding: 20px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            }
            
            div[data-testid="stMetricValue"] {
                font-size: 28px !important;
                font-weight: 700 !important;
                color: #1F2937 !important;
            }

            /* Styled Headers */
            h1, h2, h3 {
                color: #111827 !important;
                font-weight: 700 !important;
            }

            /* Form & Button Styling */
            .stButton>button {
                width: 100%;
                border-radius: 8px;
                border: none;
                background-color: #2563EB; /* Indigo/Blue */
                color: white;
                font-weight: 600;
                padding: 10px 20px;
                transition: background-color 0.2s ease;
            }
            
            .stButton>button:hover {
                background-color: #1D4ED8;
                border: none;
                color: white;
            }

            /* Custom Dataframe container */
            .stDataFrame {
                background-color: white;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid #E5E7EB;
            }

            /* Success/Info Toasts */
            div[data-testid="stToast"] {
                background-color: #111827 !important;
                color: white !important;
                border-radius: 8px !important;
            }
            
            /* Add a subtle gradient to the top of the page */
            header[data-testid="stHeader"] {
                background: transparent;
            }
        </style>
    """, unsafe_allow_html=True)

def card_container(title, content):
    """
    A helper function to wrap content in a white 'card' using Markdown.
    """
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #E5E7EB; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #374151;">{title}</h3>
            {content}
        </div>
    """, unsafe_allow_html=True)
