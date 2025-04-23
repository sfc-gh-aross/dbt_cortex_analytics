# Customer Analytics Dashboard

A sophisticated Streamlit application for analyzing customer behavior, sentiment, and engagement patterns using Snowflake's data platform and dbt for data transformation.

## Project Structure

```
.
├── dbt/                    # dbt project for data transformation
│   ├── models/            # SQL models
│   ├── seeds/             # Seed data
│   ├── macros/            # Reusable SQL macros
│   └── setup.sql          # Snowflake environment setup
├── streamlit/             # Streamlit application
│   ├── app/               # Application code
│   └── docs/              # Documentation
├── snowflake_sql/         # Additional Snowflake SQL scripts
├── data/                  # Sample data files
└── quickstart_docs/       # Quickstart documentation
```

## Features

- Interactive customer persona analysis
- Sentiment trend visualization
- Support ticket and product review analytics
- Real-time filtering and data exploration
- Exportable customer data
- AI-powered insights using Snowflake Cortex LLM functions

## Prerequisites

- Snowflake account with appropriate permissions
- Access to the following tables in the ANALYTICS schema:
  - CUSTOMER_PERSONA_SIGNALS
  - SENTIMENT_ANALYSIS
  - FACT_SUPPORT_TICKETS
  - FACT_PRODUCT_REVIEWS
- dbt Cloud account (optional, for data transformation)
- Python 3.8+ with required packages (see requirements.txt)

## Setup Instructions

1. Clone this repository
2. Set up your Snowflake environment using `dbt/setup.sql`
3. Configure your dbt project:
   - Update `dbt/dbt_project.yml` with your Snowflake credentials
   - Run `dbt deps` to install dependencies
   - Run `dbt run` to build the data models
4. Deploy the Streamlit app:
   - Navigate to the Streamlit section in Snowsight
   - Create a new Streamlit app
   - Copy the contents of `streamlit/app/` into the editor
   - Configure the app settings:
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
- Efficient use of Snowflake Cortex LLM functions

## Security

- Leverages Snowflake's built-in security model
- Row-level security is respected
- All queries are parameterized to prevent SQL injection
- Session-based authentication
- Secure handling of API keys and credentials

## Troubleshooting

If you encounter any issues:

1. Check your Snowflake permissions
2. Verify table access in the ANALYTICS schema
3. Ensure the warehouse has sufficient resources
4. Clear the browser cache if visualizations are not loading
5. Check the dbt logs for any transformation errors
6. Verify your Snowflake Cortex LLM function access

## Support

For technical support or feature requests, please contact your Snowflake administrator or open an issue in the repository. 