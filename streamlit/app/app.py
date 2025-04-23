import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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
from src.data.connection import get_snowflake_session

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
        
        # Initialize filter manager
        filter_manager = FilterManager()
        
        # Sidebar navigation
        st.sidebar.title("Customer Analytics")
        
        # Global filters section
        st.sidebar.subheader("Global Filters")
        
        # Date range filter
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(st.session_state.start_date, st.session_state.end_date),
            key="date_range"
        )
        filter_manager.update_filter("date_range", date_range)
        
        # Persona filter with search
        persona_options = ["All", "Enterprise", "SMB", "Startup", "Individual"]
        persona_search = st.sidebar.text_input("Search Personas", key="persona_search")
        filtered_personas = [p for p in persona_options if persona_search.lower() in p.lower()]
        personas = st.sidebar.multiselect(
            "Customer Personas",
            options=filtered_personas,
            default=["All"],
            key="personas"
        )
        filter_manager.update_filter("personas", personas)
        
        # Channel filter with search
        channel_options = ["All", "Email", "Chat", "Phone", "Social"]
        channel_search = st.sidebar.text_input("Search Channels", key="channel_search")
        filtered_channels = [c for c in channel_options if channel_search.lower() in c.lower()]
        channels = st.sidebar.multiselect(
            "Channels",
            options=filtered_channels,
            default=["All"],
            key="channels"
        )
        filter_manager.update_filter("channels", channels)
        # Render filter presets
        filter_manager.render_preset_management()
        
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