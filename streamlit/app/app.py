import streamlit as st
import snowflake.connector
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add the src directory to the Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Import custom modules
from src.data.connection import get_snowflake_session
from src.ui.theme import apply_theme
from src.utils.logging import setup_logging
from src.pages import (
    sentiment,
    support,
    reviews,
    journey,
    segmentation,
    insights
)

# Configure the page
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
apply_theme()

# Setup logging
logger = setup_logging()

def main():
    """Main application entry point."""
    try:
        # Initialize session state
        if "snowflake_session" not in st.session_state:
            st.session_state.snowflake_session = get_snowflake_session()
        
        # Initialize date range if not set
        if "start_date" not in st.session_state:
            st.session_state.start_date = datetime.now() - timedelta(days=30)
        if "end_date" not in st.session_state:
            st.session_state.end_date = datetime.now()
        
        # Create main content area with tabs
        main_tabs = st.tabs([
            "😊 Sentiment & Experience",
            "🛠️ Support Operations",
            "⭐ Product Feedback",
            "🛣️ Customer Journey",
            "🎯 Segmentation & Value"
        ])
        
        # Sidebar navigation
        st.sidebar.title("Customer Analytics")
        st.sidebar.markdown("---")
        
        # Global filters
        st.sidebar.subheader("Global Filters")
        
        # Date range filter
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(st.session_state.start_date, st.session_state.end_date),
            key="date_range"
        )
        
        # Persona filter
        personas = st.sidebar.multiselect(
            "Customer Personas",
            options=["All", "Enterprise", "SMB", "Startup", "Individual"],
            default=["All"],
            key="personas"
        )
        
        # Channel filter
        channels = st.sidebar.multiselect(
            "Channels",
            options=["All", "Email", "Chat", "Phone", "Social"],
            default=["All"],
            key="channels"
        )
        
        # Main content area
        with main_tabs[0]:
            sentiment.render_sentiment_page()
        
        with main_tabs[1]:
            support.render_support_page()
        
        with main_tabs[2]:
            reviews.render_reviews_page()
        
        with main_tabs[3]:
            journey.render_journey_page()
        
        with main_tabs[4]:
            segmentation.render_segmentation_page()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 