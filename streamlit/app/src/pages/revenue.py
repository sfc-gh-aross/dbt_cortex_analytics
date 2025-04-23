import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_revenue_page():
    """Render the Revenue Analytics workspace."""
    try:
        # Page header
        st.title("Revenue Analytics Dashboard")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Revenue Metrics
        with col1:
            st.subheader("Revenue Metrics")
            revenue_query = """
                SELECT 
                    ROUND(SUM(revenue_amount), 2) as total_revenue,
                    ROUND(AVG(revenue_amount), 2) as avg_revenue,
                    ROUND(SUM(revenue_amount) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
                FROM ANALYTICS.FACT_REVENUE
                WHERE revenue_date >= DATEADD(day, -30, CURRENT_DATE());
            """
            try:
                revenue_data = execute_query(revenue_query)
                metrics = revenue_data[0]
                
                # Display metrics in cards
                st.metric("Total Revenue", f"${metrics['total_revenue']:,.2f}")
                st.metric("Average Revenue", f"${metrics['avg_revenue']:,.2f}")
                st.metric("Revenue per Customer", f"${metrics['revenue_per_customer']:,.2f}")
            except Exception as e:
                log_error(e, "Revenue metrics visualization")
                st.error("Failed to load revenue metrics")
        
        # Revenue Growth
        with col2:
            st.subheader("Revenue Growth")
            growth_query = """
                SELECT 
                    DATE_TRUNC('month', revenue_date) as month,
                    ROUND(SUM(revenue_amount), 2) as monthly_revenue,
                    ROUND(SUM(revenue_amount) * 100.0 / LAG(SUM(revenue_amount)) OVER (ORDER BY DATE_TRUNC('month', revenue_date)), 2) as growth_rate
                FROM ANALYTICS.FACT_REVENUE
                GROUP BY month
                ORDER BY month;
            """
            try:
                growth_data = execute_query(growth_query)
                df_growth = pd.DataFrame(growth_data)
                
                # Create line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_growth['month'],
                    y=df_growth['monthly_revenue'],
                    mode='lines+markers',
                    name='Monthly Revenue',
                    line=dict(color='#3b82f6')
                ))
                fig.add_trace(go.Scatter(
                    x=df_growth['month'],
                    y=df_growth['growth_rate'],
                    mode='lines+markers',
                    name='Growth Rate',
                    line=dict(color='#10b981'),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title='Monthly Revenue and Growth',
                    yaxis_title='Revenue ($)',
                    yaxis2=dict(
                        title='Growth Rate (%)',
                        overlaying='y',
                        side='right'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Revenue growth visualization")
                st.error("Failed to load revenue growth data")
        
        # Customer Segments
        with col3:
            st.subheader("Customer Segments")
            segments_query = """
                SELECT 
                    customer_segment,
                    ROUND(SUM(revenue_amount), 2) as segment_revenue,
                    ROUND(AVG(revenue_amount), 2) as avg_revenue,
                    COUNT(DISTINCT customer_id) as customer_count
                FROM ANALYTICS.FACT_REVENUE
                GROUP BY customer_segment
                ORDER BY segment_revenue DESC;
            """
            try:
                segments_data = execute_query(segments_query)
                df_segments = pd.DataFrame(segments_data)
                
                # Create pie chart
                fig = px.pie(
                    df_segments,
                    values='segment_revenue',
                    names='customer_segment',
                    title='Revenue by Customer Segment',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Customer segments visualization")
                st.error("Failed to load customer segments data")
        
        # Detailed Analysis Section
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "Revenue Streams",
            "Customer Lifetime Value",
            "Value vs. Sentiment",
            "Raw Data"
        ])
        
        with tab1:
            streams_query = """
                SELECT 
                    revenue_stream,
                    DATE_TRUNC('month', revenue_date) as month,
                    ROUND(SUM(revenue_amount), 2) as stream_revenue,
                    ROUND(SUM(revenue_amount) * 100.0 / SUM(SUM(revenue_amount)) OVER (PARTITION BY DATE_TRUNC('month', revenue_date)), 2) as revenue_share
                FROM ANALYTICS.FACT_REVENUE
                GROUP BY revenue_stream, month
                ORDER BY month, stream_revenue DESC;
            """
            try:
                streams_data = execute_query(streams_query)
                df_streams = pd.DataFrame(streams_data)
                
                # Create stacked area chart
                fig = px.area(
                    df_streams,
                    x='month',
                    y='stream_revenue',
                    color='revenue_stream',
                    title='Revenue Streams Over Time',
                    labels={
                        'month': 'Month',
                        'stream_revenue': 'Revenue ($)',
                        'revenue_stream': 'Revenue Stream'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Revenue streams analysis")
                st.error("Failed to load revenue streams data")
        
        with tab2:
            clv_query = """
                SELECT 
                    customer_segment,
                    ROUND(AVG(customer_lifetime_value), 2) as avg_clv,
                    ROUND(AVG(customer_tenure_months), 2) as avg_tenure,
                    ROUND(AVG(monthly_revenue), 2) as avg_monthly_revenue
                FROM ANALYTICS.FACT_CUSTOMER_LIFETIME_VALUE
                GROUP BY customer_segment
                ORDER BY avg_clv DESC;
            """
            try:
                clv_data = execute_query(clv_query)
                df_clv = pd.DataFrame(clv_data)
                
                # Create bar chart
                fig = px.bar(
                    df_clv,
                    x='customer_segment',
                    y=['avg_clv', 'avg_monthly_revenue'],
                    title='Customer Lifetime Value Analysis',
                    barmode='group',
                    labels={
                        'customer_segment': 'Customer Segment',
                        'value': 'Value ($)',
                        'variable': 'Metric'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Customer lifetime value analysis")
                st.error("Failed to load customer lifetime value data")
        
        with tab3:
            st.subheader("Value vs. Sentiment Correlation")
            correlation_query = """
                SELECT 
                    cb.lifetime_value,
                    cps.avg_sentiment,
                    cb.persona
                FROM ANALYTICS.CUSTOMER_BASE cb
                JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps USING (customer_id)
                ORDER BY lifetime_value DESC;
            """
            try:
                correlation_data = execute_query(correlation_query)
                df_correlation = pd.DataFrame(correlation_data)
                
                # Create scatter plot with trend line
                fig = px.scatter(
                    df_correlation,
                    x='lifetime_value',
                    y='avg_sentiment',
                    color='persona',
                    trendline="ols",
                    title='Value vs. Sentiment Correlation',
                    labels={
                        'lifetime_value': 'Lifetime Value ($)',
                        'avg_sentiment': 'Average Sentiment',
                        'persona': 'Customer Persona'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display correlation coefficient
                correlation = df_correlation['lifetime_value'].corr(df_correlation['avg_sentiment'])
                st.metric("Correlation Coefficient", f"{correlation:.3f}")
            except Exception as e:
                log_error(e, "Value vs. sentiment correlation visualization")
                st.error("Failed to load value vs. sentiment correlation data")
        
        with tab4:
            raw_data_query = """
                SELECT 
                    revenue_id,
                    customer_id,
                    revenue_date,
                    revenue_amount,
                    revenue_stream,
                    customer_segment
                FROM ANALYTICS.FACT_REVENUE
                ORDER BY revenue_date DESC
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
        log_error(e, "Revenue page rendering")
        st.error("An error occurred while rendering the revenue analytics page") 