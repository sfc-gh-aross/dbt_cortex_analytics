import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from typing import Dict

# Helper function to build WHERE clauses for filters
def build_filter_clauses(active_filters: Dict, table_alias: str = 'cb', date_col: str = 'acquisition_date') -> str:
    """Builds SQL WHERE clauses based on active filters. Assumes primary table is CUSTOMER_BASE (cb)."""
    clauses = []
    
    # Date Range Filter (using acquisition_date by default for CUSTOMER_BASE)
    date_range = active_filters.get("date_range")
    if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        # Ensure start/end_date are date objects if they aren't already
        if isinstance(start_date, datetime): start_date = start_date.date()
        if isinstance(end_date, datetime): end_date = end_date.date()
        if isinstance(start_date, date) and isinstance(end_date, date):
            # Use the specified date column for the table alias
            clauses.append(f"{table_alias}.{date_col} BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'")

    # Persona Filter - REMOVED
    # personas = active_filters.get("personas")
    # if personas and "All" not in personas:
    #     # If filtering CUSTOMER_BASE directly (alias 'cb'), use cb.persona
    #     # If joining, the persona_alias argument would be used.
    #     quoted_personas = [f"'{p}'" for p in personas]
    #     clauses.append(f"{table_alias}.persona IN ({', '.join(quoted_personas)})") # Assuming persona column is directly on cb

    return " AND ".join(clauses) if clauses else "1=1"

def render_segmentation_page(active_filters: Dict):
    """Render the segmentation and value page with applied filters."""
    st.title("Segmentation & Value Analysis")
    
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
        
        # Build filter clause - Only includes date range now, applied to CUSTOMER_BASE (cb)
        # Assuming acquisition_date is the relevant date field for segmentation
        filter_where_clause = build_filter_clauses(active_filters, table_alias='cb', date_col='acquisition_date')
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Segment Analysis",
            "Value Metrics",
            "Raw Data"
        ])
        
        with tab1:
            # Segment Analysis
            st.subheader("Segment Analysis")
            # Query for segment comparison (Example: Avg LTV and Sentiment by Persona)
            # JOIN is still needed for metrics, but WHERE clause is simplified
            segment_comparison_query = f"""
                SELECT 
                    cb.persona, 
                    AVG(cb.lifetime_value) as avg_ltv,
                    AVG(cps.avg_sentiment) as avg_sentiment,
                    COUNT(DISTINCT cb.customer_id) as customer_count
                FROM ANALYTICS.CUSTOMER_BASE cb
                LEFT JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps ON cb.customer_id = cps.customer_id
                WHERE {filter_where_clause} -- Only date filter applied to cb
                GROUP BY cb.persona
                ORDER BY avg_ltv DESC NULLS LAST;
            """
            try:
                segment_comparison_data = execute_query(segment_comparison_query)
                st.dataframe(segment_comparison_data)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                log_error(e, "Segment comparison query execution")
            
            # Reshape data for Plotly Express (long format)
            segment_comparison_long = segment_comparison_data.reset_index().melt(
                id_vars='persona', 
                var_name='Segment', 
                value_name='Value'
            )

            # Create grouped bar chart
            fig = px.bar(
                segment_comparison_long, 
                x='Segment', 
                y='Value', 
                color='Segment', 
                barmode='group',
                title="Segment Comparison by Metric"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Value Metrics
            st.subheader("Value Metrics")
            # Add value metrics content here
            st.write("Key value metrics across all segments will be shown here.")
            # Placeholder metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Average CLV", "$1150")
                st.metric("Overall Purchase Frequency", "3.5 times/year")
            with col2:
                st.metric("Overall Average Basket Size", "$95")
                st.metric("Customer Acquisition Cost (CAC)", "$50")

        with tab3:
            # Raw Data View
            st.subheader("Raw Data")
            # Query for raw data view - Simplified WHERE clause
            raw_data_query = f"""
                 SELECT 
                    cb.customer_id,
                    cb.persona, 
                    cb.lifetime_value,
                    cb.acquisition_date,
                    cps.avg_sentiment,
                    cps.ticket_count
                 FROM ANALYTICS.CUSTOMER_BASE cb
                 LEFT JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps ON cb.customer_id = cps.customer_id
                 WHERE {filter_where_clause} -- Only date filter applied to cb
                 ORDER BY cb.acquisition_date DESC
                 LIMIT 500;
            """
            try:
                raw_data = execute_query(raw_data_query)
                st.dataframe(raw_data)
                st.write("Filters can be applied to explore the raw data.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                log_error(e, "Raw data query execution")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Segmentation page rendering") 