import streamlit as st
import snowflake.connector
from snowflake.connector import DictCursor
import logging
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=3600)
def get_snowflake_session():
    """Create and cache a Snowflake session.
    
    Returns:
        snowflake.connector.SnowflakeConnection: A cached Snowflake connection
    """
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