import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict, Any
import io

def create_interactive_chart(
    data: pd.DataFrame,
    chart_type: str,
    x: str,
    y: str,
    title: str,
    labels: Dict[str, str],
    color: Optional[str] = None,
    size: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    template: str = "plotly_white",
    height: int = 500,
    width: int = None,
    use_container_width: bool = True
) -> None:
    """Create an interactive chart with enhanced features.
    
    Args:
        data: DataFrame containing the data
        chart_type: Type of chart ('scatter', 'line', 'bar', 'histogram', etc.)
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        labels: Dictionary mapping column names to display labels
        color: Column name for color encoding
        size: Column name for size encoding
        hover_data: List of columns to show in hover tooltip
        template: Plotly template name
        height: Chart height in pixels
        width: Chart width in pixels
        use_container_width: Whether to use full container width
    """
    # Create base figure based on chart type
    if chart_type == 'scatter':
        fig = px.scatter(
            data,
            x=x,
            y=y,
            color=color,
            size=size,
            hover_data=hover_data,
            title=title,
            labels=labels,
            template=template
        )
    elif chart_type == 'line':
        fig = px.line(
            data,
            x=x,
            y=y,
            color=color,
            hover_data=hover_data,
            title=title,
            labels=labels,
            template=template
        )
    elif chart_type == 'bar':
        fig = px.bar(
            data,
            x=x,
            y=y,
            color=color,
            hover_data=hover_data,
            title=title,
            labels=labels,
            template=template
        )
    elif chart_type == 'histogram':
        fig = px.histogram(
            data,
            x=x,
            y=y,
            color=color,
            hover_data=hover_data,
            title=title,
            labels=labels,
            template=template
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    # Add interactive features
    fig.update_layout(
        height=height,
        width=width,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add range slider for time series data
    if pd.api.types.is_datetime64_any_dtype(data[x]):
        fig.update_xaxes(rangeslider_visible=True)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=use_container_width)

def create_drilldown_chart(
    data: pd.DataFrame,
    hierarchy: List[str],
    values: str,
    title: str,
    labels: Dict[str, str],
    color: Optional[str] = None,
    template: str = "plotly_white",
    height: int = 500,
    width: int = None,
    use_container_width: bool = True
) -> None:
    """Create a drilldown chart with hierarchical data.
    
    Args:
        data: DataFrame containing the data
        hierarchy: List of column names representing the hierarchy levels
        values: Column name for the values to display
        title: Chart title
        labels: Dictionary mapping column names to display labels
        color: Column name for color encoding
        template: Plotly template name
        height: Chart height in pixels
        width: Chart width in pixels
        use_container_width: Whether to use full container width
    """
    # Create treemap for hierarchical data
    fig = px.treemap(
        data,
        path=hierarchy,
        values=values,
        color=color,
        title=title,
        labels=labels,
        template=template
    )
    
    # Update layout for better interactivity
    fig.update_layout(
        height=height,
        width=width,
        hovermode='x unified',
        showlegend=True
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=use_container_width)

def create_comparison_chart(
    data: pd.DataFrame,
    x: str,
    y_columns: List[str],
    title: str,
    labels: Dict[str, str],
    chart_types: List[str] = None,
    template: str = "plotly_white",
    height: int = 500,
    width: int = None,
    use_container_width: bool = True
) -> None:
    """Create a comparison chart with multiple y-axes.
    
    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y_columns: List of column names for y-axes
        title: Chart title
        labels: Dictionary mapping column names to display labels
        chart_types: List of chart types for each y-column
        template: Plotly template name
        height: Chart height in pixels
        width: Chart width in pixels
        use_container_width: Whether to use full container width
    """
    if chart_types is None:
        chart_types = ['lines'] * len(y_columns)
    
    # Create subplot figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces for each y-column
    for i, (y_col, chart_type) in enumerate(zip(y_columns, chart_types)):
        if chart_type == 'lines':
            fig.add_trace(
                go.Scatter(
                    x=data[x],
                    y=data[y_col],
                    name=labels.get(y_col, y_col),
                    mode='lines+markers'
                ),
                secondary_y=(i > 0)
            )
        elif chart_type == 'bars':
            fig.add_trace(
                go.Bar(
                    x=data[x],
                    y=data[y_col],
                    name=labels.get(y_col, y_col)
                ),
                secondary_y=(i > 0)
            )
    
    # Update layout
    fig.update_layout(
        title=title,
        height=height,
        width=width,
        template=template,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add range slider for time series data
    if pd.api.types.is_datetime64_any_dtype(data[x]):
        fig.update_xaxes(rangeslider_visible=True)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=use_container_width)

def add_export_options(chart_data: pd.DataFrame, chart_title: str) -> None:
    """Add export options for chart data.
    
    Args:
        chart_data: DataFrame containing the chart data
        chart_title: Title of the chart
    """
    st.download_button(
        label="Download CSV",
        data=chart_data.to_csv(index=False).encode('utf-8'),
        file_name=f"{chart_title.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        chart_data.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button(
        label="Download Excel",
        data=excel_buffer.getvalue(),
        file_name=f"{chart_title.lower().replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) 