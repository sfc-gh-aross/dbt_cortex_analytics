# Customer Analytics Streamlit Application – PRD

**Version:** 2.1   **Date:** 25 Apr 2025   **Author:** Alex Ross 

---

## 0  Using this PRD with Cursor.ai
Feed each numbered *Prompt Block* (🔹) directly into Cursor.ai. Prompt Blocks are written as clear, single‑shot instructions so Cursor.ai can generate code, SQL, or documentation without further context. Execute them in the given order or cherry‑pick as needed.

---

## 1  Folder & File Layout  🔹Prompt Block 1
"""
Create the following repository skeleton:

```
streamlit_app/
├── app.py                 # entry‑point, assembles st.tabs()
├── components/            # one component = one dashboard tab
│   ├── __init__.py       # component registration and imports
│   ├── overview.py       # 38KB implementation
│   ├── sentiment_experience.py
│   ├── support_ops.py
│   ├── product_feedback.py
│   └── segmentation.py
├── sql/                   # ONLY SQL – one sub‑folder per dashboard
│   ├── overview/
│   │   ├── kpis.sql
│   │   ├── sentiment_trend.sql
│   │   ├── sentiment_dist.sql
│   │   ├── churn_risk_breakdown.sql
│   │   ├── risk_trend.sql
│   │   └── interaction_trend.sql
│   ├── sentiment_experience/
│   │   ├── sentiment_over_time.sql
│   │   ├── sentiment_distribution.sql
│   │   ├── volatility_vs_trend.sql
│   │   ├── sentiment_recovery_rate.sql
│   │   ├── channel_alignment.sql
│   │   └── sentiment_by_persona.sql
│   ├── support_ops/
│   │   ├── ticket_volume_trend.sql
│   │   ├── priority_breakdown.sql
│   │   ├── category_analysis.sql
│   │   ├── tickets_per_customer.sql
│   │   ├── resolution_rate.sql
│   │   ├── channel_effectiveness.sql
│   │   ├── customer_effort.sql
│   │   └── first_response_time.sql
│   ├── product_feedback/
│   │   ├── rating_trend.sql
│   │   ├── rating_distribution.sql
│   │   ├── sentiment_by_language.sql
│   │   └── recent_reviews.sql
│   └── segmentation/
│       ├── persona_distribution.sql
│       ├── value_segment_metrics.sql
│       ├── churn_vs_upsell.sql
│       ├── segment_distribution.sql
│       ├── segment_trend.sql
│       ├── segment_characteristics.sql
│       └── segment_migration.sql
├── utils/
│   ├── __init__.py       # utility function exports
│   ├── database.py       # Snowflake connector + query runner
│   ├── filters.py        # reusable multiselects/date pickers
│   ├── kpi_cards.py      # helper to render st.metric rows
│   ├── theme.py          # central colours / fonts
│   └── debug.py          # debug mode utilities
├── assets/               # static files (images, etc.)
├── sample_code/         # example implementations
└── README.md
```

Implementation rules:
* Each *components/*.py file ✨imports only its own SQL✨ from *sql/<dashboard>/*.sql.
* *app.py* registers global filters (date range, persona, value segment) and passes them as kwargs to each component.
* Use lazy loading (`st.spinner` + `@st.cache_data(ttl=300)`) around every SQL call.
* All components must implement debug mode functionality via utils/debug.py.
"""

---

## 2  Global Libraries & Theme  🔹Prompt Block 2
"""
Dependencies (add to requirements.txt):
- streamlit>=1.33
- snowflake‑conn‑python
- pandas, numpy
- plotly>=5
- altair>=5
- seaborn (only for quick data‑checks, not UI)
- streamlit‑extras (for data‑editor, copy to clipboard, etc.)

Styling:
- Primary colour #2563EB (indigo‑600), secondary #14B8A6 (teal‑500).
- Use utils/theme.py to inject base `st.markdown("<style>…</style>", unsafe_allow_html=True)`.
- All charts default to Streamlit's light theme.
"""

---

## 3  Global Filter Implementation  🔹Prompt Block 3
"""
Implement global filters in utils/filters.py with the following structure:

1. **State Management**
   ```python
   def initialize_filters() -> None:
       """Initialize filter values in session state if they don't exist."""
       if 'filters' not in st.session_state:
           default_end = datetime.now()
           default_start = default_end - timedelta(days=90)
           personas = get_filter_options()['personas']
           
           st.session_state.filters = {
               'start_date': default_start.strftime('%Y-%m-%d'),
               'end_date': default_end.strftime('%Y-%m-%d'),
               'personas': personas
           }
           
           # Initialize component states
           st.session_state.start_date_filter = default_start
           st.session_state.end_date_filter = default_end
           st.session_state.persona_filter = personas

   def sync_filter_state() -> None:
       """Sync component states with our filter state."""
       if 'start_date_filter' in st.session_state:
           st.session_state.filters['start_date'] = st.session_state.start_date_filter.strftime('%Y-%m-%d')
       if 'end_date_filter' in st.session_state:
           st.session_state.filters['end_date'] = st.session_state.end_date_filter.strftime('%Y-%m-%d')
       if 'persona_filter' in st.session_state:
           st.session_state.filters['personas'] = st.session_state.persona_filter
   ```

2. **Filter Rendering**
   ```python
   def render_global_filters() -> Dict[str, any]:
       """Render global filters and return selected values."""
       initialize_filters()
       
       with st.sidebar:
           st.markdown("### Filters")
           
           # Date range picker
           col1, col2 = st.columns(2)
           with col1:
               st.date_input(
                   "Start Date",
                   value=datetime.strptime(st.session_state.filters['start_date'], '%Y-%m-%d'),
                   max_value=datetime.strptime(st.session_state.filters['end_date'], '%Y-%m-%d'),
                   key="start_date_filter"
               )
           with col2:
               st.date_input(
                   "End Date",
                   value=datetime.strptime(st.session_state.filters['end_date'], '%Y-%m-%d'),
                   min_value=st.session_state.start_date_filter,
                   key="end_date_filter"
               )
           
           # Persona filter
           personas = get_filter_options()['personas']
           st.multiselect(
               "Persona",
               options=personas,
               default=st.session_state.filters['personas'],
               key="persona_filter"
           )
       
       sync_filter_state()
       return st.session_state.filters
   ```

3. **Access Methods**
   ```python
   def get_date_range() -> Tuple[str, str]:
       """Get the selected date range from session state."""
       initialize_filters()
       sync_filter_state()
       return st.session_state.filters['start_date'], st.session_state.filters['end_date']

   def get_persona_filter() -> List[str]:
       """Get the selected personas from session state."""
       initialize_filters()
       sync_filter_state()
       return st.session_state.filters['personas']
   ```

Implementation rules:
* Initialize filters in app.py before rendering any components
* Call sync_filter_state() after any filter changes
* Pass filter values to components via the filters dictionary
* All SQL queries must respect the selected date range and personas
* Filter state must persist across tab switches and page refreshes
"""

---

## 4  Dashboard Tabs – Design Inventory
For each tab below include:
* **KPIs** – rendered via `utils.kpi_cards.render_kpis(df)` at the very top.
* **Visual Inventory** – recommended chart type, library, SQL file, and Snowflake view/table.

### 4.1  Overview(tab = 'Overview')  🔹Prompt Block 4

#### KPIs
| KPI | Definition | SQL File |
|---|---|---|
| Average Sentiment Score | Mean sentiment_score from SENTIMENT_ANALYSIS | `overview/kpis.sql` |
| Total Interactions | Count of rows from FACT_CUSTOMER_INTERACTIONS | `overview/kpis.sql` |
| High Risk Customer % | Percentage of customers with churn_risk='High' | `overview/kpis.sql` |
| Average Product Rating | Mean review_rating from FACT_PRODUCT_REVIEWS | `overview/kpis.sql` |

#### Visual Inventory
| # | Visual | Chart | Library | SQL File | Data Source |
|---|---|---|---|---|---|
| 1 | Sentiment Trend | Line | Plotly | `overview/sentiment_trend.sql` | Snowflake Views/Tables |
| 2 | Sentiment Distribution | Bar | Altair | `overview/sentiment_dist.sql` | Snowflake Views/Tables |
| 3 | Churn Risk Breakdown | Bar | Plotly | `overview/churn_risk_breakdown.sql` | Snowflake Views/Tables |

### 4.2  Sentiment & Experience(tab = 'Sentiment & Experience')

#### KPIs
| KPI | Definition | SQL File |
|---|---|---|
| Sentiment Consistency Score | Standard deviation of sentiment scores | `sentiment_experience/sentiment_over_time.sql` |
| Cross-channel Sentiment Alignment | Correlation between different channel sentiments | `sentiment_experience/sentiment_over_time.sql` |
| Customer Experience Score | Weighted average of sentiment, rating, and support metrics | `sentiment_experience/sentiment_over_time.sql` |
| Sentiment Recovery Rate | % of negative sentiments followed by positive ones | `sentiment_experience/sentiment_over_time.sql` |

#### Visual Inventory
| # | Visual | Chart | Library | SQL File | Data Source |
| 1 | Sentiment Over Time by Source | Multi‑line | Plotly | `sentiment_experience/sentiment_over_time.sql` | Snowflake Views/Tables |
| 2 | Sentiment Distribution by Source | Bar facet | Altair | `sentiment_experience/sentiment_distribution.sql` | Snowflake Views/Tables |
| 3 | Volatility vs Trend Scatter | Scatter, color=overall_sentiment | Plotly | `sentiment_experience/volatility_vs_trend.sql` | Snowflake Views/Tables |

### 4.3  Support Operations(tab = 'Support Ops')

#### KPIs
| KPI | Definition | SQL File |
|---|---|---|
| First Response Time | Average time to first response | `support_ops/ticket_volume_trend.sql` |
| Resolution Rate | % of tickets resolved | `support_ops/priority_breakdown.sql` |
| Customer Effort Score | Derived from ticket complexity and resolution time | `support_ops/category_analysis.sql` |
| Support Channel Effectiveness | Success rate by channel | `support_ops/tickets_per_customer.sql` |

#### Visual Inventory
| # | Visual | Chart | Library | SQL File | Data Source |
| 1 | Ticket Volume Trend | Area | Plotly | `support_ops/ticket_volume_trend.sql` | Snowflake Views/Tables |
| 2 | Priority Breakdown | Pie + Bar toggle | Plotly | `support_ops/priority_breakdown.sql` | Snowflake Views/Tables |
| 3 | Category Analysis | Horizontal bar | Altair | `support_ops/category_analysis.sql` | Snowflake Views/Tables |
| 4 | Tickets per Customer | Histogram | Altair | `support_ops/tickets_per_customer.sql` | Snowflake Views/Tables |

### 4.4  Product Feedback(tab = 'Product Feedback')

#### KPIs
| KPI | Definition | SQL File |
|---|---|---|
| Review Response Rate | Ratio of reviews with responses | `product_feedback/rating_trend.sql` |
| Average Review Length | Average character count of reviews | `product_feedback/rating_distribution.sql` |
| Multi-language Review % | Percentage of non-English reviews | `product_feedback/sentiment_by_language.sql` |
| Review Sentiment Volatility | Standard deviation of review sentiments | `product_feedback/recent_reviews.sql` |

#### Visual Inventory
| # | Visual | Chart | Library | SQL File | Data Source |
| 1 | Rating Trend | Line | Plotly | `product_feedback/rating_trend.sql` | Snowflake Views/Tables |
| 2 | Rating Distribution | Bar | Altair | `product_feedback/rating_distribution.sql` | Snowflake Views/Tables |
| 3 | Sentiment by Language | Heatmap | Plotly | `product_feedback/sentiment_by_language.sql` | Snowflake Views/Tables |
| 4 | Recent Reviews Table | st.dataframe | Streamlit | `product_feedback/recent_reviews.sql` | Snowflake Views/Tables |

### 4.5  Segmentation(tab = 'Segmentation & Value')

_Note: This component presents detailed charts within expanders. While the KPIs below are defined for analytical consistency, they are not rendered as standard top-level KPI cards in the current implementation. The data for these KPIs can be derived from the specified SQL queries and corresponding visualizations._

#### KPIs
| KPI | Definition | SQL File |
|---|---|---|
| Segment Migration Rate | % of customers changing segments | `segmentation/segment_migration.sql` |
| Segment Health Score | Weighted average of segment metrics | `segmentation/value_segment_metrics.sql` |
| High-value Customer % | % of customers with lifetime_value > 1000 | `segmentation/value_segment_metrics.sql` |
| Segment Engagement Index | Weighted average of interaction frequency | `segmentation/churn_vs_upsell.sql` |

#### Visual Inventory
| # | Visual | Chart | Library | SQL File | Data Source | Notes |
|---|---|---|---|---|---|---|
| 1 | Persona Distribution | Bar | Plotly | `segmentation/persona_distribution.sql` | Snowflake Views/Tables | Main section. (Was Altair) |
| 2 | Value Segment Radar | Radar (plotly polar) | Plotly | `segmentation/value_segment_metrics.sql` | Snowflake Views/Tables | Main section |
| 3 | Churn vs Upsell Potential | Density Heatmap | Plotly | `segmentation/churn_vs_upsell.sql` | Snowflake Views/Tables | Main section. (Title was "Churn vs Upsell Density", chart type 2D Histogram) |
| 4 | Segment Explorer Table | `st.dataframe` | Streamlit | `segmentation/persona_distribution.sql` | Snowflake Views/Tables | Main section. (Was `st.data_editor`) |
| 5 | Customer Segment Distribution | Pie | Plotly | `segmentation/segment_distribution.sql` | Snowflake Views/Tables | In "Additional Segment Visualizations" expander |
| 6 | Segment Characteristics | Bar (grouped) | Plotly | `segmentation/segment_characteristics.sql` | Snowflake Views/Tables | In "Additional Segment Visualizations" expander |
| 7 | Segment Migration Analysis | Heatmap | Plotly | `segmentation/segment_migration.sql` | Snowflake Views/Tables | In "Additional Segment Visualizations" expander |
| - | Segment Trend Data | (Data loaded) | - | `segmentation/segment_trend.sql` | Snowflake Views/Tables | Data loaded for download; not directly visualized in "Additional Segment Visualizations" expander |

---

## 5  SQL Conventions  🔹Prompt Block 5
"""
* Use Jinja parameters `:start_date`, `:end_date`, `:selected_personas`, etc., exactly as shown in STREAMLIT_QUERIES.md.
* Never `SELECT *`. Explicitly list columns for Snowflake pruning.
* Wrap each KPI query in a CTE block (`WITH kpi AS (…) SELECT …`).
* Store every query in the *sql/* tree; never embed SQL in Python.
* **Data Source Mandate:** ALL data displayed in the application MUST originate directly from Snowflake queries. Never generate synthetic data or use hardcoded values within the application code.
* **Filter Implementation:** Queries *may* be designed to be filterable by parameters such as `:start_date`, `:end_date`, and `:selected_personas` (typically a comma-separated string for multiple persona selection). If a query is designed to be filterable, these parameter names should be used consistently. However, not all queries are required to be filterable; this depends on the specific data and analytical purpose of the query. For instance, queries based on highly aggregated summary tables (like `CUSTOMER_PERSONA_SIGNALS`) might not support direct date or detailed persona filtering.
  When implementing filterable queries, a common pattern for handling optional persona filtering is:
  ```sql
  -- Example for a query that supports filtering:
  -- WHERE interaction_date BETWEEN :start_date AND :end_date
  -- AND (:selected_personas = '' OR persona_column IN (SELECT value FROM TABLE(SPLIT_TO_TABLE(:selected_personas, ','))))
  ```
* **Case Sensitivity Handling:**
  - Snowflake returns column names in uppercase by default
  - Always use uppercase column names in SQL queries
  - When accessing DataFrame columns in Python code, use uppercase to match Snowflake's output
  - Example: Use `df['AVG_RATING']` instead of `df['avg_rating']`
  - Document this convention in component docstrings
  - Consider adding a helper function in utils/database.py to standardize column name handling
"""

---

## 6  Performance & Caching Guidelines  🔹Prompt Block 6
"""
- Wrap expensive queries with `@st.cache_data(ttl=300, show_spinner=False)`.
- Use Snowflake `QUERY_TAG='streamlit_app'` for monitoring.
- Chunk large result sets: prefer `LIMIT 5 000` + pagination for tables.
- Run KPI queries first and in parallel via `asyncio.gather()`.
- Cache filter options with `@st.cache_data(ttl=300)` to avoid repeated database calls.
"""

---

## 7  Accessibility & UX Details  🔹Prompt Block 7
"""
- Every Plotly chart: enable unified hover label + download PNG icon.
- Provide colour‑blind friendly palette (automatic with Plotly template `plotly_white`).
- Ensure all KPIs have `help` tool‑tips that match definitions.
- Use `st.toast()` for success/error notifications on user actions.
- Filters should be clearly visible in the sidebar with descriptive labels.
- Filter changes should trigger immediate updates across all dashboard components.
- Implement responsive layouts using `st.columns()` for better mobile support.
- Use consistent spacing and padding across all components.
- Provide clear loading states with `st.spinner()` for all data operations.
"""

---

## 8  Debug Mode Implementation  🔹Prompt Block 8
"""
The debug mode functionality is implemented in `utils/debug.py` and must be used by all components:

1. **Debug Utilities**
   - Import debug utilities: `from utils.debug import display_debug_info, setup_debug_mode`
   - Use `setup_debug_mode()` in app.py to initialize debug state
   - Implement debug display using `display_debug_info()` helper

2. **Component Implementation**
   ```python
   def render_dashboard(debug_mode: bool = False):
       # Load data first
       with st.spinner("Loading dashboard data..."):
           data = load_data()
       
       # Display debug info if enabled
       if debug_mode:
           display_debug_info(
               sql_file="path/to/query.sql",
               params={"start_date": start_date, "end_date": end_date},
               results=data,
               query_name="Dashboard Query"
           )
       
       # Render main dashboard
       render_visualizations(data)
   ```

3. **Debug Information Display**
   - SQL query text and parameters
   - Raw query results
   - Formatted DataFrame preview
   - Current filter values
   - Performance metrics (query time, data size)

4. **Global Debug Toggle**
   - Toggle in sidebar: `st.sidebar.toggle("Debug Mode")`
   - State stored in `st.session_state.debug_mode`
   - Persists across tab switches and page refreshes

5. **Performance Optimization**
   - Load data before displaying debug info
   - Cache expensive operations
   - Limit debug output for large datasets
   - Use consistent formatting across components
"""

---

## 9  Future Enhancements
* Customer Deep‑Dive modal per ID (pop‑up rather than extra tab).
* PDF/CSV export via `st.download_button`.
* Scheduled email jobs using Snowflake Tasks + Streamlit Cloud scheduled jobs.
* Additional filter types (e.g., value segments, product categories).
* Filter presets for common date ranges (e.g., "Last 30 days", "This quarter").
* Real-time data updates using Snowflake's change tracking.
* Custom theme support with dark/light mode toggle.
* Advanced filtering with saved filter presets.
* Export functionality for all visualizations and data tables.

---

### End of PRD