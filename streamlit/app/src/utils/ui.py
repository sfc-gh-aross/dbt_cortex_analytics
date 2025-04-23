import streamlit as st
from functools import wraps
import time
from typing import Callable, Any, Union, Optional
import logging
import pandas as pd

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

def display_trend_indicator(
    current_value: Union[int, float],
    previous_value: Union[int, float],
    label: str,
    format: str = "{:.1f}%",
    show_arrow: bool = True
) -> None:
    """Display a metric with trend indicator.
    
    Args:
        current_value: Current value to display
        previous_value: Previous value for comparison
        label: Label for the metric
        format: Format string for the value
        show_arrow: Whether to show trend arrow
    """
    # Calculate percentage change
    if previous_value != 0:
        change = ((current_value - previous_value) / abs(previous_value)) * 100
    else:
        change = 0
    
    # Create trend indicator
    if show_arrow:
        if change > 0:
            trend_icon = "↑"
            trend_class = "trend-up"
        elif change < 0:
            trend_icon = "↓"
            trend_class = "trend-down"
        else:
            trend_icon = "→"
            trend_class = ""
    else:
        trend_icon = ""
        trend_class = ""
    
    # Display metric
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            label=label,
            value=format.format(current_value),
            delta=format.format(change) if change != 0 else None
        )
    with col2:
        if trend_icon:
            st.markdown(f'<div class="{trend_class}" style="font-size: 2rem;">{trend_icon}</div>', unsafe_allow_html=True)

def create_card(
    title: str,
    content: Optional[str] = None,
    width: int = None
) -> None:
    """Create a card container with consistent styling.
    
    Args:
        title: Card title
        content: Optional content to display in the card
        width: Optional width of the card (in columns)
    """
    if width:
        col = st.columns(width)[0]
        with col:
            st.markdown(f"### {title}")
            if content:
                st.markdown(content)
    else:
        st.markdown(f"### {title}")
        if content:
            st.markdown(content)

def display_data_table(
    data: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
    use_container_width: bool = True
) -> None:
    """Display a styled data table with consistent formatting.
    
    Args:
        data: DataFrame to display
        title: Optional title for the table
        height: Height of the table in pixels
        use_container_width: Whether to use full container width
    """
    if title:
        st.markdown(f"### {title}")
    
    st.dataframe(
        data,
        height=height,
        use_container_width=use_container_width
    ) 