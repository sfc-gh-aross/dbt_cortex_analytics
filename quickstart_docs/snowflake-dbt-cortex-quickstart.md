# 🧠 Snowflake + dbt + Cortex LLM Functions Quickstart 🚀

Welcome to this exciting hands-on guide where you'll discover how Snowflake Cortex LLM functions can transform your data analysis! This quickstart focuses on extracting hidden insights from customer data that would be impossible to uncover with SQL alone. 🔍

## ✨ What You'll Learn ✨

In this guide, you'll:
- 📊 Set up Snowflake and dbt Cloud accounts
- 📁 Ingest nested JSON data with rich customer insights
- 🔄 Transform raw data using dbt models
- 🤖 Apply Cortex LLM functions to discover patterns and correlations
- 🧩 Uncover hidden customer sentiment and behavior patterns
- 📈 Create cross-departmental insights that drive business value

## 🏗️ Project Structure 🏗️

Your dbt project will have the following structure:

```
dbt/
├── dbt_project.yml          # Project configuration
├── models/
│   ├── staging/            # Staging models
│   │   ├── sources.yml     # Source definitions
│   │   ├── stg_customer_interactions.sql
│   │   ├── stg_product_reviews.sql
│   │   └── stg_support_tickets.sql
│   ├── fact/              # Fact models
│   │   ├── fact_customer_interactions.sql
│   │   ├── fact_product_reviews.sql
│   │   └── fact_support_tickets.sql
│   └── analysis/          # Analysis models
│       ├── sentiment_analysis.sql
│       ├── sentiment_trends.sql
│       ├── ticket_patterns.sql
│       ├── insight_summaries.sql
│       └── customer_persona_signals.sql
└── docs/                  # Documentation
    └── erd.md            # Entity Relationship Diagram
```

## 🏗️ Data Model Architecture 🏗️

Let's understand the data model we're building. The architecture consists of three main layers:

### 1. Source Layer (Raw Data)
- `CUSTOMER_INTERACTIONS` - Raw JSON containing customer interaction notes
- `PRODUCT_REVIEWS` - Raw JSON containing product reviews in multiple languages
- `SUPPORT_TICKETS` - Raw JSON containing support ticket details
- `CUSTOMERS` - Raw JSON containing customer profile data

### 2. Staging Layer (Cleaned Data)
The staging layer transforms raw JSON into structured tables:
- `STG_CUSTOMER_INTERACTIONS` - Parsed interaction data with standardized fields
- `STG_PRODUCT_REVIEWS` - Parsed review data with language identification
- `STG_SUPPORT_TICKETS` - Parsed ticket data with categorization
- `STG_CUSTOMERS` - Parsed customer profile data

### 3. Analytics Layer (Enriched Data)
The analytics layer adds AI-powered insights:
- `FACT_CUSTOMER_INTERACTIONS` - Interactions enriched with sentiment scores
- `FACT_PRODUCT_REVIEWS` - Reviews with sentiment analysis and translations
- `FACT_SUPPORT_TICKETS` - Tickets with priority scoring and resolution predictions
- `SENTIMENT_ANALYSIS` - Cross-channel sentiment tracking
- `SENTIMENT_TRENDS` - Temporal analysis of customer sentiment
- `TICKET_PATTERNS` - Support ticket behavior analysis
- `INSIGHT_SUMMARIES` - AI-generated customer interaction summaries
- `CUSTOMER_PERSONA_SIGNALS` - Comprehensive customer behavior profiles

### 📊 Entity Relationship Diagram (ERD)

![Entity Relationship Diagram](docs/erd.png)

The ERD above shows our complete data model with three distinct layers:
- **Source Layer (Top)**: Raw JSON tables containing customer data
- **Staging Layer (Middle)**: Structured tables with standardized fields
- **Analytics Layer (Bottom)**: AI-enriched tables with derived insights

All tables are connected through `customer_id`, allowing us to track customer behavior across all touchpoints. The diagram shows how raw data is progressively enriched with AI-powered insights like sentiment scores, priority levels, and persona signals.

### 🔄 Data Lineage (DAG)

![Data Lineage Graph](docs/dbt-dag.png)

The DAG above visualizes how data flows through our transformation pipeline:
- **Green nodes**: Raw source data
- **Blue nodes**: Transformed and enriched models
- **Arrows**: Dependencies between models

This lineage shows how we progressively enrich customer data, starting from raw JSON files and culminating in our comprehensive `customer_persona_signals` model.

## 🛠️ Prerequisites 🛠️

- Basic SQL knowledge
- Basic understanding of data transformation concepts
- Curiosity about AI-powered analytics! 😄

## 📝 Sign-Up for Required Services 📝

### 1. Create a Snowflake Trial Account
Sign up for a [Snowflake 30-day trial account](https://signup.snowflake.com/?utm=cortex-llm-dbt)

### 2. Create a dbt Cloud Trial Account
Sign up for a [dbt Cloud trial account](https://www.getdbt.com/signup/)

## 🏢 The Business Challenge: Unlocking Customer Insights 🏢

Our dataset contains rich customer behavior signals across interactions, reviews, and support tickets. Traditional SQL analysis would miss many of these insights, but with Cortex LLM functions, we can:

- 🔍 Discover hidden sentiment patterns in customer communications
- 🗣️ Process multilingual customer feedback without translation workflows
- 📊 Identify high-value customers at risk of churning
- 🚩 Flag potential escalation cases before they become critical
- 💡 Extract product improvement ideas from unstructured feedback

## 💾 The Dataset: Connected Customer Touchpoints 💾

Our synthetic dataset represents a complete customer journey with meaningful correlations:

1. `customer_interactions.json` - Customer interaction notes with sentiment signals
2. `product_reviews.json` - Product reviews in multiple languages with sentiment correlations
3. `support_tickets.json` - Support tickets with urgency and categorization signals

The dataset contains several customer personas (satisfied, frustrated, neutral, mixed, new) whose behaviors are consistent across all three data sources—making it perfect for demonstrating how Cortex LLM functions can identify patterns that SQL alone would miss.

## 🚀 Let's Get Started! 🚀

### Step 1: Configure Snowflake ❄️

First, let's set up our Snowflake environment:

```sql
-- Create a warehouse, database, and schema
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE WAREHOUSE CORTEX_WH 
  WITH WAREHOUSE_SIZE = 'MEDIUM' 
  AUTO_SUSPEND = 60 
  AUTO_RESUME = TRUE;

CREATE OR REPLACE DATABASE DBT_CORTEX_LLMS;

-- Create schemas for our different layers
CREATE OR REPLACE SCHEMA DBT_CORTEX_LLMS.RAW;
CREATE OR REPLACE SCHEMA DBT_CORTEX_LLMS.STAGE;
CREATE OR REPLACE SCHEMA DBT_CORTEX_LLMS.ANALYTICS;

USE WAREHOUSE CORTEX_WH;
USE DATABASE DBT_CORTEX_LLMS;
USE SCHEMA RAW;

-- Create file format for JSON 
CREATE OR REPLACE FILE FORMAT DBT_CORTEX_LLMS.RAW.JSON_FORMAT
  TYPE = 'JSON'
  STRIP_OUTER_ARRAY = TRUE;

-- Create stages pointing to our public S3 bucket
CREATE OR REPLACE STAGE DBT_CORTEX_LLMS.RAW.RAW_DATA_STAGE
  URL = 's3://snowflake-dbt-cortex-quickstart/retail_data/'
  FILE_FORMAT = DBT_CORTEX_LLMS.RAW.JSON_FORMAT;
  
-- Create raw tables
CREATE OR REPLACE TABLE DBT_CORTEX_LLMS.RAW.CUSTOMER_INTERACTIONS (
  data VARIANT
);

CREATE OR REPLACE TABLE DBT_CORTEX_LLMS.RAW.PRODUCT_REVIEWS (
  data VARIANT
);

CREATE OR REPLACE TABLE DBT_CORTEX_LLMS.RAW.SUPPORT_TICKETS (
  data VARIANT
);

-- Load data from staged files
COPY INTO DBT_CORTEX_LLMS.RAW.CUSTOMER_INTERACTIONS
FROM @DBT_CORTEX_LLMS.RAW.RAW_DATA_STAGE/customer_interactions.json
FILE_FORMAT = (FORMAT_NAME = DBT_CORTEX_LLMS.RAW.JSON_FORMAT);

COPY INTO DBT_CORTEX_LLMS.RAW.PRODUCT_REVIEWS
FROM @DBT_CORTEX_LLMS.RAW.RAW_DATA_STAGE/product_reviews.json
FILE_FORMAT = (FORMAT_NAME = DBT_CORTEX_LLMS.RAW.JSON_FORMAT);

COPY INTO DBT_CORTEX_LLMS.RAW.SUPPORT_TICKETS
FROM @DBT_CORTEX_LLMS.RAW.RAW_DATA_STAGE/support_tickets.json
FILE_FORMAT = (FORMAT_NAME = DBT_CORTEX_LLMS.RAW.JSON_FORMAT);
```

### Step 2: Configure dbt Project

Create a new directory for your dbt project and set up the following files:

#### dbt_project.yml
```yaml
name: 'dbt_cortex'
version: '1.0.0'
config-version: 2

profile: 'default'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  dbt_cortex:
    staging:
      +materialized: view
      +schema: stage
    fact:
      +materialized: table
      +schema: analytics
    analysis:
      +materialized: table
      +schema: analytics
```

#### models/staging/sources.yml
```yaml
version: 2

sources:
  - name: raw
    database: DBT_CORTEX_LLMS
    schema: RAW
    tables:
      - name: customer_interactions
      - name: product_reviews
      - name: support_tickets
```

#### models/staging/stg_customer_interactions.sql
```sql
with source as (
    select 
        data
    from {{ source('raw', 'customer_interactions') }}
),

staged as (
    select
        data:interaction_id::varchar as interaction_id,
        data:customer_id::varchar as customer_id,
        TO_TIMESTAMP_NTZ(data:interaction_date::varchar) as interaction_date,
        data:agent_id::varchar as agent_id,
        data:interaction_type::varchar as interaction_type,
        data:interaction_notes::varchar as interaction_notes
    from source
)

select * from staged
```

#### models/staging/stg_product_reviews.sql
```sql
with source as (
    select 
        data
    from {{ source('raw', 'product_reviews') }}
),

staged as (
    select
        data:review_id::varchar as review_id,
        data:customer_id::varchar as customer_id,
        data:product_id::varchar as product_id,
        TO_TIMESTAMP_NTZ(data:review_date::varchar) as review_date,
        data:review_rating::number as review_rating,
        data:review_text::varchar as review_text,
        data:review_language::varchar as review_language
    from source
)

select * from staged
```

#### models/staging/stg_support_tickets.sql
```sql
with source as (
    select 
        data
    from {{ source('raw', 'support_tickets') }}
),

staged as (
    select
        data:ticket_id::varchar as ticket_id,
        data:customer_id::varchar as customer_id,
        TO_TIMESTAMP_NTZ(data:ticket_date::varchar) as ticket_date,
        data:ticket_status::varchar as ticket_status,
        data:ticket_category::varchar as ticket_category,
        data:ticket_description::varchar as ticket_description
    from source
)

select * from staged
```

### Step 3: Set up dbt Profile

Create or update your `~/.dbt/profiles.yml`:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <your-account>
      user: <your-user>
      password: <your-password>
      role: ACCOUNTADMIN
      database: DBT_CORTEX_LLMS
      warehouse: CORTEX_WH
      schema: RAW
      threads: 4
```

### Step 4: Initialize and Test

From your project root, run:

```bash
cd dbt
dbt deps
dbt debug
dbt run
```

### Step 5: Generate Documentation

After your models are running successfully, generate and view the documentation:

```bash
cd dbt
dbt docs generate
dbt docs serve
```

Visit http://localhost:8080 to view your documentation, including the DAG visualization of your models.

## 🎯 Business Value by Department 🎯

Let's explore how different departments can leverage these Cortex LLM-powered insights:

### 🛍️ Marketing

**Without Cortex LLM:**
- Segments customers based only on purchase history
- Manual review of feedback in English only
- Campaigns based on demographic data without sentiment context

**With Cortex LLM:**
- Targets campaigns based on detected customer sentiment and needs
- Automatically processes feedback in any language
- Identifies brand advocates with high positive sentiment
- Creates personalized messaging based on specific customer concerns

### 💰 Finance

**Without Cortex LLM:**
- Tracks only quantitative metrics like revenue and refunds
- Cannot predict customer churn from sentiment
- Missing context around billing complaints

**With Cortex LLM:**
- Forecasts revenue risk from sentiment trends
- Anticipates refund requests before they occur
- Identifies payment friction points from support tickets
- Prioritizes billing issues by detected urgency

### 💼 Sales

**Without Cortex LLM:**
- Relies on CRM data without sentiment context
- Misses upsell opportunities with satisfied customers
- Cannot prioritize retention efforts effectively

**With Cortex LLM:**
- Targets retention efforts on high-churn-risk accounts
- Identifies perfect timing for upgrade conversations
- Tailors pitches to address specific detected concerns
- Provides salespeople with sentiment-aware conversation starters

### 👥 HR

**Without Cortex LLM:**
- Evaluates support agents on limited metrics
- Manual review of customer interactions
- Generic training for all agents

**With Cortex LLM:**
- Identifies which agents excel at turning around negative sentiment
- Spots training opportunities based on customer frustration signals
- Creates targeted coaching based on specific interaction patterns
- Develops training from successful de-escalation examples

### 🎧 Customer Service

**Without Cortex LLM:**
- Tickets prioritized by age or manual review
- No advance warning of escalation risk
- Cannot anticipate specific customer expectations

**With Cortex LLM:**
- Auto-prioritizes tickets based on detected urgency and sentiment
- Identifies at-risk customers before escalation occurs
- Surfaces specific expected resolution timeframes
- Provides agents with sentiment context before conversations

## 🌟 Adding Cortex Analyst and Streamlit Visualization 🌟

Let's enhance our data exploration capabilities by setting up Cortex Analyst for natural language querying and creating a beautiful Streamlit dashboard:

```sql
-- Create a schema for semantic models
CREATE OR REPLACE SCHEMA RETAIL_ANALYTICS.SEMANTIC_MODELS;

-- Create a stage for storing the semantic model YAML file
CREATE OR REPLACE STAGE RETAIL_ANALYTICS.SEMANTIC_MODELS.CUSTOMER_INSIGHTS;

-- Upload the semantic model YAML to the stage (you can do this via Snowsight UI)
-- The YAML defines business-friendly metadata about your customer data
-- allowing natural language queries through Cortex Analyst

-- Create a Streamlit in Snowflake app
-- In Snowsight, navigate to Streamlit > Create
-- Name it "Customer Insights Explorer" 
-- Select the CORTEX_WH warehouse
-- Paste the Streamlit code from the customer_insights_explorer.py file

-- Ensure the semantic model path in the Streamlit app matches your stage path:
-- SEMANTIC_MODEL_PATH = "RETAIL_ANALYTICS.SEMANTIC_MODELS.CUSTOMER_INSIGHTS/customer_insights.yaml"

-- Once configured, the app will allow business users to:
-- 1. Query customer data using natural language
-- 2. Visualize persona distributions and sentiment patterns
-- 3. Identify at-risk customers and upsell opportunities 
-- 4. Explore customer insights without writing SQL
```

With this setup, business users can explore customer personas through natural language, making data-driven decisions accessible to your entire organization! 🚀

## 📊 Visualizing Your Insights

With the Streamlit dashboard you've built, your team can now:

- 👀 Visually identify customer sentiment patterns at a glance
- 🔍 Explore detailed customer profiles enriched by AI
- 🚨 Quickly spot and prioritize at-risk relationships
- 📱 Access insights from any device with a web browser
- 🤝 Share the same view of customer health across departments

The interactive nature of the dashboard allows for exploration and discovery that static reports can't provide!

## 📚 Resources 📚

- [Snowflake Cortex LLM Documentation](https://docs.snowflake.com/en/user-guide/cortex-llm)
- [dbt Documentation](https://docs.getdbt.com/)
- [dbt-Snowflake Integration Guide](https://docs.getdbt.com/reference/warehouse-setups/snowflake-setup)
- [Streamlit in Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

## 🎉 Congratulations! 🎉

You've successfully built an advanced customer analytics pipeline that leverages Snowflake Cortex LLM functions to extract insights that would be impossible with traditional SQL alone! You can now:

- 🔮 Predict customer behavior based on sentiment patterns
- 🗣️ Understand customer feedback in any language
- ⚠️ Identify at-risk relationships before they deteriorate
- 💡 Uncover improvement opportunities from unstructured data
- 🎯 Target your efforts on the customers who need attention most
- 📈 Visualize and share these insights across your organization

This foundation can be extended to solve countless business challenges by bridging the gap between structured data and human communication. Happy analyzing! ✨
