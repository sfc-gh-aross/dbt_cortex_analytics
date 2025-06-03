-- Overview Component Queries
-- Query 01: Overview KPIs
WITH combined_metrics AS (
    SELECT
        i.interaction_id,
        i.sentiment_score,
        c.persona,
        CASE 
            WHEN i.sentiment_score < 0.3 THEN 'High'
            WHEN i.sentiment_score < 0.6 THEN 'Medium'
            ELSE 'Low'
        END as churn_risk,
        r.review_rating
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
    LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
    LEFT JOIN ANALYTICS.FACT_PRODUCT_REVIEWS r ON i.customer_id = r.customer_id
    ;

-- Query 02: Sentiment Trend
WITH daily_sentiment AS (
    SELECT
        DATE_TRUNC('day', i.interaction_date) as date,
        CAST(AVG(i.sentiment_score) as FLOAT) as avg_sentiment
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
    INNER JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
    GROUP BY DATE_TRUNC('day', i.interaction_date)
    ORDER BY DATE_TRUNC('day', i.interaction_date)
)

SELECT
    date as DATE,
    avg_sentiment as AVG_SENTIMENT,
    CAST(AVG(avg_sentiment) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as FLOAT) as MOVING_AVG_SENTIMENT
FROM daily_sentiment
ORDER BY date;

-- Query 03: Sentiment Distribution
WITH sentiment_buckets AS (
    SELECT
        CASE
            WHEN sentiment_score < 0.2 THEN 'Very Negative'
            WHEN sentiment_score < 0.4 THEN 'Negative'
            WHEN sentiment_score < 0.6 THEN 'Neutral'
            WHEN sentiment_score < 0.8 THEN 'Positive'
            ELSE 'Very Positive'
        END as sentiment_bucket,
        COUNT(*) as count
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
    LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
    GROUP BY 1
)

SELECT
    sentiment_bucket as SENTIMENT_BUCKET,
    count as COUNT,
    CAST((count * 100.0 / SUM(count) OVER ()) as FLOAT) as PERCENTAGE
FROM sentiment_buckets
ORDER BY 
    CASE sentiment_bucket
        WHEN 'Very Negative' THEN 1
        WHEN 'Negative' THEN 2
        WHEN 'Neutral' THEN 3
        WHEN 'Positive' THEN 4
        WHEN 'Very Positive' THEN 5
    END;

-- Query 04: Churn Risk Breakdown
WITH customer_risk AS (
    SELECT
        c.persona,
        CASE 
            WHEN AVG(i.sentiment_score) < 0.3 THEN 'High'
            WHEN AVG(i.sentiment_score) < 0.6 THEN 'Medium'
            ELSE 'Low'
        END as churn_risk,
        COUNT(DISTINCT i.customer_id) as customer_count
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
    LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
    GROUP BY 1
),

persona_totals AS (
    SELECT
        persona,
        SUM(customer_count) as total_customers
    FROM customer_risk
    GROUP BY 1
)

SELECT
    r.persona as PERSONA,
    r.churn_risk as CHURN_RISK,
    r.customer_count as CUSTOMER_COUNT,
    CAST((r.customer_count * 100.0 / t.total_customers) as FLOAT) as PERCENTAGE
FROM customer_risk r
JOIN persona_totals t ON r.persona = t.persona
ORDER BY 
    r.persona,
    CASE r.churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;

-- Sentiment & Experience Component Queries
-- Query 05: Sentiment Over Time
SELECT
    DATE_TRUNC('day', interaction_date) as date,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
GROUP BY 1
ORDER BY 1;

-- Query 06: Sentiment Distribution
SELECT
    sentiment_score,
    COUNT(*) as count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
GROUP BY 1
ORDER BY 1;

-- Query 07: Sentiment by Persona
SELECT
    c.persona,
    AVG(i.sentiment_score) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS i
LEFT JOIN ANALYTICS.CUSTOMER_BASE c ON i.customer_id = c.customer_id
GROUP BY 1
ORDER BY 2 DESC;

-- Support Operations Component Queries
-- Query 08: Ticket Volume Trend
SELECT
    DATE_TRUNC('day', ticket_date) as date,
    COUNT(*) as ticket_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY 1
ORDER BY 1;

-- Query 09: Priority Breakdown
SELECT
    priority_level,
    COUNT(*) as ticket_count
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY 1
ORDER BY 1;

-- Query 10: Category Analysis
SELECT
    ticket_category,
    COUNT(*) as ticket_count
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY 1
ORDER BY 2 DESC;

-- Query 11: Tickets per Customer
SELECT
    customer_id,
    COUNT(*) as ticket_count
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY 1
ORDER BY 2 DESC;

-- Product Feedback Component Queries
-- Query 12: Rating Trend
SELECT
    DATE_TRUNC('day', review_date) as date,
    AVG(review_rating) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY 1
ORDER BY 1;

-- Query 13: Rating Distribution
SELECT
    review_rating,
    COUNT(*) as count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY 1
ORDER BY 1;

-- Query 14: Sentiment by Language
SELECT
    review_language,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY 1
ORDER BY 2 DESC;

-- Query 15: Recent Reviews
SELECT
    review_date,
    customer_id,
    review_rating,
    review_text,
    review_language,
    sentiment_score
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
ORDER BY review_date DESC
LIMIT 100;

-- Segmentation Component Queries
-- Query 16: Segment Distribution
SELECT
    segment,
    COUNT(*) as customer_count,
    CAST((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()) as FLOAT) as percentage
FROM ANALYTICS.CUSTOMER_SEGMENTS
GROUP BY 1
ORDER BY 2 DESC;

-- Query 17: Segment Characteristics
SELECT
    segment,
    metric,
    value
FROM ANALYTICS.SEGMENT_CHARACTERISTICS
ORDER BY segment, metric;

-- Query 18: Segment Migration
SELECT
    from_segment,
    to_segment,
    COUNT(*) as customer_count
FROM ANALYTICS.SEGMENT_MIGRATION
GROUP BY 1, 2
ORDER BY 1, 2;

-- Query 19: Segment Trend
SELECT
    DATE_TRUNC('month', migration_date) as date,
    segment,
    COUNT(*) as customer_count
FROM ANALYTICS.SEGMENT_MIGRATION
GROUP BY 1, 2
ORDER BY 1, 2;