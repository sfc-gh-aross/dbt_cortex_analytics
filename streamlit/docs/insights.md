# Customer Analytics Insights

## 1. Customer Sentiment & Experience
- **Overall customer sentiment distribution**  
  Sources: `FACT_CUSTOMER_INTERACTIONS.sentiment_score`, `FACT_PRODUCT_REVIEWS.sentiment_score`, `FACT_SUPPORT_TICKETS.sentiment_score`
- **Sentiment trends over time**  
  Sources: `SENTIMENT_TRENDS.sentiment_history`, `SENTIMENT_TRENDS.sentiment_trend`
- **Sentiment by interaction type**  
  Sources: `FACT_CUSTOMER_INTERACTIONS.interaction_type`, `FACT_CUSTOMER_INTERACTIONS.sentiment_score`
- **Sentiment correlation with support ticket volume**  
  Sources: `FACT_SUPPORT_TICKETS`, `SENTIMENT_TRENDS`
- **Sentiment volatility by customer segment**  
  Sources: `SENTIMENT_TRENDS.sentiment_volatility`, `CUSTOMER_BASE.persona`

## 2. Support Operations
- **Support ticket volume by priority level**  
  Sources: `FACT_SUPPORT_TICKETS.priority_level`
- **Most common support ticket categories**  
  Sources: `FACT_SUPPORT_TICKETS.ticket_category`
- **Support ticket recurrence patterns**  
  Sources: `TICKET_PATTERNS.ticket_categories`, `TICKET_PATTERNS.ticket_priorities`
- **Customer satisfaction vs. ticket priority**  
  Sources: `FACT_SUPPORT_TICKETS.priority_level`, `FACT_SUPPORT_TICKETS.sentiment_score`

## 3. Product Feedback & Reviews
- **Product rating distribution**  
  Sources: `FACT_PRODUCT_REVIEWS.review_rating`
- **Review sentiment by product**  
  Sources: `FACT_PRODUCT_REVIEWS.product_id`, `FACT_PRODUCT_REVIEWS.sentiment_score`
- **Review volume trends**  
  Sources: `FACT_PRODUCT_REVIEWS.review_date`
- **Multilingual review analysis**  
  Sources: `FACT_PRODUCT_REVIEWS.review_language`, `FACT_PRODUCT_REVIEWS.review_text_english`
- **Review sentiment vs. product rating correlation**  
  Sources: `FACT_PRODUCT_REVIEWS.review_rating`, `FACT_PRODUCT_REVIEWS.sentiment_score`

## 4. Customer Behavior & Journey
- **Customer interaction frequency patterns**  
  Sources: `FACT_CUSTOMER_INTERACTIONS.interaction_date`
- **Preferred communication channels**  
  Sources: `FACT_CUSTOMER_INTERACTIONS.interaction_type`
- **Customer journey mapping**  
  Sources: `SENTIMENT_ANALYSIS` (combines all interaction types)
- **Touchpoint effectiveness**  
  Sources: `FACT_CUSTOMER_INTERACTIONS`, `FACT_PRODUCT_REVIEWS`, `FACT_SUPPORT_TICKETS`
- **Interaction type preferences by customer segment**  
  Sources: `FACT_CUSTOMER_INTERACTIONS.interaction_type`, `CUSTOMER_BASE.persona`

## 5. Customer Segmentation & Value
- **Customer lifetime value distribution**  
  Sources: `CUSTOMER_BASE.lifetime_value`
- **Customer persona distribution**  
  Sources: `CUSTOMER_BASE.persona`
- **Churn risk indicators**  
  Sources: `CUSTOMER_PERSONA_SIGNALS.churn_risk`
- **Upsell opportunity identification**  
  Sources: `CUSTOMER_PERSONA_SIGNALS.upsell_opportunity`

## 6. Customer Insights & Summaries
- **Customer interaction summaries**  
  Sources: `INSIGHT_SUMMARIES.customer_summary`
- **Customer sentiment history**  
  Sources: `SENTIMENT_TRENDS.sentiment_history`
- **Customer support ticket patterns**  
  Sources: `TICKET_PATTERNS.ticket_categories`, `TICKET_PATTERNS.ticket_priorities`
- **Customer sentiment trends**  
  Sources: `SENTIMENT_TRENDS.sentiment_trend`
- **Customer sentiment volatility**  
  Sources: `SENTIMENT_TRENDS.sentiment_volatility`

## 7. Language & Communication Analysis
- **Review language distribution**  
  Sources: `FACT_PRODUCT_REVIEWS.review_language`
- **Multilingual sentiment comparison**  
  Sources: `FACT_PRODUCT_REVIEWS.review_language`, `FACT_PRODUCT_REVIEWS.sentiment_score`
- **Translation quality assessment**  
  Sources: `FACT_PRODUCT_REVIEWS.review_text`, `FACT_PRODUCT_REVIEWS.review_text_english`

## 8. Customer Value Analysis
- **Customer value segments**  
  Sources: `CUSTOMER_BASE.lifetime_value`
- **Value vs. sentiment correlation**  
  Sources: `CUSTOMER_BASE.lifetime_value`, `SENTIMENT_TRENDS.avg_sentiment`
- **Value vs. support ticket correlation**  
  Sources: `CUSTOMER_BASE.lifetime_value`, `TICKET_PATTERNS.ticket_count`
- **Value vs. review rating correlation**  
  Sources: `CUSTOMER_BASE.lifetime_value`, `FACT_PRODUCT_REVIEWS.review_rating`

Each of these insights is fully supported by the available data structure and can be derived using the tables and columns shown in the schema. The insights are organized to show the relationships between different data points and how they can be combined to provide meaningful business intelligence.