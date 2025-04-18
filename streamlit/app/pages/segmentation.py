import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data.connection import execute_query
from src.utils.logging import log_query_execution, log_error

def render_segmentation_page():
    """Render the Segmentation & Value workspace."""
    try:
        # Page header
        st.header("Segmentation & Value Analytics")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Customer Lifetime Value Distribution
        with col1:
            st.subheader("Lifetime Value")
            value_query = """
                SELECT 
                    CASE 
                        WHEN lifetime_value >= 1000 THEN 'High Value'
                        WHEN lifetime_value >= 500 THEN 'Medium Value'
                        ELSE 'Low Value'
                    END as value_segment,
                    COUNT(*) as customer_count,
                    ROUND(AVG(lifetime_value), 2) as avg_value
                FROM ANALYTICS.CUSTOMER_BASE
                GROUP BY value_segment
                ORDER BY avg_value DESC;
            """
            try:
                value_data = execute_query(value_query)
                df_value = pd.DataFrame(value_data)
                
                # Create violin plot
                fig = px.violin(
                    df_value,
                    y='avg_value',
                    x='value_segment',
                    box=True,
                    points="all",
                    title='Customer Lifetime Value Distribution',
                    labels={
                        'value_segment': 'Value Segment',
                        'avg_value': 'Lifetime Value',
                        'customer_count': 'Customer Count'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Lifetime value visualization")
                st.error("Failed to load lifetime value data")
        
        # Customer Persona Distribution
        with col2:
            st.subheader("Persona Distribution")
            persona_query = """
                SELECT 
                    persona,
                    COUNT(*) as customer_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM ANALYTICS.CUSTOMER_BASE
                GROUP BY persona
                ORDER BY customer_count DESC;
            """
            try:
                persona_data = execute_query(persona_query)
                df_persona = pd.DataFrame(persona_data)
                
                # Create pie chart
                fig = px.pie(
                    df_persona,
                    values='customer_count',
                    names='persona',
                    title='Customer Persona Distribution',
                    labels={
                        'persona': 'Persona',
                        'customer_count': 'Customer Count',
                        'percentage': 'Percentage'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Persona distribution visualization")
                st.error("Failed to load persona distribution data")
        
        # Churn Risk Indicators
        with col3:
            st.subheader("Churn Risk")
            churn_query = """
                SELECT 
                    churn_risk,
                    COUNT(*) as customer_count,
                    ROUND(AVG(avg_sentiment), 3) as avg_sentiment,
                    ROUND(AVG(ticket_count), 2) as avg_tickets
                FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
                GROUP BY churn_risk
                ORDER BY 
                    CASE churn_risk
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'Low' THEN 3
                    END;
            """
            try:
                churn_data = execute_query(churn_query)
                df_churn = pd.DataFrame(churn_data)
                
                # Create gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=df_churn[df_churn['churn_risk'] == 'High']['customer_count'].iloc[0],
                    title={'text': "High Risk Customers"},
                    gauge={
                        'axis': {'range': [0, df_churn['customer_count'].sum()]},
                        'bar': {'color': "red"},
                        'steps': [
                            {'range': [0, df_churn[df_churn['churn_risk'] == 'Low']['customer_count'].iloc[0]], 'color': "lightgray"},
                            {'range': [df_churn[df_churn['churn_risk'] == 'Low']['customer_count'].iloc[0], df_churn[df_churn['churn_risk'] == 'Medium']['customer_count'].iloc[0]], 'color': "gray"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Churn risk visualization")
                st.error("Failed to load churn risk data")
        
        # Detailed Analysis Section
        st.markdown("---")
        st.subheader("Detailed Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs([
            "Upsell Opportunities",
            "Value Correlations",
            "Raw Data"
        ])
        
        with tab1:
            # Upsell Opportunity Identification
            upsell_query = """
                SELECT 
                    upsell_opportunity,
                    COUNT(*) as customer_count,
                    ROUND(AVG(lifetime_value), 2) as avg_lifetime_value,
                    ROUND(AVG(avg_sentiment), 3) as avg_sentiment
                FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
                JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
                GROUP BY upsell_opportunity
                ORDER BY 
                    CASE upsell_opportunity
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'Low' THEN 3
                    END;
            """
            try:
                upsell_data = execute_query(upsell_query)
                df_upsell = pd.DataFrame(upsell_data)
                
                # Create scatter plot with quadrants
                fig = px.scatter(
                    df_upsell,
                    x='avg_lifetime_value',
                    y='avg_sentiment',
                    size='customer_count',
                    color='upsell_opportunity',
                    title='Upsell Opportunity vs. Current Value',
                    labels={
                        'avg_lifetime_value': 'Current Lifetime Value',
                        'avg_sentiment': 'Average Sentiment',
                        'customer_count': 'Customer Count',
                        'upsell_opportunity': 'Upsell Opportunity'
                    }
                )
                
                # Add quadrant lines
                fig.add_shape(
                    type="line",
                    x0=df_upsell['avg_lifetime_value'].mean(),
                    y0=df_upsell['avg_sentiment'].min(),
                    x1=df_upsell['avg_lifetime_value'].mean(),
                    y1=df_upsell['avg_sentiment'].max(),
                    line=dict(color="gray", width=1, dash="dash")
                )
                fig.add_shape(
                    type="line",
                    x0=df_upsell['avg_lifetime_value'].min(),
                    y0=df_upsell['avg_sentiment'].mean(),
                    x1=df_upsell['avg_lifetime_value'].max(),
                    y1=df_upsell['avg_sentiment'].mean(),
                    line=dict(color="gray", width=1, dash="dash")
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Upsell opportunity visualization")
                st.error("Failed to load upsell opportunity data")
        
        with tab2:
            # Value vs. Sentiment Correlation
            correlation_query = """
                SELECT 
                    CORR(cb.lifetime_value, cps.avg_sentiment) as value_sentiment_correlation,
                    CORR(cb.lifetime_value, tp.ticket_count) as value_ticket_correlation,
                    CORR(cb.lifetime_value, pr.review_rating) as value_rating_correlation
                FROM ANALYTICS.CUSTOMER_BASE cb
                JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps USING (customer_id)
                JOIN ANALYTICS.TICKET_PATTERNS tp USING (customer_id)
                JOIN ANALYTICS.FACT_PRODUCT_REVIEWS pr USING (customer_id);
            """
            try:
                correlation_data = execute_query(correlation_query)
                correlations = correlation_data[0]
                
                # Create correlation heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=[[correlations['value_sentiment_correlation'], correlations['value_ticket_correlation'], correlations['value_rating_correlation']]],
                    x=['Sentiment', 'Ticket Count', 'Review Rating'],
                    y=['Lifetime Value'],
                    colorscale='RdYlGn',
                    zmin=-1,
                    zmax=1
                ))
                
                fig.update_layout(
                    title='Value Correlation Analysis',
                    xaxis_title='Metric',
                    yaxis_title='Lifetime Value'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                log_error(e, "Value correlation visualization")
                st.error("Failed to load value correlation data")
        
        with tab3:
            raw_data_query = """
                SELECT 
                    customer_id,
                    persona,
                    lifetime_value,
                    churn_risk,
                    upsell_opportunity,
                    avg_sentiment
                FROM ANALYTICS.CUSTOMER_BASE cb
                JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps USING (customer_id)
                ORDER BY lifetime_value DESC
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
        log_error(e, "Segmentation page rendering")
        st.error("An error occurred while rendering the segmentation and value page") 