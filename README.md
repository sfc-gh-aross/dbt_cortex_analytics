# Customer Analytics Dashboard

A sophisticated Streamlit application for analyzing customer behavior, sentiment, and engagement patterns using Snowflake's data platform.

## Features

- Interactive customer persona analysis
- Sentiment trend visualization
- Support ticket and product review analytics
- Real-time filtering and data exploration
- Exportable customer data

## Prerequisites

- Snowflake account with appropriate permissions
- Access to the following tables in the ANALYTICS schema:
  - CUSTOMER_PERSONA_SIGNALS
  - SENTIMENT_ANALYSIS
  - FACT_SUPPORT_TICKETS
  - FACT_PRODUCT_REVIEWS

## Deployment Instructions

1. Log in to your Snowflake account
2. Navigate to the Streamlit section in Snowsight
3. Create a new Streamlit app
4. Copy the contents of `streamlit_app.py` into the editor
5. Set the following configuration:
   - App name: Customer Analytics Dashboard
   - Warehouse: Your preferred warehouse
   - Database: Your database containing the ANALYTICS schema
   - Schema: ANALYTICS

## Usage

1. Access the dashboard through Snowsight
2. Use the sidebar filters to customize your view:
   - Date range selection
   - Customer persona filtering
   - Churn risk filtering
3. Explore the various visualizations:
   - Customer persona distribution
   - Sentiment analysis
   - Support ticket analysis
   - Product review analysis
4. Download detailed customer data using the export functionality

## Performance Optimization

- Data is cached for 1 hour to improve performance
- Queries are optimized for Snowflake's execution engine
- Progressive loading for large datasets
- Responsive UI design

## Security

- Leverages Snowflake's built-in security model
- Row-level security is respected
- All queries are parameterized to prevent SQL injection
- Session-based authentication

## Troubleshooting

If you encounter any issues:

1. Check your Snowflake permissions
2. Verify table access in the ANALYTICS schema
3. Ensure the warehouse has sufficient resources
4. Clear the browser cache if visualizations are not loading

## Support

For technical support or feature requests, please contact your Snowflake administrator. 