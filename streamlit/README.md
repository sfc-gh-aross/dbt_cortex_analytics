# Customer Intelligence Hub

This Streamlit application provides a Customer Intelligence Hub, visualizing various customer analytics dashboards. It leverages Snowflake for data storage and processing, and dbt for data transformation.

## Project Structure

```
streamlit/
├── docs/
│   ├── STREAMLIT_PRD.md
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── .streamlit/
│   │   └── secrets.toml       # Secrets configuration for Streamlit
│   ├── assets/                # Static files (images, css)
│   │   ├── download_data_dark.svg
│   │   ├── download_data_light.svg
│   │   ├── dbt-labs-signature_tm_light.svg
│   │   ├── dbt-labs-logo.svg
│   │   ├── styles.css
│   │   └── snowflake-logo.png
│   ├── components/            # Dashboard components (one per tab)
│   │   ├── __init__.py
│   │   ├── overview.py
│   │   ├── product_feedback.py
│   │   ├── segmentation.py
│   │   ├── sentiment_experience.py
│   │   └── support_ops.py
│   ├── sql/                   # SQL queries organized by dashboard
│   │   ├── overview/
│   │   ├── product_feedback/
│   │   ├── segmentation/
│   │   ├── sentiment_experience/
│   │   └── support_ops/
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── database.py        # Snowflake connector and query execution
│   │   ├── debug.py           # Debug mode utilities
│   │   ├── kpi_cards.py       # Helper for rendering st.metric cards
│   │   └── theme.py           # Theming and styling
│   ├── __init__.py
│   └── requirements.txt       # Python dependencies
└── README.md                  # This file
```

## Features

- **Interactive Dashboards**: Visualizes customer data across multiple dimensions.
    - Overview
    - Sentiment & Experience
    - Support Operations
    - Product Feedback
    - Segmentation
- **Snowflake Integration**: Connects to Snowflake to query and display data.
- **dbt Integration**: (Assumed, based on logos and typical workflow) Leverages dbt for data modeling and transformations within Snowflake.
- **Dynamic Theming**: Supports light and dark modes.
- **Global Filters**: Allows users to filter data by date range and persona.
- **Debug Mode**: Includes a debug mode for development and troubleshooting.

## Key Technologies

- **Streamlit**: For building the interactive web application.
- **Snowflake**: As the data warehouse and query engine. Utilizes Snowflake Cortex for AI functions like sentiment analysis, translation, and text classification.
- **Python**: The primary programming language.
- **Pandas, NumPy, Plotly, Altair, Seaborn**: For data manipulation and visualization.
- **dbt**: (Presumed) For data transformation and modeling.

## Setup and Installation

1.  **Clone the repository.**
2.  **Configure Snowflake Connection:**
    *   Update `src/.streamlit/secrets.toml` with your Snowflake account credentials and connection parameters.
3.  **Install Python dependencies:**
    ```bash
    pip install -r src/requirements.txt
    ```
4.  **(If applicable) Set up dbt project:**
    *   Ensure your dbt project is correctly configured to populate the necessary tables in the `ANALYTICS` schema (e.g., `FACT_CUSTOMER_INTERACTIONS`, `CUSTOMER_BASE`, `FACT_PRODUCT_REVIEWS`, `FACT_SUPPORT_TICKETS`).

## Running the Application

Navigate to the `src` directory and run the Streamlit application:

```bash
cd src
streamlit run app.py
```

## Database Schema

The application relies on several tables within a Snowflake database, typically in an `ANALYTICS` schema. Key tables include:

*   `CUSTOMER_BASE`: Dimension table for customer information, including persona and LTV.
*   `FACT_CUSTOMER_INTERACTIONS`: Fact table containing records of customer interactions, with sentiment scores derived using Snowflake Cortex.
*   `FACT_PRODUCT_REVIEWS`: Fact table for product reviews, including ratings and sentiment scores. Text is translated to English using Snowflake Cortex.
*   `FACT_SUPPORT_TICKETS`: Fact table for support tickets, with sentiment scores and priority classification derived using Snowflake Cortex.

## Components

The application is structured into several components, each representing a tab in the UI:

*   **Overview**: Provides a high-level summary of key metrics.
*   **Sentiment & Experience**: Analyzes customer sentiment and experience trends.
*   **Support Operations**: Focuses on support ticket metrics and operational efficiency.
*   **Product Feedback**: Displays insights from product reviews and ratings.
*   **Segmentation**: Shows customer segmentation based on various attributes.

Each component in the `src/components/` directory has corresponding SQL queries in the `src/sql/` directory.

## Customization

*   **Theme**: Modify `src/utils/theme.py` to change colors, fonts, and other styling aspects.
*   **Dashboards**:
    *   Add new components in `src/components/`.
    *   Register new components in `src/components/__init__.py`.
    *   Add corresponding SQL queries in `src/sql/`.
*   **Data Sources**: Update database connection details in `src/.streamlit/secrets.toml` and modify queries in `src/sql/` if your schema differs.

## Dependencies

The main Python dependencies are listed in `src/requirements.txt`:

```
streamlit>=1.33
snowflake-connector-python
pandas
numpy
plotly>=5
altair>=5
seaborn
streamlit-extras
python-dotenv==1.0.1
pyarrow<19.0.0
xlsxwriter
kaleido>=0.2.1
joypy
pywaffle
bar_chart_race
streamlit-lottie
deck.gl
```
