#!/bin/bash

# Script to deploy Streamlit app files to a Snowflake stage using SnowSQL

# Configuration
SNOWFLAKE_STAGE="DBT_CORTEX_LLMS.ANALYTICS.STREAMLIT_STAGE"
# Get the absolute path to the src directory, assuming this script is inside src
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ABS_SRC_DIR="$SCRIPT_DIR" # Since this script is in src, SCRIPT_DIR is ABS_SRC_DIR

# Function to execute a SnowSQL command and check for errors
execute_snowsql() {
    local cmd_description="$1"
    local sql_command="$2"
    local temp_sql_file

    temp_sql_file=$(mktemp) # Create a temporary file

    echo "Executing: $cmd_description"
    # Write SnowSQL commands to the temporary file
    echo "!set exit_on_error=true;" > "$temp_sql_file"
    echo "$sql_command" >> "$temp_sql_file"

    snowsql -c default -f "$temp_sql_file"
    local status=$? # Capture the exit status of snowsql

    rm "$temp_sql_file" # Clean up the temporary file

    if [ $status -ne 0 ]; then
        echo "ERROR: Failed to $cmd_description (Exit Status: $status)"
        exit 1
    fi
    echo "$cmd_description successful."
}

echo "Starting Streamlit app deployment to stage $SNOWFLAKE_STAGE..."
echo "Source directory: $ABS_SRC_DIR"

# Create or Replace the stage
execute_snowsql "Ensure stage $SNOWFLAKE_STAGE exists" "CREATE OR REPLACE STAGE $SNOWFLAKE_STAGE;"

# Upload Python files from the root of src (app.py, __init__.py)
execute_snowsql "Upload root Python files (app.py, __init__.py)" \
  "PUT file://$ABS_SRC_DIR/*.py @$SNOWFLAKE_STAGE/ overwrite=true auto_compress=false;"

# Upload requirements.txt from the root of src
execute_snowsql "Upload requirements.txt" \
  "PUT file://$ABS_SRC_DIR/requirements.txt @$SNOWFLAKE_STAGE/ overwrite=true auto_compress=false;"

# Upload files from assets directory
execute_snowsql "Upload files from assets directory" \
  "PUT file://$ABS_SRC_DIR/assets/* @$SNOWFLAKE_STAGE/assets/ overwrite=true auto_compress=false;"

# Upload files from components directory
execute_snowsql "Upload Python files from components directory" \
  "PUT file://$ABS_SRC_DIR/components/*.py @$SNOWFLAKE_STAGE/components/ overwrite=true auto_compress=false;"

# Upload files from utils directory
execute_snowsql "Upload Python files from utils directory" \
  "PUT file://$ABS_SRC_DIR/utils/*.py @$SNOWFLAKE_STAGE/utils/ overwrite=true auto_compress=false;"

# Upload files from sql/overview directory
execute_snowsql "Upload SQL files from sql/overview directory" \
  "PUT file://$ABS_SRC_DIR/sql/overview/*.sql @$SNOWFLAKE_STAGE/sql/overview/ overwrite=true auto_compress=false;"

# Upload files from sql/product_feedback directory
execute_snowsql "Upload SQL files from sql/product_feedback directory" \
  "PUT file://$ABS_SRC_DIR/sql/product_feedback/*.sql @$SNOWFLAKE_STAGE/sql/product_feedback/ overwrite=true auto_compress=false;"

# Upload files from sql/segmentation directory
execute_snowsql "Upload SQL files from sql/segmentation directory" \
  "PUT file://$ABS_SRC_DIR/sql/segmentation/*.sql @$SNOWFLAKE_STAGE/sql/segmentation/ overwrite=true auto_compress=false;"

# Upload files from sql/sentiment_experience directory
execute_snowsql "Upload SQL files from sql/sentiment_experience directory" \
  "PUT file://$ABS_SRC_DIR/sql/sentiment_experience/*.sql @$SNOWFLAKE_STAGE/sql/sentiment_experience/ overwrite=true auto_compress=false;"

# Upload files from sql/support_ops directory
execute_snowsql "Upload SQL files from sql/support_ops directory" \
  "PUT file://$ABS_SRC_DIR/sql/support_ops/*.sql @$SNOWFLAKE_STAGE/sql/support_ops/ overwrite=true auto_compress=false;"


echo "----------------------------------------------------------------------="
echo "Deployment script finished."
echo "Please ensure your SnowSQL is configured correctly (connection, warehouse, role, etc.)."
echo "After uploading, you can create or update your STREAMLIT object in Snowflake pointing to this stage."
echo "Example CREATE STREAMLIT command (adjust MAIN_FILE and QUERY_WAREHOUSE as needed):"
echo ""
echo "CREATE OR REPLACE STREAMLIT your_streamlit_app_name"
echo "  ROOT_LOCATION = '@${SNOWFLAKE_STAGE}'"
echo "  MAIN_FILE = 'app.py'"
echo "  QUERY_WAREHOUSE = your_query_warehouse;"
echo "----------------------------------------------------------------------="
