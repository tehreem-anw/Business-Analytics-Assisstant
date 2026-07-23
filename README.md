# 💼 Business Analytics Assistant

An intelligent, multi-source business intelligence and conversational analytics web application built with **Streamlit**, **OpenAI**, **Pandas**, and **Plotly**. Designed for multi-branch retail and restaurant chains, this tool allows operators to query complex, cross-source datasets using natural language, dynamically rendering accurate metrics, charts, and downloadable reports on the fly.

---

## ✨ Key Features

* **Conversational Data Extraction:** Powered by OpenAI (`gpt-4o-mini`), translating natural language questions into safe, dynamic, sandboxed Pandas execution logic.
* **Multi-Source Ingestion:** Seamlessly connect and query multiple disparate formats simultaneously:
  * **CSV Uploads:** For daily sales, transactions, or footfall logs[cite: 2].
  * **SQLite Databases:** For persistent relational records like branch-level inventory and stock counts[cite: 1, 2].
* **Adaptive Visualization Router:** Automatically detects the optimal output structure based on your query—routing data to **KPI metric blocks**, **bar charts**, **chronological line graphs**, **proportional pie charts**, or **comparative data tables**.
* **Proactive Intelligence Alerts:** Automatically flags critical business anomalies (e.g., sudden footfall drops across branches)[cite: 2].
* **Conversational Memory:** Retains full context of your chat history, allowing for seamless follow-up questions and chart modifications[cite: 2].
* **Exportable Reporting:** Download any generated insight or data slice directly as a `.csv` report with a single click[cite: 2].

---

## 🛠️ Project Architecture & File Structure

```text
├── main.py              # Core Streamlit app, UI layout, LLM engine & dynamic code executor
├── style.css            # Custom warm-palette UI styling and component overrides
├── store_inventory.db   # Local SQLite database containing branch stock levels
└── branch_sales.csv     # Sales transaction data source
