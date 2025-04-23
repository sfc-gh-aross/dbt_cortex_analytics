import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import numpy as np
from pathlib import Path
import sys
# from src.ui.theme import apply_theme
from src.utils.logging import setup_logging
from src.ui.filters import FilterManager
from src.pages import (
    sentiment,
    support,
    reviews,
    journey,
    segmentation,
    insights
)
from src.ui.components import (
    create_metric_card,
    create_trend_indicator,
    create_info_tooltip,
    create_chart_container,
    create_section_header
)
from src.ui.layout import create_sidebar
from src.data.connection import get_snowflake_session, execute_query

# Set page config - must be first Streamlit command
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
# apply_theme()

# Setup logging
logger = setup_logging()

# Add the src directory to the Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Import custom modules
# Removed get_snowflake_session import here as it's imported again below? Keeping the one from data.connection
# from src.data.connection import get_snowflake_session 

def main():
    """Main application entry point."""
    try:
        # Initialize session state
        if "snowflake_session" not in st.session_state:
            st.session_state.snowflake_session = get_snowflake_session()
        
        # Initialize date range defaults ONLY if not already set by a loaded preset
        if "start_date" not in st.session_state:
            # st.session_state.start_date = datetime.now().date() - timedelta(days=30)
            st.session_state.start_date = date(2024, 1, 1) # New default start date
        if "end_date" not in st.session_state:
            # st.session_state.end_date = datetime.now().date()
            st.session_state.end_date = date(2026, 1, 1) # New default end date
        
        # Initialize filter manager (this ensures st.session_state.active_filters exists)
        filter_manager = FilterManager()
        
        # Sidebar navigation
        st.sidebar.title("Customer Analytics")
        
        # Global filters section
        st.sidebar.subheader("Global Filters")
        
        # --- Date range filter --- 
        # Get current value from active_filters if it exists, otherwise use defaults
        # Ensure the value is a tuple of date objects
        date_range_val = st.session_state.active_filters.get("date_range")
        if not (isinstance(date_range_val, (tuple, list)) and len(date_range_val) == 2 and all(isinstance(d, date) for d in date_range_val)):
             # Fallback to initial defaults if not set or invalid in active_filters
             date_range_val = (st.session_state.start_date, st.session_state.end_date)
        
        # Instantiate the widget, setting its value based on active_filters or defaults
        date_range_widget_output = st.sidebar.date_input(
            "Date Range",
            value=date_range_val,
            key="date_range"
        )
        # Update active_filters with the *current* output of the widget for this run
        filter_manager.update_filter("date_range", date_range_widget_output)
        
        # --- Persona filter --- (REMOVED)
        # # Fetch persona options dynamically
        # persona_options = get_persona_options() 
        # # Get current value from active_filters if it exists, otherwise use default
        # personas_val = st.session_state.active_filters.get("personas", ["All"]) # Default to ["All"]
        # # Ensure it's a list
        # if not isinstance(personas_val, list):
        #     personas_val = ["All"]
        #     
        # personas_widget_output = st.sidebar.multiselect(
        #     "Customer Personas",
        #     options=persona_options,
        #     default=personas_val, # Use value from active_filters or default
        #     key="personas"
        # )
        # filter_manager.update_filter("personas", personas_widget_output)
        
        # --- Channel filter --- 
        # channel_options = ["All", "Email", "Chat", "Phone", "Social"]
        # # Get current value from active_filters if it exists, otherwise use default
        # channels_val = st.session_state.active_filters.get("channels", ["All"]) # Default to ["All"]
        # # Ensure it's a list
        # if not isinstance(channels_val, list):
        #      channels_val = ["All"]
        #      
        # channels_widget_output = st.sidebar.multiselect(
        #     "Channels",
        #     options=channel_options,
        #     default=channels_val, # Use value from active_filters or default
        #     key="channels"
        # )
        # filter_manager.update_filter("channels", channels_widget_output)
        
        # Render filter presets (contains load/save buttons which trigger reruns)
        # filter_manager.render_preset_management()
        
        # Render filter summary (optional, shows applied filters)
        filter_manager.render_filter_summary()

        # Main content area with tabs
        tab_selected = st.radio(
            "Navigation",
            ["😊 Sentiment & Experience", "🛠️ Support Operations", "⭐ Product Feedback", "🛣️ Customer Journey", "🎯 Segmentation & Value"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Main content area - only render the selected tab
        if tab_selected == "😊 Sentiment & Experience":
            if hasattr(sentiment, 'render_sentiment_page'):
                sentiment.render_sentiment_page(filter_manager.get_active_filters())
            else:
                st.info("Sentiment analysis page is under development")
        
        elif tab_selected == "🛠️ Support Operations":
            if hasattr(support, 'render_support_page'):
                support.render_support_page(filter_manager.get_active_filters())
            else:
                st.info("Support operations page is under development")
        
        elif tab_selected == "⭐ Product Feedback":
            if hasattr(reviews, 'render_reviews_page'):
                reviews.render_reviews_page(filter_manager.get_active_filters())
            else:
                st.info("Product feedback page is under development")
        
        elif tab_selected == "🛣️ Customer Journey":
            if hasattr(journey, 'render_journey_page'):
                journey.render_journey_page(filter_manager.get_active_filters())
            else:
                st.info("Customer journey page is under development")
        
        elif tab_selected == "🎯 Segmentation & Value":
            if hasattr(segmentation, 'render_segmentation_page'):
                segmentation.render_segmentation_page(filter_manager.get_active_filters())
            else:
                st.info("Segmentation page is under development")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 