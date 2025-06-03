SELECT
    DATE_TRUNC('day', interaction_date) as date,
    CASE
        WHEN lifetime_value > 1000 THEN 'High Value'
        WHEN lifetime_value > 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS value_segment,
    CAST(AVG(sentiment_score) as FLOAT) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
GROUP BY 1, 2
ORDER BY 1, 2; 