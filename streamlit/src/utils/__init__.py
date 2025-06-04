"""
Utility functions for the Streamlit dashboard.
"""

# From database.py, export the singleton connection object and the run_query function.
# Methods like execute_query or get_connection should be accessed via the snowflake_conn object.
from .database import snowflake_conn, run_query 

# From kpi_cards.py - export render_kpis. render_metric_card was not found.
from .kpi_cards import render_kpis # Removed render_metric_card

from .theme import initialize_theme, apply_theme, render_theme_toggle, toggle_theme
from .debug import display_debug_info, read_sql_file, initialize_debug_mode, render_global_debug_toggle
from .auth import get_snowflake_jwt, get_snowflake_api_base_url

__all__ = [
    # From database.py
    'snowflake_conn',
    'run_query',
    
    # From kpi_cards.py
    'render_kpis', # render_metric_card removed from here as well
    
    # From theme.py
    'initialize_theme',
    'apply_theme',
    'render_theme_toggle',
    'toggle_theme',
    
    # From debug.py
    'display_debug_info',
    'read_sql_file',
    'initialize_debug_mode',
    'render_global_debug_toggle',
    
    # From auth.py
    'get_snowflake_jwt',
    'get_snowflake_api_base_url'
] 