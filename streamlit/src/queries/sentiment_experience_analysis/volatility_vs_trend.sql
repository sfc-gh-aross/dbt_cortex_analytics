WITH customer_sentiment_stats AS (
    SELECT 
        customer_id,
        AVG(sentiment_score) as avg_sentiment,
        STDDEV(sentiment_score) as sentiment_volatility,
        COUNT(*) as interaction_count
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN :start_date AND :end_date
        {% if selected_value_segments %}
        AND customer_id IN (
            SELECT customer_id 
            FROM ANALYTICS.CUSTOMER_BASE 
            WHERE CASE 
                WHEN lifetime_value >= 1000 THEN 'High Value'
                WHEN lifetime_value >= 500 THEN 'Medium Value'
                ELSE 'Low Value'
            END IN :selected_value_segments
        )
        {% endif %}
        {% if selected_personas %}
        AND customer_id IN (
            SELECT customer_id 
            FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS 
            WHERE derived_persona IN :selected_personas
        )
        {% endif %}
    GROUP BY 1
    HAVING COUNT(*) >= 3  -- Only include customers with sufficient interactions
)
SELECT 
    customer_id,
    avg_sentiment,
    sentiment_volatility,
    interaction_count
FROM customer_sentiment_stats
ORDER BY interaction_count DESC; 