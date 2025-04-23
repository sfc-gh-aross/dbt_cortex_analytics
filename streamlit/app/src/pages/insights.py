import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from src.utils.ui import LoadingState, handle_error, show_empty_state, show_error, show_warning
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import numpy as np

@handle_error
def get_interaction_summaries():
    """Fetch customer interaction summaries."""
    summary_query = """
        SELECT 
            customer_id,
            customer_summary
        FROM ANALYTICS.INSIGHT_SUMMARIES
        ORDER BY customer_id;
    """
    data = execute_query(summary_query)
    # Convert data to proper format and types
    df = pd.DataFrame(
        {
            'customer_id': [str(row['customer_id']) for row in data],
            'customer_summary': [str(row['customer_summary']) for row in data]
        }
    )
    return df

@handle_error
def get_sentiment_history():
    """Fetch customer sentiment history."""
    sentiment_query = """
        SELECT 
            customer_id,
            sentiment_history,
            avg_sentiment,
            sentiment_trend
        FROM ANALYTICS.SENTIMENT_TRENDS
        ORDER BY customer_id;
    """
    data = execute_query(sentiment_query)
    return pd.DataFrame(data, columns=['customer_id', 'sentiment_history', 'avg_sentiment', 'sentiment_trend'])

@handle_error
def get_ticket_patterns():
    """Fetch customer support ticket patterns."""
    ticket_query = """
        SELECT 
            customer_id,
            ticket_count,
            ARRAY_TO_STRING(ticket_categories, ', ') as categories,
            ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
        FROM ANALYTICS.TICKET_PATTERNS
        ORDER BY ticket_count DESC;
    """
    data = execute_query(ticket_query)
    return pd.DataFrame(data, columns=['customer_id', 'ticket_count', 'categories', 'priorities'])

@handle_error
def get_sentiment_trends():
    """Fetch customer sentiment trends."""
    trend_query = """
        SELECT 
            customer_id,
            sentiment_trend,
            avg_sentiment,
            sentiment_volatility
        FROM ANALYTICS.SENTIMENT_TRENDS
        ORDER BY sentiment_trend DESC;
    """
    data = execute_query(trend_query)
    return pd.DataFrame(data, columns=['customer_id', 'sentiment_trend', 'avg_sentiment', 'sentiment_volatility'])

@handle_error
def get_sentiment_volatility():
    """Fetch customer sentiment volatility."""
    volatility_query = """
        SELECT 
            customer_id,
            sentiment_volatility,
            avg_sentiment,
            sentiment_trend
        FROM ANALYTICS.SENTIMENT_TRENDS
        ORDER BY sentiment_volatility DESC;
    """
    data = execute_query(volatility_query)
    return pd.DataFrame(data, columns=['customer_id', 'sentiment_volatility', 'avg_sentiment', 'sentiment_trend'])

def render_insights_page():
    """Render the insights and summaries page."""
    try:
        st.header("Insights & Summaries")
        
        # Create tabs for different insights sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Interaction Summaries",
            "Sentiment History",
            "Support Patterns",
            "Sentiment Trends",
            "Sentiment Volatility"
        ])
        
        with tab1:
            st.subheader("Customer Interaction Summaries")
            with LoadingState("Loading interaction summaries..."):
                df_summaries = get_interaction_summaries()
                if df_summaries is not None and not df_summaries.empty:
                    # Create word cloud from summaries
                    all_summaries = ' '.join(df_summaries['customer_summary'].astype(str))
                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_summaries)
                    
                    # Display word cloud
                    st.image(wordcloud.to_array(), use_column_width=True)
                    
                    # Display summary table
                    st.dataframe(df_summaries)
                else:
                    show_empty_state("No interaction summaries available")
        
        with tab2:
            st.subheader("Sentiment History")
            with LoadingState("Loading sentiment history..."):
                df_history = get_sentiment_history()
                if df_history is not None and not df_history.empty:
                    # Create line chart
                    fig = px.line(
                        df_history,
                        x='customer_id',
                        y='avg_sentiment',
                        title='Average Sentiment by Customer'
                    )
                    st.plotly_chart(fig)
                else:
                    show_empty_state("No sentiment history available")
        
        with tab3:
            st.subheader("Support Patterns")
            with LoadingState("Loading support patterns..."):
                df_patterns = get_ticket_patterns()
                if df_patterns is not None and not df_patterns.empty:
                    # Create bar chart
                    fig = px.bar(
                        df_patterns,
                        x='customer_id',
                        y='ticket_count',
                        title='Ticket Count by Customer'
                    )
                    st.plotly_chart(fig)
                else:
                    show_empty_state("No support patterns available")
        
        with tab4:
            st.subheader("Sentiment Trends")
            with LoadingState("Loading sentiment trends..."):
                df_trends = get_sentiment_trends()
                if df_trends is not None and not df_trends.empty:
                    # Create line chart
                    fig = px.line(
                        df_trends,
                        x='customer_id',
                        y='sentiment_trend',
                        title='Sentiment Trend by Customer'
                    )
                    st.plotly_chart(fig)
                else:
                    show_empty_state("No sentiment trends available")
        
        with tab5:
            st.subheader("Sentiment Volatility")
            with LoadingState("Loading sentiment volatility..."):
                df_volatility = get_sentiment_volatility()
                if df_volatility is not None and not df_volatility.empty:
                    # Create line chart
                    fig = px.line(
                        df_volatility,
                        x='customer_id',
                        y='sentiment_volatility',
                        title='Sentiment Volatility by Customer'
                    )
                    st.plotly_chart(fig)
                else:
                    show_empty_state("No sentiment volatility data available")
                    
    except Exception as e:
        show_error(f"An error occurred while rendering the insights page: {str(e)}")
        log_error(e, "Insights page rendering") 