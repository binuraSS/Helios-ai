import streamlit as st
from dashboard.config import REPORTS_DIR
from dashboard.utils import list_reports, load_report, validate_report, metrics_to_df
from dashboard.visualizations import build_market_charts
from dashboard.components import display_meta, display_metrics, display_analysis, display_critique
import pandas as pd

# -----------------------------
# Session State
# -----------------------------
if "selected_report" not in st.session_state:
    st.session_state.selected_report = None

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Helios Reports")
reports = list_reports()
if reports:
    options = [f"{r['ticker']} — {r['timestamp']}" for r in reports]
    selected_label = st.sidebar.selectbox("Select Analysis Report", options)
    selected_index = options.index(selected_label)
    st.session_state.selected_report = reports[selected_index]["file"]
else:
    st.sidebar.warning("No Helios reports found.")

# -----------------------------
# Main View
# -----------------------------
st.title("☀️ Helios AI — Financial Analysis Dashboard")

if not st.session_state.selected_report:
    st.info("Select a report from the sidebar to begin.")
    st.stop()

try:
    report = load_report(st.session_state.selected_report)
except Exception as e:
    st.error("Failed to load report")
    st.exception(e)
    st.stop()

is_valid, err = validate_report(report)
if not is_valid:
    st.error("Invalid Helios report format")
    st.code(err)
    st.json(report)
    st.stop()

# Display sections
display_meta(report.get("meta",{}))
metrics_df = metrics_to_df(report)
display_metrics(metrics_df)

# Market Visualization
st.subheader("📊 Market Visualization")
price_data = report.get("price_data",[])
if price_data:
    fig = build_market_charts(price_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Unable to render charts")
else:
    st.warning("No price data available for charts")

display_analysis(report.get("analysis",{}))
display_critique(report.get("critique",{}))
