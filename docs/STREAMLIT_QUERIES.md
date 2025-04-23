# SQL Queries for Customer Analytics Streamlit Application

## Query Guidelines & Standards

### Performance Requirements
```sql
-- All queries must meet these performance targets:
-- 1. Response time < 500ms (95th percentile)
-- 2. Resource consumption within limits
-- 3. Proper use of materialized views where applicable
-- 4. Efficient handling of large result sets

-- Example of query optimization technique:
-- Use EXPLAIN ANALYZE to verify query plans
-- EXPLAIN ANALYZE
-- [any query below]
```

### Caching Strategy
```sql
-- Queries are categorized by refresh frequency:
-- 1. Real-time (5-minute refresh):
--    - KPI metrics
--    - Active ticket counts
--    - Recent sentiment scores
-- 2. Daily refresh:
--    - Historical trends
--    - Aggregated statistics
-- 3. Static (refresh on data update):
--    - Reference data
--    - Category lookups
```

### Security & Access Control
```sql
-- Required security measures:
-- 1. Use secure bindings for all parameters
-- 2. Implement row-level security where needed
-- 3. Validate all input parameters
-- 4. Handle NULL values gracefully
```

## Global Filter Queries

### Date Range Validation
```sql
-- Get valid date range for the application
SELECT 
    MIN(GREATEST(
        (SELECT MIN(interaction_date) FROM ANALYTICS.SENTIMENT_ANALYSIS),
        (SELECT MIN(review_date) FROM ANALYTICS.FACT_PRODUCT_REVIEWS),
        (SELECT MIN(ticket_date) FROM ANALYTICS.FACT_SUPPORT_TICKETS)
    )) as min_date,
    MAX(LEAST(
        (SELECT MAX(interaction_date) FROM ANALYTICS.SENTIMENT_ANALYSIS),
        (SELECT MAX(review_date) FROM ANALYTICS.FACT_PRODUCT_REVIEWS),
        (SELECT MAX(ticket_date) FROM ANALYTICS.FACT_SUPPORT_TICKETS)
    )) as max_date;
```

### Value Segment Options
```sql
SELECT DISTINCT
    CASE 
        WHEN lifetime_value >= 1000 THEN 'High Value'
        WHEN lifetime_value >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as value_segment
FROM ANALYTICS.CUSTOMER_BASE
ORDER BY value_segment;
```

### Derived Persona Options
```sql
SELECT DISTINCT derived_persona
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
ORDER BY derived_persona;
```

### Churn Risk Options
```sql
SELECT DISTINCT churn_risk
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
ORDER BY 
    CASE churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;
```

### Upsell Opportunity Options
```sql
SELECT DISTINCT upsell_opportunity
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
ORDER BY 
    CASE upsell_opportunity
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;
```

### Interaction Type Options
```sql
SELECT DISTINCT interaction_type
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
ORDER BY interaction_type;
```

### Review Language Options
```sql
SELECT DISTINCT review_language
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
ORDER BY review_language;
```

### Customer ID Validation
```sql
-- Validate customer IDs exist across all required tables
SELECT customer_id
FROM ANALYTICS.CUSTOMER_BASE cb
WHERE EXISTS (
    SELECT 1 FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps 
    WHERE cps.customer_id = cb.customer_id
)
AND EXISTS (
    SELECT 1 FROM ANALYTICS.SENTIMENT_ANALYSIS sa 
    WHERE sa.customer_id = cb.customer_id
)
ORDER BY customer_id;
```

## Overview Dashboard Queries

### KPI Metrics
```sql
WITH date_range_metrics AS (
    -- Average Sentiment
    SELECT 
        AVG(sentiment_score) as current_avg_sentiment,
        COUNT(*) as total_interactions,
        COUNT(CASE WHEN sentiment_score > 0 THEN 1 END) / NULLIF(COUNT(*), 0) * 100 as positive_sentiment_pct
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
),
previous_period AS (
    -- Previous period metrics for comparison
    SELECT 
        AVG(sentiment_score) as prev_avg_sentiment,
        COUNT(*) as prev_total_interactions
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN 
        DATEADD(day, -DATEDIFF(day, :start_date, :end_date), :start_date) AND 
        DATEADD(day, -1, :start_date)
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
),
churn_risk AS (
    -- High Risk Customer Percentage
    SELECT 
        COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as high_risk_pct
    FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
    WHERE {% if selected_value_segments or selected_personas %}
        customer_id IN (
            SELECT DISTINCT customer_id
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
    {% endif %}
),
product_ratings AS (
    -- Average Product Rating
    SELECT 
        AVG(review_rating) as current_avg_rating,
        COUNT(*) as total_reviews
    FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    WHERE review_date BETWEEN :start_date AND :end_date
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
SELECT 
    m.current_avg_sentiment,
    m.total_interactions,
    c.high_risk_pct,
    p.current_avg_rating,
    -- Calculate deltas
    m.current_avg_sentiment - pp.prev_avg_sentiment as sentiment_delta,
    ((m.total_interactions * 1.0 / NULLIF(pp.prev_total_interactions, 0)) - 1) * 100 as interactions_delta
FROM date_range_metrics m
CROSS JOIN previous_period pp
CROSS JOIN churn_risk c
CROSS JOIN product_ratings p;
```

### Sentiment Trend
```sql
SELECT 
    DATE_TRUNC('month', interaction_date) as month,
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
GROUP BY month
ORDER BY month;
```

### Customer Sentiment Distribution
```sql
SELECT 
    overall_sentiment,
    COUNT(*) as customer_count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE {% if selected_value_segments or selected_personas or selected_churn_risk %}
    customer_id IN (
        SELECT DISTINCT customer_id
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
    )
    {% if selected_personas %}
    AND derived_persona IN :selected_personas
    {% endif %}
    {% if selected_churn_risk %}
    AND churn_risk IN :selected_churn_risk
    {% endif %}
{% endif %}
GROUP BY overall_sentiment
ORDER BY 
    CASE overall_sentiment
        WHEN 'Positive' THEN 1
        WHEN 'Neutral' THEN 2
        WHEN 'Negative' THEN 3
    END;
```

## Sentiment & Experience Analysis Queries

### Sentiment Over Time by Source
```sql
SELECT 
    DATE_TRUNC('week', interaction_date) as week,
    source_type,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(*) as interaction_count
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
    AND source_type IN :selected_sources
GROUP BY week, source_type
ORDER BY week, source_type;
```

### Sentiment Volatility vs Trend
```sql
SELECT 
    st.customer_id,
    st.sentiment_volatility,
    st.sentiment_trend,
    cps.overall_sentiment
FROM ANALYTICS.SENTIMENT_TRENDS st
JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps ON st.customer_id = cps.customer_id
WHERE {% if selected_value_segments or selected_personas or selected_churn_risk %}
    st.customer_id IN (
        SELECT DISTINCT customer_id
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
    )
    {% if selected_personas %}
    AND cps.derived_persona IN :selected_personas
    {% endif %}
    {% if selected_churn_risk %}
    AND cps.churn_risk IN :selected_churn_risk
    {% endif %}
{% endif %}
ORDER BY st.sentiment_volatility DESC;
```

## Support Operations Insights Queries

### Ticket Volume Trend
```sql
SELECT 
    DATE_TRUNC('day', ticket_date) as day,
    COUNT(*) as ticket_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM ANALYTICS.FACT_SUPPORT_TICKETS
WHERE ticket_date BETWEEN :start_date AND :end_date
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
GROUP BY day
ORDER BY day;
```

### Ticket Priority Analysis
```sql
SELECT 
    priority_level,
    COUNT(*) as ticket_count,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(DISTINCT customer_id) as unique_customers
FROM ANALYTICS.FACT_SUPPORT_TICKETS
WHERE ticket_date BETWEEN :start_date AND :end_date
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
GROUP BY priority_level
ORDER BY 
    CASE priority_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;
```

## Product Feedback Analysis Queries

### Rating Trend
```sql
SELECT 
    DATE_TRUNC('week', review_date) as week,
    AVG(review_rating) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
WHERE review_date BETWEEN :start_date AND :end_date
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
    {% if selected_languages %}
    AND review_language IN :selected_languages
    {% endif %}
GROUP BY week
ORDER BY week;
```

### Sentiment by Language
```sql
SELECT 
    review_language,
    COUNT(*) as review_count,
    AVG(sentiment_score) as avg_sentiment,
    AVG(review_rating) as avg_rating
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
WHERE review_date BETWEEN :start_date AND :end_date
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
GROUP BY review_language
ORDER BY review_count DESC;
```

## Customer Segmentation & Value Queries

### Persona Distribution
```sql
SELECT 
    derived_persona,
    COUNT(*) as customer_count,
    AVG(avg_sentiment) as avg_sentiment,
    AVG(sentiment_volatility) as avg_volatility
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE {% if selected_value_segments or selected_churn_risk %}
    customer_id IN (
        SELECT DISTINCT customer_id
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
    )
    {% if selected_churn_risk %}
    AND churn_risk IN :selected_churn_risk
    {% endif %}
{% endif %}
GROUP BY derived_persona
ORDER BY customer_count DESC;
```

### Churn Risk vs Upsell Matrix
```sql
SELECT 
    churn_risk,
    upsell_opportunity,
    COUNT(*) as customer_count,
    AVG(avg_sentiment) as avg_sentiment,
    AVG(sentiment_volatility) as avg_volatility
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE {% if selected_value_segments or selected_personas %}
    customer_id IN (
        SELECT DISTINCT customer_id
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
    )
    {% if selected_personas %}
    AND derived_persona IN :selected_personas
    {% endif %}
{% endif %}
GROUP BY churn_risk, upsell_opportunity
ORDER BY 
    CASE churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END,
    CASE upsell_opportunity
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;
```

### Individual Customer Deep Dive
```sql
WITH customer_timeline AS (
    SELECT 
        'interaction' as event_type,
        interaction_date as event_date,
        interaction_type as event_category,
        interaction_notes as event_description,
        sentiment_score
    FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
    WHERE customer_id = :selected_customer_id
    
    UNION ALL
    
    SELECT 
        'review' as event_type,
        review_date as event_date,
        CAST(review_rating as VARCHAR) as event_category,
        review_text as event_description,
        sentiment_score
    FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    WHERE customer_id = :selected_customer_id
    
    UNION ALL
    
    SELECT 
        'ticket' as event_type,
        ticket_date as event_date,
        ticket_category as event_category,
        ticket_description as event_description,
        sentiment_score
    FROM ANALYTICS.FACT_SUPPORT_TICKETS
    WHERE customer_id = :selected_customer_id
)
SELECT 
    cps.*,
    cb.lifetime_value,
    cb.products_owned,
    cb.sign_up_date,
    is.customer_summary,
    -- Also include the timeline
    t.*
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
JOIN ANALYTICS.CUSTOMER_BASE cb ON cps.customer_id = cb.customer_id
JOIN ANALYTICS.INSIGHT_SUMMARIES is ON cps.customer_id = is.customer_id
CROSS JOIN customer_timeline t
WHERE cps.customer_id = :selected_customer_id
ORDER BY t.event_date DESC;
```

## Performance-Optimized Dashboard Queries

### KPI Metrics with Error Handling
```sql
-- Add error handling wrapper
BEGIN TRY
    [... existing KPI Metrics query ...]
END TRY
BEGIN CATCH
    -- Return standardized error format
    SELECT 
        NULL as current_avg_sentiment,
        NULL as total_interactions,
        NULL as high_risk_pct,
        NULL as current_avg_rating,
        NULL as sentiment_delta,
        NULL as interactions_delta,
        'Error: ' + ERROR_MESSAGE() as error_message;
END CATCH;
```

## Enhanced Visualization Queries

### Sentiment Analysis with Confidence Intervals
```sql
SELECT 
    DATE_TRUNC('week', interaction_date) as week,
    AVG(sentiment_score) as avg_sentiment,
    STDDEV(sentiment_score) as sentiment_stddev,
    COUNT(*) as sample_size,
    -- Calculate 95% confidence interval
    AVG(sentiment_score) - 1.96 * (STDDEV(sentiment_score) / SQRT(COUNT(*))) as ci_lower,
    AVG(sentiment_score) + 1.96 * (STDDEV(sentiment_score) / SQRT(COUNT(*))) as ci_upper
FROM ANALYTICS.SENTIMENT_ANALYSIS
WHERE interaction_date BETWEEN :start_date AND :end_date
    [... existing filters ...]
GROUP BY week
HAVING COUNT(*) >= 30  -- Ensure statistical significance
ORDER BY week;
```

### Time-Based Comparisons
```sql
WITH current_period AS (
    [... existing period calculation ...]
),
previous_period AS (
    [... existing previous period calculation ...]
),
year_ago_period AS (
    SELECT 
        AVG(sentiment_score) as year_ago_sentiment,
        COUNT(*) as year_ago_count
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    WHERE interaction_date BETWEEN 
        DATEADD(year, -1, :start_date) AND 
        DATEADD(year, -1, :end_date)
        [... existing filters ...]
)
SELECT 
    cp.*,
    pp.*,
    yap.*,
    -- Calculate period-over-period changes
    ((cp.current_avg_sentiment - pp.prev_avg_sentiment) / NULLIF(pp.prev_avg_sentiment, 0)) * 100 as wow_change,
    ((cp.current_avg_sentiment - yap.year_ago_sentiment) / NULLIF(yap.year_ago_sentiment, 0)) * 100 as yoy_change
FROM current_period cp
CROSS JOIN previous_period pp
CROSS JOIN year_ago_period yap;
```

## Export & Reporting Queries

### Data Export with Row Limits
```sql
-- Implement safe pagination for large datasets
WITH filtered_data AS (
    SELECT 
        [... columns ...],
        ROW_NUMBER() OVER (ORDER BY event_date DESC) as row_num
    FROM customer_timeline
    WHERE [... filters ...]
)
SELECT *
FROM filtered_data
WHERE row_num BETWEEN :offset AND :offset + :limit
ORDER BY event_date DESC;
```

### Scheduled Report Summary
```sql
-- Daily summary for automated reports
SELECT 
    CURRENT_DATE() as report_date,
    COUNT(DISTINCT customer_id) as total_customers,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(CASE WHEN churn_risk = 'High' THEN 1 END) as high_risk_customers,
    COUNT(CASE WHEN upsell_opportunity = 'High' THEN 1 END) as upsell_opportunities,
    -- Add statistical validity checks
    CASE 
        WHEN COUNT(*) < 30 THEN 'Warning: Small sample size'
        WHEN STDDEV(sentiment_score) > 0.5 THEN 'Warning: High variance'
        ELSE 'Valid'
    END as data_quality_check
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
WHERE [... filters ...];
```

## Query Performance Monitoring

### Query Statistics Collection
```sql
-- Track query performance metrics
CREATE OR REPLACE TABLE ANALYTICS.QUERY_STATS (
    query_id VARCHAR,
    query_type VARCHAR,
    execution_time FLOAT,
    row_count INTEGER,
    execution_date TIMESTAMP_NTZ,
    error_message VARCHAR
);

-- Example usage:
-- INSERT INTO ANALYTICS.QUERY_STATS
-- SELECT 
--     RANDOM() as query_id,
--     'KPI_METRICS' as query_type,
--     TIMESTAMPDIFF(MILLISECOND, query_start_time, CURRENT_TIMESTAMP()) as execution_time,
--     row_count,
--     CURRENT_TIMESTAMP() as execution_date,
--     error_message
-- FROM [query execution];
```
