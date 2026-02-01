import os
import json
import pandas as pd

from .config import REPORTS_DIR

def list_reports():
    reports = []
    if not os.path.exists(REPORTS_DIR):
        return reports
    for filename in os.listdir(REPORTS_DIR):
        if not filename.endswith(".json") or filename.startswith("portfolio_summary"):
            continue
        try:
            name = filename.replace(".json","")
            ticker, timestamp = name.split("_",1)
            reports.append({"file": filename, "ticker": ticker, "timestamp": timestamp})
        except ValueError:
            continue
    return sorted(reports, key=lambda x:x["timestamp"], reverse=True)

def load_report(filename):
    with open(os.path.join(REPORTS_DIR, filename), "r") as f:
        return json.load(f)

def validate_report(report):
    required_keys = ["meta","analysis","critique","price_data"]
    for key in required_keys:
        if key not in report:
            return False, f"Missing key: {key}"
    return True, None

def metrics_to_df(report):
    metrics = report.get("metrics", {})
    if not metrics:
        return pd.DataFrame(columns=["Metric","Value"])
    return pd.DataFrame(metrics.items(), columns=["Metric","Value"])
