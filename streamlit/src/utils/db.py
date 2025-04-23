import streamlit as st
import snowflake.connector

# Initialize connection to Snowflake
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"]
    )

# Helper function to run queries
@st.cache_data(ttl=600)
def run_query(query, params=[]):
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall() 