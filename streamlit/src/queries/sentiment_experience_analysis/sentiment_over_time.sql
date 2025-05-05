SELECT 
    DATE_TRUNC('day', interaction_date) as date,
    interaction_source,
    AVG(sentiment_score) as avg_sentiment
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
GROUP BY 1, 2
ORDER BY 1, 2; 