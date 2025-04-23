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
def run_query(query, params=[]):
    with conn.cursor() as cur:
        cur.execute(query, params)
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
        WITH current_period AS (
            SELECT AVG(sentiment_score) as avg_sentiment
            FROM ANALYTICS.SENTIMENT_ANALYSIS
            WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        ),
        previous_period AS (
            SELECT AVG(sentiment_score) as avg_sentiment
            FROM ANALYTICS.SENTIMENT_ANALYSIS
            WHERE interaction_date BETWEEN 
                DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
                DATEADD(day, -1, '{start_date}')
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        )
        SELECT 
            current_period.avg_sentiment,
            current_period.avg_sentiment - previous_period.avg_sentiment as sentiment_delta
        FROM current_period, previous_period
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        avg_sentiment, sentiment_delta = run_query(sentiment_query, params)[0]
        st.metric(
            label="Average Sentiment",
            value=f"{avg_sentiment:.2f}" if avg_sentiment is not None else "N/A",
            delta=f"{sentiment_delta:.2f}" if sentiment_delta is not None else None
        )
    
    # Total Interactions KPI
    with col2:
        interactions_query = f"""
        WITH current_period AS (
            SELECT COUNT(*) as total_interactions
            FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
            WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        ),
        previous_period AS (
            SELECT COUNT(*) as total_interactions
            FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
            WHERE interaction_date BETWEEN 
                DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
                DATEADD(day, -1, '{start_date}')
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        )
        SELECT 
            current_period.total_interactions,
            current_period.total_interactions - previous_period.total_interactions as interactions_delta
        FROM current_period, previous_period
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        total_interactions, interactions_delta = run_query(interactions_query, params)[0]
        st.metric(
            label="Total Interactions",
            value=total_interactions if total_interactions is not None else "N/A",
            delta=interactions_delta if interactions_delta is not None else None
        )
    
    # Overall Churn Risk KPI
    with col3:
        churn_risk_query = f"""
        WITH current_period AS (
            SELECT 
                ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
            FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
            WHERE churn_risk IS NOT NULL
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        ),
        previous_period AS (
            SELECT 
                ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
            FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
            WHERE churn_risk IS NOT NULL
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        )
        SELECT 
            current_period.high_risk_percentage,
            current_period.high_risk_percentage - previous_period.high_risk_percentage as risk_delta
        FROM current_period, previous_period
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        high_risk_percentage, risk_delta = run_query(churn_risk_query, params)[0]
        st.metric(
            label="High Churn Risk",
            value=f"{high_risk_percentage:.1f}%" if high_risk_percentage is not None else "N/A",
            delta=f"{risk_delta:.1f}%" if risk_delta is not None else None
        )
    
    # Average Product Rating KPI
    with col4:
        rating_query = f"""
        WITH current_period AS (
            SELECT AVG(review_rating) as avg_rating
            FROM ANALYTICS.FACT_PRODUCT_REVIEWS
            WHERE review_date BETWEEN '{start_date}' AND '{end_date}'
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        ),
        previous_period AS (
            SELECT AVG(review_rating) as avg_rating
            FROM ANALYTICS.FACT_PRODUCT_REVIEWS
            WHERE review_date BETWEEN 
                DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
                DATEADD(day, -1, '{start_date}')
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
            {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        )
        SELECT 
            current_period.avg_rating,
            current_period.avg_rating - previous_period.avg_rating as rating_delta
        FROM current_period, previous_period
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        avg_rating, rating_delta = run_query(rating_query, params)[0]
        st.metric(
            label="Average Product Rating",
            value=f"{avg_rating:.1f}" if avg_rating is not None else "N/A",
            delta=f"{rating_delta:.1f}" if rating_delta is not None else None
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
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        GROUP BY month
        ORDER BY month
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        sentiment_trend_data = pd.DataFrame(
            run_query(sentiment_trend_query, params),
            columns=['month', 'avg_sentiment']
        )
        fig = px.line(
            sentiment_trend_data,
            x='month',
            y='avg_sentiment',
            title='Monthly Average Sentiment',
            labels={'month': 'Month', 'avg_sentiment': 'Average Sentiment Score'}
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Average Sentiment Score",
            hovermode='x unified'
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
        WHERE 1=1
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        GROUP BY overall_sentiment
        ORDER BY count DESC
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        sentiment_dist_data = pd.DataFrame(
            run_query(sentiment_dist_query, params),
            columns=['overall_sentiment', 'count']
        )
        fig = px.bar(
            sentiment_dist_data,
            x='overall_sentiment',
            y='count',
            title='Customer Sentiment Distribution',
            labels={'overall_sentiment': 'Sentiment', 'count': 'Number of Customers'}
        )
        fig.update_layout(
            xaxis_title="Sentiment",
            yaxis_title="Number of Customers",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    # Churn Risk Breakdown
    with col1:
        st.subheader("Churn Risk Breakdown")
        churn_risk_breakdown_query = f"""
        SELECT 
            churn_risk,
            COUNT(*) as count
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        WHERE churn_risk IS NOT NULL
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
        GROUP BY churn_risk
        ORDER BY 
            CASE churn_risk
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END
        """
        params = []
        if selected_value_segments:
            params.extend(selected_value_segments)
        if selected_personas:
            params.extend(selected_personas)
        churn_risk_data = pd.DataFrame(
            run_query(churn_risk_breakdown_query, params),
            columns=['churn_risk', 'count']
        )
        fig = px.bar(
            churn_risk_data,
            x='churn_risk',
            y='count',
            title='Churn Risk Distribution',
            labels={'churn_risk': 'Churn Risk Level', 'count': 'Number of Customers'}
        )
        fig.update_layout(
            xaxis_title="Churn Risk Level",
            yaxis_title="Number of Customers",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
