import streamlit as st
from src.utils.db import init_connection
from src.components.overview_dashboard import render_overview_dashboard

# Page config
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize connection
conn = init_connection()

# Sidebar filters
st.sidebar.title("Filters")

# Date range filter
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Customer value segments filter
value_segments = ["Enterprise", "Mid-Market", "SMB"]
selected_value_segments = st.sidebar.multiselect(
    "Customer Value Segments",
    value_segments,
    default=value_segments
)

# Derived personas filter
personas = ["Technical", "Business", "Executive"]
selected_personas = st.sidebar.multiselect(
    "Derived Personas",
    personas,
    default=personas
)

# Churn risk filter
churn_risks = ["High", "Medium", "Low"]
selected_churn_risks = st.sidebar.multiselect(
    "Churn Risk",
    churn_risks,
    default=churn_risks
)

# Upsell opportunity filter
upsell_opportunities = ["High", "Medium", "Low"]
selected_upsell_opportunities = st.sidebar.multiselect(
    "Upsell Opportunity",
    upsell_opportunities,
    default=upsell_opportunities
)

# Interaction type filter
interaction_types = ["Support Ticket", "Product Review", "Customer Call"]
selected_interaction_types = st.sidebar.multiselect(
    "Interaction Type",
    interaction_types,
    default=interaction_types
)

# Review language filter
review_languages = ["English", "Spanish", "French", "German"]
selected_review_languages = st.sidebar.multiselect(
    "Review Language",
    review_languages,
    default=review_languages
)

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Sentiment & Experience",
    "Support Operations",
    "Product Feedback",
    "Customer Segmentation"
])

with tab1:
    render_overview_dashboard(start_date, end_date, selected_value_segments, selected_personas)

with tab2:
    st.header("Sentiment & Experience Analysis")
    st.write("Coming soon...")

with tab3:
    st.header("Support Operations Insights")
    st.write("Coming soon...")

with tab4:
    st.header("Product Feedback Analysis")
    st.write("Coming soon...")

with tab5:
    st.header("Customer Segmentation & Value")
    st.write("Coming soon...")
