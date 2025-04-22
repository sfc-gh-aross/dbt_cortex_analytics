import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_snowflake_connection():
    try:
        # Get credentials from environment variables
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        
        # Test the connection with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        
        print(f"Successfully connected to Snowflake!")
        print(f"Snowflake version: {version}")
        
        # Test database access
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
        db, schema = cursor.fetchone()
        print(f"Current database: {db}")
        print(f"Current schema: {schema}")
        
        # Test table access
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"- {table[1]}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {str(e)}")

if __name__ == "__main__":
    test_snowflake_connection() 