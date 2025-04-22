import streamlit as st
from functools import wraps
import time
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class LoadingState:
    """Context manager for showing loading states."""
    def __init__(self, message: str = "Loading..."):
        self.message = message
        self.spinner = None

    def __enter__(self):
        self.spinner = st.spinner(self.message)
        return self.spinner.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner:
            self.spinner.__exit__(exc_type, exc_val, exc_tb)

def with_loading(message: str = "Loading..."):
    """Decorator for showing loading states during function execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with LoadingState(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_error(func: Callable) -> Callable:
    """Decorator for consistent error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again or contact support if the issue persists.")
            return None
    return wrapper

def show_empty_state(message: str = "No data available"):
    """Display a consistent empty state message."""
    st.info(message)
    st.markdown("---")

def show_success(message: str):
    """Display a success message."""
    st.success(message)

def show_warning(message: str):
    """Display a warning message."""
    st.warning(message)

def show_info(message: str):
    """Display an info message."""
    st.info(message)

def show_error(message: str):
    """Display an error message."""
    st.error(message) 