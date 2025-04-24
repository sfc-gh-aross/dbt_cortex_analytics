WITH monthly_churn AS (
    SELECT
        date_trunc('month', date) as month,
        COUNT(DISTINCT CASE WHEN status = 'churned' THEN customer_id END) as churned_customers,
        COUNT(DISTINCT customer_id) as total_customers,
        SUM(CASE WHEN status = 'churned' THEN monthly_revenue ELSE 0 END) as churned_revenue,
        SUM(monthly_revenue) as total_revenue
    FROM {{ ref('customer_metrics') }}
    GROUP BY 1
)
SELECT
    month,
    churned_customers,
    total_customers,
    churned_revenue,
    total_revenue,
    ROUND((churned_customers::float / total_customers) * 100, 2) as churn_rate,
    ROUND((churned_revenue::float / total_revenue) * 100, 2) as revenue_churn_rate
FROM monthly_churn
ORDER BY month DESC 