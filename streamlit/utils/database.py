"""
Snowflake database connection and query execution utilities.
Handles connection pooling, query execution, and result caching.
"""

from typing import Any, Dict, List, Optional, Union
import os
import snowflake.connector
from snowflake.connector import DictCursor
import streamlit as st
import pandas as pd

class SnowflakeConnection:
    """Manages Snowflake connection and query execution."""
    
    def __init__(self):
        """Initialize connection parameters from Streamlit secrets."""
        self.conn_params = {
            'user': st.secrets["snowflake"]["user"],
            'password': st.secrets["snowflake"]["password"],
            'account': st.secrets["snowflake"]["account"],
            'warehouse': st.secrets["snowflake"]["warehouse"],
            'database': st.secrets["snowflake"]["database"],
            'schema': st.secrets["snowflake"]["schema"]
        }
        self._validate_credentials()
        self._conn = None
        
        # Test connection
        try:
            conn = self.get_connection()
            cur = conn.cursor(DictCursor)
            cur.execute("SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            result = cur.fetchone()
            #st.write("Connected to Snowflake:")
            #st.write(f"- Warehouse: {result['CURRENT_WAREHOUSE()']}")
           # st.write(f"- Database: {result['CURRENT_DATABASE()']}")
           # st.write(f"- Schema: {result['CURRENT_SCHEMA()']}")
            cur.close()
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {str(e)}")
            raise
    
    def _validate_credentials(self) -> None:
        """Validate that all required credentials are present."""
        missing = [k for k, v in self.conn_params.items() if not v]
        if missing:
            raise ValueError(f"Missing required Snowflake credentials: {', '.join(missing)}")
    
    def _read_sql_file(self, sql_path: str) -> str:
        """Read SQL query from a file.
        
        Args:
            sql_path: Path to the SQL file relative to the main 'sql' directory
                      (e.g., "my_query.sql" or "subdir/my_query.sql").
            
        Returns:
            str: SQL query string
        """
        # Get the absolute path to the directory containing this file (utils/)
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the project root directory (streamlit/) by going up one level
        project_root = os.path.dirname(utils_dir)
        # Construct the absolute path to the SQL file
        # sql_path is relative to the 'sql' directory, e.g., "kpis/my_file.sql"
        full_path = os.path.join(project_root, "sql", sql_path)
        
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            st.error(f"SQL file not found at path: {full_path}") # Provide more context in error
            raise # Re-raise the error to be caught by the calling function
    
    @st.cache_resource(ttl=3600)
    def get_connection(_self) -> snowflake.connector.SnowflakeConnection:
        """Get a cached Snowflake connection.
        
        Returns:
            snowflake.connector.SnowflakeConnection: Active connection to Snowflake
        """
        if not _self._conn or _self._conn.is_closed():
            _self._conn = snowflake.connector.connect(**_self.conn_params)
        return _self._conn
    
    @st.cache_data(ttl=300)
    def execute_query(
        _self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a parameterized query and return results.
        
        Args:
            query: SQL query string or path to SQL file relative to src/sql/
            params: Dictionary of parameter values
            
        Returns:
            List of dictionaries containing query results
            
        Raises:
            snowflake.connector.errors.Error: If query execution fails
        """
        try:
            # If query is a file path, read the SQL from file
            if query.endswith('.sql'):
                query = _self._read_sql_file(query)
            
            conn = _self.get_connection()
            cur = conn.cursor(DictCursor)
            
            # Set query tag for monitoring
            cur.execute("ALTER SESSION SET QUERY_TAG='streamlit_app'")
            
            # Execute the query with parameters
            if params:
                # Convert parameters to the format expected by Snowflake
                snowflake_params = {}
                for key, value in params.items():
                    if isinstance(value, list):
                        # Convert list to comma-separated string
                        if not value:
                            snowflake_params[key] = "''"
                        else:
                            # Join list elements with commas and quote the entire string
                            snowflake_params[key] = f"'{','.join(str(v) for v in value)}'"
                    elif isinstance(value, str):
                        if not value:
                            snowflake_params[key] = "''"
                        else:
                            snowflake_params[key] = f"'{value}'"
                    elif isinstance(value, (int, float)):
                        snowflake_params[key] = str(value)
                    else:
                        snowflake_params[key] = str(value)
                
                # Replace named parameters in the query
                for key, value in snowflake_params.items():
                    query = query.replace(f":{key}", value)
                
                cur.execute(query)
            else:
                cur.execute(query)
            
            results = cur.fetchall()
            cur.close()
            return results
                    
        except snowflake.connector.errors.Error as e:
            st.error(f"Snowflake query error: {str(e)}")
            raise
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            raise

# Create a singleton instance
snowflake_conn = SnowflakeConnection()

def run_query(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        query: SQL query string or path to .sql file
        params: Optional dictionary of query parameters
        
    Returns:
        pandas DataFrame with query results
    """
    conn = SnowflakeConnection()
    
    # If query is a file path, read the SQL from file
    if query.endswith('.sql'):
        query = conn._read_sql_file(query)
    
   #st.write("Executing query with parameters:", params)
    results = conn.execute_query(query, params)
    df = pd.DataFrame(results)
    #st.write("Query results DataFrame info:")
    #st.write(df.info())
    #st.write("Query results columns:")
    #st.write(df.columns)
    return df 