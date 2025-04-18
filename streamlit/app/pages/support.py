import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_support_page():
    """Render the Support Operations workspace."""
    try:
        # Page header
        st.header("Support Operations Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Ticket Volume by Priority
        with col1:
            st.subheader("Ticket Volume")
            volume_query = """
                SELECT 
                    priority_level,
                    COUNT(*) as ticket_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM ANALYTICS.FACT_SUPPORT_TICKETS
                GROUP BY priority_level
                ORDER BY 
                    CASE priority_level
                        WHEN 'Critical' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                    END;
            """
            try:
                volume_data = execute_query(volume_query)
                # Convert Snowflake cursor results to DataFrame
                df_volume = pd.DataFrame(volume_data)
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
            except Exception as e:
                log_error(e, "Ticket volume visualization")
                st.error("Failed to load ticket volume data")
        
        # Most Common Ticket Categories
        with col2:
            st.subheader("Ticket Categories")
            categories_query = """
                SELECT 
                    ticket_category,
                    COUNT(*) as ticket_count,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment
                FROM ANALYTICS.FACT_SUPPORT_TICKETS
                GROUP BY ticket_category
                ORDER BY ticket_count DESC;
            """
            try:
                categories_data = execute_query(categories_query)
                # Convert Snowflake cursor results to DataFrame
                df_categories = pd.DataFrame(categories_data)
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
            except Exception as e:
                log_error(e, "Ticket categories visualization")
                st.error("Failed to load ticket categories data")
        
        # Ticket Recurrence Patterns
        with col3:
            st.subheader("Recurrence Patterns")
            patterns_query = """
                WITH ticket_counts AS (
                    SELECT 
                        customer_id,
                        COUNT(*) as ticket_count,
                        LISTAGG(ticket_category, ', ') WITHIN GROUP (ORDER BY ticket_date) as category_sequence,
                        LISTAGG(priority_level, ', ') WITHIN GROUP (ORDER BY ticket_date) as priority_sequence
                    FROM ANALYTICS.FACT_SUPPORT_TICKETS
                    GROUP BY customer_id
                    HAVING COUNT(*) > 1
                )
                SELECT 
                    customer_id,
                    ticket_count,
                    category_sequence,
                    priority_sequence
                FROM ticket_counts
                ORDER BY ticket_count DESC;
            """
            try:
                patterns_data = execute_query(patterns_query)
                # Convert Snowflake cursor results to DataFrame
                df_patterns = pd.DataFrame(patterns_data)
                df_patterns.columns = ['customer_id', 'ticket_count', 'category_sequence', 'priority_sequence']
                
                # Create sankey diagram
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=df_patterns['category_sequence'].str.split(', ').explode().unique(),
                        color="blue"
                    ),
                    link=dict(
                        source=df_patterns['category_sequence'].str.split(', ').str[0].astype('category').cat.codes,
                        target=df_patterns['category_sequence'].str.split(', ').str[1].astype('category').cat.codes,
                        value=df_patterns['ticket_count']
                    )
                )])
                
                fig.update_layout(title_text="Ticket Category Flow", font_size=10)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Ticket patterns visualization")
                st.error("Failed to load ticket patterns data")
        
        # Detailed Analysis Section
        st.markdown("---")
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Customer Satisfaction",
            "Ticket Patterns",
            "Raw Data"
        ])
        
        with tab1:
            # Customer Satisfaction vs. Ticket Priority
            satisfaction_query = """
                SELECT 
                    priority_level,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    COUNT(*) as ticket_count
                FROM ANALYTICS.FACT_SUPPORT_TICKETS
                GROUP BY priority_level
                ORDER BY 
                    CASE priority_level
                        WHEN 'Critical' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                    END;
            """
            try:
                satisfaction_data = execute_query(satisfaction_query)
                # Convert Snowflake cursor results to DataFrame
                df_satisfaction = pd.DataFrame(satisfaction_data)
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
            except Exception as e:
                log_error(e, "Customer satisfaction visualization")
                st.error("Failed to load customer satisfaction data")
        
        with tab2:
            # Ticket Patterns Analysis
            patterns_query = """
                SELECT 
                    customer_id,
                    ticket_count,
                    ARRAY_TO_STRING(ticket_categories, ', ') as categories,
                    ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
                FROM ANALYTICS.TICKET_PATTERNS
                ORDER BY ticket_count DESC;
            """
            try:
                patterns_data = execute_query(patterns_query)
                # Convert Snowflake cursor results to DataFrame
                df_patterns = pd.DataFrame(patterns_data)
                df_patterns.columns = ['customer_id', 'ticket_count', 'categories', 'priorities']
                
                # Create network graph
                fig = go.Figure(data=[go.Scatter(
                    x=df_patterns['ticket_count'],
                    y=df_patterns['ticket_count'],
                    mode='markers',
                    marker=dict(
                        size=df_patterns['ticket_count'],
                        color=df_patterns['ticket_count'],
                        colorscale='Viridis',
                        showscale=True
                    ),
                    text=df_patterns['categories'],
                    hoverinfo='text'
                )])
                
                fig.update_layout(
                    title='Ticket Category Relationships',
                    xaxis_title='Ticket Count',
                    yaxis_title='Ticket Count'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Ticket patterns analysis")
                st.error("Failed to load ticket patterns data")
        
        with tab3:
            raw_data_query = """
                SELECT 
                    ticket_id,
                    customer_id,
                    ticket_date,
                    priority_level,
                    ticket_category,
                    sentiment_score
                FROM ANALYTICS.FACT_SUPPORT_TICKETS
                ORDER BY ticket_date DESC
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
        log_error(e, "Support page rendering")
        st.error("An error occurred while rendering the support operations page") 