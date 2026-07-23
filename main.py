import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 1. SETUP & CONFIGURATION
# -----------------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Business Analytics Assistant", layout="wide")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Session state initialization for memory persistence
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------------------------------------------------
# 2. HELPER: PROACTIVE ANOMALY DETECTION (BONUS FEATURE)
# -----------------------------------------------------------------------------
def detect_anomalies(df):
    anomalies = []
    if "Footfall" in df.columns and "Branch" in df.columns and "Date" in df.columns:
        temp_df = df.sort_values(by=["Branch", "Date"]).copy()
        temp_df["Footfall_Change"] = temp_df.groupby("Branch")["Footfall"].pct_change()
        
        drops = temp_df[temp_df["Footfall_Change"] < -0.20]
        for _, row in drops.iterrows():
            drop_pct = abs(round(row["Footfall_Change"] * 100, 1))
            anomalies.append(
                f"🚨 **Footfall Alert:** {row['Branch']} ({row['City']}) dropped **{drop_pct}%** in footfall on {row['Date']}."
            )
    return anomalies

# -----------------------------------------------------------------------------
# 3. UI HEADERS & SIDEBAR CONNECTORS
# -----------------------------------------------------------------------------
st.title("💼 Business Analytics Assistant")
st.caption("Multi-Branch Intelligence & Real-time Cross-Source Reporting")

# --- Sidebar Branding & Controls ---
st.sidebar.markdown("### ⚙️ Control Panel")
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔌 Data Connections")

# Connector 1: CSV Upload
uploaded_file = st.sidebar.file_uploader("1. Sales Data (CSV)", type=["csv"])
csv_df = pd.read_csv(uploaded_file) if uploaded_file else None

# Connector 2: SQLite DB Connection
db_path = st.sidebar.text_input("2. Inventory Database Path", "store_inventory.db")
db_df = None

if db_path and os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        db_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        st.sidebar.success("SQLite Connected: `inventory` table")
    except Exception as e:
        st.sidebar.error(f"DB Error: {e}")

dfs_available = {}
if csv_df is not None:
    dfs_available["sales_df"] = csv_df
if db_df is not None:
    dfs_available["inventory_df"] = db_df

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD & ANOMALY ALERT BANNER
# -----------------------------------------------------------------------------
if dfs_available:
    st.subheader("📋 Connected Sources Overview")
    
    cols = st.columns(len(dfs_available))
    for idx, (name, dataframe) in enumerate(dfs_available.items()):
        with cols[idx]:
            st.markdown(f"**Dataset Source: `{name}`**")
            st.dataframe(dataframe.head(3), use_container_width=True)

    if "sales_df" in dfs_available:
        alerts = detect_anomalies(dfs_available["sales_df"])
        if alerts:
            st.subheader("⚠️ Proactive Intelligence Alerts")
            for alert in alerts:
                st.warning(alert)

    st.markdown("---")
    st.subheader("💬 Ask Anything about Your Business")

    # --- CHAT HISTORY RENDERING ---
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                st.write(msg["insight"])
                if msg.get("chart_type") == "kpi":
                    st.metric(label=msg["kpi_label"], value=msg["kpi_val"])
                elif msg.get("fig") is not None:
                    st.plotly_chart(msg["fig"], use_container_width=True)
                elif msg.get("df") is not None and not msg["df"].empty:
                    st.dataframe(msg["df"], use_container_width=True)

    # --- NEW CHAT INPUT ---
    if user_query := st.chat_input("Ask a question about revenue, footfall, or stock levels..."):
        
        # Render user message immediately for UI responsiveness
        with st.chat_message("user"):
            st.write(user_query)

        # Process Assistant response
        with st.chat_message("assistant"):
            if not api_key:
                st.error("⚠️ OpenAI API Key missing from environment! Check your .env file.")
            else:
                client = OpenAI(api_key=api_key.strip())
                
                # Spinner wrapped ONLY around the API call
                with st.spinner("Thinking..."):
                    try:
                        schema_info = {name: df.dtypes.to_dict() for name, df in dfs_available.items()}
                        sample_info = {name: df.head(2).to_json() for name, df in dfs_available.items()}

                        system_instructions = f"""
                        You are an expert business intelligence engine and conversational assistant for multi-branch retail/food chains.
                        DataFrames available: {list(dfs_available.keys())}
                        Schemas: {schema_info}
                        Sample Rows: {sample_info}

                        RULES FOR CHAT VS DATA:
                        - If the user prompt is casual conversation, greetings, or general chit-chat (e.g., "hi", "what's up", "how are you"), set `chart_type` to "chat", leave `python_code` as `""`, and reply naturally in `insight`.
                        - If the user asks a business or data question, write executable Pandas code.

                        RULES FOR PYTHON CODE:
                        - Pandas (`pd`) and Plotly Express (`px`) are available in scope.
                        - Always save your final computed DataFrame or Series into a variable named `result_df`.
                        - If calculating Average Order Value (AOV), compute `Revenue / Orders`.
                        - If a query needs both sales and inventory, join `sales_df` and `inventory_df` on common columns like `Item_ID` or `Item_Name`.
                        - CRITICAL COMPARISON RULE: NEVER use strict boolean filtering that drops rows or results in zero matches when comparing locations. Instead, use a pivot table, compute the difference, and SORT the dataframe.
                        - For follow-up chart conversions, use `pd.melt()` or aggregate so `result_df` has exactly 1 category column (`x_axis`) and 1 numeric column (`y_axis`).

                        RULES FOR CHART SELECTION:
                        - "chat": For casual conversational replies (no data/code needed).
                        - "bar": For comparisons across branches, products, or cities.
                        - "line": For trends over time (by date/week/month).
                        - "pie": For proportional sales share or percentage breakdowns. Requires exactly 1 categorical column (`x_axis`) and 1 numeric column (`y_axis`).
                        - "kpi": Single numerical outputs (total revenue, average orders).
                        - "table": For multi-metric ranked lists or detailed tables.

                        Return ONLY a JSON object with:
                        1. "python_code": Executable Pandas code storing output into `result_df` (or `""` if chat).
                        2. "chart_type": One of ["chat", "bar", "line", "pie", "kpi", "table"].
                        3. "x_axis": Column for X-axis / category labels (or null).
                        4. "y_axis": Column for Y-axis / values (or null).
                        5. "insight": Natural response text or executive summary for the user.
                        """

                        # BUILD CONVERSATIONAL MEMORY ARRAY
                        api_messages = [{"role": "system", "content": system_instructions}]
                        for msg in st.session_state.chat_history:
                            if msg["role"] == "user":
                                api_messages.append({"role": "user", "content": msg["content"]})
                            else:
                                api_messages.append({"role": "assistant", "content": msg["insight"]})

                        api_messages.append({"role": "user", "content": f'User Query: "{user_query}"'})

                        # LLM Call
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=api_messages,
                            response_format={"type": "json_object"}
                        )

                        result_json = json.loads(response.choices[0].message.content)

                    except Exception as e:
                        st.error(f"API Error: {str(e)}")
                        result_json = None

                # Spinner is now successfully closed and gone!
                if result_json:
                    try:
                        chart = result_json.get("chart_type")
                        insight_text = result_json.get("insight", "")

                        st.write(insight_text)

                        assistant_msg_data = {
                            "role": "assistant",
                            "insight": insight_text,
                            "chart_type": chart,
                            "fig": None,
                            "df": None,
                            "kpi_label": None,
                            "kpi_val": None
                        }

                        # If it's a chat message, save and skip data execution
                        if chart == "chat":
                            st.session_state.chat_history.append({"role": "user", "content": user_query})
                            st.session_state.chat_history.append(assistant_msg_data)
                        else:
                            # Safe retrieval and sanitization of generated code
                            raw_code = result_json.get("python_code") or ""
                            cleaned_code = raw_code.replace("\xa0", " ").replace("\\\n", " ").replace("\\\r\n", " ")

                            local_vars = {
                                "pd": pd,
                                "px": px,
                                **dfs_available
                            }
                            
                            result_df = None
                            if cleaned_code.strip():
                                exec(cleaned_code, {"pd": pd, "px": px}, local_vars)
                                result_df = local_vars.get("result_df")

                            # --- FALLBACK SAFETY CHECK ---
                            if (result_df is None or result_df.empty) and "sales_df" in dfs_available:
                                result_df = dfs_available["sales_df"].groupby(["Item_Name", "City"])["Revenue"].sum().reset_index()

                            if isinstance(result_df, pd.Series):
                                result_df = result_df.to_frame()

                            warm_palette = ["#ea580c", "#f59e0b", "#d97706", "#c2410c", "#b45309"]

                            # --- ADAPTIVE VISUALIZATION ROUTER ---
                            if result_df is not None and not result_df.empty:
                                if chart == "bar":
                                    fig = px.bar(
                                        result_df, 
                                        x=result_json["x_axis"], 
                                        y=result_json["y_axis"], 
                                        color=result_json["x_axis"],
                                        template="plotly_white",
                                        color_discrete_sequence=warm_palette
                                    )
                                    fig.update_layout(
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        font=dict(color="#292524", size=13),
                                        bargap=0.35,
                                        xaxis=dict(showgrid=False),
                                        yaxis=dict(showgrid=True, gridcolor="#e7e0d6")
                                    )
                                    fig.update_traces(marker_line_color='rgba(0,0,0,0)', marker_cornerradius=12)
                                    st.plotly_chart(fig, use_container_width=True)
                                    assistant_msg_data["fig"] = fig

                                elif chart == "line":
                                    fig = px.line(
                                        result_df, 
                                        x=result_json["x_axis"], 
                                        y=result_json["y_axis"], 
                                        markers=True,
                                        template="plotly_white",
                                        color_discrete_sequence=["#ea580c"]
                                    )
                                    fig.update_layout(
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        font=dict(color="#292524"),
                                        xaxis=dict(showgrid=False),
                                        yaxis=dict(showgrid=True, gridcolor="#e7e0d6")
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    assistant_msg_data["fig"] = fig

                                elif chart == "pie":
                                    fig = px.pie(
                                        result_df, 
                                        names=result_json["x_axis"], 
                                        values=result_json["y_axis"],
                                        color_discrete_sequence=warm_palette,
                                        hole=0.4
                                    )
                                    fig.update_layout(
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        font=dict(color="#292524", size=13)
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    assistant_msg_data["fig"] = fig

                                elif chart == "kpi":
                                    val = result_df.iloc[0, 0]
                                    label = result_df.columns[0] if isinstance(result_df, pd.DataFrame) else "Metric Result"
                                    st.metric(label=str(label).replace('_', ' ').upper(), value=f"{val:,.2f}" if isinstance(val, (int, float)) else str(val))
                                    
                                    assistant_msg_data["kpi_label"] = str(label).replace('_', ' ').upper()
                                    assistant_msg_data["kpi_val"] = str(val)

                                else:
                                    st.dataframe(result_df, use_container_width=True)
                                    assistant_msg_data["df"] = result_df

                                # EXPORTABLE REPORT BUTTON
                                csv_export = result_df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Export Report (CSV)",
                                    data=csv_export,
                                    file_name='branch_analytics_report.csv',
                                    mime='text/csv',
                                )

                            # Append to session state successfully
                            st.session_state.chat_history.append({"role": "user", "content": user_query})
                            st.session_state.chat_history.append(assistant_msg_data)

                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}")
else:
    st.info("👈 Connect a dataset in the sidebar to begin analysis!")
