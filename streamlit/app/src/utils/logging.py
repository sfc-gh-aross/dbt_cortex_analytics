import logging
import sys
from pathlib import Path
import streamlit as st

def setup_logging():
    """Configure logging for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger("customer_analytics")
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        log_dir / "customer_analytics.log"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Streamlit handler
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.ERROR:
                st.error(self.format(record))
            elif record.levelno >= logging.WARNING:
                st.warning(self.format(record))
            elif record.levelno >= logging.INFO:
                st.info(self.format(record))
    
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setFormatter(console_formatter)
    logger.addHandler(streamlit_handler)
    
    return logger

def log_query_execution(query: str, params: dict = None):
    """Log query execution details.
    
    Args:
        query (str): The SQL query being executed
        params (dict, optional): Query parameters. Defaults to None.
    """
    logger = logging.getLogger("customer_analytics")
    logger.info(f"Executing query: {query}")
    if params:
        logger.info(f"Query parameters: {params}")

def log_error(error: Exception, context: str = None):
    """Log error with context.
    
    Args:
        error (Exception): The error that occurred
        context (str, optional): Additional context about where the error occurred
    """
    logger = logging.getLogger("customer_analytics")
    if context:
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True) 