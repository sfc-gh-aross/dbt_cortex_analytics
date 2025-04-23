import streamlit as st
from typing import Dict, List, Any # Simplified imports
# import json # Removed
# from pathlib import Path # Removed
from datetime import datetime, date

# Helper type for filter values - simplified
FilterValue = Any # Using Any as presets logic is removed

class FilterManager:
    def __init__(self):
        # self.filter_presets_path = Path(__file__).parent.parent / "data" / "filter_presets.json" # Removed
        # self.filter_presets_path.parent.mkdir(exist_ok=True) # Removed
        
        # Initialize session state for filters if not exists
        if "active_filters" not in st.session_state:
            st.session_state.active_filters: Dict[str, FilterValue] = {}
        # if "saved_presets" not in st.session_state: # Removed preset logic
        #     self._load_presets() # Removed preset logic
    
    # --- Preset related methods REMOVED --- 
    # _serialize_value, _serialize_filters, _deserialize_value, _deserialize_filters,
    # _validate_json_file, _load_presets, _save_presets, save_current_preset,
    # load_preset, delete_preset, render_preset_management
    
    def update_filter(self, filter_name: str, value: FilterValue):
        """Update a specific filter value in session state."""
        st.session_state.active_filters[filter_name] = value
    
    def get_active_filters(self) -> Dict[str, FilterValue]:
        """Get a copy of the active filters."""
        # Return a copy to prevent modification outside the class
        return st.session_state.active_filters.copy()
    
    def render_filter_summary(self):
        """Render a summary of active filters in the sidebar."""
        active_filters = self.get_active_filters()
        if active_filters:
            st.sidebar.divider() # Add divider before summary
            st.sidebar.subheader("Active Filters")
            displayed_filters = 0
            for filter_name, value in active_filters.items():
                # Check for non-empty/non-default values before displaying
                # (Customize this logic based on your filter defaults)
                if value is not None and value != [] and value != ['All']: # Example check
                    display_value = ""
                    if isinstance(value, (date, datetime)):
                        display_value = value.strftime('%Y-%m-%d')
                    elif isinstance(value, tuple) and len(value) == 2 and all(isinstance(item, (date, datetime)) for item in value):
                         # Format date range tuple
                        display_value = f"{value[0].strftime('%Y-%m-%d')} to {value[1].strftime('%Y-%m-%d')}"
                    elif isinstance(value, list):
                         display_value = ', '.join(str(v) for v in value)
                    elif isinstance(value, bool):
                         display_value = str(value) # Display True/False
                    else:
                        display_value = str(value)

                    if display_value: # Ensure there's something to show
                        # Clean up filter name for display
                        display_name = filter_name.replace('_', ' ').title()
                        st.sidebar.markdown(f"**{display_name}**: {display_value}")
                        displayed_filters += 1
            # if displayed_filters == 0:
            #      st.sidebar.caption("No active filters applied.") # Optional: Show message if no filters
        # else: # Optional: Show message if filter dict is empty
            # st.sidebar.caption("No active filters applied.") 