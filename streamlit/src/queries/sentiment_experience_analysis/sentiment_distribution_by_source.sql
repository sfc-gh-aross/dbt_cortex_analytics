SELECT 
    interaction_source,
    sentiment_bucket,
    COUNT(*) as interaction_count
FROM (
    SELECT 
        interaction_source,
        CASE 
            WHEN sentiment_score >= 0.6 THEN 'Positive'
            WHEN sentiment_score >= 0.2 THEN 'Slightly Positive'
            WHEN sentiment_score >= -0.2 THEN 'Neutral'
            WHEN sentiment_score >= -0.6 THEN 'Slightly Negative'
            ELSE 'Negative'
        END as sentiment_bucket
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
)
GROUP BY 1, 2
ORDER BY 1, 
    CASE sentiment_bucket
        WHEN 'Positive' THEN 1
        WHEN 'Slightly Positive' THEN 2
        WHEN 'Neutral' THEN 3
        WHEN 'Slightly Negative' THEN 4
        WHEN 'Negative' THEN 5
    END; 