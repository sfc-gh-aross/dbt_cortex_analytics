import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render_overview_dashboard(conn, start_date, end_date, selected_value_segments, selected_personas):
    """Render the Overview Dashboard tab with KPIs and charts.
    
    Args:
        conn: Snowflake connection object
        start_date: Start date for filtering
        end_date: End date for filtering
        selected_value_segments: List of selected value segments
        selected_personas: List of selected personas
    """
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
        avg_sentiment, sentiment_delta = conn.cursor().execute(sentiment_query, params).fetchone()
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
        total_interactions, interactions_delta = conn.cursor().execute(interactions_query, params).fetchone()
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
        high_risk_percentage, risk_delta = conn.cursor().execute(churn_risk_query, params).fetchone()
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
        avg_rating, rating_delta = conn.cursor().execute(rating_query, params).fetchone()
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
            conn.cursor().execute(sentiment_trend_query, params).fetchall(),
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
            conn.cursor().execute(sentiment_dist_query, params).fetchall(),
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
            conn.cursor().execute(churn_risk_breakdown_query, params).fetchall(),
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