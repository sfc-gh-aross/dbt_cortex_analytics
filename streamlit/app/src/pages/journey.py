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

# Suppress FutureWarning from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

def render_journey_page():
    """Render the Customer Journey workspace."""
    try:
        # Page header
        st.header("Customer Journey Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Interaction Frequency Patterns
        with col1:
            st.subheader("Interaction Patterns")
            frequency_query = """
                SELECT 
                    customer_id,
                    COUNT(*) as interaction_count,
                    MIN(interaction_date) as first_interaction,
                    MAX(interaction_date) as last_interaction
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                GROUP BY customer_id
                ORDER BY interaction_count DESC;
            """
            try:
                frequency_data = execute_query(frequency_query)
                df_frequency = pd.DataFrame(frequency_data, columns=['customer_id', 'interaction_count', 'first_interaction', 'last_interaction'])
                
                # Create heat calendar
                fig = px.density_heatmap(
                    df_frequency,
                    x='first_interaction',
                    y='last_interaction',
                    z='interaction_count',
                    title='Interaction Frequency Patterns',
                    labels={
                        'first_interaction': 'First Interaction',
                        'last_interaction': 'Last Interaction',
                        'interaction_count': 'Interaction Count'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Interaction frequency visualization")
                st.error("Failed to load interaction frequency data")
        
        # Preferred Communication Channels
        with col2:
            st.subheader("Communication Channels")
            channels_query = """
                SELECT 
                    interaction_type,
                    COUNT(*) as interaction_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                GROUP BY interaction_type
                ORDER BY interaction_count DESC;
            """
            try:
                channels_data = execute_query(channels_query)
                df_channels = pd.DataFrame(channels_data, columns=['interaction_type', 'interaction_count', 'percentage'])
                
                # Create donut chart
                fig = px.pie(
                    df_channels,
                    values='interaction_count',
                    names='interaction_type',
                    hole=0.4,
                    title='Preferred Communication Channels',
                    labels={
                        'interaction_type': 'Channel',
                        'interaction_count': 'Interaction Count',
                        'percentage': 'Percentage'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Communication channels visualization")
                st.error("Failed to load communication channels data")
        
        # Customer Journey Mapping
        with col3:
            st.subheader("Journey Mapping")
            journey_query = """
                SELECT 
                    customer_id,
                    ARRAY_AGG(
                        CASE 
                            WHEN source_type = 'interaction' THEN 'Interaction'
                            WHEN source_type = 'review' THEN 'Review'
                            WHEN source_type = 'ticket' THEN 'Support'
                        END
                    ) WITHIN GROUP (ORDER BY interaction_date) as journey_sequence
                FROM ANALYTICS.SENTIMENT_ANALYSIS
                GROUP BY customer_id;
            """
            try:
                journey_data = execute_query(journey_query)
                df_journey = pd.DataFrame(journey_data)
                
                # Create flow diagram
                if not df_journey.empty and 'journey_sequence' in df_journey.columns:
                    # Convert journey sequences to proper format
                    sequences = df_journey['journey_sequence'].apply(lambda x: x if isinstance(x, list) else [])
                    unique_nodes = pd.Series([item for sublist in sequences for item in sublist]).unique()
                    
                    if len(unique_nodes) > 1:
                        # Create node mapping
                        node_map = {node: idx for idx, node in enumerate(unique_nodes)}
                        
                        # Prepare source and target arrays
                        sources = []
                        targets = []
                        values = []
                        
                        for sequence in sequences:
                            if len(sequence) > 1:
                                for i in range(len(sequence) - 1):
                                    sources.append(node_map[sequence[i]])
                                    targets.append(node_map[sequence[i + 1]])
                                    values.append(1)
                        
                        fig = go.Figure(data=[go.Sankey(
                            node=dict(
                                pad=15,
                                thickness=20,
                                line=dict(color="black", width=0.5),
                                label=unique_nodes,
                                color="blue"
                            ),
                            link=dict(
                                source=sources,
                                target=targets,
                                value=values
                            )
                        )])
                        
                        fig.update_layout(title_text="Customer Journey Flow", font_size=10)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data points to create a meaningful journey flow diagram")
                else:
                    st.warning("No journey sequence data available")
            except Exception as e:
                log_error(e, "Journey mapping visualization")
                st.error("Failed to load journey mapping data")
        
        # Detailed Analysis Section
        st.markdown("---")
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "Touchpoint Analysis",
            "Segment Preferences",
            "Interaction Summaries",
            "Raw Data"
        ])
        
        with tab1:
            # Touchpoint Effectiveness
            touchpoint_query = """
                SELECT 
                    source_type,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    COUNT(*) as interaction_count
                FROM ANALYTICS.SENTIMENT_ANALYSIS
                GROUP BY source_type
                ORDER BY avg_sentiment DESC;
            """
            try:
                touchpoint_data = execute_query(touchpoint_query)
                df_touchpoint = pd.DataFrame(touchpoint_data, columns=['source_type', 'avg_sentiment', 'interaction_count'])
                
                # Create bar chart with error bars
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_touchpoint['source_type'],
                    y=df_touchpoint['avg_sentiment'],
                    error_y=dict(
                        type='data',
                        array=df_touchpoint['avg_sentiment'] * 0.1
                    ),
                    name='Average Sentiment'
                ))
                
                fig.update_layout(
                    title='Touchpoint Effectiveness',
                    xaxis_title='Touchpoint Type',
                    yaxis_title='Average Sentiment'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Touchpoint analysis visualization")
                st.error("Failed to load touchpoint analysis data")
        
        with tab2:
            # Interaction Type Preferences by Customer Segment
            segment_query = """
                SELECT 
                    cb.persona,
                    ci.interaction_type,
                    COUNT(*) as interaction_count
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS ci
                JOIN ANALYTICS.CUSTOMER_BASE cb ON ci.customer_id = cb.customer_id
                GROUP BY cb.persona, ci.interaction_type
                ORDER BY cb.persona, interaction_count DESC;
            """
            try:
                segment_data = execute_query(segment_query)
                
                if not segment_data:
                    st.warning("No data returned from the segment query")
                    return
                
                # Convert list of dictionaries to DataFrame
                df_segment = pd.DataFrame(segment_data, columns=['persona', 'interaction_type', 'interaction_count'])
                
                # Create grouped bar chart
                if not df_segment.empty:
                    fig = px.bar(
                        df_segment,
                        x='interaction_type',
                        y='interaction_count',
                        color='persona',
                        title='Interaction Type Preferences by Customer Segment',
                        labels={
                            'interaction_type': 'Interaction Type',
                            'interaction_count': 'Interaction Count',
                            'persona': 'Customer Segment'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for segment preferences")
            except Exception as e:
                log_error(e, "Segment preferences visualization")
                st.error("Failed to load segment preferences data")
        
        with tab3:
            # Customer Interaction Summaries
            summaries_query = """
                SELECT 
                    customer_id,
                    customer_summary
                FROM ANALYTICS.INSIGHT_SUMMARIES
                ORDER BY customer_id;
            """
            try:
                summaries_data = execute_query(summaries_query)
                df_summaries = pd.DataFrame(summaries_data, columns=['customer_id', 'customer_summary'])
                
                if not df_summaries.empty:
                    # Create word cloud
                    text = ' '.join(df_summaries['customer_summary'].dropna())
                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                    
                    # Create a new figure
                    plt.figure(figsize=(10, 5))
                    plt.clf()  # Clear the current figure
                    plt.imshow(wordcloud.to_array())
                    plt.axis('off')
                    plt.title('Customer Interaction Themes')
                    st.pyplot(plt)
                    plt.close()  # Close the figure to free memory
                else:
                    st.warning("No customer summaries available")
            except Exception as e:
                log_error(e, "Interaction summaries visualization")
                st.error("Failed to load interaction summaries data")
        
        with tab4:
            # Raw Data Display
            raw_data_query = """
                SELECT 
                    customer_id,
                    interaction_type,
                    interaction_date,
                    sentiment_score
                FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
                ORDER BY interaction_date DESC
                LIMIT 100;
            """
            try:
                raw_data = execute_query(raw_data_query)
                df_raw = pd.DataFrame(raw_data, columns=['customer_id', 'interaction_type', 'interaction_date', 'sentiment_score'])
                
                if not df_raw.empty:
                    st.dataframe(df_raw)
                else:
                    st.warning("No raw data available")
            except Exception as e:
                log_error(e, "Raw data display")
                st.error("Failed to load raw data")
                
    except Exception as e:
        log_error(e, "Customer Journey page")
        st.error("An error occurred while loading the Customer Journey page") 