WITH customer_segments AS (
    SELECT
        c.customer_id,
        c.persona,
        CASE
            WHEN c.lifetime_value > 1000 THEN 'High Value'
            WHEN c.lifetime_value > 500 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS value_segment,
        CASE
            WHEN c.products_owned >= 3 THEN 'Power User'
            WHEN c.products_owned = 2 THEN 'Regular User'
            ELSE 'New User'
        END AS usage_segment,
        CASE
            WHEN AVG(COALESCE(i.sentiment_score, 0)) > 0.5 THEN 'Positive'
            WHEN AVG(COALESCE(i.sentiment_score, 0)) < -0.5 THEN 'Negative'
            ELSE 'Neutral'
        END AS sentiment_segment
    FROM ANALYTICS.CUSTOMER_BASE c
    LEFT JOIN ANALYTICS.FACT_CUSTOMER_INTERACTIONS i ON c.customer_id = i.customer_id
    GROUP BY 1, 2, 3, 4
)
SELECT
    value_segment || ' - ' || usage_segment || ' - ' || sentiment_segment AS segment,
    COUNT(*) as customer_count,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as FLOAT) as percentage
FROM customer_segments
GROUP BY 1
ORDER BY 2 DESC; 