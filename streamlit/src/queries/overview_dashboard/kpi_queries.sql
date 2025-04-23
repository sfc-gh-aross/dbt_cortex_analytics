-- Overview Dashboard KPI Queries
-- Purpose: Contains SQL queries for calculating key performance indicators
-- Input Parameters: start_date, end_date, selected_value_segments, selected_personas
-- Output: Various KPI metrics including average sentiment, total interactions, churn risk, and product ratings

-- Average Sentiment KPI Query
-- Returns: current_period_avg_sentiment, previous_period_avg_sentiment, sentiment_delta
WITH current_period AS (
    SELECT AVG(sentiment_score) as avg_sentiment
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN :start_date AND :end_date
    {value_segment_filter}
    {persona_filter}
),
previous_period AS (
    SELECT AVG(sentiment_score) as avg_sentiment
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN 
        DATEADD(day, -DATEDIFF(day, :start_date, :end_date), :start_date) AND 
        DATEADD(day, -1, :start_date)
    {value_segment_filter}
    {persona_filter}
)
SELECT 
    current_period.avg_sentiment as current_period_avg_sentiment,
    previous_period.avg_sentiment as previous_period_avg_sentiment,
    current_period.avg_sentiment - previous_period.avg_sentiment as sentiment_delta
FROM current_period, previous_period;

-- Total Interactions KPI Query
-- Returns: current_period_total_interactions, previous_period_total_interactions, interactions_delta
WITH current_period AS (
    SELECT COUNT(*) as total_interactions
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
    WHERE interaction_date BETWEEN :start_date AND :end_date
    {value_segment_filter}
    {persona_filter}
),
previous_period AS (
    SELECT COUNT(*) as total_interactions
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
    WHERE interaction_date BETWEEN 
        DATEADD(day, -DATEDIFF(day, :start_date, :end_date), :start_date) AND 
        DATEADD(day, -1, :start_date)
    {value_segment_filter}
    {persona_filter}
)
SELECT 
    current_period.total_interactions as current_period_total_interactions,
    previous_period.total_interactions as previous_period_total_interactions,
    current_period.total_interactions - previous_period.total_interactions as interactions_delta
FROM current_period, previous_period;

-- Churn Risk KPI Query
-- Returns: high_risk_percentage, previous_high_risk_percentage, risk_delta
WITH current_period AS (
    SELECT 
        ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    WHERE churn_risk IS NOT NULL
    {value_segment_filter}
    {persona_filter}
),
previous_period AS (
    SELECT 
        ROUND(COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as high_risk_percentage
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    WHERE churn_risk IS NOT NULL
    {value_segment_filter}
    {persona_filter}
)
SELECT 
    current_period.high_risk_percentage,
    previous_period.high_risk_percentage as previous_high_risk_percentage,
    current_period.high_risk_percentage - previous_period.high_risk_percentage as risk_delta
FROM current_period, previous_period;

-- Average Product Rating KPI Query
-- Returns: current_period_avg_rating, previous_period_avg_rating, rating_delta
WITH current_period AS (
    SELECT AVG(review_rating) as avg_rating
    FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    WHERE review_date BETWEEN :start_date AND :end_date
    {value_segment_filter}
    {persona_filter}
),
previous_period AS (
    SELECT AVG(review_rating) as avg_rating
    FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    WHERE review_date BETWEEN 
        DATEADD(day, -DATEDIFF(day, :start_date, :end_date), :start_date) AND 
        DATEADD(day, -1, :start_date)
    {value_segment_filter}
    {persona_filter}
)
SELECT 
    current_period.avg_rating as current_period_avg_rating,
    previous_period.avg_rating as previous_period_avg_rating,
    current_period.avg_rating - previous_period.avg_rating as rating_delta
FROM current_period, previous_period; 