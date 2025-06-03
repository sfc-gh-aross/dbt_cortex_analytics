### 📊 Picking the Prettiest Visual for Your Streamlit Chart

> Use this cheat-sheet whenever you add a figure to your Streamlit app. It maps **what you want to show** ➜ **which library will make it look (and feel) great**, with one-line snippets you can paste straight in.

| When you need… | Library & one-liner | Why it *looks* best |
|---|---|---|
| **Sleek dashboard or animated time-series** | **Plotly / Plotly Express**<br>`st.plotly_chart(fig)` | Polished default palette, silky hover/zoom, built-in animations, finance & sci-viz templates. |
| **Statistical exploration with linked views** | **Altair (Vega-Lite)**<br>`st.altair_chart(chart)` | Concise grammar, elegant typography, instant tool-tip & brush, Streamlit-themed styles. |
| **A jaw-dropping map or 3-D scene** | **PyDeck / deck.gl**<br>`st.pydeck_chart(deck_obj)` | GPU-powered layers, realistic lighting, full-screen toggle (≥ v1.42). Handles huge geodata. |
| **High-energy, attention-grabbing storytelling** | **Apache ECharts**<br>`st_echarts(opts)` | Flashy Asian-style visuals, rich animations, exotic charts (sunburst, flame-graph, word-cloud). |
| **Custom JS interactions or live tickers** | **Bokeh**<br>`st.bokeh_chart(p)` | Publication-quality styling plus two-way Python↔JS callbacks and real-time streaming. |
| **No-code, drag-and-drop analysis** | **Pygwalker (Kanaries)**<br>`st.write(pyg.walk(df, env="Streamlit"))` | Auto-suggests charts, lets non-devs explore data visually inside your app. |
| **Agnostic API that scales & streams** | **HoloViews / hvPlot**<br>`st.bokeh_chart(df.hvplot(kind="scatter"))` | Chooses the best backend for you, beautiful defaults, facet linking, streaming support. |

---

#### 🚦 Quick Decision Rules

| Goal | Go with… | Rationale |
|---|---|---|
| **Fast & beautiful default** | Plotly Express **or** Altair | 1-3 lines of code → polished chart. |
| **Maps / 3-D layers** | PyDeck | WebGL performance + lighting. |
| **Zero-code exploration** | Pygwalker | Drag, drop, done. |
| **Complex, custom interactions** | Bokeh | JS callbacks at your fingertips. |
| **Exotic or animated storytelling** | ECharts | Dozens of rare chart types. |
| **Streaming / very large data** | HoloViews | Built-in datashader & stream support. |

---

#### 📝 Tips Before You Ship

* **Stay native:** each helper (`st.plotly_chart`, `st.altair_chart`, …) auto-sizes to Streamlit’s layout—use them instead of raw HTML.
* **Theming:** Plotly & Altair inherit Streamlit’s theme automatically; for PyDeck/Bokeh, set `st.set_page_config(theme=…)` or apply CSS.
* **Performance preview:** Test with a sample of your data first—GPU layers (PyDeck) and heavy animations (ECharts) can tax the browser.
* **Accessibility:** Keep colour-blind palettes (e.g., Plotly’s `px.colors.qualitative.Safe`) in mind for dashboards viewed by many users.

---

Copy-paste the snippet, swap in your dataframe or figure, and your Streamlit app will always show the *best-looking* chart for the job.