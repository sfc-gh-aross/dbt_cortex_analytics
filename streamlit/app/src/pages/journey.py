import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import warnings
from typing import Dict

# Suppress FutureWarning from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

def render_journey_page(active_filters: Dict):
    """Render the customer journey page with applied filters."""
    st.title("Customer Journey Analysis")
    
    # Example journey metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Average Journey Length", "45 days", "-5 days")
    with metric_cols[1]:
        st.metric("Conversion Rate", "35%", "+3%")
    with metric_cols[2]:
        st.metric("Drop-off Rate", "25%", "-2%")
    with metric_cols[3]:
        st.metric("Time to Conversion", "30 days", "-3 days")
    
    try:
        # Page header
        st.header("Customer Journey Analytics")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Journey Stages",
            "Interaction Analysis",
            "Raw Data"
        ])
        
        with tab1:
            # Journey Stages Analysis
            st.subheader("Journey Stages Analysis")
            stage_data = pd.DataFrame({
                'Stage': ["Awareness", "Consideration", "Decision", "Purchase", "Retention"],
                'Users': [1000, 800, 600, 400, 300]
            })
            st.bar_chart(stage_data.set_index('Stage'))
        
        with tab2:
            # Interaction Analysis
            st.subheader("Interaction Analysis")
            timeline_data = pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
                'Users': [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100, 50, 25]
            })
            st.line_chart(timeline_data.set_index('Date'))
        
        with tab3:
            # Raw Data View
            st.subheader("Raw Data")
            raw_data_placeholder = pd.DataFrame({
                'CustomerID': [1, 2, 3, 4, 5],
                'InteractionType': ['View', 'Click', 'Purchase', 'View', 'Click'],
                'Timestamp': pd.to_datetime(['2023-01-10', '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14']),
                'Value': [10, 0, 150, 25, 0]
            })
            st.dataframe(raw_data_placeholder)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Journey page rendering") 