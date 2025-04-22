import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from src.utils.ui import LoadingState, handle_error, show_empty_state, show_error
from src.utils.ui_enhanced import (
    with_tooltip,
    EnhancedLoadingState,
    show_toast,
    enhanced_dataframe,
    with_loading_and_feedback
)

@with_loading_and_feedback(
    message="Fetching sentiment data...",
    success_message=None,
    error_message="Failed to load sentiment data"
)
def get_sentiment_data():
    """Fetch sentiment distribution data."""
    sentiment_query = """
        SELECT 
            CASE 
                WHEN sentiment_score < -0.3 THEN 'Negative'
                WHEN sentiment_score > 0.3 THEN 'Positive'
                ELSE 'Neutral'
            END as sentiment_category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        GROUP BY sentiment_category
        ORDER BY count DESC;
    """
    data = execute_query(sentiment_query)
    return pd.DataFrame(data, columns=['sentiment_category', 'count', 'percentage'])

@handle_error
def get_sentiment_trends():
    """Fetch sentiment trends data."""
    trends_query = """
        SELECT 
            DATE_TRUNC('day', interaction_date) as date,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        GROUP BY date
        ORDER BY date;
    """
    data = execute_query(trends_query)
    return pd.DataFrame(data, columns=['date', 'avg_sentiment', 'interaction_count'])

@handle_error
def get_sentiment_by_type():
    """Fetch sentiment by interaction type data."""
    type_query = """
        SELECT 
            interaction_type,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        GROUP BY interaction_type
        ORDER BY avg_sentiment DESC;
    """
    data = execute_query(type_query)
    return pd.DataFrame(data, columns=['interaction_type', 'avg_sentiment', 'interaction_count'])

@handle_error
def get_sentiment_correlation():
    """Fetch sentiment correlation data."""
    correlation_query = """
        WITH daily_metrics AS (
            SELECT 
                DATE_TRUNC('day', interaction_date) as date,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as interaction_count
            FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
            GROUP BY date
        )
        SELECT 
            date,
            avg_sentiment,
            interaction_count
        FROM daily_metrics
        ORDER BY date;
    """
    data = execute_query(correlation_query)
    return pd.DataFrame(data, columns=['date', 'avg_sentiment', 'interaction_count'])

@handle_error
def get_sentiment_volatility():
    """Fetch sentiment volatility data."""
    volatility_query = """
        WITH customer_metrics AS (
            SELECT 
                customer_id,
                AVG(sentiment_score) as avg_sentiment,
                STDDEV(sentiment_score) as sentiment_volatility,
                COUNT(*) as interaction_count
            FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
            GROUP BY customer_id
        )
        SELECT 
            customer_id,
            avg_sentiment,
            sentiment_volatility,
            interaction_count
        FROM customer_metrics
        ORDER BY sentiment_volatility DESC
        LIMIT 10;
    """
    data = execute_query(volatility_query)
    return pd.DataFrame(data, columns=['customer_id', 'avg_sentiment', 'sentiment_volatility', 'interaction_count'])

def render_sentiment_page():
    """Render the Sentiment & Experience workspace."""
    try:
        # Page header with tooltip
        @with_tooltip("Analyze customer sentiment across different interaction types and time periods")
        def render_header():
            st.header("Sentiment & Experience Analytics")
        render_header()
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Overall Sentiment Distribution
        with col1:
            @with_tooltip("Distribution of customer sentiment across all interactions")
            def render_sentiment_distribution():
                st.subheader("Overall Sentiment")
            render_sentiment_distribution()
            
            with EnhancedLoadingState("Loading sentiment distribution...") as loader:
                df_sentiment = get_sentiment_data()
                if df_sentiment is not None and not df_sentiment.empty:
                    df_sentiment['count'] = pd.to_numeric(df_sentiment['count'])
                    fig = px.bar(
                        df_sentiment,
                        x='sentiment_category',
                        y='count',
                        color='sentiment_category',
                        title='Overall Sentiment Distribution',
                        labels={
                            'sentiment_category': 'Sentiment Category',
                            'count': 'Count',
                            'percentage': 'Percentage'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_empty_state("No sentiment data available")
        
        # Sentiment Trends
        with col2:
            @with_tooltip("Track how customer sentiment changes over time")
            def render_sentiment_trends():
                st.subheader("Sentiment Trends")
            render_sentiment_trends()
            
            with EnhancedLoadingState("Loading sentiment trends...") as loader:
                df_trends = get_sentiment_trends()
                if df_trends is not None and not df_trends.empty:
                    fig = px.line(
                        df_trends,
                        x='date',
                        y='avg_sentiment',
                        title='Sentiment Trends Over Time',
                        labels={
                            'date': 'Date',
                            'avg_sentiment': 'Average Sentiment',
                            'interaction_count': 'Interaction Count'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_empty_state("No trend data available")
        
        # Sentiment by Interaction Type
        with col3:
            @with_tooltip("Compare sentiment across different types of customer interactions")
            def render_sentiment_by_type():
                st.subheader("Sentiment by Type")
            render_sentiment_by_type()
            
            with EnhancedLoadingState("Loading sentiment by type...") as loader:
                df_type = get_sentiment_by_type()
                if df_type is not None and not df_type.empty:
                    fig = px.bar(
                        df_type,
                        x='interaction_type',
                        y='avg_sentiment',
                        color='interaction_count',
                        title='Sentiment by Interaction Type',
                        labels={
                            'interaction_type': 'Interaction Type',
                            'avg_sentiment': 'Average Sentiment',
                            'interaction_count': 'Interaction Count'
                        }
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_empty_state("No interaction type data available")
        
        # Detailed Analysis Section
        st.markdown("---")
        @with_tooltip("Explore detailed sentiment analysis and correlations")
        def render_detailed_analysis():
            st.subheader("Detailed Analysis")
        render_detailed_analysis()
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Sentiment Correlations",
            "Volatility Analysis",
            "Raw Data"
        ])
        
        with tab1:
            with EnhancedLoadingState("Loading correlation data...") as loader:
                df_correlation = get_sentiment_correlation()
                if df_correlation is not None and not df_correlation.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_correlation['date'],
                        y=df_correlation['avg_sentiment'],
                        name='Average Sentiment',
                        line=dict(color='#3b82f6')
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_correlation['date'],
                        y=df_correlation['interaction_count'],
                        name='Interaction Count',
                        line=dict(color='#10b981'),
                        yaxis='y2'
                    ))
                    fig.update_layout(
                        title='Sentiment vs. Interaction Volume',
                        yaxis=dict(title='Average Sentiment'),
                        yaxis2=dict(
                            title='Interaction Count',
                            overlaying='y',
                            side='right'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_empty_state("No correlation data available")
        
        with tab2:
            with EnhancedLoadingState("Loading volatility data...") as loader:
                df_volatility = get_sentiment_volatility()
                if df_volatility is not None and not df_volatility.empty:
                    df_volatility['interaction_count'] = pd.to_numeric(df_volatility['interaction_count'], errors='coerce')
                    df_volatility = df_volatility.dropna(subset=['interaction_count'])
                    
                    if not df_volatility.empty:
                        fig = px.scatter(
                            df_volatility,
                            x='avg_sentiment',
                            y='sentiment_volatility',
                            size='interaction_count',
                            hover_data=['customer_id'],
                            title='Customer Sentiment Volatility vs. Average'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        show_empty_state("No volatility data available")
                else:
                    show_empty_state("No volatility data available")
        
        with tab3:
            with EnhancedLoadingState("Loading raw data...") as loader:
                df_raw = get_sentiment_data()
                if df_raw is not None and not df_raw.empty:
                    enhanced_dataframe(
                        df_raw,
                        height=400,
                        use_container_width=True
                    )
                else:
                    show_empty_state("No raw data available")
                    
    except Exception as e:
        show_toast(f"An error occurred while rendering the sentiment page: {str(e)}", "error")
        log_error(e, "Sentiment page rendering") 