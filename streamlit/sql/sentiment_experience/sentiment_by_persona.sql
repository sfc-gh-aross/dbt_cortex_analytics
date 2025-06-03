SELECT
    DATE_TRUNC('day', interaction_date) AS date,
    cb.persona,
    AVG(sentiment_score) AS avg_sentiment,
    STDDEV(sentiment_score) AS sentiment_volatility,
    (MAX(sentiment_score) - MIN(sentiment_score)) AS sentiment_trend
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
LEFT JOIN ANALYTICS.CUSTOMER_BASE cb ON i.customer_id = cb.customer_id
GROUP BY 1, 2
ORDER BY 1, 2; 