-- =============================================
-- 1. Customer Sentiment & Experience
-- =============================================

-- 1. Overall customer sentiment distribution
SELECT 
    CASE 
        WHEN sentiment_score < -0.3 THEN 'Negative'
        WHEN sentiment_score > 0.3 THEN 'Positive'
        ELSE 'Neutral'
    END as sentiment_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM (
    SELECT sentiment_score FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
    UNION ALL
    SELECT sentiment_score FROM ANALYTICS.FACT_PRODUCT_REVIEWS
    UNION ALL
    SELECT sentiment_score FROM ANALYTICS.FACT_SUPPORT_TICKETS
)
GROUP BY sentiment_category
ORDER BY count DESC;

-- 2. Sentiment trends over time
SELECT 
    DATE_TRUNC('day', interaction_date) as date,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY date
ORDER BY date;

-- 3. Sentiment by interaction type
SELECT 
    interaction_type,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY interaction_type
ORDER BY avg_sentiment DESC;

-- 4. Sentiment correlation with support ticket volume
WITH daily_metrics AS (
    SELECT 
        DATE_TRUNC('day', interaction_date) as date,
        AVG(sentiment_score) as avg_sentiment,
        COUNT(CASE WHEN source_type = 'ticket' THEN 1 END) as ticket_count
    FROM ANALYTICS.SENTIMENT_ANALYSIS
    GROUP BY date
)
SELECT 
    CORR(avg_sentiment, ticket_count) as sentiment_ticket_correlation
FROM daily_metrics;

-- 5. Sentiment volatility by customer segment
SELECT 
    cb.persona,
    ROUND(AVG(cps.sentiment_volatility), 3) as avg_volatility,
    COUNT(DISTINCT cps.customer_id) as customer_count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY cb.persona
ORDER BY avg_volatility DESC;

-- =============================================
-- 2. Support Operations
-- =============================================

-- 6. Support ticket volume by priority level
SELECT 
    priority_level,
    COUNT(*) as ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY priority_level
ORDER BY 
    CASE priority_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;

-- 7. Most common support ticket categories
SELECT 
    ticket_category,
    COUNT(*) as ticket_count,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY ticket_category
ORDER BY ticket_count DESC;

-- 8. Support ticket recurrence patterns
SELECT 
    customer_id,
    COUNT(*) as ticket_count,
    ARRAY_TO_STRING(ticket_categories, ', ') as category_sequence,
    ARRAY_TO_STRING(ticket_priorities, ', ') as priority_sequence
FROM ANALYTICS.TICKET_PATTERNS
WHERE ticket_count > 1
ORDER BY ticket_count DESC;

-- 9. Customer satisfaction vs. ticket priority
SELECT 
    priority_level,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as ticket_count
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY priority_level
ORDER BY 
    CASE priority_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;

-- =============================================
-- 3. Product Feedback & Reviews
-- =============================================

-- 10. Product rating distribution
SELECT 
    review_rating,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_rating
ORDER BY review_rating;

-- 11. Review sentiment by product
SELECT 
    product_id,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY product_id
ORDER BY avg_sentiment DESC;

-- 12. Review volume trends
SELECT 
    DATE_TRUNC('day', review_date) as date,
    COUNT(*) as review_count,
    ROUND(AVG(review_rating), 2) as avg_rating
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY date
ORDER BY date;

-- 13. Multilingual review analysis
SELECT 
    review_language,
    COUNT(*) as review_count,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY review_count DESC;

-- 14. Review sentiment vs. product rating correlation
SELECT 
    CORR(review_rating, sentiment_score) as rating_sentiment_correlation
FROM ANALYTICS.FACT_PRODUCT_REVIEWS;

-- =============================================
-- 4. Customer Behavior & Journey
-- =============================================

-- 15. Customer interaction frequency patterns
SELECT 
    customer_id,
    COUNT(*) as interaction_count,
    MIN(interaction_date) as first_interaction,
    MAX(interaction_date) as last_interaction
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY customer_id
ORDER BY interaction_count DESC;

-- 16. Preferred communication channels
SELECT 
    interaction_type,
    COUNT(*) as interaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY interaction_type
ORDER BY interaction_count DESC;

-- 17. Customer journey mapping
SELECT 
    customer_id,
    ARRAY_AGG(
        CASE 
            WHEN source_type = 'interaction' THEN 'Interaction'
            WHEN source_type = 'review' THEN 'Review'
            WHEN source_type = 'ticket' THEN 'Support'
        END
    ) WITHIN GROUP (ORDER BY interaction_date) as journey_sequence
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY customer_id;

-- 18. Touchpoint effectiveness
SELECT 
    source_type,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY source_type
ORDER BY avg_sentiment DESC;

-- 19. Interaction type preferences by customer segment
SELECT 
    cb.persona,
    ci.interaction_type,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS ci
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY cb.persona, ci.interaction_type
ORDER BY cb.persona, interaction_count DESC;

-- =============================================
-- 5. Customer Segmentation & Value
-- =============================================

-- 20. Customer lifetime value distribution
SELECT 
    CASE 
        WHEN lifetime_value >= 1000 THEN 'High Value'
        WHEN lifetime_value >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as value_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(lifetime_value), 2) as avg_value
FROM ANALYTICS.CUSTOMER_BASE
GROUP BY value_segment
ORDER BY avg_value DESC;

-- 21. Customer persona distribution
SELECT 
    persona,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.CUSTOMER_BASE
GROUP BY persona
ORDER BY customer_count DESC;

-- 22. Churn risk indicators
SELECT 
    churn_risk,
    COUNT(*) as customer_count,
    ROUND(AVG(avg_sentiment), 3) as avg_sentiment,
    ROUND(AVG(ticket_count), 2) as avg_tickets
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS
GROUP BY churn_risk
ORDER BY 
    CASE churn_risk
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;

-- 23. Upsell opportunity identification
SELECT 
    upsell_opportunity,
    COUNT(*) as customer_count,
    ROUND(AVG(lifetime_value), 2) as avg_lifetime_value,
    ROUND(AVG(avg_sentiment), 3) as avg_sentiment
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY upsell_opportunity
ORDER BY 
    CASE upsell_opportunity
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;

-- =============================================
-- 6. Customer Insights & Summaries
-- =============================================

-- 24. Customer interaction summaries
SELECT 
    customer_id,
    customer_summary
FROM ANALYTICS.INSIGHT_SUMMARIES
ORDER BY customer_id;

-- 25. Customer sentiment history
SELECT 
    customer_id,
    sentiment_history,
    avg_sentiment,
    sentiment_trend
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY customer_id;

-- 26. Customer support ticket patterns
SELECT 
    customer_id,
    ticket_count,
    ARRAY_TO_STRING(ticket_categories, ', ') as categories,
    ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
FROM ANALYTICS.TICKET_PATTERNS
ORDER BY ticket_count DESC;

-- 27. Customer sentiment trends
SELECT 
    customer_id,
    sentiment_trend,
    avg_sentiment,
    sentiment_volatility
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY sentiment_trend DESC;

-- 28. Customer sentiment volatility
SELECT 
    customer_id,
    sentiment_volatility,
    avg_sentiment,
    sentiment_trend
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY sentiment_volatility DESC;

-- =============================================
-- 7. Language & Communication Analysis
-- =============================================

-- 29. Review language distribution
SELECT 
    review_language,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY review_count DESC;

-- 30. Multilingual sentiment comparison
SELECT 
    review_language,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY avg_sentiment DESC;

-- 31. Translation quality assessment
SELECT 
    review_language,
    COUNT(*) as total_reviews,
    COUNT(CASE WHEN review_text_english IS NOT NULL THEN 1 END) as translated_reviews,
    ROUND(COUNT(CASE WHEN review_text_english IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as translation_rate
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY total_reviews DESC;

-- =============================================
-- 8. Customer Value Analysis
-- =============================================

-- 32. Customer value segments
SELECT 
    CASE 
        WHEN lifetime_value >= 1000 THEN 'High Value'
        WHEN lifetime_value >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as value_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(lifetime_value), 2) as avg_value,
    ROUND(SUM(lifetime_value), 2) as total_value
FROM ANALYTICS.CUSTOMER_BASE
GROUP BY value_segment
ORDER BY avg_value DESC;

-- 33. Value vs. sentiment correlation
SELECT 
    CORR(cb.lifetime_value, cps.avg_sentiment) as value_sentiment_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps USING (customer_id);

-- 34. Value vs. support ticket correlation
SELECT 
    CORR(cb.lifetime_value, tp.ticket_count) as value_ticket_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.TICKET_PATTERNS tp USING (customer_id);

-- 35. Value vs. review rating correlation
SELECT 
    CORR(cb.lifetime_value, pr.review_rating) as value_rating_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.FACT_PRODUCT_REVIEWS pr USING (customer_id);