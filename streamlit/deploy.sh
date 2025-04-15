#!/bin/bash
# Simple deployment script for Customer Insights Dashboard

# Display header
echo "🚀 Customer Insights Dashboard Deployment"
echo "=========================================="
echo ""

# Try to use the snowflake.yml file directly first
if [ -f "snowflake.yml" ]; then
  echo "Found snowflake.yml file. Attempting to deploy with Snowflake CLI..."
  echo "snow streamlit deploy streamlit_app --replace --database DBT_CORTEX_LLMS --schema ANALYTICS --role DBT_ROLE"
  snow streamlit deploy streamlit_app --replace --database DBT_CORTEX_LLMS --schema ANALYTICS --role DBT_ROLE
  
  # Check if deployment worked
  if [ $? -eq 0 ]; then
    echo "✅ Deployment successful with Snowflake CLI!"
    exit 0
  else
    echo "❌ Deployment with Snowflake CLI failed."
    echo "This could be due to missing connection details or permissions."
  fi
fi

# If we get here, try running the SQL script
echo ""
echo "Attempting to deploy using SQL script..."
echo ""

# Use Snowsql with configuration
echo "For successful deployment, you'll need to provide your Snowflake connection details when prompted:"
echo "- Account (yourorg-account)"
echo "- Username"
echo "- Password (will not be displayed)"
echo "- Database (DBT_CORTEX_LLMS)"
echo "- Schema (ANALYTICS)"
echo "- Role (DBT_ROLE)"
echo ""

echo "Running: snowsql -f streamlits_setup.sql"
snowsql -f streamlits_setup.sql -d DBT_CORTEX_LLMS -s ANALYTICS -r DBT_ROLE

# Check if deployment worked
if [ $? -eq 0 ]; then
  echo "✅ Deployment successful with SQL script!"
else
  echo "❌ SQL deployment also failed."
  echo ""
  echo "You can also try the deployment bash script:"
  echo "cd .. && ./.snow/deploy/streamlit/deploy.sh"
fi 