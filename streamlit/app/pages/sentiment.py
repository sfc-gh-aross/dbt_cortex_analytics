import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_sentiment_page():
    """Render the Sentiment & Experience workspace."""
    try:
        # Page header
        st.header("Sentiment & Experience Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Overall Sentiment Distribution
        with col1:
            st.subheader("Overall Sentiment")
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
            try:
                sentiment_data = execute_query(sentiment_query)
                # Create DataFrame with explicit column names
                df_sentiment = pd.DataFrame(
                    sentiment_data,
                    columns=['sentiment_category', 'count', 'percentage']
                )
                
                # Convert count to numeric if it's not already
                df_sentiment['count'] = pd.to_numeric(df_sentiment['count'])
                
                # Create stacked bar chart
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
            except Exception as e:
                log_error(e, "Sentiment distribution visualization")
                st.error("Failed to load sentiment distribution data")
        
        # Sentiment Trends
        with col2:
            st.subheader("Sentiment Trends")
            trends_query = """
                SELECT 
                    DATE_TRUNC('day', interaction_date) as date,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    COUNT(*) as interaction_count
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                GROUP BY date
                ORDER BY date;
            """
            try:
                trends_data = execute_query(trends_query)
                df_trends = pd.DataFrame(
                    trends_data,
                    columns=['date', 'avg_sentiment', 'interaction_count']
                )
                
                # Create line chart
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
            except Exception as e:
                log_error(e, "Sentiment trends visualization")
                st.error("Failed to load sentiment trends data")
        
        # Sentiment by Interaction Type
        with col3:
            st.subheader("Sentiment by Type")
            type_query = """
                SELECT 
                    interaction_type,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    COUNT(*) as interaction_count
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                GROUP BY interaction_type
                ORDER BY avg_sentiment DESC;
            """
            try:
                type_data = execute_query(type_query)
                df_type = pd.DataFrame(
                    type_data,
                    columns=['interaction_type', 'avg_sentiment', 'interaction_count']
                )
                
                # Create bar chart
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
            except Exception as e:
                log_error(e, "Sentiment by type visualization")
                st.error("Failed to load sentiment by type data")
        
        # Detailed Analysis Section
        st.markdown("---")
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Sentiment Correlations",
            "Volatility Analysis",
            "Raw Data"
        ])
        
        with tab1:
            # Sentiment Correlation with Support Ticket Volume
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
            try:
                correlation_data = execute_query(correlation_query)
                df_correlation = pd.DataFrame(
                    correlation_data,
                    columns=['date', 'avg_sentiment', 'interaction_count']
                )
                
                # Create dual-axis line chart
                fig = go.Figure()
                
                # Add sentiment line
                fig.add_trace(go.Scatter(
                    x=df_correlation['date'],
                    y=df_correlation['avg_sentiment'],
                    name='Average Sentiment',
                    line=dict(color='#3b82f6')
                ))
                
                # Add interaction count line
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
            except Exception as e:
                log_error(e, "Sentiment correlation visualization")
                st.error("Failed to load sentiment correlation data")
        
        with tab2:
            # Sentiment Volatility by Customer
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
            try:
                volatility_data = execute_query(volatility_query)
                df_volatility = pd.DataFrame(
                    volatility_data,
                    columns=['customer_id', 'avg_sentiment', 'sentiment_volatility', 'interaction_count']
                )
                
                # Create scatter plot
                fig = px.scatter(
                    df_volatility,
                    x='avg_sentiment',
                    y='sentiment_volatility',
                    size='interaction_count',
                    hover_data=['customer_id'],
                    title='Customer Sentiment Volatility vs. Average',
                    labels={
                        'avg_sentiment': 'Average Sentiment',
                        'sentiment_volatility': 'Sentiment Volatility',
                        'interaction_count': 'Interaction Count'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Sentiment volatility visualization")
                st.error("Failed to load sentiment volatility data")
        
        with tab3:
            raw_data_query = """
                SELECT 
                    customer_id,
                    interaction_date,
                    interaction_type,
                    sentiment_score
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                ORDER BY interaction_date DESC
                LIMIT 1000;
            """
            try:
                raw_data = execute_query(raw_data_query)
                df_raw = pd.DataFrame(raw_data)
                st.dataframe(df_raw)
            except Exception as e:
                log_error(e, "Raw data display")
                st.error("Failed to load raw data")
    
    except Exception as e:
        log_error(e, "Sentiment page rendering")
        st.error("An error occurred while rendering the sentiment analytics page") 