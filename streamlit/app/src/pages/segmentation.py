import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from typing import Dict

def render_segmentation_page(active_filters: Dict):
    """Render the segmentation and value page with applied filters."""
    st.title("Segmentation & Value Analysis")
    
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
    
    # Example segmentation metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Total Segments", "8", "+2")
    with metric_cols[1]:
        st.metric("Average CLV", "$1,250", "+$150")
    with metric_cols[2]:
        st.metric("Segment Growth", "15%", "+3%")
    with metric_cols[3]:
        st.metric("Retention Rate", "85%", "+5%")
    
    # Example segment distribution (replace with actual data)
    st.markdown("### Segment Distribution")
    segment_data = pd.DataFrame({
        'Segment': ["High Value", "Medium Value", "Low Value", "At Risk"],
        'Customers': [500, 1000, 1500, 200]
    })
    st.bar_chart(segment_data.set_index('Segment'))
    
    # Example value trends (replace with actual data)
    st.markdown("### Customer Value Trends")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        clv = [1000, 1050, 1100, 1150, 1200, 1250, 1300] * (len(date_range) // 7 + 1)
        clv = clv[:len(date_range)]  # Ensure same length
        
        value_data = pd.DataFrame({
            'Date': date_range,
            'Average CLV': clv
        })
        st.line_chart(value_data.set_index('Date'))

    try:
        # Page header
        st.header("Segmentation & Value Analytics")
        st.markdown("Analyze customer segments and their value distribution")
        
        # Key Metrics Section
        st.subheader("Key Metrics")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Value Distribution",
            "Churn Risk",
            "Raw Data"
        ])
        
        with tab1:
            value_query = """
                SELECT 
                    CASE 
                        WHEN lifetime_value >= 1000 THEN 'High Value'
                        WHEN lifetime_value >= 500 THEN 'Medium Value'
                        ELSE 'Low Value'
                    END as value_segment,
                    COUNT(*) as customer_count,
                    ROUND(AVG(lifetime_value), 2) as avg_value
                FROM ANALYTICS.CUSTOMER_BASE
                GROUP BY value_segment
                ORDER BY avg_value DESC;
            """
            try:
                value_data = execute_query(value_query)
                df_value = pd.DataFrame(value_data, columns=['value_segment', 'customer_count', 'avg_value'])
                
                # Create violin plot
                fig = px.violin(
                    df_value,
                    y='avg_value',
                    x='value_segment',
                    box=True,
                    points="all",
                    title='Customer Lifetime Value Distribution',
                    labels={
                        'value_segment': 'Value Segment',
                        'avg_value': 'Lifetime Value',
                        'customer_count': 'Customer Count'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Lifetime value visualization")
                st.error("Failed to load lifetime value data")
        
        with tab2:
            churn_query = """
                SELECT 
                    churn_risk,
                    COUNT(*) as customer_count,
                    ROUND(AVG(avg_sentiment), 2) as avg_sentiment,
                    ROUND(AVG(ticket_count), 1) as avg_tickets
                FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
                GROUP BY churn_risk
                ORDER BY 
                    CASE churn_risk
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'Low' THEN 3
                    END;
            """
            try:
                churn_data = execute_query(churn_query)
                df_churn = pd.DataFrame(churn_data, columns=['churn_risk', 'customer_count', 'avg_sentiment', 'avg_tickets'])
                
                # Create bar chart
                fig = px.bar(
                    df_churn,
                    x='churn_risk',
                    y=['customer_count'],
                    title='Customer Distribution by Churn Risk',
                    labels={
                        'churn_risk': 'Churn Risk Level',
                        'value': 'Number of Customers',
                        'variable': 'Metric'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Churn risk visualization")
                st.error("Failed to load churn risk data")
        
        with tab3:
            raw_query = """
                SELECT 
                    cps.customer_id,
                    cb.persona,
                    cb.lifetime_value,
                    cps.churn_risk,
                    cps.upsell_opportunity,
                    cps.avg_sentiment,
                    cps.ticket_count
                FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
                JOIN ANALYTICS.CUSTOMER_BASE cb ON cps.customer_id = cb.customer_id
                ORDER BY cb.lifetime_value DESC
                LIMIT 1000;
            """
            try:
                raw_data = execute_query(raw_query)
                df_raw = pd.DataFrame(raw_data)
                st.dataframe(df_raw)
            except Exception as e:
                log_error(e, "Raw data display")
                st.error("Failed to load raw data")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Segmentation page rendering") 