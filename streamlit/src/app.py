import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from components.overview_dashboard import render_overview_dashboard
from components.sentiment_experience_analysis import render_sentiment_experience_analysis

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"]
    )

conn = init_connection()

# Page config
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar filters
st.sidebar.title("Global Filters")

# Date range filter
st.sidebar.subheader("Date Range")
default_end_date = datetime.now()
default_start_date = default_end_date - timedelta(days=365)
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=default_start_date,
        min_value=default_start_date - timedelta(days=3650),
        max_value=default_end_date
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=default_end_date,
        min_value=start_date,
        max_value=default_end_date
    )

# Value Segment filter
st.sidebar.subheader("Customer Value Segment")
value_segments_query = """
SELECT DISTINCT persona
FROM ANALYTICS.CUSTOMER_BASE
WHERE persona IS NOT NULL
ORDER BY persona
"""
value_segments = [row[0] for row in conn.cursor().execute(value_segments_query).fetchall()]
selected_value_segments = st.sidebar.multiselect(
    "Select Value Segments",
    value_segments,
    default=value_segments
)

# Persona filter
st.sidebar.subheader("Derived Persona")
personas_query = """
SELECT DISTINCT derived_persona
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE derived_persona IS NOT NULL
ORDER BY derived_persona
"""
personas = [row[0] for row in conn.cursor().execute(personas_query).fetchall()]
selected_personas = st.sidebar.multiselect(
    "Select Personas",
    personas,
    default=personas
)

# Churn Risk filter
st.sidebar.subheader("Churn Risk")
churn_risks_query = """
SELECT DISTINCT churn_risk 
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS 
WHERE churn_risk IS NOT NULL
ORDER BY churn_risk
"""
churn_risks = [row[0] for row in conn.cursor().execute(churn_risks_query).fetchall()]
selected_churn_risks = st.sidebar.multiselect(
    "Select Churn Risk Levels",
    churn_risks,
    default=churn_risks
)

# Main content
st.title("Customer Analytics Dashboard")

# Tab navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Sentiment & Experience", 
    "Support Operations", 
    "Product Feedback", 
    "Customer Segmentation"
])

with tab1:
    render_overview_dashboard(conn, start_date, end_date, selected_value_segments, selected_personas)

with tab2:
    render_sentiment_experience_analysis(conn, start_date, end_date, selected_value_segments, selected_personas)

with tab3:
    st.header("Support Operations")
    st.info("Support Operations tab is under development")

with tab4:
    st.header("Product Feedback")
    st.info("Product Feedback tab is under development")

with tab5:
    st.header("Customer Segmentation")
    st.info("Customer Segmentation tab is under development") 