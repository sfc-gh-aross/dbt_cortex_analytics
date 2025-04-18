# Product Requirements Document  
**Project:** Customer Analytics Dashboard  
**Platform:** Streamlit + Snowflake  
**Delivery window:** **1 week (by 25 April 2025)**  

---

## 1  Executive Summary  

| Item | Description |
|------|-------------|
| **Project overview** | Build a multi‑page Streamlit dashboard that surfaces customer behavior, sentiment, support efficiency and product‑review insights by querying Snowflake directly. |
| **Business objectives** | • Increase data‑driven decision‑making for CX, Product & Support teams • Reduce average support‑ticket resolution time by 10 % • Lift NPS by 3 points in 90 days. |
| **Key stakeholders** | VP Customer Success (exec sponsor) • Head of Product Ops • Support Ops Manager • Data Engineering Lead • Security Officer |
| **Success metrics** | Dashboard adoption ≥ 85 % of target users in 30 days • Median page‑load ≤ 2 s • ≤ 1 critical bug post–go‑live • > 95 % query‑success rate |

---

## 2  Product Overview  

**Core features & capabilities**  
1. Sentiment & Experience workspace (5 charts)  
2. Support Operations workspace (4 charts)  
3. Product Feedback workspace (5 charts)  
4. Customer Journey workspace (5 charts)  
5. Segmentation & Value workspace (5 charts)  
6. Insights & Summaries workspace (5 widgets)  

**Target users / personas**  
- **CX Analyst** – investigates sentiment shifts  
- **Support Lead** – tracks ticket backlog & SLA compliance  
- **Product Manager** – monitors feature feedback & churn risk  
- **Executive** – consumes high‑level KPIs in weekly reviews  

**Snowflake integration points**  
- Uses **ANALYTICS** database & schemas referenced in the guide.  
- All dashboards query Snowflake via the Snowpark‑optimized `snowflake-connector-python`.  
- Role‑based security enforced with `CUSTOMER_ANALYTICS_APP` Snowflake role.  

**Technical architecture (high‑level)**  
```
┌────────────┐   HTTPS   ┌────────────┐   Snowpark   ┌─────────────┐
│   Browser  │◄────────►│  Streamlit  │◄────────────►│  Snowflake  │
└────────────┘           │  (EC2/Snow)│              └─────────────┘
                         └────────────┘
```
- Optional Redis layer for Streamlit `st.cache_data` persistence.  
- CI/CD: GitHub Actions → Streamlit Community Cloud / Snowflake Native App.

---

## 3  Detailed Requirements  

### A. Customer Persona Analysis  
| Requirement | Detail |
|-------------|--------|
| **Visualization** | *Persona Distribution* pie chart; *Interaction Type × Persona* grouped‑bar |
| **Data sources** | `ANALYTICS.CUSTOMER_BASE`, `ANALYTICS.FACT_CUSTOMER_INTERACTIONS` |
| **Transforms** | Daily Snowflake task populates dimensional table `DIM_PERSONA_STATS` |
| **Filtering** | Segment, date‑range, channel, geographic region |
| **Segmentation** | Dynamic multi‑select tied to Snowflake secure UDF `GET_SEGMENT_IDS()` |

### B. Sentiment Analysis  
| Requirement | Detail |
|-------------|--------|
| **Visuals** | *Sentiment Trends Over Time* multi‑series line; *Sentiment by Interaction Type* heatmap; *Sentiment ↔ Ticket Volume* dual‑axis line |
| **Granularity** | Hour, day, week roll‑ups via `DATE_TRUNC` |
| **Real‑time need** | ≤ 15 min lag using Snowflake streams + tasks |

### C. Support Ticket Analytics  
| Requirement | Detail |
|-------------|--------|
| **Charts** | *Ticket Volume by Priority* stacked‑area; *Common Categories* treemap; *Recurrence Patterns* Sankey; *Priority vs CSAT* scatter |
| **Response‑time KPI** | P90 resolution time displayed; target ≤ 24 h |
| **Resolution tracking** | Drill‑through link to Zendesk ticket ID |

### D. Product Review Analytics  
| Requirement | Detail |
|-------------|--------|
| **Visuals** | Rating histogram, Sentiment‑by‑Product bubble, Volume trend area, Multi‑lingual radar, Rating ↔ Sentiment scatter |
| **Scoring** | Normalized 1‑5 stars, sentiment score –1 … 1 |
| **Correlation** | Show Pearson r via Snowflake `CORR()` |

---

## 4  Technical Requirements  

| Category | Specification |
|----------|---------------|
| **Snowflake** | Warehouse `CX_WH` (X‑SMALL, auto‑scale 1‑3) • All queries drawn **exactly** from the guide to leverage result cache |
| **Data model** | Star schema with fact tables (`FACT_*`) & shared dims (`DIM_DATE`, `DIM_CUSTOMER`) |
| **Performance** | P95 query run‑time ≤ 500 ms; dashboard render ≤ 2 s |
| **Security** | • Row‑level security on `customer_id` using Snowflake RLS policies • Secrets stored in Streamlit `st.secrets` • TLS 1.2+ |
| **Compliance** | GDPR & SOC 2: no PII persisted outside Snowflake; audit via `ACCOUNT_USAGE.QUERY_HISTORY` |
| **Caching** | • Leverage Snowflake Result Cache (24 h) • Streamlit `cache_data(ttl=3600)` for slow analytics • Optional Redis for cross‑session cache |

---

## 5  User Interface Requirements  

| Aspect | Guideline |
|--------|-----------|
| **Layout** | Top‑level sidebar nav ➜ 6 workspaces (Sentiment, Support, Reviews, Journey, Segmentation, Insights). Each workspace uses Streamlit tabs for sub‑charts. |
| **Filtering** | Global date‑range, persona multi‑select, channel chips. Filters propagate via `st.session_state`. |
| **Export** | Per‑chart “Download CSV” and global “Export PDF” (html2pdf) buttons. |
| **Responsive** | Columns resize with `st.container()` + CSS grid; mobile breakpoint ≤ 600 px collapses sidebar. |
| **Accessibility** | WCAG 2.1 AA • color‑safe palettes • alternative text on all charts • keyboard‑navigable filters. |

---

## 6  Data Requirements  

| Item | Details |
|------|---------|
| **Snowflake tables** | `FACT_CUSTOMER_INTERACTIONS`, `FACT_SUPPORT_TICKETS`, `FACT_PRODUCT_REVIEWS`, `SENTIMENT_ANALYSIS`, `CUSTOMER_BASE`, `CUSTOMER_PERSONA_SIGNALS`, `TICKET_PATTERNS`, `INSIGHT_SUMMARIES` |
| **Refresh frequency** | Incremental loads every 15 min via Snowflake tasks + streams |
| **Quality standards** | NULL sentiment_score ≤ 0.5 % • Duplicate ticket_id = 0 |
| **Retention** | Raw logs 3 yrs; aggregated tables 5 yrs; in line with GDPR erase on request |

---

## 7  Non‑Functional Requirements  

| Area | Target |
|------|--------|
| **Performance** | < 2 s P95 full‑page render |
| **Scalability** | 200 concurrent users; Snowflake auto‑scale |
| **Security** | SSO via Okta OIDC; MFA enforced; column‑level masking for PII |
| **Compliance** | GDPR Art 30 records; SOC 2 Type II; ISO 27001 |
| **Reliability** | 99.9 % uptime; automated backup & point‑in‑time recovery (24h) |

---

## 8  Implementation Timeline (1 Week Sprint)  

| Day | Milestone |
|-----|-----------|
| **Day 0 (Fri 18 Apr)** | Kickoff; confirm scope & access |
| **Day 1 (Mon)** | Snowflake role/warehouse setup; scaffold Streamlit project; stub queries |
| **Day 2 (Tue)** | Implement Sentiment & Support workspaces; basic filters |
| **Day 3 (Wed)** | Implement Reviews & Journey workspaces; caching layer |
| **Day 4 (Thu)** | Implement Segmentation & Insights workspaces; export functions |
| **Day 5 (Fri)** | Security hardening, unit tests, Lighthouse perf check |
| **Day 6 (Sat)** | UAT with stakeholders, bug fixes |
| **Day 7 (Sun 25 Apr)** | Production deploy; post‑launch monitoring |

---

## 9  Success Criteria  

| Dimension | Metric | Target |
|-----------|--------|--------|
| **Performance** | P95 page‑load | ≤ 2 s |
| **Adoption** | Weekly active users (WAU) | ≥ 85 % of 120 target users |
| **Business impact** | Avg ticket resolution time | –10 % within 30 days |
|  | NPS change | +3 points in 90 days |
| **Technical quality** | Critical defects post‑launch | 0 |
|  | Query error rate | < 2 % |

---

### Alignment & Validation  

- **Snowflake best practices** adhered to: virtual‑warehouse autoscaling, result‑cache reuse, streams + tasks for incremental loads, role‑based security.  
- **Streamlit integration specifics**: `snowflake.connector`, `st.cache_data`, multipage app structure, Secrets Manager.  
- **Security & Privacy**: no local data persistence, masking policies for PII, audit logs turned on.  
- **Stakeholder mapping**: requirements traceable to CX, Product, Support, Exec OKRs.  
- **Validation plan**: unit tests for each SQL query, synthetic‑data perf tests, accessibility audit, stakeholder UAT sign‑off.

---

*This PRD references only the visualizations, SQL queries and dashboards defined in* **complete_dashboard_guide.md** citeturn0file0.