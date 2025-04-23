import streamlit as st
import plotly.graph_objects as go

def create_metric_card(title, value, trend=None, tooltip=None):
    """Create a metric card with optional trend indicator and tooltip.
    
    Args:
        title (str): Metric title
        value (str): Metric value
        trend (float, optional): Trend percentage. Positive for increase, negative for decrease
        tooltip (str, optional): Tooltip text to show on hover
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=f"{trend:.1f}%" if trend is not None else None
        )
    
    if tooltip and col2.button("ℹ️", key=f"info_{title}"):
        st.info(tooltip)

def create_trend_indicator(value, threshold=0.1):
    """Create a trend indicator based on the value.
    
    Args:
        value (float): The value to indicate trend for
        threshold (float): Threshold for considering a significant change
    
    Returns:
        str: HTML string with trend indicator
    """
    if abs(value) < threshold:
        return "→"  # Neutral
    elif value > 0:
        return "↑"  # Up
    else:
        return "↓"  # Down

def create_info_tooltip(text):
    """Create an info tooltip with the given text.
    
    Args:
        text (str): Tooltip text
    
    Returns:
        str: HTML string with tooltip
    """
    return f'<span title="{text}">ℹ️</span>'

def create_chart_container(title, chart, height=400):
    """Create a container for a chart with title.
    
    Args:
        title (str): Chart title
        chart (plotly.graph_objects.Figure): Plotly figure
        height (int): Chart height in pixels
    """
    st.subheader(title)
    st.plotly_chart(chart, use_container_width=True, height=height)

def create_section_header(title, description=None):
    """Create a section header with optional description.
    
    Args:
        title (str): Section title
        description (str, optional): Section description
    """
    st.markdown(f"### {title}")
    if description:
        st.markdown(description) 