import streamlit as st
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime, date

class FilterManager:
    def __init__(self):
        self.filter_presets_path = Path(__file__).parent.parent / "data" / "filter_presets.json"
        self.filter_presets_path.parent.mkdir(exist_ok=True)
        
        # Initialize session state for filters if not exists
        if "active_filters" not in st.session_state:
            st.session_state.active_filters = {}
        if "saved_presets" not in st.session_state:
            self._load_presets()
    
    def _serialize_filters(self, filters: Dict) -> Dict:
        """Convert date objects to strings for JSON serialization."""
        serialized = {}
        for key, value in filters.items():
            if isinstance(value, (date, datetime)):
                serialized[key] = value.isoformat()
            elif isinstance(value, list):
                serialized[key] = [
                    item.isoformat() if isinstance(item, (date, datetime)) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    def _deserialize_filters(self, filters: Dict) -> Dict:
        """Convert date strings back to date objects."""
        deserialized = {}
        for key, value in filters.items():
            if isinstance(value, str):
                try:
                    # Try to parse as datetime first
                    deserialized[key] = datetime.fromisoformat(value).date()
                except (ValueError, TypeError):
                    deserialized[key] = value
            elif isinstance(value, list):
                deserialized[key] = [
                    datetime.fromisoformat(item).date() if isinstance(item, str) and 'T' in item else item
                    for item in value
                ]
            else:
                deserialized[key] = value
        return deserialized
    
    def _validate_json_file(self):
        """Validate and fix the JSON file if needed."""
        if not self.filter_presets_path.exists():
            return
        
        try:
            # Try to read the file
            with open(self.filter_presets_path, "r") as f:
                content = f.read().strip()
                
            # If file is empty or invalid, initialize with empty dict
            if not content:
                with open(self.filter_presets_path, "w") as f:
                    json.dump({}, f)
                return
            
            # Try to parse the JSON
            json.loads(content)
            
        except json.JSONDecodeError:
            # If JSON is invalid, create a new empty file
            with open(self.filter_presets_path, "w") as f:
                json.dump({}, f)
    
    def _load_presets(self):
        """Load saved filter presets from file."""
        try:
            # Validate the JSON file first
            self._validate_json_file()
            
            if self.filter_presets_path.exists():
                with open(self.filter_presets_path, "r") as f:
                    content = f.read().strip()
                    if not content:
                        st.session_state.saved_presets = {}
                        return
                        
                    loaded_presets = json.loads(content)
                    st.session_state.saved_presets = {
                        name: self._deserialize_filters(filters)
                        for name, filters in loaded_presets.items()
                    }
            else:
                st.session_state.saved_presets = {}
        except Exception as e:
            st.error(f"Error loading filter presets: {str(e)}")
            # Initialize with empty presets on error
            st.session_state.saved_presets = {}
            # Create a new empty file
            with open(self.filter_presets_path, "w") as f:
                json.dump({}, f)
    
    def _save_presets(self):
        """Save filter presets to file."""
        try:
            serialized_presets = {
                name: self._serialize_filters(filters)
                for name, filters in st.session_state.saved_presets.items()
            }
            with open(self.filter_presets_path, "w") as f:
                json.dump(serialized_presets, f, indent=2)  # Add indentation for better readability
        except Exception as e:
            st.error(f"Error saving filter presets: {str(e)}")
            # Try to create a new empty file
            try:
                with open(self.filter_presets_path, "w") as f:
                    json.dump({}, f)
            except:
                pass
    
    def save_current_preset(self, preset_name: str):
        """Save current filter state as a preset."""
        if not preset_name.strip():
            st.error("Preset name cannot be empty")
            return
            
        st.session_state.saved_presets[preset_name] = st.session_state.active_filters.copy()
        self._save_presets()
        st.success(f"Filter preset '{preset_name}' saved successfully!")
    
    def load_preset(self, preset_name: str):
        """Load a saved filter preset."""
        if preset_name in st.session_state.saved_presets:
            st.session_state.active_filters = st.session_state.saved_presets[preset_name].copy()
            st.success(f"Filter preset '{preset_name}' loaded successfully!")
        else:
            st.error(f"Preset '{preset_name}' not found!")
    
    def delete_preset(self, preset_name: str):
        """Delete a saved filter preset."""
        if preset_name in st.session_state.saved_presets:
            del st.session_state.saved_presets[preset_name]
            self._save_presets()
            st.success(f"Filter preset '{preset_name}' deleted successfully!")
        else:
            st.error(f"Preset '{preset_name}' not found!")
    
    def update_filter(self, filter_name: str, value: any):
        """Update a specific filter value."""
        st.session_state.active_filters[filter_name] = value
    
    def get_active_filters(self) -> Dict:
        """Get all active filters."""
        return st.session_state.active_filters.copy()
    
    def render_filter_summary(self):
        """Render a summary of active filters."""
        if st.session_state.active_filters:
            st.sidebar.subheader("Active Filters")
            for filter_name, value in st.session_state.active_filters.items():
                if value:  # Only show non-empty filters
                    if isinstance(value, (date, datetime)):
                        st.sidebar.markdown(f"**{filter_name}**: {value.strftime('%Y-%m-%d')}")
                    elif isinstance(value, list):
                        st.sidebar.markdown(f"**{filter_name}**: {', '.join(str(v) for v in value)}")
                    else:
                        st.sidebar.markdown(f"**{filter_name}**: {value}")
    
    def render_preset_management(self):
        """Render the preset management interface."""
        st.sidebar.subheader("Filter Presets")
        
        # Save current preset
        new_preset_name = st.sidebar.text_input("Save current filters as preset:")
        if new_preset_name and st.sidebar.button("Save Preset"):
            self.save_current_preset(new_preset_name)
        
        # Load/Delete presets
        if st.session_state.saved_presets:
            st.sidebar.markdown("**Saved Presets**")
            for preset_name in st.session_state.saved_presets:
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    if st.sidebar.button(f"Load: {preset_name}"):
                        self.load_preset(preset_name)
                with col2:
                    if st.sidebar.button(f"Delete: {preset_name}"):
                        self.delete_preset(preset_name) 