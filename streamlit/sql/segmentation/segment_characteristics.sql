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
),
segment_metrics AS (
    SELECT
        value_segment || ' - ' || usage_segment || ' - ' || sentiment_segment AS segment,
        COUNT(DISTINCT c.customer_id) AS customer_count,
        AVG(c.lifetime_value) AS avg_lifetime_value,
        AVG(c.products_owned) AS avg_products_owned,
        AVG(COALESCE(i.sentiment_score, 0)) AS avg_sentiment,
        COUNT(DISTINCT t.ticket_id) AS ticket_count,
        AVG(r.review_rating) AS avg_review_rating
    FROM customer_segments cs
    JOIN ANALYTICS.CUSTOMER_BASE c ON cs.customer_id = c.customer_id
    LEFT JOIN ANALYTICS.FACT_CUSTOMER_INTERACTIONS i ON c.customer_id = i.customer_id
    LEFT JOIN ANALYTICS.FACT_SUPPORT_TICKETS t ON c.customer_id = t.customer_id
    LEFT JOIN ANALYTICS.FACT_PRODUCT_REVIEWS r ON c.customer_id = r.customer_id
    GROUP BY 1
)
SELECT
    segment,
    'Lifetime Value' AS metric,
    ROUND(avg_lifetime_value, 2) AS value
FROM segment_metrics
UNION ALL
SELECT
    segment,
    'Products Owned' AS metric,
    ROUND(avg_products_owned, 1) AS value
FROM segment_metrics
UNION ALL
SELECT
    segment,
    'Sentiment Score' AS metric,
    ROUND(avg_sentiment, 2) AS value
FROM segment_metrics
UNION ALL
SELECT
    segment,
    'Support Tickets' AS metric,
    ROUND(ticket_count * 1.0 / customer_count, 2) AS value
FROM segment_metrics
UNION ALL
SELECT
    segment,
    'Review Rating' AS metric,
    ROUND(avg_review_rating, 1) AS value
FROM segment_metrics
ORDER BY segment, metric; 