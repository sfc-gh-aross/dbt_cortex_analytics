import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import numpy as np

def render_insights_page():
    """Render the insights and summaries page."""
    st.header("Insights & Summaries")
    
    # Create tabs for different insights sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Interaction Summaries",
        "Sentiment History",
        "Support Patterns",
        "Sentiment Trends",
        "Sentiment Volatility"
    ])
    
    with tab1:
        st.subheader("Customer Interaction Summaries")
        try:
            # Get customer interaction summaries
            summary_query = """
                SELECT 
                    customer_id,
                    customer_summary
                FROM ANALYTICS.INSIGHT_SUMMARIES
                ORDER BY customer_id;
            """
            summary_data = execute_query(summary_query)
            
            if summary_data:
                # Convert tuples to DataFrame with proper column names
                df_summaries = pd.DataFrame(summary_data, columns=['customer_id', 'customer_summary'])
                
                # Create word cloud from summaries
                all_summaries = ' '.join(df_summaries['customer_summary'].astype(str))
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_summaries)
                
                # Display word cloud
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
                # Display summary table
                st.dataframe(df_summaries)
            else:
                st.warning("No interaction summary data available")
        except Exception as e:
            log_error(e, "Interaction summaries visualization")
            st.error("Failed to load interaction summaries")
    
    with tab2:
        st.subheader("Customer Sentiment History")
        try:
            # Get sentiment history
            sentiment_query = """
                SELECT 
                    customer_id,
                    sentiment_history,
                    avg_sentiment,
                    sentiment_trend
                FROM ANALYTICS.SENTIMENT_TRENDS
                ORDER BY customer_id;
            """
            sentiment_data = execute_query(sentiment_query)
            
            if sentiment_data:
                # Convert tuples to DataFrame with proper column names
                df_sentiment = pd.DataFrame(sentiment_data, columns=['customer_id', 'sentiment_history', 'avg_sentiment', 'sentiment_trend'])
                
                # Create a line chart for each customer's sentiment history
                for _, row in df_sentiment.iterrows():
                    st.write(f"Customer {row['customer_id']}")
                    # Parse the sentiment history string into a list of floats
                    try:
                        sentiment_values = json.loads(row['sentiment_history'])
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            y=sentiment_values,
                            mode='lines',
                            name='Sentiment History'
                        ))
                        fig.update_layout(
                            height=100,
                            showlegend=False,
                            margin=dict(l=0, r=0, t=0, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not parse sentiment history for customer {row['customer_id']}")
                        continue
            else:
                st.warning("No sentiment history data available")
        except Exception as e:
            log_error(e, "Sentiment history visualization")
            st.error("Failed to load sentiment history")
    
    with tab3:
        st.subheader("Customer Support Ticket Patterns")
        try:
            # Get ticket patterns
            ticket_query = """
                SELECT 
                    customer_id,
                    ticket_count,
                    ARRAY_TO_STRING(ticket_categories, ', ') as categories,
                    ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
                FROM ANALYTICS.TICKET_PATTERNS
                ORDER BY ticket_count DESC;
            """
            ticket_data = execute_query(ticket_query)
            
            if ticket_data:
                # Convert tuples to DataFrame with proper column names
                df_tickets = pd.DataFrame(ticket_data, columns=['customer_id', 'ticket_count', 'categories', 'priorities'])
                
                # Convert ticket_count to numeric if it's not already
                df_tickets['ticket_count'] = pd.to_numeric(df_tickets['ticket_count'])
                
                # Create network graph for ticket categories
                st.write("Ticket Category Distribution")
                fig = go.Figure()
                
                # Add nodes and edges based on ticket categories
                fig.add_trace(go.Scatter(
                    x=df_tickets['ticket_count'],
                    y=df_tickets['ticket_count'],
                    mode='markers',
                    text=df_tickets['categories'],
                    marker=dict(
                        size=df_tickets['ticket_count'] * 2,
                        color=df_tickets['ticket_count'],
                        colorscale='Viridis'
                    )
                ))
                
                fig.update_layout(
                    title='Ticket Category Distribution',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display ticket pattern table
                st.dataframe(df_tickets)
            else:
                st.warning("No ticket pattern data available")
        except Exception as e:
            log_error(e, "Ticket patterns visualization")
            st.error("Failed to load ticket patterns")
    
    with tab4:
        st.subheader("Customer Sentiment Trends")
        try:
            # Get sentiment trends
            trend_query = """
                SELECT 
                    customer_id,
                    sentiment_trend,
                    avg_sentiment,
                    sentiment_volatility
                FROM ANALYTICS.SENTIMENT_TRENDS
                ORDER BY sentiment_trend DESC;
            """
            trend_data = execute_query(trend_query)
            
            if trend_data:
                # Convert tuples to DataFrame with proper column names
                df_trends = pd.DataFrame(trend_data, columns=['customer_id', 'sentiment_trend', 'avg_sentiment', 'sentiment_volatility'])
                
                # Convert numeric columns
                df_trends['sentiment_trend'] = pd.to_numeric(df_trends['sentiment_trend'])
                df_trends['avg_sentiment'] = pd.to_numeric(df_trends['avg_sentiment'])
                df_trends['sentiment_volatility'] = pd.to_numeric(df_trends['sentiment_volatility'])
                
                # Create area chart for sentiment trends
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_trends.index,
                    y=df_trends['sentiment_trend'],
                    fill='tozeroy',
                    name='Sentiment Trend'
                ))
                
                fig.update_layout(
                    title='Customer Sentiment Trends',
                    xaxis_title='Customer Index',
                    yaxis_title='Sentiment Trend'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display trend metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Sentiment", f"{df_trends['avg_sentiment'].mean():.2f}")
                with col2:
                    st.metric("Average Volatility", f"{df_trends['sentiment_volatility'].mean():.2f}")
            else:
                st.warning("No sentiment trend data available")
        except Exception as e:
            log_error(e, "Sentiment trends visualization")
            st.error("Failed to load sentiment trends")
    
    with tab5:
        st.subheader("Customer Sentiment Volatility")
        try:
            # Get sentiment volatility
            volatility_query = """
                SELECT 
                    customer_id,
                    sentiment_volatility,
                    avg_sentiment,
                    sentiment_trend
                FROM ANALYTICS.SENTIMENT_TRENDS
                ORDER BY sentiment_volatility DESC;
            """
            volatility_data = execute_query(volatility_query)
            
            if volatility_data:
                # Convert tuples to DataFrame with proper column names
                df_volatility = pd.DataFrame(volatility_data, columns=['customer_id', 'sentiment_volatility', 'avg_sentiment', 'sentiment_trend'])
                
                # Convert numeric columns
                df_volatility['sentiment_volatility'] = pd.to_numeric(df_volatility['sentiment_volatility'])
                df_volatility['avg_sentiment'] = pd.to_numeric(df_volatility['avg_sentiment'])
                df_volatility['sentiment_trend'] = pd.to_numeric(df_volatility['sentiment_trend'])
                
                # Create bar chart with error bars
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_volatility.index,
                    y=df_volatility['sentiment_volatility'],
                    error_y=dict(
                        type='data',
                        array=df_volatility['sentiment_volatility'] * 0.1
                    ),
                    name='Sentiment Volatility'
                ))
                
                fig.update_layout(
                    title='Customer Sentiment Volatility',
                    xaxis_title='Customer Index',
                    yaxis_title='Volatility'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display volatility metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Highest Volatility", f"{df_volatility['sentiment_volatility'].max():.2f}")
                with col2:
                    st.metric("Average Volatility", f"{df_volatility['sentiment_volatility'].mean():.2f}")
            else:
                st.warning("No sentiment volatility data available")
        except Exception as e:
            log_error(e, "Sentiment volatility visualization")
            st.error("Failed to load sentiment volatility") 