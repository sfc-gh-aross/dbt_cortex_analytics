-- Daily interaction trend
SELECT
    DATE_TRUNC('day', i.interaction_date) AS DATE,
    COUNT(DISTINCT i.interaction_id) AS INTERACTION_COUNT,
    COUNT(DISTINCT i.customer_id) AS UNIQUE_CUSTOMERS
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
GROUP BY 1
ORDER BY 1; 