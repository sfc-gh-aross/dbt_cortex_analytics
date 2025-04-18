# Cursor.ai Onboarding Documentation Pack

> **Purpose:** Provide every new contributor with a single, authoritative package that covers setup, architecture, operations, and team conventions for the Customer Analytics Dashboard (Streamlit + Snowflake).

---

## 1 README / Quick‑Start Guide

### 1.1 Project Overview

A multi‑page Streamlit application that visualizes customer sentiment, support operations and product‑review insights by querying Snowflake.

### 1.2 Prerequisites

| Tool               | Version |
| ------------------ | ------- |
| Python             | 3.11    |
| SnowSQL            | ≥ 1.2   |
| Node (for tooling) | 20 LTS  |
| Cursor CLI         | ≥ 0.14  |

### 1.3 Local Setup (5 min)

```bash
# Clone & enter repo
$ git clone git@alexfrancsross/customer‑analytics‑dashboard.git
$ cd customer‑analytics‑dashboard

# Create & activate venv
$ python -m venv .venv && source .venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt

# Copy secrets template & fill Snowflake creds
$ cp .streamlit/secrets.example.toml .streamlit/secrets.toml

# Run dev server
$ streamlit run app.py  # http://localhost:8501
```

*Need data?* Run `make seed` to load a 1 k‑row synthetic sample into your dev Snowflake warehouse.

---

## 2 System‑Architecture Diagram

```text
┌─────────────┐   HTTPS    ┌─────────────────┐   Snowpark    ┌────────────┐
│   Browser   │◄──────────►│   Streamlit App │◄──────────────►│  Snowflake │
└─────────────┘            │   (EC2 / SC)    │               └────────────┘
                            └────────┬────────┘
                                     │  Redis (optional, cache)
                                     ▼
                               Observability (Grafana/Loki)
```

- EC2 = self‑hosted in AWS; SC = Streamlit Cloud deployment.
- Ingress via CloudFront + WAF with TLS 1.2+.
- Okta OIDC broker supplies JWT to Streamlit session.

---

## 3 Development Environment Setup

1. **Clone & virtualenv** – see README.
2. **Cursor settings** – project‑wide `.cursor.json`:

```json
{
  "index": "./src",
  "pythonVersion": "3.11",
  "excluded": [".venv", "tests/_helpers"]
}
```

3. **Pre‑commit**: `pre‑commit install` (runs black, isort, flake8).
4. **IDE plugins**: Pyright for type‑checking, Streamlit Snippets.
5. **Docker (optional)**: `docker compose up dev` spins an isolated stack.

---

## 4 Data‑Model & ERD

### 4.1 High‑Level ERD

```
CUSTOMER_BASE ─┬─< FACT_CUSTOMER_INTERACTIONS
               ├─< FACT_SUPPORT_TICKETS
               ├─< FACT_PRODUCT_REVIEWS
               └─< CUSTOMER_PERSONA_SIGNALS
```

- **Dimensional conformity**: `customer_id`, `date_key` present in all facts.
- **SCD‑Type 2** for personas (`CUSTOMER_PERSONA_SIGNALS`).

### 4.2 Table Dictionary (excerpt)

| Table                  | PK          | Grain    | Row cnt (dev) |
| ---------------------- | ----------- | -------- | ------------- |
| `FACT_SUPPORT_TICKETS` | `ticket_id` | 1 ticket | 65 k          |
| `FACT_PRODUCT_REVIEWS` | `review_id` | 1 review | 180 k         |

Full DDL in [`/snowflake/ddl.sql`](../snowflake/ddl.sql).

---

## 5 API Reference / Integration Guide

### 5.1 Internal Endpoints

| Method | Path                            | Purpose                           |
| ------ | ------------------------------- | --------------------------------- |
| `GET`  | `/api/v1/summary/<customer_id>` | Return interaction summary JSON   |
| `POST` | `/api/v1/feedback`              | Persist manual sentiment override |

*Auth*: Bearer JWT issued by Okta (aud `customer‑analytics‑dashboard`). *Errors*: 4xx → client, 5xx → server. Common codes in `/docs/api_errors.md`.

### 5.2 External Services

- **Zendesk** – webhook posts ticket updates → Snowpipe.
- **Slack** – optional slash‑command `/sentiment` calls the summary endpoint.

---

## 6 Design System / UI Style Guide

| Token         | Value                   |
| ------------- | ----------------------- |
| Primary Color | `#2563eb` (blue‑600)    |
| Accent Color  | `#10b981` (emerald‑500) |
| Font Family   | Inter, sans‑serif       |

- Use Streamlit `st.tabs`, `st.metric`, `st.container` with consistent elevations.
- Accessibility: color‑contrast ≥ 4.5:1, focus rings enabled.
- Motion: subtle 150 ms ease‑out via `st.markdown("<style>…</style>")`.

---

## 7 Test Strategy & Coverage Report

| Layer       | Framework                          | Notes                                  |
| ----------- | ---------------------------------- | -------------------------------------- |
| Unit        | **pytest**                         | Mock Snowflake with `snowpark.mock`    |
| Integration | **pytest + Streamlit Test Runner** | Boot app, hit endpoints                |
| E2E         | **Playwright**                     | Headless Chromium, record to `/videos` |

- CI: GitHub Actions → `pytest --cov=src --cov-report=xml` (badge in README).
- Target ≥ 85 % statement coverage.

---

## 8 Deployment & Release Playbook

1. **Branching**: trunk‑based; feature branches → PR → squash‑merge.
2. **Versioning**: semantic (`vMAJOR.MINOR.PATCH`).
3. **CI pipeline**:
   - Lint → Test → Build Docker → Push ECR.
4. **Promotion**:
   - Tag `vX.Y.Z` triggers deploy to **staging** (Streamlit Cloud).
   - Manual approval deploys to **prod**.
5. **Rollback**: `streamlit apps rollback <tag>` or re‑point load‑balancer.

---

## 9 Runbook / Operational Handbook

| Check             | Command / URL                           | Action if fails                           |
| ----------------- | --------------------------------------- | ----------------------------------------- |
| Health            | `/healthz`                              | Restart container, check Snowflake status |
| Warehouse credits | Snowflake Usage dashboard               | Scale‑down or add credits                 |
| App logs          | Loki query `{app="customer‑analytics"}` | Investigate error spikes                  |

*PagerDuty service*: **Customer‑Analytics‑Dashboard‑Prod**.

---

## 10 Security & Compliance Checklist

-

---

## 11 Glossary & Acronyms

| Term          | Definition                          |
| ------------- | ----------------------------------- |
| **CX**        | Customer Experience                 |
| **NPS**       | Net Promoter Score                  |
| **LTV / CLV** | Customer Lifetime Value             |
| **RLS**       | Row‑Level Security                  |
| **PII**       | Personally Identifiable Information |

---

## 12 Onboarding Checklist (First Week)

| Day | Task                                                                        |
| --- | --------------------------------------------------------------------------- |
| 1   | Receive repo access, join Slack channels `#customer‑analytics` & `#support` |
| 1   | Install Python 3.11, Cursor CLI, run quick‑start                            |
| 2   | Pair with buddy, deploy personal feature branch to dev workspace            |
| 3   | Review data model doc, run `pytest` suite                                   |
| 4   | Ship first PR (typo fix or doc update)                                      |
| 5   | Attend architecture deep‑dive, schedule retro with buddy                    |

---

## 13 Change Log / Release Notes (Template)

```markdown
## [vX.Y.Z] – 2025‑MM‑DD
### Added
- New Sentiment Volatility box‑plot
### Fixed
- Snowflake timeout handling in Support tab
### Changed
- Upgraded Streamlit 1.34 → 1.35
```

Full log auto‑generated via GitHub release automation.

---

## 14 Contribution Guide (CONTRIBUTING.md)

1. **Fork & branch**: `feature/<ticket‑id>‑<slug>`.
2. **Code style**: run `make format` (black + isort).
3. **Commit messages**: conventional (`feat:`, `fix:`, `docs:`).
4. **PR checklist**:
   -
5. **Review process**: 1 approver if <50 LOC, 2 approvers otherwise.

---

## 15 Project Folder & File Structure

```text
customer‑analytics‑dashboard/
├── app.py                  # entry point; sets up sidebar navigation
├── pages/                  # multi‑page Streamlit pages (auto‑loaded)
│   ├── 1_sentiment.py      # Sentiment & Experience workspace
│   ├── 2_support.py        # Support Operations workspace
│   ├── 3_reviews.py        # Product Feedback workspace
│   ├── 4_journey.py        # Customer Journey workspace
│   ├── 5_segments.py       # Segmentation & Value workspace
│   └── 6_insights.py       # Insights & Summaries workspace
├── src/                    # reusable Python modules (imported by pages)
│   ├── __init__.py
│   ├── data/               # Snowflake query wrappers & caching utils
│   │   ├── connection.py   # get_snowflake_session()
│   │   ├── queries.py      # SQL strings lifted verbatim from guide
│   │   └── transforms.py   # pandas manipulation helpers
│   ├── ui/                 # custom Streamlit components & widgets
│   │   ├── charts.py       # wrapper functions around altair/plotly
│   │   └── theme.py        # color tokens, typography
│   └── utils/              # misc helpers (logging, constants)
├── tests/                  # pytest units & integration tests
│   ├── data/test_queries.py
│   ├── ui/test_charts.py
│   └── e2e/test_app.py     # Playwright end‑to‑end tests
├── .streamlit/
│   ├── config.toml         # Streamlit theme, server settings
│   └── secrets.toml        # Snowflake creds (KMS‑encrypted in prod)
├── requirements.txt        # Python deps (pinned)
├── Makefile                # common tasks (format, lint, test, run)
├── docker-compose.yml      # optional dev stack (app + redis)
├── docs/                   # markdown docs (this onboarding pack)
│   └── img/architecture.png
├── .cursor.json            # Cursor project settings
├── .pre‑commit‑config.yaml # lint & format hooks
└── README.md               # quick‑start (symlink to docs version)
```

**Best‑practice notes**

- **Flat page modules** under `pages/` let Streamlit’s multipage loader pick them up automatically; numeric prefixes enforce sidebar order.
- **src/data/** encapsulates Snowflake logic; **no SQL inside pages** – keeps UI and data layers decoupled.
- **st.cache\_data** decorators live only in `data/queries.py`; prevents re‑caching in multiple layers.
- **tests/** mirrors package paths; use `snowpark.mock` to stub Snowflake.
- Configuration stays in **.streamlit/** and environment variables (managed by Streamlit Secrets in prod).
- **docs/** co‑located with code to keep dev & doc PRs atomic; rendered by Cursor’s doc viewer.
- **Makefile** gives OSHA‑like safety: `make ci` runs the exact CI steps locally.

---

> ⭐ **Welcome aboard!** This pack should get you from *clone* ➜ *contributor* in a single sprint.

