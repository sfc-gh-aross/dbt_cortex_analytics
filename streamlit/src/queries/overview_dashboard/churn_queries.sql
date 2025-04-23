-- Overview Dashboard Churn Risk Queries
-- Purpose: Contains SQL queries for churn risk analysis and visualization
-- Input Parameters: start_date, end_date, selected_value_segments, selected_personas
-- Output: Churn risk distribution data

-- Churn Risk Breakdown Query
-- Returns: churn_risk, count
SELECT 
    churn_risk,
    COUNT(*) as count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE churn_risk IS NOT NULL
{value_segment_filter}
{persona_filter}
GROUP BY churn_risk
ORDER BY 
    CASE churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END; 