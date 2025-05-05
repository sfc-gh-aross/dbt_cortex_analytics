import os
import streamlit as st

@st.cache_data(ttl=300)
def load_query(query_name: str, query_dir: str) -> str:
    """Load SQL query from file.
    
    Args:
        query_name: Name of the query file without .sql extension
        query_dir: Directory containing the query file
        
    Returns:
        str: SQL query text
    """
    query_path = os.path.join('src', 'queries', query_dir, f'{query_name}.sql')
    with open(query_path, 'r') as f:
        return f.read()

@st.cache_data(ttl=300)
def execute_query(conn, query: str, params: list = None) -> list:
    """Execute SQL query and return results.
    
    Args:
        conn: Snowflake connection object
        query: SQL query text
        params: Query parameters (optional)
        
    Returns:
        list: Query results
    """
    with conn.cursor() as cur:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
