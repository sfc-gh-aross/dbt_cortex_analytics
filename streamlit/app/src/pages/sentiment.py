import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from src.utils.ui import (
    display_trend_indicator,
    create_card,
    display_data_table,
    show_empty_state,
    handle_error
)
from src.utils.ui_enhanced import (
    with_tooltip,
    EnhancedLoadingState,
    show_toast,
    enhanced_dataframe,
    with_loading_and_feedback
)
from typing import Dict
import os

@with_loading_and_feedback(
    message="Fetching sentiment data...",
    success_message=None,
    error_message="Failed to load sentiment data"
)
def get_sentiment_data():
    """Fetch sentiment distribution data."""
    sentiment_query = """
        SELECT 
            CASE 
                WHEN sentiment_score < -0.3 THEN 'Negative'
                WHEN sentiment_score > 0.3 THEN 'Positive'
                ELSE 'Neutral'
            END as sentiment_category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY sentiment_category
        ORDER BY count DESC;
    """
    try:
        data = execute_query(sentiment_query)
        # Convert to list of dictionaries with proper types
        result = []
        for row in data:
            result.append({
                'sentiment_category': str(row['SENTIMENT_CATEGORY']),
                'count': int(row['COUNT']),
                'percentage': float(row['PERCENTAGE'])
            })
        return result
    except Exception as e:
        st.error(f"Error processing sentiment data: {str(e)}")
        st.write("Raw data:", data)
        return []

@handle_error
def get_sentiment_trends():
    """Fetch sentiment trends data."""
    trends_query = """
        SELECT 
            DATE_TRUNC('day', interaction_date) as date,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY date
        ORDER BY date;
    """
    try:
        data = execute_query(trends_query)
        # Convert to list of dictionaries with proper types
        result = []
        for row in data:
            result.append({
                'date': pd.to_datetime(row['DATE']).date(),
                'avg_sentiment': float(row['AVG_SENTIMENT']),
                'interaction_count': int(row['INTERACTION_COUNT'])
            })
        return result
    except Exception as e:
        st.error(f"Error processing sentiment trends data: {str(e)}")
        st.write("Raw data:", data)
        return []

@handle_error
def get_sentiment_by_type():
    """Fetch sentiment by interaction type data."""
    type_query = """
        SELECT 
            source_type as interaction_type,
            ROUND(AVG(sentiment_score), 3) as avg_sentiment,
            COUNT(*) as interaction_count
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        GROUP BY source_type
        ORDER BY avg_sentiment DESC;
    """
    data = execute_query(type_query)
    # Convert data to proper format and types
    df = pd.DataFrame(
        {
            'interaction_type': [str(row['interaction_type']) for row in data],
            'avg_sentiment': [float(row['avg_sentiment']) for row in data],
            'interaction_count': [int(row['interaction_count']) for row in data]
        }
    )
    return df

@handle_error
def get_sentiment_correlation():
    """Fetch sentiment correlation data."""
    correlation_query = """
        WITH daily_metrics AS (
            SELECT 
                DATE_TRUNC('day', interaction_date) as date,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as interaction_count
            FROM ANALYTICS.SENTIMENT_ANALYSIS
            GROUP BY date
        )
        SELECT 
            date,
            avg_sentiment,
            interaction_count
        FROM daily_metrics
        ORDER BY date;
    """
    data = execute_query(correlation_query)
    df = pd.DataFrame(data, columns=['date', 'avg_sentiment', 'interaction_count'])
    # Ensure proper data types
    df['date'] = pd.to_datetime(df['date']).dt.date  # Convert to date to avoid datetime64 issues
    df['avg_sentiment'] = pd.to_numeric(df['avg_sentiment'], errors='coerce').astype('float64')
    df['interaction_count'] = pd.to_numeric(df['interaction_count'], errors='coerce').astype('Int64')
    return df

@handle_error
def get_sentiment_volatility():
    """Fetch sentiment volatility data."""
    volatility_query = """
        SELECT 
            customer_id,
            avg_sentiment,
            sentiment_volatility,
            ticket_count
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        ORDER BY sentiment_volatility DESC
        LIMIT 10;
    """
    data = execute_query(volatility_query)
    # Convert data to proper format and types
    df = pd.DataFrame(
        {
            'customer_id': [str(row['customer_id']) for row in data],
            'avg_sentiment': [float(row['avg_sentiment']) for row in data],
            'sentiment_volatility': [float(row['sentiment_volatility']) for row in data],
            'ticket_count': [int(row['ticket_count']) for row in data]
        }
    )
    return df

def render_sentiment_page(active_filters: Dict):
    """Render the sentiment analysis page with applied filters."""
    st.title("Sentiment & Experience Analysis")
    
    # Example sentiment metrics (replace with actual data)
    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Customer Satisfaction", "85%", "+2%")
    with metric_cols[1]:
        st.metric("Response Time", "2.5h", "-0.5h")
    with metric_cols[2]:
        st.metric("Resolution Rate", "92%", "+3%")
    
    # Example sentiment trends chart (replace with actual data)
    st.markdown("### Sentiment Trends")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        sentiment_scores = [0.7, 0.8, 0.75, 0.85, 0.9, 0.88, 0.92] * (len(date_range) // 7 + 1)
        sentiment_scores = sentiment_scores[:len(date_range)]  # Ensure same length
        
        chart_data = pd.DataFrame({
            'Date': date_range,
            'Sentiment Score': sentiment_scores
        })
        st.line_chart(chart_data.set_index('Date'))
    
    # Example sentiment breakdown by persona (replace with actual data)
    st.markdown("### Sentiment by Customer Persona")
    
    # Define all possible personas
    all_personas = ["Enterprise", "SMB", "Startup", "Individual"]
    
    # Get selected personas from filters
    selected_personas = active_filters.get("personas", ["All"])
    
    # If "All" is selected or no specific personas are selected, show all personas
    if "All" in selected_personas or not selected_personas:
        display_personas = all_personas
    else:
        display_personas = selected_personas
    
    # Create persona data
    persona_data = pd.DataFrame({
        'Persona': display_personas,
        'Positive': [85, 75, 90, 80][:len(display_personas)],
        'Neutral': [10, 15, 5, 15][:len(display_personas)],
        'Negative': [5, 10, 5, 5][:len(display_personas)]
    })
    
    # Display the chart
    st.bar_chart(persona_data.set_index('Persona'))
    
    # Add a note if specific personas are selected
    if "All" not in selected_personas and selected_personas:
        st.info(f"Showing data for selected personas: {', '.join(selected_personas)}")

    try:
        # Page header with tooltip
        st.header("Sentiment & Experience Analytics")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Sentiment Distribution",
            "Trend Analysis",
            "Raw Data"
        ])
        
        with tab1:
            # Sentiment Distribution Card
            create_card(
                title="Sentiment Distribution",
                content="Distribution of customer sentiment across all interactions"
            )
            
            with st.spinner("Loading sentiment distribution..."):
                st.write("Fetching sentiment data...")
                df_sentiment = get_sentiment_data()
                st.write(f"Data received: {df_sentiment is not None}")
                if df_sentiment is not None:
                    st.write(f"Data shape: {len(df_sentiment)}")
                    st.write("Sample data:", df_sentiment[:5])
                    st.write("Data types:", {k: type(v) for k, v in df_sentiment[0].items()})
                
                if df_sentiment is not None and df_sentiment:
                    try:
                        # Convert data to proper types and format
                        df_display = pd.DataFrame(df_sentiment)
                        df_display['count'] = pd.to_numeric(df_display['count'], errors='coerce')
                        df_display['percentage'] = pd.to_numeric(df_display['percentage'], errors='coerce')
                        df_display['sentiment_category'] = df_display['sentiment_category'].astype(str)
                        
                        # Display the data in a table format
                        st.subheader("Sentiment Distribution Data", divider="rainbow")
                        st.dataframe(
                            df_display,
                            column_config={
                                "sentiment_category": st.column_config.TextColumn(
                                    "Sentiment Category",
                                    help="The category of sentiment"
                                ),
                                "count": st.column_config.NumberColumn(
                                    "Count",
                                    help="Number of interactions",
                                    format="%d"
                                ),
                                "percentage": st.column_config.NumberColumn(
                                    "Percentage",
                                    help="Percentage of total",
                                    format="%.2f%%"
                                )
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # Create a bar chart
                        st.subheader("Sentiment Distribution", divider="rainbow")
                        st.bar_chart(
                            df_display.set_index('sentiment_category')['count'],
                            use_container_width=True
                        )
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Positive Sentiment",
                                f"{df_display[df_display['sentiment_category'] == 'Positive']['count'].iloc[0]}",
                                f"{df_display[df_display['sentiment_category'] == 'Positive']['percentage'].iloc[0]:.1f}%"
                            )
                        with col2:
                            st.metric(
                                "Neutral Sentiment",
                                f"{df_display[df_display['sentiment_category'] == 'Neutral']['count'].iloc[0]}",
                                f"{df_display[df_display['sentiment_category'] == 'Neutral']['percentage'].iloc[0]:.1f}%"
                            )
                        with col3:
                            st.metric(
                                "Negative Sentiment",
                                f"{df_display[df_display['sentiment_category'] == 'Negative']['count'].iloc[0]}",
                                f"{df_display[df_display['sentiment_category'] == 'Negative']['percentage'].iloc[0]:.1f}%"
                            )
                        
                    except Exception as e:
                        st.error(f"Error creating visualizations: {str(e)}")
                        st.write("Error details:", e)
                        import traceback
                        st.write("Full traceback:", traceback.format_exc())
                else:
                    st.write("No data available for visualization")
                    show_empty_state("No sentiment data available")
        
        with tab2:
            # Trend Analysis
            st.subheader("Sentiment Trends Over Time")
            with st.spinner("Loading sentiment trends..."):
                st.write("Fetching trend data...")
                df_trends = get_sentiment_trends()
                st.write(f"Data received: {df_trends is not None}")
                if df_trends is not None:
                    st.write(f"Data shape: {len(df_trends)}")
                    st.write("Sample data:", df_trends[:5])
                    st.write("Data types:", {k: type(v) for k, v in df_trends[0].items()})
                
                if df_trends is not None and df_trends:
                    try:
                        # Convert date column to datetime if it's not already
                        st.write("Converting date column...")
                        df_trends = pd.DataFrame(df_trends)
                        df_trends['date'] = pd.to_datetime(df_trends['date'])
                        
                        # Create line chart for sentiment trends
                        st.write("Creating line chart...")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_trends['date'].tolist(),
                            y=df_trends['avg_sentiment'].tolist(),
                            mode='lines+markers',
                            name='Average Sentiment'
                        ))
                        fig.update_layout(
                            title='Average Sentiment Over Time',
                            xaxis_title='Date',
                            yaxis_title='Average Sentiment Score',
                            yaxis_range=[-1, 1],
                            hovermode='x unified',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#111827')
                        )
                        st.write("Rendering line chart...")
                        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                        
                        # Add a bar chart for interaction volume
                        st.write("Creating volume chart...")
                        fig2 = go.Figure(data=[go.Bar(
                            x=df_trends['date'].tolist(),
                            y=df_trends['interaction_count'].tolist(),
                            name='Interaction Count'
                        )])
                        fig2.update_layout(
                            title='Interaction Volume Over Time',
                            xaxis_title='Date',
                            yaxis_title='Number of Interactions',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#111827')
                        )
                        st.write("Rendering volume chart...")
                        st.plotly_chart(fig2, use_container_width=True, theme="streamlit")
                    except Exception as e:
                        st.error(f"Error creating charts: {str(e)}")
                        st.write("Error details:", e)
                else:
                    st.write("No data available for visualization")
                    show_empty_state("No trend data available")
        
        with tab3:
            # Raw Data View
            st.subheader("Raw Sentiment Data")
            with st.spinner("Loading raw data..."):
                df_sentiment = get_sentiment_data()
                if df_sentiment is not None and df_sentiment:
                    display_data_table(pd.DataFrame(df_sentiment))
                else:
                    show_empty_state("No data available")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Sentiment page rendering") 