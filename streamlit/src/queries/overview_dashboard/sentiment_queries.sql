-- Overview Dashboard Sentiment Queries
-- Purpose: Contains SQL queries for sentiment analysis and visualization
-- Input Parameters: start_date, end_date, selected_value_segments, selected_personas
-- Output: Sentiment trend data and distribution data

-- Sentiment Trend Query
-- Returns: month, avg_sentiment
SELECT 
    DATE_TRUNC('month', interaction_date) as month,
    AVG(sentiment_score) as avg_sentiment
FROM ANALYTICS.SENTIMENT_ANALYSIS
WHERE interaction_date BETWEEN :start_date AND :end_date
{value_segment_filter}
{persona_filter}
GROUP BY month
ORDER BY month;

-- Customer Sentiment Distribution Query
-- Returns: overall_sentiment, count
SELECT 
    overall_sentiment,
    COUNT(*) as count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE 1=1
{value_segment_filter}
{persona_filter}
GROUP BY overall_sentiment
ORDER BY count DESC; 