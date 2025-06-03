WITH customer_value AS (
    SELECT
        CUSTOMER_ID,
        LIFETIME_VALUE
    FROM ANALYTICS.CUSTOMER_BASE
),
high_value_customers AS (
    SELECT
        COUNT(DISTINCT CUSTOMER_ID) AS num_high_value_customers
    FROM customer_value
    WHERE LIFETIME_VALUE > 1000
),
total_customers AS (
    SELECT
        COUNT(DISTINCT CUSTOMER_ID) AS num_total_customers
    FROM customer_value
)
SELECT
    (SELECT num_high_value_customers FROM high_value_customers) * 100.0 / (SELECT num_total_customers FROM total_customers) AS HIGH_VALUE_CUSTOMER_PERCENTAGE
FROM total_customers; 