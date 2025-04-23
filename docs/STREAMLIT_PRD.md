# Customer Analytics Streamlit Application - PRD

**Version:** 1.0.1
**Date:** {{ TODAY'S DATE }}
**Author:** AI Assistant (Gemini) & User
**Last Updated:** {{ TODAY'S DATE }}

## 1. Introduction & Goals

**Purpose:** To create an interactive, visually appealing, and insightful Streamlit application for analyzing customer data derived from various sources (interactions, product reviews, support tickets). The application aims to provide actionable insights into customer sentiment, support effectiveness, product feedback, and overall customer health.

**Goals:**
*   Provide a centralized dashboard for key customer metrics.
*   Visualize sentiment trends and distributions across different customer touchpoints.
*   Analyze support ticket patterns, priorities, and potential bottlenecks.
*   Surface insights from product reviews, including multi-lingual feedback.
*   Enable segmentation and analysis based on customer personas, value, churn risk, and upsell opportunities.
*   Offer interactive filtering capabilities for focused analysis.
*   Adhere to best practices for UI/UX, ensuring the app is intuitive, performant, and aesthetically pleasing.

**Success Metrics:**
* **User Adoption:** Track daily/weekly active users across different roles
* **Performance:** Page load times < 2 seconds for main dashboard, < 1 second for filtered views
* **User Satisfaction:** Collect feedback through a built-in feedback widget
* **Business Impact:** Monitor actions taken based on insights (e.g., successful interventions for high-risk customers)

## 2. Target Audience

*   **Customer Success Managers (CSMs):** To monitor individual customer health, sentiment, and identify at-risk customers or upsell opportunities.
*   **Support Managers:** To analyze ticket volumes, priorities, categories, and agent performance (if agent data were included).
*   **Product Managers:** To understand product feedback, feature requests, and sentiment related to specific products (if product ID filtering is added).
*   **Marketing Analysts:** To understand customer personas, segment audiences, and analyze sentiment trends.
*   **Executives:** To get a high-level overview of customer satisfaction, churn risk, and overall business health related to customer experience.

**User Stories:**
* As a CSM, I want to quickly identify my at-risk customers so I can proactively reach out before they churn
* As a Support Manager, I want to understand ticket patterns so I can optimize team staffing
* As a Product Manager, I want to analyze sentiment trends by product feature to prioritize improvements
* As a Marketing Analyst, I want to segment customers effectively for targeted campaigns
* As an Executive, I want to track overall customer health metrics at a glance

## 3. Key Features & Functionality

The application will be structured using `st.tabs` for clear navigation between different analysis areas, inspired by the tabs shown in the sample image. A persistent sidebar (`st.sidebar`) will house global filters.

### 3.1 Global Filters (Sidebar)

*   **Date Range:** `st.date_input` with start and end dates to filter data across all relevant tables (e.g., `interaction_date`, `review_date`, `ticket_date`). Default to a sensible range (e.g., last year or all time).
*   **Customer Value Segment:** `st.multiselect` based on the `value_segment` derived in Query 7 (`High Value`, `Medium Value`, `Low Value`). Populated from `ANALYTICS.CUSTOMER_BASE`.
*   **Derived Persona:** `st.multiselect` based on `derived_persona` from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS`.
*   **Churn Risk:** `st.multiselect` based on `churn_risk` from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS`.
*   **Upsell Opportunity:** `st.multiselect` based on `upsell_opportunity` from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS`.
*   **Interaction Type:** `st.multiselect` based on `interaction_type` from `ANALYTICS.FACT_CUSTOMER_INTERACTIONS`.
*   **Review Language:** `st.multiselect` based on `review_language` from `ANALYTICS.FACT_PRODUCT_REVIEWS`.

*(UX Note: Display active filters clearly below the controls in the sidebar, as shown in the sample image.)*

**Filter Behavior:**
* Filters should apply instantly with visual feedback
* Add "Clear All" and "Reset to Default" options
* Show count of filtered results
* Allow saving filter combinations as presets
* Add date range presets (Last 7 days, Last 30 days, YTD, etc.)

### 3.2 Overview Dashboard (Default Tab)

*   **KPIs:** Display key metrics prominently at the top using `st.metric`, potentially in `st.columns`. Calculate these based on filtered data.
    *   **Average Sentiment:** Overall average `sentiment_score` from `ANALYTICS.SENTIMENT_ANALYSIS`. Include delta vs. previous period if feasible.
    *   **Total Interactions:** Count of records in `ANALYTICS.SENTIMENT_ANALYSIS`. Include delta.
    *   **Overall Churn Risk:** Percentage of customers classified as 'High' risk in `ANALYTICS.CUSTOMER_PERSONA_SIGNALS`. Include delta or comparison.
    *   **Average Product Rating:** Average `review_rating` from `ANALYTICS.FACT_PRODUCT_REVIEWS`. Include delta.
*   **Sentiment Trend:** `st.line_chart` showing average `sentiment_score` from `ANALYTICS.SENTIMENT_ANALYSIS` aggregated by month/week over the selected date range.
*   **Customer Sentiment Distribution:** `st.bar_chart` showing the count of customers per `overall_sentiment` category (`Positive`, `Neutral`, `Negative`) from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS` (similar to Query 1).
*   **Churn Risk Breakdown:** `st.bar_chart` showing customer counts by `churn_risk` level (`High`, `Medium`, `Low`) from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS` (similar to Query 2).

### 3.3 Sentiment & Experience Analysis Tab

*   **Sentiment Over Time (by Source):** `st.line_chart` showing average `sentiment_score` trend, allowing users to select/deselect sources (`interaction`, `review`, `ticket`) using `st.multiselect`. Data from `ANALYTICS.SENTIMENT_ANALYSIS`.
*   **Sentiment Distribution (by Source):** Use `st.columns` to show `st.bar_chart` for sentiment distribution for each source (`interaction`, `review`, `ticket`).
*   **Sentiment Volatility vs. Trend:** `st.scatter_chart` plotting `sentiment_volatility` against `sentiment_trend` for customers (`ANALYTICS.SENTIMENT_TRENDS`), potentially colored by `overall_sentiment`. Add tooltips showing `customer_id`.
*   **Interaction Type Sentiment:** `st.bar_chart` showing average `sentiment_score` per `interaction_type` (`ANALYTICS.FACT_CUSTOMER_INTERACTIONS`) (similar to Query 6).

### 3.4 Support Operations Insights Tab

*   **Ticket Volume Trend:** `st.line_chart` showing the number of tickets created over time (`ANALYTICS.FACT_SUPPORT_TICKETS`, aggregated by day/week/month).
*   **Ticket Priority Breakdown:** `st.bar_chart` or `st.plotly_chart` (e.g., a pie chart) showing the count of tickets by `priority_level` (`ANALYTICS.FACT_SUPPORT_TICKETS`) (similar to Query 3). Include average sentiment per priority level.
*   **Ticket Category Analysis:** `st.bar_chart` showing ticket count per `ticket_category` (`ANALYTICS.FACT_SUPPORT_TICKETS`), perhaps ordered by volume.
*   **Tickets per Customer Distribution:** `st.histogram` (using Plotly via `st.plotly_chart`) showing the distribution of `ticket_count` per customer (`ANALYTICS.TICKET_PATTERNS`).
*   **Extracted Insights Table:** `st.dataframe` displaying recent tickets (`ANALYTICS.FACT_SUPPORT_TICKETS`) with columns for `ticket_description`, `priority_level`, `expected_resolution_timeframe`, `requested_remedy`. Allow sorting.

### 3.5 Product Feedback Analysis Tab

*   **Average Rating Trend:** `st.line_chart` showing average `review_rating` over time (`ANALYTICS.FACT_PRODUCT_REVIEWS`).
*   **Rating Distribution:** `st.bar_chart` showing the count of reviews for each `review_rating` (1 to 5).
*   **Sentiment by Language:** `st.bar_chart` showing average `sentiment_score` and review count per `review_language` (`ANALYTICS.FACT_PRODUCT_REVIEWS`) (similar to Query 5).
*   **Review Samples:** `st.dataframe` showing recent reviews, including `review_text`, `review_text_english`, `review_rating`, `sentiment_score`. Maybe use `st.expander` for longer reviews.
*   *(Future: Add Product ID filter if data allows)*

### 3.6 Customer Segmentation & Value Tab

*   **Persona Distribution:** `st.bar_chart` showing customer counts per `derived_persona` (`ANALYTICS.CUSTOMER_PERSONA_SIGNALS`).
*   **Value Segments Analysis:** Use `st.columns` to show key metrics (Avg Sentiment, Avg Tickets, Avg Rating) per `value_segment` using `st.metric` or small bar charts (`ANALYTICS.CUSTOMER_PERSONA_SIGNALS` joined with `ANALYTICS.CUSTOMER_BASE`) (similar to Query 7).
*   **Churn Risk vs. Upsell Opportunity:** `st.plotly_chart` (e.g., a 2D histogram or density heatmap) showing the distribution of customers based on `churn_risk` and `upsell_opportunity` (`ANALYTICS.CUSTOMER_PERSONA_SIGNALS`). Color intensity could represent customer count. (Similar to Query 4).
*   **Segment Explorer Table:** `st.data_editor` or `st.dataframe` showing data from `ANALYTICS.CUSTOMER_PERSONA_SIGNALS` allowing sorting and filtering by persona, churn risk, upsell opportunity, etc. Include `customer_summary`.

### 3.7 Individual Customer Deep Dive (Optional/Future Feature)

*   Add a `st.selectbox` (perhaps in the sidebar or a dedicated tab) to search/select a specific `customer_id`.
*   Display a dedicated view for that customer:
    *   Key signals (`derived_persona`, `churn_risk`, `upsell_opportunity`, `avg_sentiment`, etc.) using `st.metric`.
    *   The `customer_summary` from `ANALYTICS.INSIGHT_SUMMARIES`.
    *   Timeline/Table of their interactions, reviews, and tickets using dataframes.

### 3.8 Data Export & Sharing

* **Export Options:**
    * CSV export for all data tables
    * PDF export for dashboard views
    * Scheduled report generation and email delivery
* **URL Sharing:**
    * Generate shareable links with filter states preserved
    * Optional password protection for sensitive views

### 3.9 User Preferences & Settings

* **Customization Options:**
    * Default dashboard view
    * Preferred date range
    * Chart color schemes
    * Metric display formats
* **Notifications:**
    * Alert settings for key metrics
    * Email digest frequency
    * Custom threshold alerts

## 4. Data Sources & Requirements

### 4.1 Data Sources

**Snowflake Database:** `DBT_CORTEX_LLMS`
**Schema:** `ANALYTICS`

**Core Tables:**
*   `ANALYTICS.CUSTOMER_PERSONA_SIGNALS`
*   `ANALYTICS.FACT_CUSTOMER_INTERACTIONS`
*   `ANALYTICS.FACT_PRODUCT_REVIEWS`
*   `ANALYTICS.FACT_SUPPORT_TICKETS`
*   `ANALYTICS.SENTIMENT_ANALYSIS`
*   `ANALYTICS.SENTIMENT_TRENDS`
*   `ANALYTICS.TICKET_PATTERNS`
*   `ANALYTICS.CUSTOMER_BASE`
*   `ANALYTICS.INSIGHT_SUMMARIES`

### 4.2 Data Requirements

**Critical Requirements:**
* **Source of Truth:** All data MUST come exclusively from the Snowflake tables defined in `dbt_alternative.sql`. No other data sources are permitted.
* **No Mock Data:** The application MUST NOT use any mock, sample, or hard-coded data, even during development.
* **Data Integrity:** All visualizations, metrics, and analysis MUST reflect actual data from Snowflake tables.
* **Filter Consistency:** All filters MUST operate on the actual columns and values present in the Snowflake tables.
* **Reference Data:** Any reference data (e.g., category labels, status types) MUST be derived from the existing Snowflake table values.

**Development Guidelines:**
* Use actual table schemas for type checking and validation
* Derive all dropdown/selection options from table data
* Test with real data volumes and distributions
* Handle all possible NULL values and edge cases in real data
* Use actual date ranges from the data for temporal filters

**Prohibited Practices:**
* ❌ Hard-coding any metrics or values
* ❌ Using mock or sample data, even temporarily
* ❌ Creating synthetic data for testing
* ❌ Adding placeholder visualizations
* ❌ Using assumed or example category values

### 4.3 Data Refresh & Caching

**Real-time metrics updated every 5 minutes**
**Historical data refreshed daily**
**Cache invalidation strategy for filtered views**
**Backup data source handling for system resilience**

## 5. Visualizations & UI/UX Details

*   **Layout:** Primarily use `st.tabs` for main sections and `st.sidebar` for global filters. Use `st.columns` within tabs for side-by-side charts/metrics.
*   **Charts:** Leverage native Streamlit charts (`st.line_chart`, `st.bar_chart`, `st.scatter_chart`, `st.metric`) where possible for simplicity and performance. Use `st.plotly_chart` for more complex visualizations (histograms, heatmaps, potentially pie charts if deemed appropriate UX-wise). Ensure clear titles and labels on all charts.
*   **Interactivity:** Filters should dynamically update all relevant charts and tables on the page. Use tooltips on charts to show specific data points. Make data tables (`st.dataframe`, `st.data_editor`) sortable.
*   **Feedback:** Use `st.spinner("Loading data...")` during Snowflake query execution. Use `st.toast` for brief notifications if needed (e.g., "Filters applied"). Display informative messages like `st.info` if filters result in no data.
*   **Styling:** Aim for a clean, modern aesthetic similar to the provided sample image. Use whitespace effectively. Ensure good contrast and readability. Leverage Streamlit's default theme options first. Minimal custom CSS via `st.markdown` only if absolutely necessary for specific branding or layout tweaks.

**Accessibility Requirements:**
* WCAG 2.1 AA compliance
* Keyboard navigation support
* Screen reader compatibility
* Color-blind friendly palettes
* Responsive design for different screen sizes

**Error States & Empty States:**
* Clear error messages for query failures
* Helpful empty state messages with suggested actions
* Graceful degradation when features are unavailable
* Retry mechanisms for failed data loads

## 6. Non-Functional Requirements

*   **Performance:** Implement caching (`@st.cache_data`) for Snowflake queries to ensure responsiveness, especially when filters change. Optimize queries for speed. Paginate large tables if necessary.
*   **Maintainability:** Write clean, modular Python code with comments where necessary. Store Snowflake connection details securely using Streamlit secrets.
*   **Error Handling:** Gracefully handle potential database connection errors or query failures, displaying informative messages to the user.

**Security Requirements:**
* Role-based access control (RBAC)
* Data encryption in transit and at rest
* Audit logging of user actions
* Compliance with data privacy regulations

**Performance Targets:**
* Page load time < 2 seconds (95th percentile)
* Query response time < 500ms (95th percentile)
* Support for 100+ concurrent users
* Maximum memory usage < 2GB

**Monitoring & Logging:**
* Application health metrics
* User interaction tracking
* Error rate monitoring
* Performance profiling
* Usage analytics

## 7. Implementation Phases

### Phase 1 (MVP) - Weeks 1-4
* Basic dashboard with essential KPIs
* Core filtering functionality
* Primary visualizations
* Basic error handling

### Phase 2 - Weeks 5-8
* Advanced analytics features
* Export functionality
* Enhanced filtering
* Performance optimizations

### Phase 3 - Weeks 9-12
* User customization features
* Advanced sharing options
* Integration with other tools
* Enhanced security features

## 8. Testing Requirements

**Functional Testing:**
* Unit tests for data processing
* Integration tests for Snowflake queries
* End-to-end testing of user workflows
* Cross-browser compatibility

**Performance Testing:**
* Load testing with simulated users
* Query performance benchmarking
* Memory leak detection
* Cache effectiveness validation

**User Testing:**
* Usability testing with representatives from each user role
* A/B testing of new features
* Accessibility testing
* Beta testing program

## 9. Maintenance & Support

**Regular Maintenance:**
* Daily monitoring of system health
* Weekly performance review
* Monthly security patches
* Quarterly feature updates

**Support Procedures:**
* Tier 1: Basic user support
* Tier 2: Technical issues
* Tier 3: Data & system problems
* Documentation & training materials

## 10. Success Criteria & KPIs

**Usage Metrics:**
* Daily Active Users (DAU)
* Average session duration
* Feature adoption rates
* Export/share activity

**Performance Metrics:**
* Page load times
* Query response times
* Error rates
* System uptime

**Business Impact:**
* Reduction in customer churn
* Improvement in support efficiency
* Increase in upsell success rate
* User satisfaction scores

## 11. Future Considerations

*   Add Product ID filtering.
*   Include Agent ID analysis in the Support section.
*   Integrate topic modeling results for reviews/tickets.
*   Add functionality to export filtered data (e.g., to CSV).
*   Implement the "Individual Customer Deep Dive" feature.
*   Add user authentication/authorization if needed.
*   More sophisticated time-based comparisons (WoW, MoM changes).

**Technical Debt Management:**
* Regular code reviews
* Performance optimization sprints
* Documentation updates
* Architecture evolution planning

**Innovation Roadmap:**
* AI-powered insights
* Predictive analytics
* Mobile app development
* API development for external integration

## 12. Appendix

**Glossary:**
* Key terms and definitions
* Technical acronyms
* Business metrics explained

**Reference Materials:**
* Snowflake schema documentation
* UI/UX guidelines
* Brand style guide
* Security policies

## 13. Recommended Project Structure

A well-organized project structure is crucial for maintainability and collaboration. Here's a recommended structure for this Streamlit application:

```
.
├── .streamlit/
│   └── secrets.toml         # Store Snowflake credentials and other secrets
│   └── config.toml          # Streamlit theme and configuration options
├── app.py                   # Main Streamlit application script (entry point)
├── src/                     # Source code directory for modularity
│   ├── components/          # Reusable UI components
│   │   ├── overview_dashboard.py
│   │   ├── customer_insights.py
│   │   └── product_analytics.py
│   ├── queries/            # SQL queries organized by component
│   │   ├── overview_dashboard/
│   │   │   ├── kpi_queries.sql
│   │   │   ├── sentiment_queries.sql
│   │   │   └── churn_queries.sql
│   │   ├── customer_insights/
│   │   │   ├── persona_queries.sql
│   │   │   └── interaction_queries.sql
│   │   └── product_analytics/
│   │       ├── review_queries.sql
│   │       └── rating_queries.sql
│   ├── __init__.py
│   ├── data_loader.py       # Functions to connect to Snowflake and fetch data
│   ├── charts.py            # Functions to generate Plotly/Streamlit charts
│   ├── filters.py           # Logic for handling sidebar filters
│   ├── processing.py        # Data processing/transformation functions
│   └── utils.py             # General utility functions
├── assets/                  # Static assets (images, custom CSS if unavoidable)
│   └── logo.png
│   └── custom_style.css
├── tests/                   # Unit and integration tests
│   ├── test_data_loader.py
│   └── test_processing.py
├── .gitignore               # Specifies intentionally untracked files
├── requirements.txt         # Project dependencies
└── README.md                # Project overview, setup instructions
```

**Explanation:**

*   **`.streamlit/`**: Standard Streamlit directory for configuration (`config.toml`) and secrets management (`secrets.toml`).
*   **`app.py`**: The main entry point for the Streamlit application. It handles global setup, sidebar definition, and tab navigation using `st.tabs()`.
*   **`src/components/`**: Contains modular UI components for each tab of the application:
    *   **`overview_dashboard.py`**: Component for the Overview Dashboard tab
    *   **`customer_insights.py`**: Component for the Customer Insights tab
    *   **`product_analytics.py`**: Component for the Product Analytics tab
*   **`src/queries/`**: Contains all SQL queries organized by component and functionality:
    *   **`overview_dashboard/`**: Queries for the Overview Dashboard
        *   **`kpi_queries.sql`**: Queries for KPI metrics
        *   **`sentiment_queries.sql`**: Queries for sentiment analysis
        *   **`churn_queries.sql`**: Queries for churn risk analysis
    *   **`customer_insights/`**: Queries for Customer Insights
        *   **`persona_queries.sql`**: Queries for persona analysis
        *   **`interaction_queries.sql`**: Queries for customer interactions
    *   **`product_analytics/`**: Queries for Product Analytics
        *   **`review_queries.sql`**: Queries for product reviews
        *   **`rating_queries.sql`**: Queries for rating analysis
*   **`src/`**: A dedicated source directory to keep the codebase organized and modular.
    *   **`data_loader.py`**: Centralizes all Snowflake connection logic and data fetching. This module reads and executes queries from the `queries/` directory.
    *   **`charts.py`**: Contains functions dedicated to creating the various charts (line, bar, scatter, plotly) used across different components.
    *   **`filters.py`**: Encapsulates the logic for creating and managing the global sidebar filters and applying them to the data.
    *   **`processing.py`**: If any complex data transformations are needed after fetching from Snowflake but before visualization, place them here.
    *   **`utils.py`**: For miscellaneous helper functions used across the application.

**SQL Query Organization Guidelines:**

1. **Modularity**: Each query file should focus on a specific aspect of the dashboard (e.g., KPIs, sentiment, churn).
2. **Reusability**: Common query patterns should be extracted into reusable CTEs or views.
3. **Documentation**: Each query file should include:
   * Purpose of the query
   * Input parameters
   * Expected output format
   * Any dependencies on other queries
4. **Version Control**: Track changes to queries separately from application code.
5. **Testing**: Include sample data and expected results for query testing.
6. **Performance**: Optimize queries for execution time and resource usage.
7. **Maintainability**: Use consistent naming conventions and formatting.

This structure separates concerns (data loading, visualization, component layout), making the application easier to understand, test, and maintain as it grows. The use of components instead of pages allows for better code organization and reusability while maintaining a single-page application experience.
