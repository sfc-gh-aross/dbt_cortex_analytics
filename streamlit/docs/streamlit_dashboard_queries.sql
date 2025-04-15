-- 1. Overall customer sentiment distribution
SELECT 
    CASE 
        WHEN sentiment_score < -0.3 THEN 'Negative'
        WHEN sentiment_score > 0.3 THEN 'Positive'
        ELSE 'Neutral'
    END as sentiment_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM (
    SELECT sentiment_score FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
    UNION ALL
    SELECT sentiment_score FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    UNION ALL
    SELECT sentiment_score FROM ANALYTICS.FACT_SUPPORT_TICKETS
)
GROUP BY sentiment_category
ORDER BY count DESC;

-- 2. Sentiment trends over time
SELECT 
    DATE_TRUNC('day', interaction_date) as date,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY date
ORDER BY date;

-- 3. Sentiment by interaction type
SELECT 
    interaction_type,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY interaction_type
ORDER BY avg_sentiment DESC;

-- 4. Sentiment correlation with support ticket volume
WITH daily_metrics AS (
    SELECT 
        DATE_TRUNC('day', interaction_date) as date,
        AVG(sentiment_score) as avg_sentiment,
        COUNT(CASE WHEN source_type = 'ticket' THEN 1 END) as ticket_count
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    GROUP BY date
)
SELECT 
    CORR(avg_sentiment, ticket_count) as sentiment_ticket_correlation
FROM daily_metrics;

-- 5. Sentiment volatility by customer segment
SELECT 
    cb.persona,
    ROUND(AVG(cps.sentiment_volatility), 3) as avg_volatility,
    COUNT(DISTINCT cps.customer_id) as customer_count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY cb.persona
ORDER BY avg_volatility DESC;