import streamlit as st
import pandas as pd

def display_meta(meta):
    st.subheader("Report Metadata")
    cols = st.columns(4)
    cols[0].metric("Ticker", meta.get("ticker","—"))
    cols[1].metric("Model", meta.get("model","—"))
    cols[2].metric("Version", meta.get("version","—"))
    cols[3].metric("Timestamp", meta.get("timestamp","—"))

def display_metrics(metrics_df):
    st.subheader("Computed Metrics")
    if metrics_df.empty:
        st.warning("No metrics found")
    else:
        st.dataframe(metrics_df, use_container_width=True)

def display_analysis(analysis):
    st.subheader("Agent Analysis")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### Market Researcher")
        st.write(analysis.get("market_researcher","No output"))
    with col2:
        st.markdown("### Quantitative Analyst")
        st.write(analysis.get("technical_analysis","No output"))

def display_critique(critique):
    st.subheader("Strategic Critique")
    st.write(critique.get("strategic_critic","No critique"))
    consistency = critique.get("consistency","unknown")
    if consistency=="high": st.success("High agent agreement")
    elif consistency=="medium": st.warning("Partial disagreement")
    elif consistency=="low": st.error("Low consistency")
    else: st.info("Consistency not classified")
