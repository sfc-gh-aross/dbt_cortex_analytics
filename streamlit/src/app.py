import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from components.overview_dashboard import render_overview_dashboard

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
    layout="wide"
)

# Sidebar filters
st.sidebar.title("Filters")

# Date range filter
st.sidebar.subheader("Date Range")
default_end_date = datetime.now()
default_start_date = default_end_date - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", default_start_date)
end_date = st.sidebar.date_input("End Date", default_end_date)

# Value Segment filter
st.sidebar.subheader("Value Segment")
value_segments_query = """
SELECT DISTINCT persona
FROM ANALYTICS.CUSTOMER_BASE
ORDER BY persona
"""
value_segments = [row[0] for row in conn.cursor().execute(value_segments_query).fetchall()]
selected_value_segments = st.sidebar.multiselect(
    "Select Value Segments",
    value_segments,
    default=value_segments
)

# Persona filter
st.sidebar.subheader("Persona")
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

# Main content
st.title("Customer Analytics Dashboard")

# Tab navigation
tab1, tab2, tab3 = st.tabs(["Overview", "Customer Insights", "Product Analytics"])

with tab1:
    render_overview_dashboard(conn, start_date, end_date, selected_value_segments, selected_personas)

with tab2:
    st.header("Customer Insights")
    # TODO: Implement Customer Insights tab

with tab3:
    st.header("Product Analytics")
    # TODO: Implement Product Analytics tab 