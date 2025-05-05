import streamlit as st
import pandas as pd
import plotly.express as px
import os
from data_loader import load_query, execute_query

def load_sentiment_query(query_name):
    """Load SQL query from sentiment experience analysis directory."""
    query_path = os.path.join('src', 'queries', 'sentiment_experience_analysis', f'{query_name}.sql')
    with open(query_path, 'r') as f:
        return f.read()

@st.cache_data(ttl=300)
def get_sentiment_over_time(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Get sentiment over time data."""
    query = load_query('sentiment_over_time', 'sentiment_experience_analysis')
    params = []
    if selected_value_segments:
        params.extend(selected_value_segments)
    if selected_personas:
        params.extend(selected_personas)
    return pd.DataFrame(
        execute_query(conn, query, params),
        columns=['date', 'interaction_source', 'avg_sentiment']
    )

@st.cache_data(ttl=300)
def get_sentiment_distribution(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Get sentiment distribution by source data."""
    query = load_query('sentiment_distribution_by_source', 'sentiment_experience_analysis')
    params = []
    if selected_value_segments:
        params.extend(selected_value_segments)
    if selected_personas:
        params.extend(selected_personas)
    return pd.DataFrame(
        execute_query(conn, query, params),
        columns=['interaction_source', 'sentiment_bucket', 'interaction_count']
    )

@st.cache_data(ttl=300)
def get_volatility_trend(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Get volatility vs trend data."""
    query = load_query('volatility_vs_trend', 'sentiment_experience_analysis')
    params = []
    if selected_value_segments:
        params.extend(selected_value_segments)
    if selected_personas:
        params.extend(selected_personas)
    return pd.DataFrame(
        execute_query(conn, query, params),
        columns=['customer_id', 'avg_sentiment', 'sentiment_volatility', 'interaction_count']
    )

@st.cache_data(ttl=300)
def get_interaction_type_sentiment(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Get interaction type sentiment data."""
    query = load_query('interaction_type_sentiment', 'sentiment_experience_analysis')
    params = []
    if selected_value_segments:
        params.extend(selected_value_segments)
    if selected_personas:
        params.extend(selected_personas)
    return pd.DataFrame(
        execute_query(conn, query, params),
        columns=['interaction_type', 'avg_sentiment', 'interaction_count']
    )

def render_sentiment_experience_analysis(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Render the Sentiment & Experience Analysis tab with charts.
    
    Args:
        conn: Snowflake connection object
        start_date: Start date for filtering
        end_date: End date for filtering
        selected_value_segments: List of selected value segments
        selected_personas: List of selected personas
    """
    st.header("Sentiment & Experience Analysis")
    
    # Load data with loading spinners
    with st.spinner("Loading sentiment data..."):
        sentiment_over_time = get_sentiment_over_time(conn, start_date, end_date, selected_value_segments, selected_personas)
        sentiment_distribution = get_sentiment_distribution(conn, start_date, end_date, selected_value_segments, selected_personas)
        volatility_trend = get_volatility_trend(conn, start_date, end_date, selected_value_segments, selected_personas)
        interaction_type_sentiment = get_interaction_type_sentiment(conn, start_date, end_date, selected_value_segments, selected_personas)
    
    # Sentiment Over Time Chart
    st.subheader("Sentiment Over Time")
    if sentiment_over_time.empty:
        st.info("No sentiment data available for the selected period.")
    else:
        # Multi-select for interaction sources
        available_sources = sentiment_over_time['interaction_source'].unique()
        selected_sources = st.multiselect(
            "Select Interaction Sources",
            options=available_sources,
            default=available_sources[:2],
            help="Choose which interaction sources to display in the chart"
        )
        
        filtered_data = sentiment_over_time[sentiment_over_time['interaction_source'].isin(selected_sources)]
        fig = px.line(
            filtered_data,
            x='date',
            y='avg_sentiment',
            color='interaction_source',
            title='Sentiment Trend by Source',
            labels={'date': 'Date', 'avg_sentiment': 'Average Sentiment Score'}
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Average Sentiment Score",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment Distribution by Source
    st.subheader("Sentiment Distribution by Source")
    if sentiment_distribution.empty:
        st.info("No sentiment distribution data available.")
    else:
        # Create three columns for the bar charts
        cols = st.columns(3)
        sources = sentiment_distribution['interaction_source'].unique()
        
        for i, source in enumerate(sources):
            with cols[i % 3]:
                source_data = sentiment_distribution[sentiment_distribution['interaction_source'] == source]
                fig = px.bar(
                    source_data,
                    x='sentiment_bucket',
                    y='interaction_count',
                    title=f'Sentiment Distribution - {source}',
                    labels={'sentiment_bucket': 'Sentiment', 'interaction_count': 'Count'}
                )
                fig.update_layout(
                    xaxis_title="Sentiment",
                    yaxis_title="Count",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Volatility vs Trend Chart
    st.subheader("Sentiment Volatility vs Trend")
    if volatility_trend.empty:
        st.info("No volatility data available for the selected period.")
    else:
        fig = px.scatter(
            volatility_trend,
            x='avg_sentiment',
            y='sentiment_volatility',
            size='interaction_count',
            hover_data=['customer_id'],
            title='Customer Sentiment Volatility vs Average Sentiment',
            labels={'avg_sentiment': 'Average Sentiment', 'sentiment_volatility': 'Sentiment Volatility'}
        )
        fig.update_layout(
            xaxis_title="Average Sentiment",
            yaxis_title="Sentiment Volatility",
            hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Interaction Type Sentiment
    st.subheader("Interaction Type Sentiment")
    if interaction_type_sentiment.empty:
        st.info("No interaction type sentiment data available.")
    else:
        fig = px.bar(
            interaction_type_sentiment,
            x='interaction_type',
            y='avg_sentiment',
            title='Average Sentiment by Interaction Type',
            labels={'interaction_type': 'Interaction Type', 'avg_sentiment': 'Average Sentiment'}
        )
        fig.update_layout(
            xaxis_title="Interaction Type",
            yaxis_title="Average Sentiment",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True) 