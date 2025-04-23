import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import warnings
from typing import Dict

# Suppress FutureWarning from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

def render_journey_page(active_filters: Dict):
    """Render the customer journey page with applied filters."""
    st.title("Customer Journey Analysis")
    
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
    
    # Example journey metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Average Journey Length", "45 days", "-5 days")
    with metric_cols[1]:
        st.metric("Conversion Rate", "35%", "+3%")
    with metric_cols[2]:
        st.metric("Drop-off Rate", "25%", "-2%")
    with metric_cols[3]:
        st.metric("Time to Conversion", "30 days", "-3 days")
    
    # Example journey stages chart (replace with actual data)
    st.markdown("### Journey Stage Progression")
    stage_data = pd.DataFrame({
        'Stage': ["Awareness", "Consideration", "Decision", "Purchase", "Retention"],
        'Users': [1000, 800, 600, 400, 300]
    })
    st.bar_chart(stage_data.set_index('Stage'))
    
    # Example journey timeline (replace with actual data)
    st.markdown("### Journey Timeline")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        engagement = [50, 60, 70, 80, 90, 100, 110] * (len(date_range) // 7 + 1)
        engagement = engagement[:len(date_range)]  # Ensure same length
        
        timeline_data = pd.DataFrame({
            'Date': date_range,
            'User Engagement': engagement
        })
        st.line_chart(timeline_data.set_index('Date'))

    try:
        # Page header
        st.header("Customer Journey Analytics")
        st.markdown("Analyze customer journey patterns and touchpoint interactions")
        
        # Key Metrics Section
        st.subheader("Key Metrics")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Sentiment Journey",
            "Interaction Types",
            "Raw Data"
        ])
        
        with tab1:
            journey_query = """
                WITH sentiment_journey AS (
                    SELECT 
                        customer_id,
                        interaction_date,
                        sentiment_score,
                        source_type
                    FROM ANALYTICS.SENTIMENT_ANALYSIS
                    ORDER BY interaction_date
                )
                SELECT 
                    customer_id,
                    ARRAY_AGG(sentiment_score) WITHIN GROUP (ORDER BY interaction_date) as sentiment_journey,
                    ARRAY_AGG(source_type) WITHIN GROUP (ORDER BY interaction_date) as touchpoint_sequence,
                    COUNT(*) as touchpoint_count,
                    AVG(sentiment_score) as avg_sentiment
                FROM sentiment_journey
                GROUP BY customer_id
                ORDER BY touchpoint_count DESC
                LIMIT 100;
            """
            try:
                journey_data = execute_query(journey_query)
                df_journey = pd.DataFrame(journey_data)
                df_journey.columns = ['customer_id', 'sentiment_journey', 'touchpoint_sequence', 'touchpoint_count', 'avg_sentiment']
                
                if not df_journey.empty:
                    # Parse the sentiment journey arrays
                    def parse_sentiment_array(s):
                        try:
                            # Remove brackets and split by commas
                            s = s.strip('[]').replace('\n', '')
                            return [float(x.strip()) for x in s.split(',') if x.strip()]
                        except:
                            return []
                    
                    # Convert string arrays to lists of floats
                    df_journey['sentiment_journey'] = df_journey['sentiment_journey'].apply(parse_sentiment_array)
                    
                    # Create line chart of average sentiment by touchpoint sequence
                    sentiment_series = pd.DataFrame(df_journey['sentiment_journey'].tolist()).mean()
                    fig = px.line(
                        x=range(len(sentiment_series)),
                        y=sentiment_series,
                        title='Average Sentiment Journey',
                        labels={
                            'x': 'Touchpoint Sequence',
                            'y': 'Average Sentiment'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No journey data available")
            except Exception as e:
                log_error(e, "Journey flow visualization")
                st.error("Failed to load journey flow data")
        
        with tab2:
            interaction_query = """
                SELECT 
                    interaction_type,
                    COUNT(*) as interaction_count,
                    ROUND(AVG(sentiment_score), 2) as avg_sentiment,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                GROUP BY interaction_type
                ORDER BY interaction_count DESC;
            """
            try:
                interaction_data = execute_query(interaction_query)
                df_interactions = pd.DataFrame(interaction_data)
                df_interactions.columns = ['interaction_type', 'interaction_count', 'avg_sentiment', 'unique_customers']
                
                if not df_interactions.empty:
                    fig = px.bar(
                        df_interactions,
                        x='interaction_type',
                        y='interaction_count',
                        color='avg_sentiment',
                        title='Interaction Types and Sentiment',
                        labels={
                            'interaction_type': 'Interaction Type',
                            'interaction_count': 'Number of Interactions',
                            'avg_sentiment': 'Average Sentiment'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No interaction data available")
            except Exception as e:
                log_error(e, "Interaction analysis visualization")
                st.error("Failed to load interaction analysis data")
        
        with tab3:
            raw_query = """
                SELECT 
                    sa.customer_id,
                    sa.interaction_date,
                    sa.sentiment_score,
                    sa.source_type,
                    cb.persona,
                    cb.lifetime_value
                FROM ANALYTICS.SENTIMENT_ANALYSIS sa
                JOIN ANALYTICS.CUSTOMER_BASE cb ON sa.customer_id = cb.customer_id
                ORDER BY sa.interaction_date DESC
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
        log_error(e, "Journey page rendering") 