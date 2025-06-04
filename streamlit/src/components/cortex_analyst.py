import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import os
import time
import json
import requests
import pandas as pd # Ensure pandas is imported
from datetime import datetime, timedelta
from utils.utils import get_snowflake_connection, execute_query # Assuming load_query is not needed for this specific flow, added execute_query
import toml # Added for parsing config.toml

# --- Environment Detection ---
_IS_SNOWFLAKE_ENVIRONMENT = False
try:
    import _snowflake
    _IS_SNOWFLAKE_ENVIRONMENT = True
except ImportError:
    pass

# --- Constants ---
SEMANTIC_MODEL_PATH = "@DBT_CORTEX_LLMS.SEMANTIC_MODELS.YAML_STAGE/semantic_model.yaml" # As per PRD, corrected path (adjusted based on error)
API_TIMEOUT_SECONDS = 120
# For _snowflake.send_snow_api_request, path is relative to account, not full URL
SNOWFLAKE_CORTEX_ANALYST_API_PATH = "/api/v2/cortex/analyst/message"

def render_cortex_analyst_tab(filters: dict, debug_mode: bool = False):
    """Render the 'Ask Your Data' tab (Cortex Analyst interface) using REST API"""
    
    st.markdown("""
    <style>
    .custom-ask-button-container div[data-testid="stButton"] button p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    title_col, icon_col = st.columns([10,1], gap="small")
    with title_col:
        st.header("Ask Your Data (Powered by Cortex Analyst)")
    with icon_col:
        st.markdown("ℹ️", help="Allows users to ask business questions in natural language about client analytics. Interfaces with Cortex Analyst via REST API, leveraging a semantic model for answers.")
    
    st.markdown(
        "Use the text box below to ask questions about customer interactions, reviews, support tickets, and personas in natural language. "
        "Cortex Analyst will translate your question into SQL and provide an answer using the Customer Analytics Semantic Model."
    )
    
    # Sample questions with business value context
    st.subheader("Try these sample questions:")
    
    sample_questions_col1, sample_questions_col2 = st.columns(2)
    
    with sample_questions_col1:
        if st.button("Can I see a count of customers and their average sentiment score, grouped by predicted churn risk level?", 
                    help="Why this matters: Understands customer churn likelihood and associated sentiment across different risk levels.",
                    key="sample_q1"):
            st.session_state.user_question = "Can I see a count of customers and their average sentiment score, grouped by predicted churn risk level?"
    
    with sample_questions_col2:
        if st.button("Can you list my top 20 high LTV customers with 'High' churn_risk and a significantly negative sentiment trend, showing key persona signals?", 
                    help="Why this matters: Identifies key high-value customers at risk of churning and the reasons, enabling proactive retention efforts.",
                    key="sample_q2"):
            st.session_state.user_question = "Can you list my top 20 high LTV customers with 'High' churn_risk and a significantly negative sentiment trend, showing key persona signals?"
    
    # Adding a third sample question from verified_queries
    if st.button("Can you identify products where I have an average rating below 3.0 or average review sentiment below -0.1, highlighting potential problem areas?", 
                help="Why this matters: Pinpoints underperforming products based on customer feedback, guiding improvement strategies.",
                key="sample_q3"):
        st.session_state.user_question = "Can you identify products where I have an average rating below 3.0 or average review sentiment below -0.1, highlighting potential problem areas?"
    
    # Adding a fourth sample question from verified_queries
    if st.button("Can you analyze my critical and high priority support tickets, grouped by derived customer persona and ticket category?",
                help="Why this matters: Helps prioritize support resources by understanding which customer segments and issue types generate the most critical tickets.",
                key="sample_q4"): 
        st.session_state.user_question = "Can you analyze my critical and high priority support tickets, grouped by derived customer persona and ticket category?"

    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    
    user_question_input = st.text_area("Your question:", value=st.session_state.user_question, height=100, placeholder="e.g., 'Show me top clients by YTD revenue'", key="user_question_text_area")
    
    st.markdown('<div class="custom-ask-button-container">', unsafe_allow_html=True)
    ask_button_clicked = st.button("Ask Cortex Analyst", key="ask_button")
    st.markdown('</div>', unsafe_allow_html=True)

    if ask_button_clicked:
        if user_question_input:
            st.session_state.user_question = user_question_input # Ensure latest input is used
            ask_cortex_analyst_api(user_question_input)
        else:
            st.warning("Please enter a question.")

    # Display previous conversation/results if any
    if "cortex_analyst_response" in st.session_state and st.session_state.cortex_analyst_response:
        response_data = st.session_state.cortex_analyst_response
        display_cortex_response(
            response_data.get("api_response_json"), 
            response_data.get("execution_time"),
            response_data.get("request_id")
        )

def get_snowflake_credentials_and_url():
    """
    Get Snowflake account, user, Programmatic Access Token (PAT) and API URL 
    for Cortex Analyst API access in standalone mode.
    PAT is read from SNOWFLAKE_PAT_TOKEN environment variable or Streamlit secret.
    """
    try: 
        account_identifier_env = None
        user_env = None # Still useful for context/logging, though not directly for PAT auth header
        pat_token_env = None # Added for PAT
        source_log = []

        # Priority 1: Snowpark session (when running in Snowflake) - for account/user
        # PAT is not sourced from Snowpark session.
        try:
            snowpark_conn = get_snowflake_connection()
            if hasattr(snowpark_conn, 'get_current_account') and hasattr(snowpark_conn, 'get_current_user'):
                current_account = snowpark_conn.get_current_account()
                current_user = snowpark_conn.get_current_user()
                if current_account and current_user:
                    account_identifier_env = current_account.strip('"').upper()
                    user_env = current_user.strip('"').upper()
                    source_log.append("Snowpark session for account/user")
                else:
                    if st.session_state.get("debug_mode"):
                        st.info("Snowpark session returned empty account/user. Trying other methods.")
            else:
                if st.session_state.get("debug_mode"):
                    st.info("Snowpark session object does not have get_current_account/user methods. Trying other methods.")
        except Exception as e:
            if st.session_state.get("debug_mode"):
                st.info(f"Could not get account/user from Snowpark session: {e}. Trying environment variables...")

        # Priority 2: Environment variables
        if not account_identifier_env:
            env_account = os.getenv("SNOWFLAKE_ACCOUNT")
            if env_account:
                account_identifier_env = env_account.upper()
                source_log.append("environment variables for account")
        if not user_env:
            env_user = os.getenv("SNOWFLAKE_USER")
            if env_user:
                user_env = env_user.upper()
                source_log.append("environment variables for user")
        
        env_pat_token = os.getenv("SNOWFLAKE_PAT_TOKEN") # Get PAT from env
        if env_pat_token:
            pat_token_env = env_pat_token
            source_log.append("environment variable for PAT")
        else:
            if st.session_state.get("debug_mode"):
                 st.info("SNOWFLAKE_PAT_TOKEN env var not found. Trying Streamlit secrets...")

        # Priority 3: Streamlit secrets
        if not pat_token_env or not account_identifier_env or not user_env:
            try:
                if hasattr(st, 'secrets'):
                    # Nested [snowflake] section in secrets.toml
                    if "snowflake" in st.secrets:
                        snowflake_secrets = st.secrets.snowflake
                        if not account_identifier_env:
                            account_secret = snowflake_secrets.get("account")
                            if account_secret:
                                account_identifier_env = str(account_secret).upper()
                                source_log.append("Streamlit secrets for account (snowflake.account)")
                        if not user_env:
                            user_secret = snowflake_secrets.get("user")
                            if user_secret:
                                user_env = str(user_secret).upper()
                                source_log.append("Streamlit secrets for user (snowflake.user)")
                        if not pat_token_env:
                            pat_secret = snowflake_secrets.get("pat_token") # e.g., secrets.snowflake.pat_token
                            if pat_secret:
                                pat_token_env = str(pat_secret)
                                source_log.append("Streamlit secrets for PAT (snowflake.pat_token)")
                    # Fallback to top-level secrets for broader compatibility if [snowflake] or specific keys are missing
                    if not account_identifier_env:
                        account_secret_top = st.secrets.get("SNOWFLAKE_ACCOUNT")
                        if account_secret_top:
                            account_identifier_env = str(account_secret_top).upper()
                            source_log.append("Streamlit secrets for account (SNOWFLAKE_ACCOUNT fallback)")
                    if not user_env:
                        user_secret_top = st.secrets.get("SNOWFLAKE_USER")
                        if user_secret_top:
                            user_env = str(user_secret_top).upper()
                            source_log.append("Streamlit secrets for user (SNOWFLAKE_USER fallback)")
                    
                    # PAT Fallback logic starts here
                    if not pat_token_env: # If not found in [snowflake].pat_token
                        pat_secret_top_direct = st.secrets.get("pat_token") # Check for top-level 'pat_token'
                        if pat_secret_top_direct:
                            pat_token_env = str(pat_secret_top_direct)
                            source_log.append("Streamlit secrets for PAT (top-level 'pat_token')")

                    if not pat_token_env: # If still not found, check for conventional top-level 'SNOWFLAKE_PAT_TOKEN'
                        pat_secret_top_conventional = st.secrets.get("SNOWFLAKE_PAT_TOKEN") 
                        if pat_secret_top_conventional:
                            pat_token_env = str(pat_secret_top_conventional)
                            source_log.append("Streamlit secrets for PAT (SNOWFLAKE_PAT_TOKEN fallback)")

                    if not (account_identifier_env and user_env and pat_token_env) and st.session_state.get("debug_mode"):
                        missing_creds = []
                        if not account_identifier_env: missing_creds.append("ACCOUNT")
                        if not user_env: missing_creds.append("USER (for context)")
                        if not pat_token_env: missing_creds.append("PAT_TOKEN")
                        st.info(f"{', '.join(missing_creds)} not found in Streamlit secrets. Trying config.toml for account/user.")
                else:
                    if st.session_state.get("debug_mode"): 
                        st.info("st.secrets attribute not available. Skipping Streamlit secrets.")
            except Exception as e: 
                if st.session_state.get("debug_mode"): 
                    st.info(f"Error accessing Streamlit secrets: {e}. Trying config.toml for account/user.")

        # Priority 4: Snowflake config.toml (for account/user, PAT not typically stored here)
        if not (account_identifier_env and user_env):
            current_script_dir_for_config = os.path.dirname(os.path.abspath(__file__))
            project_root_for_config = os.path.dirname(os.path.dirname(current_script_dir_for_config))
            config_toml_path = os.path.join(project_root_for_config, ".snowflake", "config.toml")
            
            if os.path.exists(config_toml_path):
                try:
                    parsed_config = toml.load(config_toml_path)
                    default_conn_name = parsed_config.get("default_connection_name", "default") 
                    conn_details = None
                    if f"connections.{default_conn_name}" in parsed_config:
                        conn_details = parsed_config[f"connections.{default_conn_name}"]
                    elif default_conn_name in parsed_config:
                         conn_details = parsed_config[default_conn_name]
                    elif "default" in parsed_config.get("connections",{}):
                        conn_details = parsed_config["connections"]["default"]
                    else:
                        if "connections" in parsed_config and isinstance(parsed_config["connections"], dict):
                            for name, c_details in parsed_config["connections"].items():
                                if isinstance(c_details, dict) and (c_details.get("accountname") or c_details.get("account")) and c_details.get("username"): 
                                    conn_details = c_details
                                    if st.session_state.get("debug_mode"):
                                        st.info(f"Using first available connection '{name}' from config.toml as no clear default was specified/found.")
                                    break
                        if not conn_details and (parsed_config.get("accountname") or parsed_config.get("account")) and parsed_config.get("username"):
                            conn_details = parsed_config

                    if conn_details:
                        if not account_identifier_env:
                            acc_id_toml = conn_details.get("accountname") or conn_details.get("account")
                            if acc_id_toml:
                                account_identifier_env = str(acc_id_toml).upper()
                                source_log.append(f"Snowflake config.toml for account ({config_toml_path})")
                        if not user_env:
                            user_toml = conn_details.get("username") or conn_details.get("user")
                            if user_toml:
                                user_env = str(user_toml).upper()
                                source_log.append(f"Snowflake config.toml for user ({config_toml_path})")
                        
                        if not (account_identifier_env and user_env) and st.session_state.get("debug_mode"):
                            st.info(f"'account(name)' or 'user(name)' not found/already sourced from config.toml section.")
                    else:
                        if st.session_state.get("debug_mode"):
                            st.info(f"Could not determine a connection section with account/user in {config_toml_path}.")
                except Exception as e:
                    if st.session_state.get("debug_mode"):
                        st.warning(f"Error parsing Snowflake config.toml at {config_toml_path}: {e}")
            else:
                if st.session_state.get("debug_mode"):
                    st.info(f"Snowflake config.toml not found at {config_toml_path}.")

        if source_log and st.session_state.get("debug_mode"):
            st.success(f"Sourced Snowflake connection details from: {', '.join(list(set(source_log)))}.")
        
        # PAT is essential for standalone API calls now
        if not account_identifier_env or not pat_token_env:
            error_message_parts = []
            if not account_identifier_env: error_message_parts.append("SNOWFLAKE_ACCOUNT")
            if not pat_token_env: error_message_parts.append("SNOWFLAKE_PAT_TOKEN")
            st.error(f"Missing critical credentials for API call: {', '.join(error_message_parts)}. Please set them (e.g., via env vars or Streamlit secrets). SNOWFLAKE_USER is optional but good for context.")
            return None, None, None, None # user, pat_token, base_api_url, account_identifier

        # If user_env is still None but not critical for PAT auth, provide a default or note it.
        if not user_env and st.session_state.get("debug_mode"):
            st.info("SNOWFLAKE_USER not found, but not strictly required for PAT authentication header.")

        api_account_identifier = account_identifier_env.upper()
        api_user = user_env.upper() if user_env else None # User might be None

        account_locator_for_url = api_account_identifier.split('.')[0].lower().replace("_", "-")
        base_api_url = f"https://{account_locator_for_url}.snowflakecomputing.com"
        
        if st.session_state.get("debug_mode"):
            st.success("Successfully sourced credentials for PAT-based standalone API call.")
        return api_user, pat_token_env, base_api_url, api_account_identifier
        
    except Exception as e: 
        st.error(f"A critical error occurred in get_snowflake_credentials_and_url: {e}")
        return None, None, None, None # user, pat_token, base_api_url, account_identifier

def ask_cortex_analyst_api(question):
    """Query Cortex Analyst with the user's natural language question using REST API"""
    
    st.session_state.cortex_analyst_response = None # Clear previous response

    st.write(f"**Your Question:** {question}")
    start_time = time.time()

    # Construct messages_payload (common for both execution paths)
    messages_payload = []
    # Basic conversation history - adapt if more complex history is needed
    # if "conversation_history" in st.session_state: 
    #     messages_payload.extend(st.session_state.conversation_history)
    
    messages_payload.append({
        "role": "user",
        "content": [{"type": "text", "text": question}]
    })

    payload = {
        "messages": messages_payload,
        "semantic_model_file": SEMANTIC_MODEL_PATH, # This path should be valid for both contexts
        "stream": False 
    }

    with st.spinner("Asking Cortex Analyst... This may take a moment."):
        try:
            if _IS_SNOWFLAKE_ENVIRONMENT:
                # --- Snowflake Environment: Use _snowflake.send_snow_api_request ---
                if st.session_state.get("debug_mode"):
                    st.info("Running in Snowflake environment. Using _snowflake.send_snow_api_request.")

                timeout_ms = API_TIMEOUT_SECONDS * 1000
                
                snow_response = _snowflake.send_snow_api_request(
                    "POST",
                    SNOWFLAKE_CORTEX_ANALYST_API_PATH,
                    {},
                    {},
                    payload,
                    None,
                    timeout_ms
                )
                execution_time = time.time() - start_time
                
                response_status = snow_response.get("status")
                response_content_str = snow_response.get("content", "{}")
                api_response_json_data = json.loads(response_content_str)

                if response_status is not None and response_status < 400:
                    st.session_state.cortex_analyst_response = {
                        "api_response_json": api_response_json_data,
                        "execution_time": execution_time,
                        "request_id": api_response_json_data.get("request_id")
                    }
                    # Update conversation history (simple version)
                    # if "conversation_history" not in st.session_state:
                    #     st.session_state.conversation_history = []
                    # st.session_state.conversation_history.append(messages_payload[-1]) # Add user message
                    # if "message" in api_response_json_data:
                    #      st.session_state.conversation_history.append(api_response_json_data["message"])
                else:
                    error_message_sis = f"Cortex Analyst API request failed (Snowflake Env): Status {response_status}"
                    error_details_sis = api_response_json_data
                    if 'message' in error_details_sis: # Make it more descriptive if possible
                        error_message_sis += f" - {error_details_sis.get('message', 'No details')}"
                    
                    st.error(error_message_sis) # Display error immediately
                    # if st.session_state.get("debug_mode"): # Redundant, st.error should suffice
                    #     st.json(error_details_sis)

                    st.session_state.cortex_analyst_response = {
                        "api_response_json": {"error": error_message_sis, "details": error_details_sis},
                        "execution_time": execution_time,
                        "request_id": error_details_sis.get("request_id")
                    }

            else:
                # --- Standalone Environment: Use requests library with Programmatic Access Token (PAT) ---
                if st.session_state.get("debug_mode"):
                    st.info("Running in standalone environment. Using 'requests' library with Programmatic Access Token (PAT).")

                sf_user, pat_token, base_api_url, account_identifier = get_snowflake_credentials_and_url()
                if not (pat_token and base_api_url and account_identifier): # sf_user is optional here
                    # get_snowflake_credentials_and_url() already displayed an error.
                    # Ensure st.rerun() was called there if appropriate
                    return 

                api_url = f"{base_api_url}{SNOWFLAKE_CORTEX_ANALYST_API_PATH}" 

                headers = {
                    "Authorization": f"Bearer {pat_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-Snowflake-Account": account_identifier,
                    "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN" # Specify PAT type
                }
                
                # HTTPBasicAuth is removed as we are using Bearer token with PAT
                # from requests.auth import HTTPBasicAuth
                # auth = HTTPBasicAuth(username, password) 
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=API_TIMEOUT_SECONDS) # auth=auth removed
                execution_time = time.time() - start_time
                response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                
                api_response_json_data = response.json()

                st.session_state.cortex_analyst_response = {
                    "api_response_json": api_response_json_data,
                    "execution_time": execution_time,
                    "request_id": api_response_json_data.get("request_id")
                }
                # Update conversation history (simple version)
                # if "conversation_history" not in st.session_state:
                #     st.session_state.conversation_history = []
                # st.session_state.conversation_history.append(messages_payload[-1])
                # if "message" in api_response_json_data:
                #      st.session_state.conversation_history.append(api_response_json_data["message"])

        except requests.exceptions.HTTPError as http_err: # Specific to 'requests'
            error_message = f"Cortex Analyst API request failed: {http_err.response.status_code}"
            error_details_requests = {}
            try:
                error_details_requests = http_err.response.json()
                error_message += f" - {error_details_requests.get('message', 'No details')}"
                # st.json(error_details_requests) # display_cortex_response will handle details
            except json.JSONDecodeError:
                error_details_requests = {"raw_text": str(http_err.response.text)}
                error_message += f" - Could not parse error JSON. Raw response: {http_err.response.text[:200]}..."
            
            st.error(error_message) # Display error immediately
            st.session_state.cortex_analyst_response = {
                "api_response_json": {"error": error_message, "details": error_details_requests},
                "execution_time": time.time() - start_time if 'start_time' in locals() else 0,
                "request_id": None
            }
        except requests.exceptions.RequestException as req_e: # Specific to 'requests'
            error_message = f"Error calling Cortex Analyst API (Requests): {req_e}"
            st.error(error_message)
            st.session_state.cortex_analyst_response = {
                "api_response_json": {"error": error_message, "details": str(req_e)},
                "execution_time": time.time() - start_time if 'start_time' in locals() else 0,
                "request_id": None
            }
        except Exception as e: 
            # Catch-all for other unexpected errors, including potential errors from _snowflake.send_snow_api_request
            # or json.loads if content is not valid JSON from SiS path.
            error_message = f"An unexpected error occurred: {e}"
            st.error(error_message)
            st.session_state.cortex_analyst_response = {
                "api_response_json": {"error": error_message, "details": str(e)},
                "execution_time": time.time() - start_time if 'start_time' in locals() else 0,
                "request_id": None
            }
        finally:
            st.rerun() # Rerun to display the response or error

def display_cortex_response(api_response_json, execution_time, request_id):
    """Helper function to display the structured response from Cortex Analyst API."""
    
    if not api_response_json:
        st.warning("No response data to display.")
        return

    if "error" in api_response_json:
        # Ensure the error message is prominently displayed, as previous st.error calls
        # might have been cleared by a st.rerun().
        error_msg_text = api_response_json.get('error', 'An unknown error occurred with Cortex Analyst.')
        st.error(error_msg_text)
        
        if "details" in api_response_json and api_response_json['details']:
            with st.expander("Error Details", expanded=True): # Expanded by default for visibility
                details_content = api_response_json['details']
                if isinstance(details_content, dict) or isinstance(details_content, list):
                    st.json(details_content)
                else:
                    # Use st.code for potentially long string stack traces or messages
                    st.code(str(details_content), language=None) 
        return

    analyst_message = api_response_json.get("message")
    if not analyst_message or "content" not in analyst_message:
        st.warning("Response format is not as expected.")
        st.json(api_response_json)
        return

    analyst_content = analyst_message["content"]
    
    generated_sql = None
    sql_confidence = None
    suggestions_list = []

    st.markdown("---") # Separator for the response section

    for item_idx, item in enumerate(analyst_content):
        item_type = item.get("type")

        if item_type == "text":
            st.subheader("Answer:")
            st.markdown(item.get("text", "No textual answer provided."))
        
        elif item_type == "sql":
            generated_sql = item.get("statement")
            sql_confidence = item.get("confidence")
            if generated_sql:
                with st.expander("Generated SQL Query", expanded=False):
                    st.code(generated_sql, language="sql")
                    if sql_confidence:
                        verified_query_used = sql_confidence.get("verified_query_used")
                        if verified_query_used:
                            st.markdown("**Verified Query Used:**")
                            st.json(verified_query_used, expanded=False)
                        # You can add more details from sql_confidence if needed

        elif item_type == "suggestions":
            suggestions_list.extend(item.get("suggestions", []))
        
        # Add handling for other types like "data" if the API might return direct data
        # For now, focusing on executing the SQL

    st.caption(f"Response retrieved in {execution_time:.2f} seconds. Request ID: {request_id or 'N/A'}")

    if generated_sql:
        st.subheader("Query Results:")
        connection = get_snowflake_connection()
        df = execute_query(connection, generated_sql)
        
        if df.empty: # execute_query from utils.utils handles its own st.error and returns empty df on error or no data.
            st.info("Query returned no data, or an error occurred during its execution (check for error messages above).")
        else:
            data_tab, chart_tab = st.tabs(["Data 📄", "Chart 📉"])
            with data_tab:
                st.dataframe(df, use_container_width=True)
            with chart_tab:
                display_charts_for_df(df, chart_key_prefix=f"cortex_chart_{request_id or 'default'}")
    
    if suggestions_list:
        st.subheader("You might also want to ask:")
        num_suggestions = len(suggestions_list)
        cols_per_row = 3
        
        for i in range(0, num_suggestions, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < num_suggestions:
                    suggestion_text = suggestions_list[i+j]
                    if cols[j].button(suggestion_text, key=f"suggestion_{request_id}_{i+j}"):
                        st.session_state.user_question = suggestion_text
                        # Clear previous response before asking new question
                        st.session_state.cortex_analyst_response = None 
                        st.rerun() # This will repopulate the text_area and user can click "Ask"
                                                # Or, we can directly call ask_cortex_analyst_api here

    # Display warnings and response metadata if present
    warnings = api_response_json.get("warnings")
    if warnings:
        with st.expander("Warnings from Cortex Analyst"):
            for warning_idx, warning in enumerate(warnings):
                st.warning(warning.get("message", f"Unnamed warning {warning_idx+1}"))

    response_metadata = api_response_json.get("response_metadata")
    if response_metadata:
        with st.expander("Response Metadata"):
            st.json(response_metadata)
    
def display_charts_for_df(df: pd.DataFrame, chart_key_prefix: str):
    """Displays charting options for a given DataFrame."""
    if df.empty or len(df.columns) < 1:
        st.caption("Not enough data or columns to draw charts.")
        return

    # Create a copy of the DataFrame to avoid modifying the original one passed to the function
    # All subsequent operations for plotting will be done on plot_df
    plot_df = df.copy()

    if len(plot_df.columns) == 1: # If only one column, bar chart of value counts or just show data
        st.caption(f"Only one column ('{plot_df.columns[0]}') in results. Displaying as a bar chart of its values if appropriate.")
        try:
            col_name = plot_df.columns[0]
            # Attempt conversion if not numeric
            if not pd.api.types.is_numeric_dtype(plot_df[col_name]):
                plot_df[col_name] = pd.to_numeric(plot_df[col_name], errors='coerce')
            
            if pd.api.types.is_numeric_dtype(plot_df[col_name]): # Check again after conversion
                 st.bar_chart(plot_df[col_name], use_container_width=True)
            else: # Try value counts for non-numeric or if conversion failed
                 st.bar_chart(plot_df[col_name].value_counts(), use_container_width=True)
        except Exception as e:
            st.warning(f"Could not automatically plot single column: {e}")
        return

    # For 2 or more columns
    st.write("Select columns for charting:")
    all_cols = plot_df.columns.tolist()
    
    col1_select, col2_select = st.columns(2)
    
    x_axis_options = all_cols
    x_axis = col1_select.selectbox(
        "X-axis:", 
        options=x_axis_options, 
        index=0, 
        key=f"{chart_key_prefix}_x_axis"
    )
    
    y_axis_options = [col for col in all_cols if col != x_axis]
    if not y_axis_options: # Should not happen if len(plot_df.columns) >= 2, but as a safe guard.
        y_axis_options = all_cols 
        
    y_axis_default_index = 0
    if y_axis_options: # Ensure options exist
        # Try to find the first column that is numeric or can be coerced to numeric
        found_numeric_default = False
        for i, col_name in enumerate(y_axis_options):
            if pd.api.types.is_numeric_dtype(plot_df[col_name]) or \
               pd.api.types.is_numeric_dtype(pd.to_numeric(plot_df[col_name], errors='coerce')):
                y_axis_default_index = i
                found_numeric_default = True
                break
        
        if not found_numeric_default and len(y_axis_options) > 1:
            y_axis_default_index = 1 # Fallback to index 1 if no numeric found and multiple options
    
    y_axis = col2_select.selectbox(
        "Y-axis (must be numeric for most charts):", 
        options=y_axis_options, 
        index=y_axis_default_index if y_axis_options else 0,
        key=f"{chart_key_prefix}_y_axis"
    )

    if not x_axis or not y_axis:
        st.caption("Please select both X and Y axes.")
        return
    
    # Attempt to convert the selected y_axis column to numeric if it's not already
    if y_axis in plot_df.columns and not pd.api.types.is_numeric_dtype(plot_df[y_axis]):
        original_nan_count = plot_df[y_axis].isnull().sum()
        try:
            plot_df[y_axis] = pd.to_numeric(plot_df[y_axis], errors='coerce')
            converted_nan_count = plot_df[y_axis].isnull().sum()
            if converted_nan_count > original_nan_count:
                st.info(f"Some values in Y-axis ('{y_axis}') could not be converted to numeric and are now represented as missing values.")
        except Exception as e:
            st.warning(f"Failed to convert Y-axis column '{y_axis}' to a numeric type: {e}. Charts may not render as expected.")

    # Check if Y axis is numeric, warn if not for certain charts
    if y_axis in plot_df.columns and not pd.api.types.is_numeric_dtype(plot_df[y_axis]):
        st.warning(f"Y-axis ('{y_axis}') is not numeric. Line and Bar charts might not render correctly.")

    chart_type = st.selectbox(
        "Select chart type:",
        options=["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot"],
        key=f"{chart_key_prefix}_chart_type"
    )

    try:
        # Group by X-axis and sum/mean Y-axis if X is categorical and Y is numeric
        # This helps avoid overplotting or errors with altair/st charts
        df_for_agg_charts = plot_df # Start with plot_df (which is a copy of original df)
        if pd.api.types.is_categorical_dtype(plot_df[x_axis]) or pd.api.types.is_object_dtype(plot_df[x_axis]):
            if y_axis in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df[y_axis]): # Check if y_axis is now numeric
                # Check if multiple y-values per x-category
                if plot_df.groupby(x_axis)[y_axis].count().max() > 1:
                    agg_func = st.radio("Aggregate Y-axis by:", ("Sum", "Mean"), horizontal=True, key=f"{chart_key_prefix}_agg")
                    if agg_func == "Sum":
                        df_for_agg_charts = plot_df.groupby(x_axis, as_index=False)[y_axis].sum()
                    else: # Mean
                        df_for_agg_charts = plot_df.groupby(x_axis, as_index=False)[y_axis].mean()
                    st.caption(f"Note: Y-axis ('{y_axis}') aggregated by {agg_func.lower()} per X-axis category ('{x_axis}').")


        if chart_type == "Bar Chart":
            st.bar_chart(df_for_agg_charts.set_index(x_axis)[y_axis], use_container_width=True)
        elif chart_type == "Line Chart":
            st.line_chart(df_for_agg_charts.set_index(x_axis)[y_axis], use_container_width=True)
        elif chart_type == "Area Chart":
            st.area_chart(df_for_agg_charts.set_index(x_axis)[y_axis], use_container_width=True)
        elif chart_type == "Scatter Plot":
            # Scatter plot should use plot_df which has undergone type conversion but not aggregation
            st.scatter_chart(plot_df, x=x_axis, y=y_axis, use_container_width=True) # Size and color can be added
            
    except Exception as e:
        st.error(f"Could not render chart: {e}")
        st.caption("Please ensure selected columns are compatible with the chart type (e.g., Y-axis is numeric for line/bar charts).")

# Removed simulate_cortex_analyst_response and ask_cortex_analyst_api_real
# as they are now replaced by the live API call.

# Ensure render_cortex_analyst_tab is the main function called if this script is run,
# or that it's correctly imported and called by a main app.py.
# For Streamlit tabs, this structure is usually fine as is. 