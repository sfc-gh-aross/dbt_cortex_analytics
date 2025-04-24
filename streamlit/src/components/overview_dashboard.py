import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

def load_query(query_name):
    """Load SQL query from file."""
    query_path = os.path.join('src', 'queries', 'overview_dashboard', f'{query_name}.sql')
    with open(query_path, 'r') as f:
        return f.read()

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
    
    # Load and execute KPI queries
    kpi_query = load_query('kpi_queries')
    kpi_params = {
        'start_date': start_date,
        'end_date': end_date,
        'value_segment_filter': f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else "",
        'persona_filter': f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""
    }
    
    # Execute KPI query
    params = []
    if selected_value_segments:
        params.extend(selected_value_segments)
    if selected_personas:
        params.extend(selected_personas)
    
    kpi_results = conn.cursor().execute(kpi_query, params).fetchall()
    
    # Display KPIs
    with col1:
        st.metric(
            label="Average Sentiment",
            value=f"{kpi_results[0][0]:.2f}" if kpi_results[0][0] is not None else "N/A",
            delta=f"{kpi_results[0][2]:.2f}" if kpi_results[0][2] is not None else None
        )
    
    with col2:
        st.metric(
            label="Total Interactions",
            value=kpi_results[1][0] if kpi_results[1][0] is not None else "N/A",
            delta=kpi_results[1][2] if kpi_results[1][2] is not None else None
        )
    
    with col3:
        st.metric(
            label="High Churn Risk",
            value=f"{kpi_results[2][0]:.1f}%" if kpi_results[2][0] is not None else "N/A",
            delta=f"{kpi_results[2][2]:.1f}%" if kpi_results[2][2] is not None else None
        )
    
    with col4:
        st.metric(
            label="Average Product Rating",
            value=f"{kpi_results[3][0]:.1f}" if kpi_results[3][0] is not None else "N/A",
            delta=f"{kpi_results[3][2]:.1f}" if kpi_results[3][2] is not None else None
        )
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    # Sentiment Trend Chart
    with col1:
        st.subheader("Sentiment Trend")
        sentiment_query = load_query('sentiment_queries')
        sentiment_params = {
            'start_date': start_date,
            'end_date': end_date,
            'value_segment_filter': kpi_params['value_segment_filter'],
            'persona_filter': kpi_params['persona_filter']
        }
        
        sentiment_data = pd.DataFrame(
            conn.cursor().execute(sentiment_query, params).fetchall(),
            columns=['month', 'avg_sentiment']
        )
        
        fig = px.line(
            sentiment_data,
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
        sentiment_dist_query = load_query('sentiment_queries')
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
        churn_query = load_query('churn_queries')
        churn_data = pd.DataFrame(
            conn.cursor().execute(churn_query, params).fetchall(),
            columns=['churn_risk', 'count']
        )
        
        fig = px.bar(
            churn_data,
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
    
    # Revenue Trend
    with col2:
        st.subheader("Revenue Trend")
        revenue_query = load_query('revenue_trend')
        revenue_data = pd.DataFrame(
            conn.cursor().execute(revenue_query).fetchall(),
            columns=['month', 'total_revenue', 'active_customers']
        )
        
        fig = px.line(
            revenue_data,
            x='month',
            y='total_revenue',
            title='Monthly Revenue Trend',
            labels={'month': 'Month', 'total_revenue': 'Total Revenue'}
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Revenue",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True) 