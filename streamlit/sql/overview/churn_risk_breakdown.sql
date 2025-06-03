-- Churn risk breakdown by persona
SELECT
    c.persona as PERSONA,
    cps.churn_risk as CHURN_RISK,
    COUNT(DISTINCT c.customer_id) as CUSTOMER_COUNT,
    CAST((COUNT(DISTINCT c.customer_id) * 100.0 / SUM(COUNT(DISTINCT c.customer_id)) OVER (PARTITION BY c.persona)) as FLOAT) as PERCENTAGE
FROM ANALYTICS.CUSTOMER_BASE c
JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps ON c.customer_id = cps.customer_id
GROUP BY c.persona, cps.churn_risk
ORDER BY 
    c.persona,
    CASE cps.churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END 