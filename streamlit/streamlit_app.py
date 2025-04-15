import streamlit as st
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session

# Load environment variables
load_dotenv()

# Configuration
DEPLOYMENT_MODE = os.getenv('DEPLOYMENT_MODE', 'snowflake')  # 'snowflake' or 'standalone'

# Debug information
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show deployment mode
st.sidebar.info(f"Deployment Mode: {DEPLOYMENT_MODE}")

# Custom CSS for consistent styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stDataFrame {
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session
@st.cache_resource
def get_session():
    try:
        if DEPLOYMENT_MODE == 'snowflake':
            return get_active_session()
        else:
            # For standalone deployment, use connection parameters from environment variables
            connection_parameters = {
                "account": os.getenv('SNOWFLAKE_ACCOUNT'),
                "user": os.getenv('SNOWFLAKE_USER'),
                "password": os.getenv('SNOWFLAKE_PASSWORD'),
                "role": os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
                "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                "database": os.getenv('SNOWFLAKE_DATABASE', 'DBT_CORTEX_LLMS'),
                "schema": os.getenv('SNOWFLAKE_SCHEMA', 'ANALYTICS')
            }
            # Show connection parameters (excluding password)
            debug_params = {k: v for k, v in connection_parameters.items() if k != 'password'}
            st.sidebar.write("Connection Parameters:", debug_params)
            return Session.builder.configs(connection_parameters).create()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        return None

# Cache expensive queries
@st.cache_data(ttl=3600)
def get_customer_persona_data():
    try:
        session = get_session()
        if session is None:
            return pd.DataFrame()
        
        df = session.sql("""
            SELECT 
                customer_id,
                derived_persona,
                avg_sentiment,
                sentiment_trend,
                sentiment_volatility,
                churn_risk,
                upsell_opportunity,
                ticket_count,
                avg_rating
            FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        """).to_pandas()
        
        st.sidebar.success(f"Successfully loaded {len(df)} customer records")
        # Add debug information
        st.sidebar.write("DataFrame columns:", df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"Failed to load customer persona data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_sentiment_analysis_data():
    try:
        session = get_session()
        if session is None:
            return pd.DataFrame()
        
        return session.sql("""
            SELECT 
                customer_id,
                interaction_date,
                sentiment_score,
                source_type
            FROM ANALYTICS.SENTIMENT_ANALYSIS
            ORDER BY interaction_date
        """).to_pandas()
    except Exception as e:
        st.error(f"Failed to load sentiment analysis data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_support_tickets_data():
    try:
        session = get_session()
        if session is None:
            return pd.DataFrame()
        
        return session.sql("""
            SELECT 
                customer_id,
                ticket_date,
                ticket_status,
                ticket_category,
                priority_level,
                sentiment_score
            FROM ANALYTICS.FACT_SUPPORT_TICKETS
        """).to_pandas()
    except Exception as e:
        st.error(f"Failed to load support tickets data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_product_reviews_data():
    try:
        session = get_session()
        if session is None:
            return pd.DataFrame()
        
        return session.sql("""
            SELECT 
                customer_id,
                review_date,
                review_rating,
                review_language,
                sentiment_score
            FROM ANALYTICS.FACT_PRODUCT_REVIEWS
        """).to_pandas()
    except Exception as e:
        st.error(f"Failed to load product reviews data: {str(e)}")
        return pd.DataFrame()

# Sidebar filters
def create_sidebar_filters():
    st.sidebar.title("Filters")
    
    # Date range filter
    min_date = datetime.now() - timedelta(days=365)
    max_date = datetime.now()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Persona filter
    persona_data = get_customer_persona_data()
    if not persona_data.empty:
        personas = persona_data['derived_persona'].unique()
        selected_personas = st.sidebar.multiselect(
            "Customer Personas",
            options=personas,
            default=personas
        )
    else:
        selected_personas = []
    
    # Churn risk filter
    churn_risks = ['High', 'Medium', 'Low']
    selected_risks = st.sidebar.multiselect(
        "Churn Risk",
        options=churn_risks,
        default=churn_risks
    )
    
    return {
        'date_range': date_range,
        'personas': selected_personas,
        'churn_risks': selected_risks
    }

# Main dashboard layout
def main():
    # Get filters
    filters = create_sidebar_filters()
    
    # Load data
    persona_data = get_customer_persona_data()
    if persona_data.empty:
        st.warning("No customer data available. Please check your connection settings.")
        return
        
    sentiment_data = get_sentiment_analysis_data()
    tickets_data = get_support_tickets_data()
    reviews_data = get_product_reviews_data()
    
    # Apply filters
    filtered_persona_data = persona_data[
        (persona_data['derived_persona'].isin(filters['personas'])) &
        (persona_data['churn_risk'].isin(filters['churn_risks']))
    ]
    
    # Title and overview
    st.title("Customer Analytics Dashboard")
    st.markdown("""
        This dashboard provides comprehensive insights into customer behavior, sentiment, and engagement patterns.
        Use the filters in the sidebar to customize your view.
    """)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Customers",
            len(filtered_persona_data),
            f"{len(filtered_persona_data) - len(persona_data)} filtered"
        )
    
    with col2:
        avg_sentiment = filtered_persona_data['avg_sentiment'].mean()
        st.metric(
            "Average Sentiment",
            f"{avg_sentiment:.2f}",
            f"{filtered_persona_data['avg_sentiment'].std():.2f} std"
        )
    
    with col3:
        churn_risk = filtered_persona_data['churn_risk'].value_counts().get('High', 0)
        st.metric(
            "High Churn Risk",
            churn_risk,
            f"{churn_risk/len(filtered_persona_data)*100:.1f}%"
        )
    
    with col4:
        avg_rating = filtered_persona_data['avg_rating'].mean()
        st.metric(
            "Average Rating",
            f"{avg_rating:.1f}",
            f"{filtered_persona_data['avg_rating'].std():.1f} std"
        )
    
    # Customer Persona Distribution
    st.subheader("Customer Persona Distribution")
    fig_persona = px.pie(
        filtered_persona_data,
        names='derived_persona',
        title='Distribution of Customer Personas'
    )
    st.plotly_chart(fig_persona, use_container_width=True)
    
    # Sentiment Analysis
    st.subheader("Sentiment Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sentiment = px.histogram(
            filtered_persona_data,
            x='avg_sentiment',
            title='Sentiment Score Distribution'
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        fig_trend = px.scatter(
            filtered_persona_data,
            x='sentiment_trend',
            y='avg_sentiment',
            color='churn_risk',
            title='Sentiment Trend vs Average Sentiment'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Support Ticket Analysis
    if not tickets_data.empty:
        st.subheader("Support Ticket Analysis")
        fig_tickets = px.box(
            tickets_data,
            x='priority_level',
            y='sentiment_score',
            title='Sentiment Distribution by Ticket Priority'
        )
        st.plotly_chart(fig_tickets, use_container_width=True)
    
    # Product Reviews Analysis
    if not reviews_data.empty:
        st.subheader("Product Reviews Analysis")
        fig_reviews = px.scatter(
            reviews_data,
            x='review_rating',
            y='sentiment_score',
            color='review_language',
            title='Review Rating vs Sentiment by Language'
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    # Detailed Customer Data
    st.subheader("Detailed Customer Data")
    st.dataframe(
        filtered_persona_data,
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main() 