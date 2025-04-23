import streamlit as st

def apply_theme():
    """Apply custom theme to the Streamlit application."""
    st.markdown("""
        <style>
            /* Main theme colors - WCAG 2.1 AA compliant */
            :root {
                --primary-color: #1a56db;  /* Darker blue for better contrast */
                --secondary-color: #059669;  /* Darker green for better contrast */
                --background-color: #ffffff;
                --text-color: #111827;  /* Darker text for better readability */
                --border-color: #e5e7eb;
                --card-background: #f9fafb;
                --success-color: #059669;
                --warning-color: #d97706;
                --error-color: #dc2626;
                --info-color: #2563eb;
            }
            
            /* General styling */
            .stApp {
                background-color: var(--background-color);
                color: var(--text-color);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            
            /* Card-based layout system */
            .element-container {
                background-color: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            /* Consistent spacing */
            .stMarkdown {
                margin-bottom: 1rem;
            }
            
            /* Header spacing */
            .stHeader {
                margin-bottom: 2rem;
            }
            
            /* Section spacing */
            .stSubheader {
                margin-top: 2rem;
                margin-bottom: 1.5rem;
            }
            
            /* Tab spacing */
            .stTabs {
                margin-top: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            /* Chart spacing */
            .stPlotlyChart {
                margin-bottom: 2rem;
            }
            
            /* Metric spacing */
            .stMetric {
                margin-bottom: 1.5rem;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background-color: var(--card-background);
                border-right: 1px solid var(--border-color);
                padding: 1.5rem;
            }
            
            /* Button styling */
            .stButton > button {
                background-color: var(--primary-color);
                color: white;
                border-radius: 0.5rem;
                padding: 0.75rem 1.5rem;
                border: none;
                font-weight: 500;
                transition: background-color 0.2s;
                margin-bottom: 1rem;
            }
            
            .stButton > button:hover {
                background-color: #1e40af;
            }
            
            /* Table styling */
            .stDataFrame {
                border: 1px solid var(--border-color);
                border-radius: 0.75rem;
                overflow: hidden;
                margin-bottom: 1.5rem;
            }
            
            /* Visual indicators for trends */
            .trend-up {
                color: var(--success-color);
            }
            
            .trend-down {
                color: var(--error-color);
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .stSidebar {
                    width: 100%;
                }
                
                .element-container {
                    padding: 1rem;
                    margin-bottom: 1rem;
                }
            }
            
            /* Accessibility improvements */
            .stMarkdown a {
                color: var(--primary-color);
                text-decoration: underline;
            }
            
            .stMarkdown a:hover {
                color: #1e40af;
            }
            
            /* Focus states for keyboard navigation */
            .stButton > button:focus,
            .stSelectbox > div:focus,
            .stTextInput > div:focus {
                outline: 2px solid var(--primary-color);
                outline-offset: 2px;
            }
        </style>
    """, unsafe_allow_html=True)

def get_color_palette():
    """Return the application's color palette.
    
    Returns:
        dict: Color palette dictionary
    """
    return {
        "primary": "#1a56db",
        "secondary": "#059669",
        "background": "#ffffff",
        "text": "#111827",
        "border": "#e5e7eb",
        "card": "#f9fafb",
        "success": "#059669",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#2563eb"
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