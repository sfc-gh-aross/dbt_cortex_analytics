import streamlit as st
from datetime import datetime, timedelta

def create_sidebar():
    """Create the application sidebar with filters and navigation.
    
    Returns:
        dict: Dictionary containing filter values
    """
    st.sidebar.title("Customer Analytics")
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    today = datetime.now()
    default_start = today - timedelta(days=30)
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(default_start, today),
        max_value=today
    )
    
    # Customer segment filter
    st.sidebar.subheader("Customer Segment")
    segments = st.sidebar.multiselect(
        "Select segments",
        options=["Enterprise", "SMB", "Startup", "Individual"],
        default=["Enterprise", "SMB"]
    )
    
    # Channel filter
    st.sidebar.subheader("Channel")
    channels = st.sidebar.multiselect(
        "Select channels",
        options=["Email", "Chat", "Phone", "Social"],
        default=["Email", "Chat"]
    )
    
    # Product filter
    st.sidebar.subheader("Product")
    products = st.sidebar.multiselect(
        "Select products",
        options=["Product A", "Product B", "Product C"],
        default=["Product A", "Product B"]
    )
    
    return {
        "date_range": date_range,
        "segments": segments,
        "channels": channels,
        "products": products
    } 