import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from typing import Dict

# Helper function to build WHERE clauses for filters
def build_filter_clauses(active_filters: Dict, table_alias: str = 'st', date_col: str = 'ticket_date') -> str:
    """Builds SQL WHERE clauses based on active filters."""
    clauses = []
    
    # Date Range Filter
    date_range = active_filters.get("date_range")
    if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        # Ensure start/end_date are date objects if they aren't already
        if isinstance(start_date, datetime): start_date = start_date.date()
        if isinstance(end_date, datetime): end_date = end_date.date()
        if isinstance(start_date, date) and isinstance(end_date, date):
            clauses.append(f"{table_alias}.{date_col} BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'")

    # Persona Filter - REMOVED
    # personas = active_filters.get("personas")
    # if personas and "All" not in personas:
    #     # Ensure personas are properly quoted for the IN clause
    #     quoted_personas = [f"'{p}'" for p in personas]
    #     clauses.append(f"{persona_alias}.{persona_col} IN ({', '.join(quoted_personas)})")
        
    # Add other filters (e.g., channels) here if needed

    return " AND ".join(clauses) if clauses else "1=1" # Return '1=1' if no filters to avoid syntax errors

def render_support_page(active_filters: Dict):
    """Render the support operations page with applied filters."""
    st.title("Support Operations Dashboard")
    
    # Example support metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Total Tickets", "1,234", "+12%")
    with metric_cols[1]:
        st.metric("First Response Time", "2.3h", "-0.5h")
    with metric_cols[2]:
        st.metric("Resolution Time", "8.5h", "-1.2h")
    with metric_cols[3]:
        st.metric("Customer Satisfaction", "92%", "+3%")
    
    # Example ticket trends chart (replace with actual data)
    st.markdown("### Ticket Volume Trends")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        ticket_volume = [100, 120, 110, 130, 140, 150, 160] * (len(date_range) // 7 + 1)
        ticket_volume = ticket_volume[:len(date_range)]  # Ensure same length
        
        chart_data = pd.DataFrame({
            'Date': date_range,
            'Ticket Volume': ticket_volume
        })
        st.line_chart(chart_data.set_index('Date'))
    
    # Example channel distribution (replace with actual data)
    st.markdown("### Support Channel Distribution")
    channel_data = pd.DataFrame({
        'Channel': ["Email", "Chat", "Phone", "Social"],
        'Volume': [500, 300, 200, 234]
    })
    st.bar_chart(channel_data.set_index('Channel'))

    try:
        # Page header
        st.header("Support Operations Analytics")
        
        # Build filter clauses
        # Join needed for persona filter - REMOVED
        # needs_join = "personas" in active_filters and active_filters["personas"] and "All" not in active_filters["personas"]
        join_clause = "" # No longer joining for persona
        # Assuming 'ticket_date' is the relevant date column in FACT_SUPPORT_TICKETS
        # Assuming 'persona' is the relevant column in CUSTOMER_BASE - REMOVED
        filter_where_clause = build_filter_clauses(active_filters, table_alias='st', date_col='ticket_date') # Removed persona args
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Ticket Volume by Priority
        with col1:
            st.subheader("Ticket Volume")
            volume_query = f"""
                SELECT 
                    st.priority_level,
                    COUNT(*) as ticket_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM ANALYTICS.FACT_SUPPORT_TICKETS st
                {join_clause}
                WHERE {filter_where_clause} 
                GROUP BY st.priority_level
                ORDER BY 
                    CASE st.priority_level
                        WHEN 'Critical' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                    END;
            """
            try:
                volume_data = execute_query(volume_query)
                # Convert Snowflake cursor results to DataFrame
                if volume_data:
                    df_volume = pd.DataFrame(volume_data)
                    # Ensure columns match query output even if no data
                    df_volume.columns = ['priority_level', 'ticket_count', 'percentage'] 
                    
                    # Create stacked area chart
                    fig = px.area(
                        df_volume,
                        x='priority_level',
                        y='ticket_count',
                        color='priority_level',
                        title='Ticket Volume by Priority',
                        labels={
                            'priority_level': 'Priority Level',
                            'ticket_count': 'Ticket Count',
                            'percentage': 'Percentage'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No ticket volume data found for the selected filters.")
            except Exception as e:
                log_error(e, "Ticket volume visualization")
                st.error("Failed to load ticket volume data")
        
        # Most Common Ticket Categories
        with col2:
            st.subheader("Ticket Categories")
            categories_query = f"""
                SELECT 
                    st.ticket_category,
                    COUNT(*) as ticket_count,
                    ROUND(AVG(st.sentiment_score), 3) as avg_sentiment
                FROM ANALYTICS.FACT_SUPPORT_TICKETS st
                {join_clause}
                WHERE {filter_where_clause} 
                GROUP BY st.ticket_category
                ORDER BY ticket_count DESC;
            """
            try:
                categories_data = execute_query(categories_query)
                if categories_data:
                    df_categories = pd.DataFrame(categories_data)
                    # Ensure columns match query output
                    df_categories.columns = ['ticket_category', 'ticket_count', 'avg_sentiment']
                    
                    # Create treemap
                    fig = px.treemap(
                        df_categories,
                        path=['ticket_category'],
                        values='ticket_count',
                        color='avg_sentiment',
                        color_continuous_scale='RdYlGn',
                        title='Most Common Ticket Categories',
                        labels={
                            'ticket_category': 'Category',
                            'ticket_count': 'Ticket Count',
                            'avg_sentiment': 'Average Sentiment'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                     st.info("No ticket category data found for the selected filters.")
            except Exception as e:
                log_error(e, "Ticket categories visualization")
                st.error("Failed to load ticket categories data")
        
        # Ticket Recurrence Patterns
        with col3:
            st.subheader("Recurrence Patterns")
            # This query uses ANALYTICS.TICKET_PATTERNS which might already be aggregated.
            # Applying filters here might require joining TICKET_PATTERNS back to CUSTOMER_BASE.
            # For now, leaving this unfiltered until table structure is confirmed.
            patterns_query = """
                SELECT 
                    customer_id,
                    ticket_count,
                    ARRAY_TO_STRING(ticket_categories, ', ') as categories,
                    ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
                FROM ANALYTICS.TICKET_PATTERNS
                ORDER BY ticket_count DESC
                LIMIT 50; -- Added LIMIT to prevent overly large Sankey diagrams
            """
            # --- Example of how filtering *might* be applied if TICKET_PATTERNS has customer_id ---
            # patterns_needs_join = "personas" in active_filters and active_filters["personas"] and "All" not in active_filters["personas"]
            # patterns_join_clause = "LEFT JOIN ANALYTICS.CUSTOMER_BASE cb ON tp.customer_id = cb.customer_id" if patterns_needs_join else ""
            # # Assuming TICKET_PATTERNS doesn't have a date, so we only filter by persona if needed
            # patterns_filter_where_clause = "1=1"
            # personas = active_filters.get("personas")
            # if patterns_needs_join:
            #     quoted_personas = [f"'{p}'" for p in personas]
            #     patterns_filter_where_clause = f"cb.persona IN ({', '.join(quoted_personas)})"
            #
            # patterns_query = f"""
            #     SELECT 
            #         tp.customer_id,
            #         tp.ticket_count,
            #         ARRAY_TO_STRING(tp.ticket_categories, ', ') as categories,
            #         ARRAY_TO_STRING(tp.ticket_priorities, ', ') as priorities
            #     FROM ANALYTICS.TICKET_PATTERNS tp
            #     {patterns_join_clause}
            #     WHERE {patterns_filter_where_clause}
            #     ORDER BY tp.ticket_count DESC
            #     LIMIT 50; 
            # """
            # --- End Example ---
            
            try:
                patterns_data = execute_query(patterns_query)
                if patterns_data:
                    # Convert Snowflake cursor results to DataFrame
                    df_patterns = pd.DataFrame(patterns_data)
                    # Ensure columns match query output
                    df_patterns.columns = ['customer_id', 'ticket_count', 'category_sequence', 'priorities'] 
                    
                    # Basic data prep for Sankey (might need refinement)
                    if len(df_patterns) > 1 and 'category_sequence' in df_patterns.columns:
                        # Attempting a simpler Sankey or alternative visualization if complex flow fails
                        # For simplicity, let's just show the table for now if Sankey prep is complex/error-prone
                        st.dataframe(df_patterns[['customer_id', 'ticket_count', 'category_sequence']].head(10))
                        st.caption("Top customers by ticket recurrence (limited view)")
                        # TODO: Re-implement Sankey or alternative flow viz if needed
                    else:
                        st.info("Not enough data or required columns missing for recurrence pattern visualization.")

                else:
                    st.info("No recurrence pattern data found.") # Add message if no data
            except Exception as e:
                log_error(e, "Ticket patterns visualization")
                st.error("Failed to load ticket patterns data")
        
        # Detailed Analysis Section
        st.subheader("Detailed Analysis")
        
        # Re-use the main filter clauses for consistency
        # filter_where_clause and join_clause defined earlier should apply here too
        
        tab1, tab2, tab3 = st.tabs([
            "Customer Satisfaction",
            "Ticket Patterns", # This tab's query was already handled above
            "Raw Data"
        ])
        
        with tab1:
            # Customer Satisfaction vs. Ticket Priority
            # Apply the same filters and join as other FACT_SUPPORT_TICKET queries
            satisfaction_query = f"""
                SELECT 
                    st.priority_level,
                    ROUND(AVG(st.sentiment_score), 3) as avg_sentiment,
                    COUNT(*) as ticket_count
                FROM ANALYTICS.FACT_SUPPORT_TICKETS st
                {join_clause}
                WHERE {filter_where_clause}
                GROUP BY st.priority_level
                ORDER BY 
                    CASE st.priority_level
                        WHEN 'Critical' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                    END;
            """
            try:
                satisfaction_data = execute_query(satisfaction_query)
                if satisfaction_data:
                    # Convert Snowflake cursor results to DataFrame
                    df_satisfaction = pd.DataFrame(satisfaction_data)
                    # Ensure columns match query output
                    df_satisfaction.columns = ['priority_level', 'avg_sentiment', 'ticket_count'] 
                    
                    # Create scatter plot with trend line
                    fig = px.scatter(
                        df_satisfaction,
                        x='ticket_count',
                        y='avg_sentiment',
                        color='priority_level',
                        size='ticket_count',
                        trendline="ols",
                        title='Customer Satisfaction vs. Ticket Priority',
                        labels={
                            'ticket_count': 'Ticket Count',
                            'avg_sentiment': 'Average Sentiment',
                            'priority_level': 'Priority Level'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No customer satisfaction data found for the selected filters.")
            except Exception as e:
                log_error(e, "Customer satisfaction visualization")
                st.error("Failed to load customer satisfaction data")
        
        with tab2:
            # Ticket Patterns Analysis - Displaying results from the query executed earlier in col3
            st.write("Recurrence pattern data (from above)")
            if 'df_patterns' in locals() and not df_patterns.empty:
                 st.dataframe(df_patterns.head(20)) # Show a preview in the tab
            else:
                 st.info("No recurrence pattern data found for the selected filters.")
        
        with tab3:
             # Raw Data View - Apply filters here too
            raw_data_query = f"""
                SELECT 
                    st.ticket_id,
                    st.customer_id,
                    st.ticket_date,
                    st.priority_level,
                    st.ticket_category,
                    st.sentiment_score
                    -- Optionally include persona if joined: , cb.persona 
                FROM ANALYTICS.FACT_SUPPORT_TICKETS st
                {join_clause}
                WHERE {filter_where_clause}
                ORDER BY st.ticket_date DESC
                LIMIT 1000;
            """
            try:
                raw_data = execute_query(raw_data_query)
                if raw_data:
                    df_raw = pd.DataFrame(raw_data)
                    # Adjust columns based on whether join_clause was active
                    # Assuming base columns: ticket_id, customer_id, ticket_date, priority_level, ticket_category, sentiment_score
                    # If joined, add persona
                    st.dataframe(df_raw)
                else:
                    st.info("No raw ticket data found for the selected filters.")
            except Exception as e:
                log_error(e, "Raw data display")
                st.error("Failed to load raw data")
    
    except Exception as e:
        log_error(e, "Support page rendering")
        st.error("An error occurred while rendering the support operations page") 