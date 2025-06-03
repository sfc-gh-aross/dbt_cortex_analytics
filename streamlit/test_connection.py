import streamlit as st
from utils.database import test_connection
import os

st.set_page_config(page_title="Snowflake Connection Test")

st.title("Snowflake Connection Test")

# Debug information
st.write("Current working directory:", os.getcwd())
st.write("Secrets file exists:", os.path.exists(".streamlit/secrets.toml"))

# List all available secrets
st.write("Available secrets:", list(st.secrets.keys()))

# Debug snowflake section
if "snowflake" in st.secrets:
    st.write("Snowflake section exists")
    st.write("Snowflake keys:", list(st.secrets["snowflake"].keys()))
else:
    st.write("Snowflake section does not exist")

if test_connection():
    st.success("✅ Successfully connected to Snowflake!")
    st.write("Connection details:")
    st.json({
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    })
else:
    st.error("❌ Failed to connect to Snowflake. Please check your credentials in .streamlit/secrets.toml") 