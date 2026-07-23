# 💼 Business Analytics Assistant

Name: Tehreem Anwar                                                                                    
Email: tehreemhb@gmail.com

An intelligent, multi-source business intelligence and conversational analytics web application built with **Streamlit**, **OpenAI**, **Pandas**, and **Plotly**. Designed specifically for multi-branch retail and restaurant chains, this tool allows operators to query complex, cross-source datasets using natural language, dynamically rendering accurate metrics, charts, and downloadable reports on the fly.

---

## 📋 Project Overview

Managing multi-branch retail and food chains is chaotic—owners and managers are flooded with fragmented data across CSV files, local databases, and inventory spreadsheets. The **Business Analytics Assistant** bridges this gap using an intelligent conversational interface that handles multi-source reporting, automated chart generation, and proactive anomaly detection instantly.

---

## ✨ Features

* **Natural Language Query Interface:** Ask complex business questions in plain English and receive instant, accurate answers translated into executed data logic.
* **Multi-Branch / Multi-Location Analytics:** Filter, aggregate, and compare sales, orders, and stock levels across multiple locations (e.g., Karachi, Lahore, Islamabad).
* **Automatic Visualization Selection:** Dynamically routes data outputs to the optimal visual component—**KPI metric blocks**, **bar charts**, **chronological line graphs**, **proportional pie charts**, or **comparative data tables**.
* **Plain-English Insight Summary:** Every query is paired with an executive summary that explains the results clearly.
* **Conversational Memory:** Retains context across chat history using Streamlit session state for seamless follow-up questions and chart updates.
* **Exportable Reporting:** Download any generated insight or processed data slice directly as a `.csv` report with a single click.
* **Proactive Anomaly Detection:** Automatically scans uploaded sales logs and alerts users when footfall drops by more than 20% across branches.
* **Cross-Source Analysis:** Blends and joins live sales data from uploaded CSVs with warehouse stock records stored in SQLite.

---

## 🛠️ Tech Stack

* **Frontend / UI:** Streamlit (with custom CSS warm-palette overrides)
* **AI & LLM Engine:** OpenAI API (`gpt-4o-mini`) using JSON mode response formatting
* **Data Processing & Manipulation:** Pandas
* **Data Visualization:** Plotly Express
* **Database & Ingestion:** SQLite & CSV file connectors
* **Environment Management:** Python-dotenv

---

## 🔌 Data Connectors Implemented

1. **CSV Connector:** Ingests daily sales, transactions, order counts, and footfall logs dynamically via the sidebar uploader (`branch_sales.csv`).
2. **SQLite Database Connector:** Connects directly to relational database files (`store_inventory.db`) to query live persistent records like branch inventory, stock counts, and unit pricing from the `inventory` table.

---

## 🤖 AI Models Used & AI Usage Declaration

* **AI Model:** `gpt-4o-mini` via the OpenAI API.
* **Where AI is Used in the Application:**
  * **Code Generation:** Translates natural language questions into safe, sandboxed Pandas code blocks executed against available DataFrames.
  * **Visual Routing:** Analyzes query intent to select the best output component (`bar`, `line`, `pie`, `kpi`, `table`, or `chat`) and map appropriate axes.
  * **Executive Summarization:** Synthesizes analysis results into clear, human-readable business takeaways.
  * **Contextual Conversational State:** Evaluates previous conversation turns to handle follow-up queries accurately.

---

## 🏃 How to Run the Project

1. Launch the Streamlit web application:
2. Open the local application link in your browser
3. Use the sidebar to upload your sales CSV file and connect your SQLite database.
4. Start asking business questions in plain English!

---

## ⚠️ Known Limitations
* **Key Standardization:** Cross-source joins rely on common joining columns (such as `Item_Name` or `City`) having identical casing and formatting across both CSV and SQLite sources.
* **Dynamic Code Execution Scope:** Query execution uses standard Pandas operations; highly non-standard or ambiguous phrasing may require slight rephrasing for optimal code translation.
* **Database Schema Assumptions:** The SQLite connector currently targets specific table schemas (`inventory`); custom user-uploaded DB tables require manual schema mapping.
