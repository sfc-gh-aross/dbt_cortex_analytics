def get_sentiment_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    WITH current_period AS (
        SELECT AVG(sentiment_score) as avg_sentiment
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    ),
    previous_period AS (
        SELECT AVG(sentiment_score) as avg_sentiment
        FROM ANALYTICS.SENTIMENT_ANALYSIS
        WHERE interaction_date BETWEEN 
            DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
            DATEADD(day, -1, '{start_date}')
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    )
    SELECT 
        current_period.avg_sentiment,
        current_period.avg_sentiment - previous_period.avg_sentiment as sentiment_delta
    FROM current_period, previous_period
    """

def get_interactions_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    WITH current_period AS (
        SELECT COUNT(*) as total_interactions
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    ),
    previous_period AS (
        SELECT COUNT(*) as total_interactions
        FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
        WHERE interaction_date BETWEEN 
            DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
            DATEADD(day, -1, '{start_date}')
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    )
    SELECT 
        current_period.total_interactions,
        current_period.total_interactions - previous_period.total_interactions as interactions_delta
    FROM current_period, previous_period
    """

def get_churn_risk_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    WITH current_period AS (
        SELECT 
            ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        WHERE churn_risk IS NOT NULL
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    ),
    previous_period AS (
        SELECT 
            ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
        FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
        WHERE churn_risk IS NOT NULL
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    )
    SELECT 
        current_period.high_risk_percentage,
        current_period.high_risk_percentage - previous_period.high_risk_percentage as risk_delta
    FROM current_period, previous_period
    """

def get_rating_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    WITH current_period AS (
        SELECT AVG(review_rating) as avg_rating
        FROM ANALYTICS.FACT_PRODUCT_REVIEWS
        WHERE review_date BETWEEN '{start_date}' AND '{end_date}'
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    ),
    previous_period AS (
        SELECT AVG(review_rating) as avg_rating
        FROM ANALYTICS.FACT_PRODUCT_REVIEWS
        WHERE review_date BETWEEN 
            DATEADD(day, -DATEDIFF(day, '{start_date}', '{end_date}'), '{start_date}') AND 
            DATEADD(day, -1, '{start_date}')
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
        {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    )
    SELECT 
        current_period.avg_rating,
        current_period.avg_rating - previous_period.avg_rating as rating_delta
    FROM current_period, previous_period
    """

def get_sentiment_trend_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    SELECT 
        DATE_TRUNC('month', interaction_date) as month,
        AVG(sentiment_score) as avg_sentiment
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN '{start_date}' AND '{end_date}'
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    GROUP BY month
    ORDER BY month
    """

def get_sentiment_dist_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    SELECT 
        overall_sentiment,
        COUNT(*) as count
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    WHERE 1=1
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    GROUP BY overall_sentiment
    ORDER BY count DESC
    """

def get_churn_risk_breakdown_query(start_date, end_date, selected_value_segments, selected_personas):
    return f"""
    SELECT 
        churn_risk,
        COUNT(*) as count
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    WHERE churn_risk IS NOT NULL
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_BASE WHERE persona IN ({','.join(['%s'] * len(selected_value_segments))}))" if selected_value_segments else ""}
    {f"AND customer_id IN (SELECT customer_id FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS WHERE derived_persona IN ({','.join(['%s'] * len(selected_personas))}))" if selected_personas else ""}
    GROUP BY churn_risk
    ORDER BY 
        CASE churn_risk
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
        END
    """ 