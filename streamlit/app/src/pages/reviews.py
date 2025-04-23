import streamlit as st
import pandas as pd
from src.data.connection import execute_query
from src.utils.logging import log_error
from src.utils.visualization import (
    create_interactive_chart,
    create_drilldown_chart,
    create_comparison_chart,
    add_export_options
)
import plotly.express as px
from typing import Dict

def render_reviews_page(active_filters: Dict):
    """Render the product feedback page with applied filters."""
    st.title("Product Reviews Analysis")
    
    # Main content
    
    # Example review metrics (replace with actual data)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Average Rating", "4.5", "+0.2")
    with metric_cols[1]:
        st.metric("Total Reviews", "2,345", "+15%")
    with metric_cols[2]:
        st.metric("Positive Reviews", "85%", "+5%")
    with metric_cols[3]:
        st.metric("Response Rate", "95%", "+2%")
    
    # Example rating trends chart (replace with actual data)
    st.markdown("### Rating Trends")
    if "date_range" in active_filters:
        start_date, end_date = active_filters["date_range"]
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        ratings = [4.2, 4.3, 4.4, 4.5, 4.6, 4.5, 4.7] * (len(date_range) // 7 + 1)
        ratings = ratings[:len(date_range)]  # Ensure same length
        
        chart_data = pd.DataFrame({
            'Date': date_range,
            'Average Rating': ratings
        })
        st.line_chart(chart_data.set_index('Date'))
    
    # Example review distribution (replace with actual data)
    st.markdown("### Review Distribution")
    rating_data = pd.DataFrame({
        'Rating': [1, 2, 3, 4, 5],
        'Count': [50, 100, 200, 800, 1200]
    })
    st.bar_chart(rating_data.set_index('Rating'))

    try:
        # Page header
        st.header("Product Feedback Analytics")
        st.markdown("Analyze customer reviews and feedback across products")
        
        # Key Metrics Section
        st.subheader("Key Metrics")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Review Ratings",
            "Sentiment by Product",
            "Review Volume Trends"
        ])
        
        with tab1:
            ratings_query = """
                SELECT 
                    product_id,
                    ROUND(AVG(review_rating), 2) as avg_rating,
                    COUNT(*) as review_count,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY product_id
                ORDER BY avg_rating DESC;
            """
            try:
                ratings_data = execute_query(ratings_query)
                df_ratings = pd.DataFrame(ratings_data, columns=['product_id', 'avg_rating', 'review_count', 'unique_customers'])
                # Ensure proper data types
                df_ratings['product_id'] = df_ratings['product_id'].astype('string')
                df_ratings['avg_rating'] = pd.to_numeric(df_ratings['avg_rating'], errors='coerce').astype('float64')
                df_ratings['review_count'] = pd.to_numeric(df_ratings['review_count'], errors='coerce').astype('Int64')
                df_ratings['unique_customers'] = pd.to_numeric(df_ratings['unique_customers'], errors='coerce').astype('Int64')
                
                if not df_ratings.empty:
                    fig = px.bar(
                        df_ratings,
                        x='product_id',
                        y='avg_rating',
                        color='review_count',
                        title='Average Ratings by Product',
                        labels={
                            'product_id': 'Product ID',
                            'avg_rating': 'Average Rating',
                            'review_count': 'Number of Reviews'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No ratings data available")
            except Exception as e:
                log_error(e, "Ratings visualization")
                st.error("Failed to load ratings data")
        
        with tab2:
            sentiment_query = """
                SELECT 
                    pr.product_id,
                    ROUND(AVG(pr.sentiment_score), 2) as avg_sentiment,
                    COUNT(*) as review_count
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS pr
                GROUP BY pr.product_id
                ORDER BY avg_sentiment DESC;
            """
            try:
                sentiment_data = execute_query(sentiment_query)
                df_sentiment = pd.DataFrame(sentiment_data, columns=['product_id', 'avg_sentiment', 'review_count'])
                
                if not df_sentiment.empty:
                    fig = px.scatter(
                        df_sentiment,
                        x='product_id',
                        y='avg_sentiment',
                        size='review_count',
                        title='Sentiment Analysis by Product',
                        labels={
                            'product_id': 'Product ID',
                            'avg_sentiment': 'Average Sentiment',
                            'review_count': 'Number of Reviews'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No sentiment data available")
            except Exception as e:
                log_error(e, "Sentiment visualization")
                st.error("Failed to load sentiment data")
        
        with tab3:
            volume_query = """
                SELECT 
                    DATE_TRUNC('month', review_date) as month,
                    COUNT(*) as review_count
                FROM ANALYTICS.FACT_PRODUCT_REVIEWS
                GROUP BY month
                ORDER BY month;
            """
            try:
                volume_data = execute_query(volume_query)
                df_volume = pd.DataFrame(volume_data, columns=['month', 'review_count'])
                
                if not df_volume.empty:
                    fig = px.line(
                        df_volume,
                        x='month',
                        y='review_count',
                        title='Review Volume Trends',
                        labels={
                            'month': 'Month',
                            'review_count': 'Number of Reviews'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No volume data available")
            except Exception as e:
                log_error(e, "Volume trends visualization")
                st.error("Failed to load volume trends data")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        log_error(e, "Reviews page rendering") 