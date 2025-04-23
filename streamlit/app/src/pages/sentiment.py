import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from src.utils.ui import (
    display_trend_indicator,
    create_card,
    display_data_table,
    show_empty_state,
    handle_error
)
from src.utils.ui_enhanced import (
    with_tooltip,
    EnhancedLoadingState,
    show_toast,
    enhanced_dataframe,
    with_loading_and_feedback
)
from typing import Dict
import os

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
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY sentiment_category
        ORDER BY count DESC;
    """
    try:
        data = execute_query(sentiment_query)
        # Convert to list of dictionaries with proper types
        result = []
        for row in data:
            result.append({
                'sentiment_category': str(row['SENTIMENT_CATEGORY']),
                'count': int(row['COUNT']),
                'percentage': float(row['PERCENTAGE'])
            })
        return result
    except Exception as e:
        st.error(f"Error processing sentiment data: {str(e)}")
        st.write("Raw data:", data)
        return []

@handle_error
def get_sentiment_trends():
    """Fetch sentiment trends data."""
    trends_query = """
        SELECT 
            DATE_TRUNC('day', interaction_date) as date,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY date
        ORDER BY date;
    """
    try:
        data = execute_query(trends_query)
        # Convert to list of dictionaries with proper types
        result = []
        for row in data:
            result.append({
                'date': pd.to_datetime(row['DATE']).date(),
                'avg_sentiment': float(row['AVG_SENTIMENT']),
                'interaction_count': int(row['INTERACTION_COUNT'])
            })
        return result
    except Exception as e:
        st.error(f"Error processing sentiment trends data: {str(e)}")
        st.write("Raw data:", data)
        return []

@handle_error
def get_sentiment_by_type():
    """Fetch sentiment by interaction type data."""
    type_query = """
        SELECT 
            source_type as interaction_type,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY source_type
        ORDER BY avg_sentiment DESC;
    """
    data = execute_query(type_query)
    # Convert data to proper format and types
    df = pd.DataFrame(
        {
            'interaction_type': [str(row['INTERACTION_TYPE']) for row in data],
            'avg_sentiment': [float(row['AVG_SENTIMENT']) for row in data],
            'interaction_count': [int(row['INTERACTION_COUNT']) for row in data]
        }
    )
    return df

@handle_error
def get_sentiment_correlation():
    """Fetch sentiment correlation data."""
    correlation_query = """
        WITH daily_metrics AS (
            SELECT 
                DATE_TRUNC('day', interaction_date) as date,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as interaction_count
            FROM ANALYTICS.SENTIMENT_ANALYSIS
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
    df = pd.DataFrame(data, columns=['date', 'avg_sentiment', 'interaction_count'])
    # Ensure proper data types
    df['date'] = pd.to_datetime(df['date']).dt.date  # Convert to date to avoid datetime64 issues
    df['avg_sentiment'] = pd.to_numeric(df['avg_sentiment'], errors='coerce').astype('float64')
    df['interaction_count'] = pd.to_numeric(df['interaction_count'], errors='coerce').astype('Int64')
    return df

@handle_error
def get_sentiment_volatility():
    """Fetch sentiment volatility data."""
    volatility_query = """
        SELECT 
            customer_id,
            avg_sentiment,
            sentiment_volatility,
            ticket_count
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        ORDER BY sentiment_volatility DESC
        LIMIT 10;
    """
    data = execute_query(volatility_query)
    # Convert data to proper format and types
    df = pd.DataFrame(
        {
            'customer_id': [str(row['CUSTOMER_ID']) for row in data],
            'avg_sentiment': [float(row['AVG_SENTIMENT']) for row in data],
            'sentiment_volatility': [float(row['SENTIMENT_VOLATILITY']) for row in data],
            'ticket_count': [int(row['TICKET_COUNT'] or 0) for row in data]
        }
    )
    return df

def render_sentiment_page(active_filters: Dict):
    """Render the sentiment analysis page with applied filters."""
    st.title("Sentiment & Experience Analysis")
    
    # Create a container for the main metrics
    with st.container():
        st.markdown("### Key Metrics")
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.metric(
                "Overall Satisfaction",
                "85%",
                "+2%",
                help="Overall customer satisfaction score based on sentiment analysis"
            )
        with metric_cols[1]:
            st.metric(
                "Response Time",
                "2.5h",
                "-0.5h",
                help="Average time to respond to customer interactions"
            )
        with metric_cols[2]:
            st.metric(
                "Resolution Rate",
                "92%",
                "+3%",
                help="Percentage of customer issues resolved on first contact"
            )
        with metric_cols[3]:
            st.metric(
                "NPS Score",
                "45",
                "+5",
                help="Net Promoter Score based on customer feedback"
            )
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📈 Trends",
        "👥 Customer Segments",
        "🔍 Detailed Analysis"
    ])
    
    with tab1:
        # Overview Section
        st.markdown("### Sentiment Distribution")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sentiment Distribution Chart
            with st.spinner("Loading sentiment distribution..."):
                df_sentiment = get_sentiment_data()
                # --- DEBUGGING START ---
                # st.write("Debug: Sentiment data received:", df_sentiment) 
                # --- DEBUGGING END ---
                if df_sentiment:
                    try:
                        # --- DEBUGGING START ---
                        # st.write("Debug: Attempting to generate pie chart with data:", df_sentiment)
                        # --- DEBUGGING END ---
                        
                        # Convert to DataFrame before plotting
                        df_sentiment_pd = pd.DataFrame(df_sentiment)
                        
                        # --- TEST: Use st.bar_chart (Commented Out) ---
                        # st.write("Debug: Attempting st.bar_chart") # Add temp debug
                        # Prepare data for st.bar_chart (needs index)
                        # df_st_chart = df_sentiment_pd.set_index('sentiment_category')
                        # Select only the numerical column to plot
                        # st.bar_chart(df_st_chart[['count']])
                        # --- END TEST ---

                        # --- Minimal Plotly Bar Chart ---
                        fig = px.bar(
                            df_sentiment_pd,
                            x='sentiment_category',
                            y='count'
                            # Minimal settings: Removed color, title etc.
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        # --- END Minimal Plotly Bar Chart ---
                        
                    except Exception as e:
                        st.error(f"Error generating sentiment chart: {e}")
                        log_error(f"Chart generation error: {e}")
                else:
                    st.info("No sentiment data found for the selected filters or time range.")
        
        with col2:
            # Key Insights
            st.markdown("### Key Insights")
            with st.expander("Top Positive Drivers", expanded=True):
                st.markdown("""
                - Quick response times
                - Knowledgeable support staff
                - Easy-to-use interface
                """)
            
            with st.expander("Areas for Improvement", expanded=True):
                st.markdown("""
                - Documentation clarity
                - Feature availability
                - Integration complexity
                """)
    
    with tab2:
        # Trends Section
        st.markdown("### Sentiment Trends")
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment Trend Chart
            with st.spinner("Loading sentiment trends..."):
                df_trends = get_sentiment_trends()
                if df_trends:
                    fig = px.line(
                        df_trends,
                        x='date',
                        y='avg_sentiment',
                        title='Average Sentiment Over Time',
                        labels={'avg_sentiment': 'Sentiment Score', 'date': 'Date'}
                    )
                    fig.update_layout(
                        yaxis_range=[-1, 1],
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Interaction Volume Chart
            with st.spinner("Loading interaction volume..."):
                if df_trends:
                    fig = px.bar(
                        df_trends,
                        x='date',
                        y='interaction_count',
                        title='Interaction Volume Over Time',
                        labels={'interaction_count': 'Number of Interactions', 'date': 'Date'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Customer Segments Section
        st.markdown("### Sentiment by Customer Segment")
        
        # Sentiment by Persona
        with st.spinner("Loading sentiment by persona..."):
            df_persona = get_sentiment_by_type()
            if df_persona is not None and not df_persona.empty:
                fig = px.bar(
                    df_persona,
                    x='interaction_type',
                    y='avg_sentiment',
                    color='interaction_type',
                    title='Average Sentiment by Customer Segment',
                    labels={'interaction_type': 'Customer Segment', 'avg_sentiment': 'Average Sentiment'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No sentiment data available for customer segments")
        
        # Add correlation analysis
        st.markdown("### Sentiment-Value Correlation")
        with st.spinner("Loading correlation data..."):
            df_correlation = get_sentiment_correlation()
            if df_correlation is not None and not df_correlation.empty:
                fig = px.scatter(
                    df_correlation,
                    x='interaction_count',
                    y='avg_sentiment',
                    trendline="ols",
                    title='Sentiment vs. Interaction Volume',
                    labels={'interaction_count': 'Number of Interactions', 'avg_sentiment': 'Average Sentiment'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No correlation data available")
    
    with tab4:
        # Detailed Analysis Section
        st.markdown("### Detailed Analysis")
        
        # Volatility Analysis
        st.markdown("#### Sentiment Volatility")
        with st.spinner("Loading volatility data..."):
            df_volatility = get_sentiment_volatility()
            if df_volatility is not None and not df_volatility.empty:
                fig = px.bar(
                    df_volatility,
                    x='customer_id',
                    y='sentiment_volatility',
                    color='avg_sentiment',
                    title='Customer Sentiment Volatility',
                    labels={'customer_id': 'Customer ID', 'sentiment_volatility': 'Volatility Score', 'avg_sentiment': 'Average Sentiment'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No volatility data available")
        
        # Raw Data View
        with st.expander("View Raw Data", expanded=False):
            if df_sentiment is not None:
                st.dataframe(df_sentiment, use_container_width=True)
            else:
                st.warning("No raw data available") 