import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_reviews_page():
    """Render the Product Feedback workspace."""
    try:
        # Page header
        st.header("Product Feedback Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Rating Distribution
        with col1:
            st.subheader("Rating Distribution")
            rating_query = """
                SELECT 
                    review_rating,
                    COUNT(*) as review_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY review_rating
                ORDER BY review_rating;
            """
            try:
                rating_data = execute_query(rating_query)
                if rating_data:
                    df_rating = pd.DataFrame(rating_data, columns=['review_rating', 'review_count', 'percentage'])
                    
                    # Create histogram
                    fig = px.histogram(
                        df_rating,
                        x='review_rating',
                        y='review_count',
                        title='Review Rating Distribution',
                        labels={
                            'review_rating': 'Rating',
                            'review_count': 'Review Count',
                            'percentage': 'Percentage'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No rating data available")
            except Exception as e:
                log_error(e, "Rating distribution visualization")
                st.error("Failed to load rating distribution data")
        
        # Review Sentiment by Product
        with col2:
            st.subheader("Sentiment by Product")
            sentiment_query = """
                SELECT 
                    product_id,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    ROUND(AVG(review_rating), 2) as avg_rating,
                    COUNT(*) as review_count
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY product_id
                ORDER BY avg_sentiment DESC;
            """
            try:
                sentiment_data = execute_query(sentiment_query)
                if sentiment_data:
                    df_sentiment = pd.DataFrame(sentiment_data, columns=['product_id', 'avg_sentiment', 'avg_rating', 'review_count'])
                    
                    # Create bubble chart
                    fig = px.scatter(
                        df_sentiment,
                        x='avg_sentiment',
                        y='avg_rating',
                        size='review_count',
                        color='product_id',
                        title='Review Sentiment by Product',
                        labels={
                            'avg_sentiment': 'Average Sentiment',
                            'avg_rating': 'Average Rating',
                            'review_count': 'Review Count',
                            'product_id': 'Product'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No sentiment data available")
            except Exception as e:
                log_error(e, "Sentiment by product visualization")
                st.error("Failed to load sentiment by product data")
        
        # Review Volume Trends
        with col3:
            st.subheader("Review Volume")
            volume_query = """
                SELECT 
                    DATE_TRUNC('day', review_date) as date,
                    COUNT(*) as review_count,
                    ROUND(AVG(review_rating), 2) as avg_rating
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY date
                ORDER BY date;
            """
            try:
                volume_data = execute_query(volume_query)
                if volume_data:
                    df_volume = pd.DataFrame(volume_data, columns=['date', 'review_count', 'avg_rating'])
                    
                    # Create area chart
                    fig = px.area(
                        df_volume,
                        x='date',
                        y='review_count',
                        title='Review Volume Trends',
                        labels={
                            'date': 'Date',
                            'review_count': 'Review Count',
                            'avg_rating': 'Average Rating'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No volume data available")
            except Exception as e:
                log_error(e, "Review volume visualization")
                st.error("Failed to load review volume data")
        
        # Detailed Analysis Section
        st.markdown("---")
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Multilingual Analysis",
            "Rating-Sentiment Correlation",
            "Raw Data"
        ])
        
        with tab1:
            # Multilingual Review Analysis
            language_query = """
                SELECT 
                    review_language,
                    COUNT(*) as review_count,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    ROUND(AVG(review_rating), 2) as avg_rating
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY review_language
                ORDER BY review_count DESC;
            """
            try:
                language_data = execute_query(language_query)
                if language_data:
                    df_language = pd.DataFrame(language_data, columns=['review_language', 'review_count', 'avg_sentiment', 'avg_rating'])
                    
                    # Create radar chart
                    fig = go.Figure()
                    
                    for language in df_language['review_language']:
                        language_data = df_language[df_language['review_language'] == language]
                        if not language_data.empty:
                            fig.add_trace(go.Scatterpolar(
                                r=[
                                    language_data['review_count'].iloc[0],
                                    language_data['avg_sentiment'].iloc[0],
                                    language_data['avg_rating'].iloc[0]
                                ],
                                theta=['Review Count', 'Average Sentiment', 'Average Rating'],
                                fill='toself',
                                name=language
                            ))
                    
                    if len(fig.data) > 0:
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, max(df_language['review_count'])]
                                )
                            ),
                            title='Multilingual Review Analysis',
                            showlegend=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No language data available for visualization")
                else:
                    st.warning("No language data available")
            except Exception as e:
                log_error(e, "Multilingual analysis visualization")
                st.error("Failed to load multilingual analysis data")
        
        with tab2:
            # Review Sentiment vs. Product Rating Correlation
            correlation_query = """
                SELECT 
                    review_rating,
                    sentiment_score,
                    COUNT(*) as review_count
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY review_rating, sentiment_score
                ORDER BY review_rating, sentiment_score;
            """
            try:
                correlation_data = execute_query(correlation_query)
                if correlation_data:
                    df_correlation = pd.DataFrame(correlation_data, columns=['review_rating', 'sentiment_score', 'review_count'])
                    
                    # Create scatter plot with color gradient
                    fig = px.scatter(
                        df_correlation,
                        x='review_rating',
                        y='sentiment_score',
                        size='review_count',
                        color='review_count',
                        color_continuous_scale='Viridis',
                        title='Review Rating vs. Sentiment Correlation',
                        labels={
                            'review_rating': 'Review Rating',
                            'sentiment_score': 'Sentiment Score',
                            'review_count': 'Review Count'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No correlation data available")
            except Exception as e:
                log_error(e, "Rating-sentiment correlation visualization")
                st.error("Failed to load rating-sentiment correlation data")
        
        with tab3:
            raw_data_query = """
                SELECT 
                    review_id,
                    product_id,
                    review_date,
                    review_rating,
                    sentiment_score,
                    review_language
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                ORDER BY review_date DESC
                LIMIT 1000;
            """
            try:
                raw_data = execute_query(raw_data_query)
                if raw_data:
                    df_raw = pd.DataFrame(raw_data, columns=['review_id', 'product_id', 'review_date', 'review_rating', 'sentiment_score', 'review_language'])
                    st.dataframe(df_raw)
                else:
                    st.warning("No raw data available")
            except Exception as e:
                log_error(e, "Raw data display")
                st.error("Failed to load raw data")
    
    except Exception as e:
        log_error(e, "Reviews page rendering")
        st.error("An error occurred while rendering the product feedback page") 