import streamlit as st
from typing import Any, Callable, Optional
import pandas as pd
from functools import wraps
import time

def with_tooltip(text: str) -> Callable:
    """Decorator to add a tooltip to any Streamlit component."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            st.markdown(f'<div title="{text}">', unsafe_allow_html=True)
            result = func(*args, **kwargs)
            st.markdown('</div>', unsafe_allow_html=True)
            return result
        return wrapper
    return decorator

class EnhancedLoadingState:
    """Simple loading state with spinner."""
    def __init__(self, message: str = "Loading..."):
        self.message = message
        self.spinner = None

    def __enter__(self):
        self.spinner = st.spinner(self.message)
        return self.spinner.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner:
            self.spinner.__exit__(exc_type, exc_val, exc_tb)

def show_toast(message: str, type: str = "success", duration: int = 3):
    """Show a toast notification with customizable type and duration."""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    elif type == "info":
        st.info(message)
    time.sleep(duration)

def enhanced_dataframe(
    data: pd.DataFrame,
    height: int = 400,
    use_container_width: bool = True
) -> None:
    """Display an enhanced dataframe with sorting and filtering capabilities."""
    st.dataframe(
        data,
        height=height,
        use_container_width=use_container_width
    )

def with_loading_and_feedback(
    message: str = "Loading...",
    success_message: Optional[str] = None,
    error_message: Optional[str] = None
) -> Callable:
    """Decorator that adds loading state and feedback to a function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                with EnhancedLoadingState(message):
                    result = func(*args, **kwargs)
                    if success_message:
                        show_toast(success_message, "success")
                    return result
            except Exception as e:
                if error_message:
                    show_toast(f"{error_message}: {str(e)}", "error")
                raise
        return wrapper
    return decorator 