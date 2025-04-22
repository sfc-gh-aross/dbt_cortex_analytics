# Customer Analytics Dashboard Guide

This guide provides a comprehensive overview of all visualizations in the customer analytics dashboard, including their descriptions, SQL queries, and recommended visualization types.

## 1. Customer Sentiment & Experience

### Overall Customer Sentiment Distribution
**Description**: Shows distribution of positive/neutral/negative sentiment across different interaction types  
**Visualization**: Stacked bar chart  
**Why**: Shows distribution of positive/neutral/negative sentiment across different interaction types  
**SQL Query**:
```sql
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
```

### Sentiment Trends Over Time
**Description**: Shows sentiment progression and patterns over time  
**Visualization**: Line chart with multiple series  
**Why**: Shows sentiment progression and patterns over time  
**SQL Query**:
```sql
SELECT 
    DATE_TRUNC('day', interaction_date) as date,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY date
ORDER BY date;
```

### Sentiment by Interaction Type
**Description**: Shows intensity of sentiment across different interaction types  
**Visualization**: Heatmap  
**Why**: Shows intensity of sentiment across different interaction types  
**SQL Query**:
```sql
SELECT 
    interaction_type,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY interaction_type
ORDER BY avg_sentiment DESC;
```

### Sentiment Correlation with Support Ticket Volume
**Description**: Shows relationship between sentiment and ticket volume over time  
**Visualization**: Dual-axis line chart  
**Why**: Shows relationship between sentiment and ticket volume over time  
**SQL Query**:
```sql
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
```

### Sentiment Volatility by Customer Segment
**Description**: Shows distribution and range of sentiment scores within each segment  
**Visualization**: Box plot  
**Why**: Shows distribution and range of sentiment scores within each segment  
**SQL Query**:
```sql
SELECT 
    cb.persona,
    ROUND(AVG(cps.sentiment_volatility), 3) as avg_volatility,
    COUNT(DISTINCT cps.customer_id) as customer_count
FROM ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY cb.persona
ORDER BY avg_volatility DESC;
```

## 2. Support Operations

### Support Ticket Volume by Priority Level
**Description**: Shows volume trends while maintaining priority level visibility  
**Visualization**: Stacked area chart  
**Why**: Shows volume trends while maintaining priority level visibility  
**SQL Query**:
```sql
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
```

### Most Common Support Ticket Categories
**Description**: Shows hierarchy and relative size of ticket categories  
**Visualization**: Treemap  
**Why**: Shows hierarchy and relative size of ticket categories  
**SQL Query**:
```sql
SELECT 
    ticket_category,
    COUNT(*) as ticket_count,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment
FROM ANALYTICS.FACT_SUPPORT_TICKETS
GROUP BY ticket_category
ORDER BY ticket_count DESC;
```

### Support Ticket Recurrence Patterns
**Description**: Shows flow of ticket categories and priorities over time  
**Visualization**: Sankey diagram  
**Why**: Shows flow of ticket categories and priorities over time  
**SQL Query**:
```sql
SELECT 
    customer_id,
    COUNT(*) as ticket_count,
    ARRAY_TO_STRING(ticket_categories, ', ') as category_sequence,
    ARRAY_TO_STRING(ticket_priorities, ', ') as priority_sequence
FROM ANALYTICS.TICKET_PATTERNS
WHERE ticket_count > 1
ORDER BY ticket_count DESC;
```

### Customer Satisfaction vs. Ticket Priority
**Description**: Shows correlation between priority and satisfaction  
**Visualization**: Scatter plot with trend line  
**Why**: Shows correlation between priority and satisfaction  
**SQL Query**:
```sql
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
```

## 3. Product Feedback & Reviews

### Product Rating Distribution
**Description**: Shows frequency distribution of ratings  
**Visualization**: Histogram  
**Why**: Shows frequency distribution of ratings  
**SQL Query**:
```sql
SELECT 
    review_rating,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_rating
ORDER BY review_rating;
```

### Review Sentiment by Product
**Description**: Shows three dimensions: product, sentiment, and review volume  
**Visualization**: Bubble chart  
**Why**: Shows three dimensions: product, sentiment, and review volume  
**SQL Query**:
```sql
SELECT 
    product_id,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY product_id
ORDER BY avg_sentiment DESC;
```

### Review Volume Trends
**Description**: Shows cumulative review volume over time  
**Visualization**: Area chart  
**Why**: Shows cumulative review volume over time  
**SQL Query**:
```sql
SELECT 
    DATE_TRUNC('day', review_date) as date,
    COUNT(*) as review_count,
    ROUND(AVG(review_rating), 2) as avg_rating
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY date
ORDER BY date;
```

### Multilingual Review Analysis
**Description**: Shows sentiment patterns across different languages  
**Visualization**: Radar chart  
**Why**: Shows sentiment patterns across different languages  
**SQL Query**:
```sql
SELECT 
    review_language,
    COUNT(*) as review_count,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY review_count DESC;
```

### Review Sentiment vs. Product Rating Correlation
**Description**: Shows relationship between rating and sentiment  
**Visualization**: Scatter plot with color gradient  
**Why**: Shows relationship between rating and sentiment  
**SQL Query**:
```sql
SELECT 
    CORR(review_rating, sentiment_score) as rating_sentiment_correlation
FROM ANALYTICS.FACT_PRODUCT_REVIEWS;
```

## 4. Customer Behavior & Journey

### Customer Interaction Frequency Patterns
**Description**: Shows interaction patterns across days/weeks  
**Visualization**: Heat calendar  
**Why**: Shows interaction patterns across days/weeks  
**SQL Query**:
```sql
SELECT 
    customer_id,
    COUNT(*) as interaction_count,
    MIN(interaction_date) as first_interaction,
    MAX(interaction_date) as last_interaction
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY customer_id
ORDER BY interaction_count DESC;
```

### Preferred Communication Channels
**Description**: Shows proportion of interactions by channel  
**Visualization**: Donut chart  
**Why**: Shows proportion of interactions by channel  
**SQL Query**:
```sql
SELECT 
    interaction_type,
    COUNT(*) as interaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS
GROUP BY interaction_type
ORDER BY interaction_count DESC;
```

### Customer Journey Mapping
**Description**: Shows typical customer interaction sequences  
**Visualization**: Flow diagram  
**Why**: Shows typical customer interaction sequences  
**SQL Query**:
```sql
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
```

### Touchpoint Effectiveness
**Description**: Shows average sentiment with variance for each touchpoint  
**Visualization**: Bar chart with error bars  
**Why**: Shows average sentiment with variance for each touchpoint  
**SQL Query**:
```sql
SELECT 
    source_type,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    COUNT(*) as interaction_count
FROM ANALYTICS.SENTIMENT_ANALYSIS
GROUP BY source_type
ORDER BY avg_sentiment DESC;
```

### Interaction Type Preferences by Customer Segment
**Description**: Compares interaction types across segments  
**Visualization**: Grouped bar chart  
**Why**: Compares interaction types across segments  
**SQL Query**:
```sql
SELECT 
    cb.persona,
    ci.interaction_type,
    COUNT(*) as interaction_count
FROM ANALYTICS.FACT_CUSTOMER_INTERACTIONS ci
JOIN ANALYTICS.CUSTOMER_BASE cb USING (customer_id)
GROUP BY cb.persona, ci.interaction_type
ORDER BY cb.persona, interaction_count DESC;
```

## 5. Customer Segmentation & Value

### Customer Lifetime Value Distribution
**Description**: Shows distribution and density of customer values  
**Visualization**: Violin plot  
**Why**: Shows distribution and density of customer values  
**SQL Query**:
```sql
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
```

### Customer Persona Distribution
**Description**: Shows proportion of different personas  
**Visualization**: Pie chart  
**Why**: Shows proportion of different personas  
**SQL Query**:
```sql
SELECT 
    persona,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.CUSTOMER_BASE
GROUP BY persona
ORDER BY customer_count DESC;
```

### Churn Risk Indicators
**Description**: Shows risk level with clear thresholds  
**Visualization**: Gauge chart  
**Why**: Shows risk level with clear thresholds  
**SQL Query**:
```sql
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
```

### Upsell Opportunity Identification
**Description**: Shows opportunity vs. current value  
**Visualization**: Scatter plot with quadrants  
**Why**: Shows opportunity vs. current value  
**SQL Query**:
```sql
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
```

## 6. Customer Insights & Summaries

### Customer Interaction Summaries
**Description**: Highlights key themes in customer interactions  
**Visualization**: Word cloud  
**Why**: Highlights key themes in customer interactions  
**SQL Query**:
```sql
SELECT 
    customer_id,
    customer_summary
FROM ANALYTICS.INSIGHT_SUMMARIES
ORDER BY customer_id;
```

### Customer Sentiment History
**Description**: Shows sentiment trend in compact form  
**Visualization**: Sparkline  
**Why**: Shows sentiment trend in compact form  
**SQL Query**:
```sql
SELECT 
    customer_id,
    sentiment_history,
    avg_sentiment,
    sentiment_trend
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY customer_id;
```

### Customer Support Ticket Patterns
**Description**: Shows relationships between ticket categories  
**Visualization**: Network graph  
**Why**: Shows relationships between ticket categories  
**SQL Query**:
```sql
SELECT 
    customer_id,
    ticket_count,
    ARRAY_TO_STRING(ticket_categories, ', ') as categories,
    ARRAY_TO_STRING(ticket_priorities, ', ') as priorities
FROM ANALYTICS.TICKET_PATTERNS
ORDER BY ticket_count DESC;
```

### Customer Sentiment Trends
**Description**: Shows sentiment relative to neutral  
**Visualization**: Area chart with baseline  
**Why**: Shows sentiment relative to neutral  
**SQL Query**:
```sql
SELECT 
    customer_id,
    sentiment_trend,
    avg_sentiment,
    sentiment_volatility
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY sentiment_trend DESC;
```

### Customer Sentiment Volatility
**Description**: Shows range of sentiment variation  
**Visualization**: Bar chart with error bars  
**Why**: Shows range of sentiment variation  
**SQL Query**:
```sql
SELECT 
    customer_id,
    sentiment_volatility,
    avg_sentiment,
    sentiment_trend
FROM ANALYTICS.SENTIMENT_TRENDS
ORDER BY sentiment_volatility DESC;
```

## 7. Language & Communication Analysis

### Review Language Distribution
**Description**: Shows proportion of reviews by language  
**Visualization**: Tree map  
**Why**: Shows proportion of reviews by language  
**SQL Query**:
```sql
SELECT 
    review_language,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY review_count DESC;
```

### Multilingual Sentiment Comparison
**Description**: Compares sentiment across languages  
**Visualization**: Grouped bar chart  
**Why**: Compares sentiment across languages  
**SQL Query**:
```sql
SELECT 
    review_language,
    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
    ROUND(AVG(review_rating), 2) as avg_rating,
    COUNT(*) as review_count
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY avg_sentiment DESC;
```

### Translation Quality Assessment
**Description**: Shows relationship between original and translated sentiment  
**Visualization**: Parallel coordinates plot  
**Why**: Shows relationship between original and translated sentiment  
**SQL Query**:
```sql
SELECT 
    review_language,
    COUNT(*) as total_reviews,
    COUNT(CASE WHEN review_text_english IS NOT NULL THEN 1 END) as translated_reviews,
    ROUND(COUNT(CASE WHEN review_text_english IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as translation_rate
FROM ANALYTICS.FACT_PRODUCT_REVIEWS
GROUP BY review_language
ORDER BY total_reviews DESC;
```

## 8. Customer Value Analysis

### Customer Value Segments
**Description**: Shows distribution across value tiers  
**Visualization**: Funnel chart  
**Why**: Shows distribution across value tiers  
**SQL Query**:
```sql
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
```

### Value vs. Sentiment Correlation
**Description**: Shows relationship between value and sentiment  
**Visualization**: Scatter plot with trend line  
**Why**: Shows relationship between value and sentiment  
**SQL Query**:
```sql
SELECT 
    CORR(cb.lifetime_value, cps.avg_sentiment) as value_sentiment_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.CUSTOMER_PERSONA_SIGNALS cps USING (customer_id);
```

### Value vs. Support Ticket Correlation
**Description**: Shows three dimensions: value, ticket count, and sentiment  
**Visualization**: Bubble chart  
**Why**: Shows three dimensions: value, ticket count, and sentiment  
**SQL Query**:
```sql
SELECT 
    CORR(cb.lifetime_value, tp.ticket_count) as value_ticket_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.TICKET_PATTERNS tp USING (customer_id);
```

### Value vs. Review Rating Correlation
**Description**: Shows relationship between value and review ratings  
**Visualization**: Heatmap  
**Why**: Shows relationship between value and review ratings  
**SQL Query**:
```sql
SELECT 
    CORR(cb.lifetime_value, pr.review_rating) as value_rating_correlation
FROM ANALYTICS.CUSTOMER_BASE cb
JOIN ANALYTICS.FACT_PRODUCT_REVIEWS pr USING (customer_id);
```

## 9. Revenue Analytics

**Description**: Shows revenue trends, customer value, and financial metrics  
**Visualization**: Multiple charts including line charts, bar charts, and metrics  
**Why**: Provides financial insights and revenue tracking  
**SQL Query**:
```sql
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    SUM(amount) as total_revenue,
    COUNT(DISTINCT customer_id) as active_customers,
    AVG(amount) as avg_transaction_value
FROM ANALYTICS.FACT_TRANSACTIONS
GROUP BY month
ORDER BY month;
```

## Visualization Best Practices

Each visualization should include:
- Clear titles and labels
- Interactive tooltips with detailed metrics
- Appropriate color schemes for data types
- Consistent time periods for trend analysis
- Clear legends and axis labels
- Responsive design for different screen sizes 