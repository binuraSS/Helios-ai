# helios.py — Phase 7 (CLEAN + STABLE)

import sys
import os
import json
from datetime import datetime
import pandas as pd
import yfinance as yf
from crewai import Agent, Task, Crew, LLM
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ----------------
# Setup
# ----------------
tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
print(f"\n☀️ HELIOS AI — Portfolio Analysis for {', '.join(tickers)}")

os.makedirs("reports", exist_ok=True)

llm = LLM(model="ollama/llama3.2", temperature=0.2)

# ----------------
# Data Functions
# ----------------
def fetch_price_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="3mo")
    if hist.empty:
        return pd.DataFrame()
    hist = hist.reset_index()
    hist["Date"] = hist["Date"].astype(str)  # JSON-safe
    return hist[["Date", "Close"]]

def compute_technical_indicators(hist_df):
    if hist_df.empty:
        return {}, "No technical data available."

    close = hist_df["Close"]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    volatility = close.std()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi14 = rsi.iloc[-1]

    metrics = {
        "MA20": round(ma20, 2),
        "MA50": round(ma50, 2),
        "RSI14": round(rsi14, 2),
        "Volatility": round(volatility, 4)
    }

    tech_str = (
        f"MA20: {metrics['MA20']}\n"
        f"MA50: {metrics['MA50']}\n"
        f"RSI14: {metrics['RSI14']}\n"
        f"Volatility: {metrics['Volatility']}"
    )

    return metrics, tech_str

def fetch_price_summary(hist_df):
    if hist_df.empty:
        return "No price data available."

    latest = hist_df["Close"].iloc[-1]
    avg = hist_df["Close"].mean()
    vol = hist_df["Close"].std()

    return (
        f"Latest close: {latest:.2f}\n"
        f"Average close: {avg:.2f}\n"
        f"Volatility: {vol:.2f}"
    )

# ----------------
# Agents
# ----------------
argus = Agent(
    role="Market Researcher",
    goal="Describe market tone using price data only",
    backstory="Data-grounded analyst. No speculation.",
    llm=llm
)

daedalus = Agent(
    role="Quantitative Analyst",
    goal="Interpret technical indicators strictly",
    backstory="Technical analyst. No sentiment.",
    llm=llm
)

critic = Agent(
    role="Strategic Critic",
    goal="Evaluate consistency and reliability",
    backstory="Reviewer focused on logical consistency.",
    llm=llm
)

# ----------------
# Portfolio Processing
# ----------------
portfolio_summary = []

for ticker in tickers:
    print(f"\n🔹 Processing {ticker}...")
    filename = f"reports/{ticker}_{datetime.utcnow().isoformat().replace(':','-')}.json"

    try:
        hist_df = fetch_price_data(ticker)
        price_summary = fetch_price_summary(hist_df)
        metrics, tech_data_str = compute_technical_indicators(hist_df)

        # ----------------
        # Agent Tasks
        # ----------------
        argus_task = Task(
            description=f"Using ONLY the price data below:\n{price_summary}\nReturn 3 bullet points.",
            expected_output="Three bullet points.",
            agent=argus
        )

        daedalus_task = Task(
            description=f"Using ONLY the technical indicators below:\n{tech_data_str}\nReturn 3 bullet points.",
            expected_output="Three bullet points.",
            agent=daedalus
        )

        crew = Crew(
            agents=[argus, daedalus],
            tasks=[argus_task, daedalus_task],
            process="sequential"
        )

        results = crew.kickoff()
        argus_result = results.tasks_output[0].raw
        daedalus_result = results.tasks_output[1].raw

        critic_task = Task(
            description=(
                f"Review analysis for {ticker}:\n"
                f"Market Research:\n{argus_result}\n"
                f"Technical Analysis:\n{daedalus_result}"
            ),
            expected_output="Critique report.",
            agent=critic
        )

        critic_crew = Crew(
            agents=[critic],
            tasks=[critic_task],
            process="sequential"
        )

        critic_results = critic_crew.kickoff()
        critic_text = critic_results.tasks_output[0].raw

        consistency = "low" if "inconsistent" in critic_text.lower() else "high"

        helios_report = {
            "meta": {
                "project": "Helios AI",
                "version": "0.1",
                "timestamp": datetime.utcnow().isoformat(),
                "ticker": ticker,
                "model": "llama3.2"
            },
            "inputs": {
                "price_summary": price_summary,
                "technical_indicators": tech_data_str
            },
            "metrics": metrics,
            "analysis": {
                "market_researcher": argus_result,
                "technical_analysis": daedalus_result
            },
            "critique": {
                "strategic_critic": critic_text,
                "consistency": consistency
            },
            "price_data": hist_df.to_dict(orient="records")
        }

        with open(filename, "w") as f:
            json.dump(helios_report, f, indent=2)

        portfolio_summary.append({
            "ticker": ticker,
            "status": "success",
            "report_file": filename
        })

        print(f"✅ {ticker} report saved")

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        portfolio_summary.append({
            "ticker": ticker,
            "status": "error",
            "error": str(e)
        })

# ----------------
# Save Summary
# ----------------
summary_file = f"reports/portfolio_summary_{datetime.utcnow().isoformat().replace(':','-')}.json"
with open(summary_file, "w") as f:
    json.dump(portfolio_summary, f, indent=2)

print(f"\n📁 Portfolio summary saved to {summary_file}")

