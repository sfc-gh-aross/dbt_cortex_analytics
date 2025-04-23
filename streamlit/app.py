import streamlit as st
import snowflake.connector
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize connection to Snowflake
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"]
    )

conn = init_connection()

# Helper function to run queries
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Sidebar filters
st.sidebar.title("Global Filters")

# Date Range Filter
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

# Customer Value Segment Filter
value_segments_query = """
SELECT DISTINCT persona 
FROM ANALYTICS.CUSTOMER_BASE 
WHERE persona IS NOT NULL
ORDER BY persona
"""
value_segments = [row[0] for row in run_query(value_segments_query)]
selected_value_segments = st.sidebar.multiselect(
    "Customer Persona",
    options=value_segments,
    default=value_segments
)

# Derived Persona Filter
personas_query = """
SELECT DISTINCT derived_persona 
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS 
WHERE derived_persona IS NOT NULL
ORDER BY derived_persona
"""
personas = [row[0] for row in run_query(personas_query)]
selected_personas = st.sidebar.multiselect(
    "Derived Persona",
    options=personas,
    default=personas
)

# Churn Risk Filter
churn_risks_query = """
SELECT DISTINCT churn_risk 
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS 
WHERE churn_risk IS NOT NULL
ORDER BY churn_risk
"""
churn_risks = [row[0] for row in run_query(churn_risks_query)]
selected_churn_risks = st.sidebar.multiselect(
    "Churn Risk",
    options=churn_risks,
    default=churn_risks
)

# Upsell Opportunity Filter
upsell_opportunities_query = """
SELECT DISTINCT upsell_opportunity 
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS 
WHERE upsell_opportunity IS NOT NULL
ORDER BY upsell_opportunity
"""
upsell_opportunities = [row[0] for row in run_query(upsell_opportunities_query)]
selected_upsell_opportunities = st.sidebar.multiselect(
    "Upsell Opportunity",
    options=upsell_opportunities,
    default=upsell_opportunities
)

# Interaction Type Filter
interaction_types_query = """
SELECT DISTINCT interaction_type 
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS 
WHERE interaction_type IS NOT NULL
ORDER BY interaction_type
"""
interaction_types = [row[0] for row in run_query(interaction_types_query)]
selected_interaction_types = st.sidebar.multiselect(
    "Interaction Type",
    options=interaction_types,
    default=interaction_types
)

# Review Language Filter
review_languages_query = """
SELECT DISTINCT review_language 
FROM ANALYTICS.FACT_PRODUCT_REVIEWS 
WHERE review_language IS NOT NULL
ORDER BY review_language
"""
review_languages = [row[0] for row in run_query(review_languages_query)]
selected_review_languages = st.sidebar.multiselect(
    "Review Language",
    options=review_languages,
    default=review_languages
)

# Main content
st.title("Customer Analytics Dashboard")

# Overview Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Sentiment & Experience", 
    "Support Operations", 
    "Product Feedback", 
    "Customer Segmentation"
])

with tab1:
    st.header("Overview Dashboard")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Average Sentiment KPI
    with col1:
        sentiment_query = f"""
        SELECT AVG(sentiment_score) as avg_sentiment
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
        """
        avg_sentiment = run_query(sentiment_query)[0][0]
        st.metric(
            label="Average Sentiment",
            value=f"{avg_sentiment:.2f}",
            delta="0.1"  # TODO: Calculate actual delta
        )
    
    # Total Interactions KPI
    with col2:
        interactions_query = f"""
        SELECT COUNT(*) as total_interactions
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
        """
        total_interactions = run_query(interactions_query)[0][0]
        st.metric(
            label="Total Interactions",
            value=total_interactions,
            delta="100"  # TODO: Calculate actual delta
        )
    
    # Overall Churn Risk KPI
    with col3:
        churn_risk_query = f"""
        SELECT 
            ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        WHERE churn_risk IS NOT NULL
        """
        high_risk_percentage = run_query(churn_risk_query)[0][0]
        st.metric(
            label="High Churn Risk",
            value=f"{high_risk_percentage:.1f}%",
            delta="-2.5%"  # TODO: Calculate actual delta
        )
    
    # Average Product Rating KPI
    with col4:
        rating_query = f"""
        SELECT AVG(review_rating) as avg_rating
        FROM ANALYTICS.FACT_PRODUCT_REVIEWS
        WHERE review_date BETWEEN '{start_date}' AND '{end_date}'
        """
        avg_rating = run_query(rating_query)[0][0]
        st.metric(
            label="Average Product Rating",
            value=f"{avg_rating:.1f}",
            delta="0.2"  # TODO: Calculate actual delta
        )
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    # Sentiment Trend Chart
    with col1:
        st.subheader("Sentiment Trend")
        sentiment_trend_query = f"""
        SELECT 
            DATE_TRUNC('month', interaction_date) as month,
            AVG(sentiment_score) as avg_sentiment
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY month
        ORDER BY month
        """
        sentiment_trend_data = pd.DataFrame(
            run_query(sentiment_trend_query),
            columns=['month', 'avg_sentiment']
        )
        fig = px.line(
            sentiment_trend_data,
            x='month',
            y='avg_sentiment',
            title='Monthly Average Sentiment'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer Sentiment Distribution
    with col2:
        st.subheader("Customer Sentiment Distribution")
        sentiment_dist_query = f"""
        SELECT 
            overall_sentiment,
            COUNT(*) as count
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        GROUP BY overall_sentiment
        ORDER BY count DESC
        """
        sentiment_dist_data = pd.DataFrame(
            run_query(sentiment_dist_query),
            columns=['overall_sentiment', 'count']
        )
        fig = px.bar(
            sentiment_dist_data,
            x='overall_sentiment',
            y='count',
            title='Distribution of Customer Sentiment'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn Risk Breakdown
    st.subheader("Churn Risk Breakdown")
    churn_risk_dist_query = f"""
    SELECT 
        churn_risk,
        COUNT(*) as count
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    GROUP BY churn_risk
    ORDER BY 
        CASE churn_risk
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
        END
    """
    churn_risk_data = pd.DataFrame(
        run_query(churn_risk_dist_query),
        columns=['churn_risk', 'count']
    )
    fig = px.bar(
        churn_risk_data,
        x='churn_risk',
        y='count',
        title='Distribution of Churn Risk Levels'
    )
    st.plotly_chart(fig, use_container_width=True)
