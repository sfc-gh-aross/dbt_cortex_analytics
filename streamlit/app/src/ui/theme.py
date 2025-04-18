import streamlit as st

def apply_theme():
    """Apply custom theme to the Streamlit application."""
    st.markdown("""
        <style>
            /* Main theme colors */
            :root {
                --primary-color: #2563eb;
                --secondary-color: #10b981;
                --background-color: #ffffff;
                --text-color: #1f2937;
                --border-color: #e5e7eb;
            }
            
            /* General styling */
            .stApp {
                background-color: var(--background-color);
                color: var(--text-color);
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background-color: var(--background-color);
                border-right: 1px solid var(--border-color);
            }
            
            /* Button styling */
            .stButton > button {
                background-color: var(--primary-color);
                color: white;
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                border: none;
                font-weight: 500;
            }
            
            .stButton > button:hover {
                background-color: #1d4ed8;
            }
            
            /* Metric card styling */
            .stMetric {
                background-color: var(--background-color);
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                padding: 1rem;
            }
            
            /* Chart container styling */
            .element-container {
                background-color: var(--background-color);
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            /* Hide empty containers */
            .element-container:empty {
                display: none;
                margin: 0;
                padding: 0;
                border: none;
            }
            
            /* Table styling */
            .stDataFrame {
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .stSidebar {
                    width: 100%;
                }
            }
        </style>
    """, unsafe_allow_html=True)

def get_color_palette():
    """Return the application's color palette.
    
    Returns:
        dict: Color palette dictionary
    """
    return {
        "primary": "#2563eb",
        "secondary": "#10b981",
        "background": "#ffffff",
        "text": "#1f2937",
        "border": "#e5e7eb",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6"
    }

def get_typography():
    """Return the application's typography settings.
    
    Returns:
        dict: Typography settings dictionary
    """
    return {
        "font_family": "Inter, sans-serif",
        "heading_sizes": {
            "h1": "2.5rem",
            "h2": "2rem",
            "h3": "1.75rem",
            "h4": "1.5rem",
            "h5": "1.25rem",
            "h6": "1rem"
        },
        "body_size": "1rem",
        "small_size": "0.875rem"
    } 