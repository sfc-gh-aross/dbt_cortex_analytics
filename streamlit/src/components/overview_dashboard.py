import streamlit as st
import pandas as pd
import plotly.express as px
from ..queries.overview_queries import (
    get_sentiment_query,
    get_interactions_query,
    get_churn_risk_query,
    get_rating_query,
    get_sentiment_trend_query,
    get_sentiment_dist_query,
    get_churn_risk_breakdown_query
)
from ..utils.db import run_query

def render_overview_dashboard(start_date, end_date, selected_value_segments, selected_personas):
    st.header("Overview Dashboard")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Average Sentiment KPI
    with col1:
        sentiment_query = get_sentiment_query(start_date, end_date, selected_value_segments, selected_personas)
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
        interactions_query = get_interactions_query(start_date, end_date, selected_value_segments, selected_personas)
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
        churn_risk_query = get_churn_risk_query(start_date, end_date, selected_value_segments, selected_personas)
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
        rating_query = get_rating_query(start_date, end_date, selected_value_segments, selected_personas)
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
        sentiment_trend_query = get_sentiment_trend_query(start_date, end_date, selected_value_segments, selected_personas)
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
        sentiment_dist_query = get_sentiment_dist_query(start_date, end_date, selected_value_segments, selected_personas)
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
        churn_risk_breakdown_query = get_churn_risk_breakdown_query(start_date, end_date, selected_value_segments, selected_personas)
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