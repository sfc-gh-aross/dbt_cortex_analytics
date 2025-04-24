SELECT
    date_trunc('month', date) as month,
    SUM(monthly_revenue) as total_revenue,
    COUNT(DISTINCT customer_id) as active_customers
FROM {{ ref('customer_metrics') }}
WHERE status = 'active'
GROUP BY 1
ORDER BY 1 