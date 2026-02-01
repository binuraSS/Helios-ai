import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_market_charts(price_data):
    df = pd.DataFrame(price_data)
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
        row_heights=[0.7,0.3], subplot_titles=("Price & Trend","RSI (14)")
    )
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close", line=dict(width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], name="MA20", line=dict(dash="dot")), row=1,col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], name="MA50", line=dict(dash="dash")), row=1,col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI", line=dict(color="orange")), row=2,col=1)
    fig.add_hline(y=70, line_dash="dash", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", row=2, col=1)
    fig.update_layout(height=650, legend=dict(orientation="h"), margin=dict(t=50,b=40))
    return fig
