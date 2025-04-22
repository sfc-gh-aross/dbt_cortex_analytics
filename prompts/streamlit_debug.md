Prompt:
conda activate py311

Run the Streamlit app using streamlit run:
conda activate py311 && DEPLOYMENT_MODE=snowflake SNOWFLAKE_ACCOUNT=SFSEEUROPE-DEMO_AROSS SNOWFLAKE_PASSWORD='*hZMAiqGx*s_qwv7' SNOWFLAKE_USER=DBT_USER SNOWFLAKE_ROLE=DBT_ROLE SNOWFLAKE_WAREHOUSE=CORTEX_WH SNOWFLAKE_DATABASE=DBT_CORTEX_LLMS SNOWFLAKE_SCHEMA=ANALYTICS streamlit run app.py

load the .env file if needed. Monitor for any terminal errors, including those triggered by UI interactions—not just on initial load. For each error, analyze the cause, apply a fix, and rerun the app. Repeat this process until all errors are resolved and the app runs error-free. use the settings below

# Deployment mode (snowflake or standalone)
DEPLOYMENT_MODE=standalone
# Snowflake connection parameters
SNOWFLAKE_ACCOUNT=SFSEEUROPE-DEMO_AROSS
SNOWFLAKE_PASSWORD=*hZMAiqGx*s_qwv7
SNOWFLAKE_USER=DBT_USER
SNOWFLAKE_ROLE=DBT_ROLE
SNOWFLAKE_WAREHOUSE=CORTEX_WH
SNOWFLAKE_DATABASE=DBT_CORTEX_LLMS
SNOWFLAKE_SCHEMA=ANALYTICS