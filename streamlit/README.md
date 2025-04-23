# Customer Analytics Streamlit App

## Overview
A centralized dashboard for analyzing customer data from various sources including interactions, product reviews, and support tickets. The application provides actionable insights into customer sentiment, support effectiveness, product feedback, and overall customer health.

## Key Features
* Interactive dashboard with essential KPIs and metrics
* Sentiment trend analysis across customer touchpoints
* Support ticket pattern analysis and priority tracking
* Product feedback analysis with multi-lingual support
* Customer segmentation by persona, value, churn risk, and upsell opportunity
* Global filtering capabilities for focused analysis
* Real-time data updates with 5-minute refresh for KPIs
* Daily refresh for historical trends and aggregated statistics

## Architecture & Folder Structure
```
.
├── .streamlit/
│   └── secrets.toml         # Snowflake credentials
│   └── config.toml          # Streamlit configuration
├── app.py                   # Main application entry point
├── src/                     # Source code modules
│   ├── components/          # Reusable UI components
│   │   ├── overview_dashboard.py
│   │   ├── sentiment_experience.py
│   │   ├── support_operations.py
│   │   ├── product_feedback.py
│   │   └── customer_segmentation.py
│   ├── queries/            # SQL query definitions
│   │   ├── overview_queries.py
│   │   ├── sentiment_queries.py
│   │   ├── support_queries.py
│   │   ├── product_queries.py
│   │   └── segmentation_queries.py
│   └── utils/              # Utility functions
│       └── db.py           # Database connection and query execution
├── assets/                  # Static assets
├── tests/                   # Unit and integration tests
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Setup & Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure Snowflake credentials in `.streamlit/secrets.toml`

## Running the App
1. Ensure Snowflake credentials are configured
2. Activate the virtual environment
3. Run the app: `streamlit run app.py`
4. Access the dashboard at `http://localhost:8501`

## Usage Tips
* Use the sidebar for global filtering across all views
* KPIs update every 5 minutes automatically
* Historical data refreshes daily
* Export functionality available for all data tables
* URL sharing preserves filter states
* Keyboard navigation supported
* Screen reader compatible

## Contributing
* Follow the project structure and coding standards
* Write unit tests for new features
* Document all changes in pull requests
* Ensure WCAG 2.1 AA compliance
* Maintain performance targets:
  * Page load time < 2 seconds (95th percentile)
  * Query response time < 500ms (95th percentile)
  * Maximum memory usage < 2GB

## License
Proprietary - All rights reserved