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
        FROM ANALYTICS.SENTIMENT_ANALYSIS
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
            source_type as interaction_type,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY source_type
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
    return pd.DataFrame(data, columns=['date', 'avg_sentiment', 'interaction_count'])

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
    return pd.DataFrame(data, columns=['customer_id', 'avg_sentiment', 'sentiment_volatility', 'ticket_count'])

def render_sentiment_page(active_filters: Dict):
    """Render the sentiment analysis page with applied filters."""
    st.title("Sentiment & Experience Analysis")
    
    # Display active filters summary
    st.markdown("### Applied Filters")
    filter_cols = st.columns(3)
    
    with filter_cols[0]:
        if "date_range" in active_filters:
            start_date, end_date = active_filters["date_range"]
            st.metric("Date Range", f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    with filter_cols[1]:
        if "personas" in active_filters:
            personas = active_filters["personas"]
            st.metric("Customer Personas", ", ".join(personas) if personas else "All")
    
    with filter_cols[2]:
        if "channels" in active_filters:
            channels = active_filters["channels"]
            st.metric("Channels", ", ".join(channels) if channels else "All")
    
    # Main content
    st.markdown("---")
    
    # Example sentiment metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Overall Sentiment", "Positive", "+5%")
    with metric_cols[1]:
        st.metric("Customer Satisfaction", "85%", "+2%")
    with metric_cols[2]:
        st.metric("Response Time", "2.5h", "-0.5h")
    with metric_cols[3]:
        st.metric("Resolution Rate", "92%", "+3%")
    
    # Example sentiment trends chart (replace with actual data)
    st.markdown("### Sentiment Trends")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        sentiment_scores = [0.7, 0.8, 0.75, 0.85, 0.9, 0.88, 0.92] * (len(date_range) // 7 + 1)
        sentiment_scores = sentiment_scores[:len(date_range)]  # Ensure same length
        
        chart_data = pd.DataFrame({
            'Date': date_range,
            'Sentiment Score': sentiment_scores
        })
        st.line_chart(chart_data.set_index('Date'))
    
    # Example sentiment breakdown by persona (replace with actual data)
    st.markdown("### Sentiment by Customer Persona")
    
    # Define all possible personas
    all_personas = ["Enterprise", "SMB", "Startup", "Individual"]
    
    # Get selected personas from filters
    selected_personas = active_filters.get("personas", ["All"])
    
    # If "All" is selected or no specific personas are selected, show all personas
    if "All" in selected_personas or not selected_personas:
        display_personas = all_personas
    else:
        display_personas = selected_personas
    
    # Create persona data
    persona_data = pd.DataFrame({
        'Persona': display_personas,
        'Positive': [85, 75, 90, 80][:len(display_personas)],
        'Neutral': [10, 15, 5, 15][:len(display_personas)],
        'Negative': [5, 10, 5, 5][:len(display_personas)]
    })
    
    # Display the chart
    st.bar_chart(persona_data.set_index('Persona'))
    
    # Add a note if specific personas are selected
    if "All" not in selected_personas and selected_personas:
        st.info(f"Showing data for selected personas: {', '.join(selected_personas)}")

    try:
        # Page header with tooltip
        st.header("Sentiment & Experience Analytics")
        st.markdown("Analyze customer sentiment across different interaction types and time periods")
        
        # Key Metrics Section
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        # Overall Sentiment Score
        with col1:
            sentiment_metrics_query = """
                SELECT 
                    ROUND(AVG(sentiment_score), 2) as current_sentiment,
                    ROUND(AVG(CASE WHEN interaction_date >= DATEADD('month', -1, CURRENT_DATE()) THEN sentiment_score END), 2) as recent_sentiment
                FROM ANALYTICS.SENTIMENT_ANALYSIS;
            """
            metrics_data = execute_query(sentiment_metrics_query)
            if metrics_data and len(metrics_data) > 0:
                current_sentiment = metrics_data[0][0] or 0
                previous_sentiment = metrics_data[0][1] or 0
                display_trend_indicator(
                    current_value=current_sentiment,
                    previous_value=previous_sentiment,
                    label="Overall Sentiment Score",
                    format="{:.2f}"
                )
        
        # Positive Sentiment Rate
        with col2:
            positive_rate_query = """
                WITH sentiment_counts AS (
                    SELECT 
                        COUNT(CASE WHEN sentiment_score > 0.3 THEN 1 END) as positive_count,
                        COUNT(*) as total_count
                    FROM ANALYTICS.SENTIMENT_ANALYSIS
                    WHERE interaction_date >= DATEADD('month', -1, CURRENT_DATE())
                )
                SELECT 
                    ROUND(100.0 * positive_count / NULLIF(total_count, 0), 1) as positive_rate
                FROM sentiment_counts;
            """
            rate_data = execute_query(positive_rate_query)
            if rate_data and len(rate_data) > 0:
                current_positive = rate_data[0][0] or 0
                display_trend_indicator(
                    current_value=current_positive,
                    previous_value=0,  # No previous value available
                    label="Positive Sentiment Rate",
                    format="{:.1f}%"
                )
        
        # Sentiment Volatility
        with col3:
            volatility_metrics_query = """
                SELECT 
                    ROUND(AVG(sentiment_volatility), 2) as avg_volatility
                FROM ANALYTICS.SENTIMENT_TRENDS;
            """
            volatility_data = execute_query(volatility_metrics_query)
            if volatility_data and len(volatility_data) > 0:
                current_volatility = volatility_data[0][0] or 0
                display_trend_indicator(
                    current_value=current_volatility,
                    previous_value=0,  # No previous value available
                    label="Average Sentiment Volatility",
                    format="{:.2f}"
                )
        
        # Main Analysis Section
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Sentiment Distribution",
            "Trend Analysis",
            "Raw Data"
        ])
        
        with tab1:
            # Sentiment Distribution Card
            create_card(
                title="Sentiment Distribution",
                content="Distribution of customer sentiment across all interactions"
            )
            
            with st.spinner("Loading sentiment distribution..."):
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
        
        with tab2:
            # Trend Analysis Card
            create_card(
                title="Sentiment Trends",
                content="Track how customer sentiment changes over time"
            )
            
            with st.spinner("Loading sentiment trends..."):
                df_trends = get_sentiment_trends()
                if df_trends is not None and not df_trends.empty:
                    fig = px.line(
                        df_trends,
                        x='date',
                        y='avg_sentiment',
                        labels={
                            'date': 'Date',
                            'avg_sentiment': 'Average Sentiment',
                            'interaction_count': 'Interaction Count'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_empty_state("No trend data available")
        
        with tab3:
            # Raw Data Card
            create_card(
                title="Raw Data",
                content="Detailed sentiment data for further analysis"
            )
            
            with st.spinner("Loading raw data..."):
                raw_query = """
                    SELECT 
                        customer_id,
                        interaction_date,
                        source_type,
                        sentiment_score
                    FROM ANALYTICS.SENTIMENT_ANALYSIS
                    ORDER BY interaction_date DESC
                    LIMIT 1000;
                """
                raw_data = execute_query(raw_query)
                if raw_data is not None:
                    df_raw = pd.DataFrame(raw_data, columns=['customer_id', 'interaction_date', 'source_type', 'sentiment_score'])
                    display_data_table(
                        data=df_raw,
                        title="Sentiment Data",
                        height=400
                    )
                else:
                    show_empty_state("No raw data available")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Sentiment page rendering") 