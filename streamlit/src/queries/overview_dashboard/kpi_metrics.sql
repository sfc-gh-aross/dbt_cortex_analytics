WITH customer_metrics AS (
    SELECT
        COUNT(DISTINCT customer_id) as total_customers,
        COUNT(DISTINCT CASE WHEN status = 'active' THEN customer_id END) as active_customers,
        COUNT(DISTINCT CASE WHEN status = 'churned' THEN customer_id END) as churned_customers,
        AVG(monthly_revenue) as avg_revenue_per_customer
    FROM {{ ref('customer_metrics') }}
    WHERE date = (SELECT MAX(date) FROM {{ ref('customer_metrics') }})
)
SELECT
    total_customers,
    active_customers,
    ROUND((churned_customers::FLOAT / NULLIF(total_customers, 0) * 100), 2) as churn_rate,
    ROUND(avg_revenue_per_customer, 2) as avg_revenue_per_customer
FROM customer_metrics 