import streamlit as st
import snowflake.connector
from snowflake.connector import DictCursor
import logging
from functools import lru_cache
import os
from dotenv import load_dotenv
import pandas as pd
import random
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_mock_data(query: str) -> list:
    """Generate mock data for standalone mode."""
    personas = ['High Value', 'Mid Value', 'Low Value']
    interaction_types = ['Email', 'Phone', 'Chat', 'Web']
    
    if 'FACT_CUSTOMER_INTERACTIONS' in query and 'CUSTOMER_BASE' in query:
        # Generate mock segment data
        mock_data = []
        for persona in personas:
            for interaction in interaction_types:
                mock_data.append({
                    'PERSONA': persona,
                    'INTERACTION_TYPE': interaction,
                    'INTERACTION_COUNT': random.randint(50, 500)
                })
        return mock_data
    
    return []

@st.cache_resource(ttl=3600)
def get_snowflake_session():
    """Create and cache a Snowflake session.
    
    Returns:
        snowflake.connector.SnowflakeConnection: A cached Snowflake connection
    """
    if os.getenv("DEPLOYMENT_MODE") == "standalone":
        logger.info("Running in standalone mode")
        return None
        
    try:
        # Get credentials from environment variables
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            cursor_class=DictCursor
        )
        logger.info("Successfully connected to Snowflake")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {str(e)}")
        raise

@st.cache_data(ttl=3600)
def execute_query(query: str, params: dict = None) -> list:
    """Execute a Snowflake query with caching.
    
    Args:
        query (str): The SQL query to execute
        params (dict, optional): Query parameters. Defaults to None.
        
    Returns:
        list: Query results as a list of dictionaries
    """
    if os.getenv("DEPLOYMENT_MODE") == "standalone":
        return get_mock_data(query)
        
    try:
        conn = get_snowflake_session()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        cursor.close()
        
        return results
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise

def clear_cache():
    """Clear all cached data and resources."""
    execute_query.clear()
    get_snowflake_session.clear() 