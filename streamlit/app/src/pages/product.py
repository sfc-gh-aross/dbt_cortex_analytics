import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_product_page():
    """Render the Product Performance workspace."""
    try:
        # Page header
        st.header("Product Performance Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Product Rating Distribution
        with col1:
            st.subheader("Product Rating Distribution")
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
                df_rating = pd.DataFrame(rating_data)
                
                # Create histogram
                fig = px.histogram(
                    df_rating,
                    x='review_rating',
                    y='review_count',
                    title='Product Rating Distribution',
                    labels={
                        'review_rating': 'Rating',
                        'review_count': 'Review Count',
                        'percentage': 'Percentage'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Product rating distribution visualization")
                st.error("Failed to load product rating distribution data")
        
        # Feature Adoption Metrics
        with col2:
            st.subheader("Feature Adoption")
            adoption_query = """
                SELECT 
                    ROUND(AVG(active_users_per_feature), 2) as avg_active_users,
                    ROUND(AVG(usage_frequency), 2) as avg_usage_frequency,
                    ROUND(AVG(adoption_rate), 2) as avg_adoption_rate
                FROM ANALYTICS.FACT_FEATURE_USAGE
                WHERE usage_date >= DATEADD(day, -30, CURRENT_DATE());
            """
            try:
                adoption_data = execute_query(adoption_query)
                metrics = adoption_data[0]
                
                # Display metrics in cards
                st.metric("Active Users per Feature", f"{metrics['avg_active_users']}")
                st.metric("Average Usage Frequency", f"{metrics['avg_usage_frequency']}")
                st.metric("Average Adoption Rate", f"{metrics['avg_adoption_rate']}%")
            except Exception as e:
                log_error(e, "Feature adoption metrics visualization")
                st.error("Failed to load feature adoption metrics")
        
        # Performance Metrics
        with col3:
            st.subheader("Performance Metrics")
            performance_query = """
                SELECT 
                    feature_name,
                    ROUND(AVG(response_time_ms), 2) as avg_response_time,
                    ROUND(AVG(error_rate), 2) as avg_error_rate,
                    ROUND(AVG(success_rate), 2) as avg_success_rate
                FROM ANALYTICS.FACT_FEATURE_PERFORMANCE
                GROUP BY feature_name
                ORDER BY avg_response_time DESC
                LIMIT 5;
            """
            try:
                performance_data = execute_query(performance_query)
                df_performance = pd.DataFrame(performance_data)
                
                # Create radar chart
                fig = go.Figure()
                
                # Add traces for each metric
                fig.add_trace(go.Scatterpolar(
                    r=df_performance['avg_response_time'],
                    theta=df_performance['feature_name'],
                    fill='toself',
                    name='Response Time (ms)'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=df_performance['avg_error_rate'],
                    theta=df_performance['feature_name'],
                    fill='toself',
                    name='Error Rate (%)'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=df_performance['avg_success_rate'],
                    theta=df_performance['feature_name'],
                    fill='toself',
                    name='Success Rate (%)'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(df_performance['avg_response_time'])]
                        )
                    ),
                    title='Feature Performance Metrics',
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Performance metrics visualization")
                st.error("Failed to load performance metrics")
        
        # Usage Trends
        with col3:
            st.subheader("Usage Trends")
            trends_query = """
                SELECT 
                    DATE_TRUNC('day', usage_date) as date,
                    COUNT(DISTINCT user_id) as active_users,
                    ROUND(AVG(usage_duration_minutes), 2) as avg_usage_duration
                FROM ANALYTICS.FACT_FEATURE_USAGE
                GROUP BY date
                ORDER BY date;
            """
            try:
                trends_data = execute_query(trends_query)
                df_trends = pd.DataFrame(trends_data)
                
                # Create line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_trends['date'],
                    y=df_trends['active_users'],
                    mode='lines+markers',
                    name='Active Users',
                    line=dict(color='#3b82f6')
                ))
                fig.add_trace(go.Scatter(
                    x=df_trends['date'],
                    y=df_trends['avg_usage_duration'],
                    mode='lines+markers',
                    name='Average Usage Duration',
                    line=dict(color='#10b981'),
                    yaxis='y2'
                ))
                fig.update_layout(
                    title='Daily Usage Trends',
                    yaxis_title='Active Users',
                    yaxis2=dict(
                        title='Average Usage Duration (min)',
                        overlaying='y',
                        side='right'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Usage trends visualization")
                st.error("Failed to load usage trends data")
        
        # Detailed Analysis Section
        st.title("Product Analytics Dashboard")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Feature Usage Patterns",
            "Performance Correlation",
            "Raw Data"
        ])
        
        with tab1:
            patterns_query = """
                SELECT 
                    feature_name,
                    usage_time_of_day,
                    COUNT(*) as usage_count,
                    ROUND(AVG(usage_duration_minutes), 2) as avg_duration
                FROM ANALYTICS.FACT_FEATURE_USAGE
                GROUP BY feature_name, usage_time_of_day
                ORDER BY usage_count DESC;
            """
            try:
                patterns_data = execute_query(patterns_query)
                df_patterns = pd.DataFrame(patterns_data)
                
                # Create heatmap
                fig = px.density_heatmap(
                    df_patterns,
                    x='usage_time_of_day',
                    y='feature_name',
                    z='usage_count',
                    title='Feature Usage Patterns by Time of Day',
                    labels={
                        'usage_time_of_day': 'Time of Day',
                        'feature_name': 'Feature',
                        'usage_count': 'Usage Count'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Usage patterns analysis")
                st.error("Failed to load usage patterns data")
        
        with tab2:
            correlation_query = """
                SELECT 
                    feature_name,
                    ROUND(AVG(response_time_ms), 2) as avg_response_time,
                    ROUND(AVG(usage_frequency), 2) as avg_usage_frequency,
                    ROUND(AVG(user_satisfaction), 2) as avg_satisfaction
                FROM ANALYTICS.FACT_FEATURE_PERFORMANCE
                GROUP BY feature_name;
            """
            try:
                correlation_data = execute_query(correlation_query)
                df_correlation = pd.DataFrame(correlation_data)
                
                # Create scatter plot matrix
                fig = px.scatter_matrix(
                    df_correlation,
                    dimensions=['avg_response_time', 'avg_usage_frequency', 'avg_satisfaction'],
                    color='feature_name',
                    title='Feature Performance Correlation Matrix'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Performance correlation analysis")
                st.error("Failed to load correlation data")
        
        with tab3:
            raw_data_query = """
                SELECT 
                    feature_name,
                    user_id,
                    usage_date,
                    usage_duration_minutes,
                    response_time_ms,
                    error_rate,
                    success_rate
                FROM ANALYTICS.FACT_FEATURE_USAGE
                ORDER BY usage_date DESC
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
        log_error(e, "Product page rendering")
        st.error("An error occurred while rendering the product performance page") 