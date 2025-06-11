#!/usr/bin/env python3
"""
engagementProcessing.py – compute community‑engagement metrics for one repo.

usage:
    python engagementProcessing.py ORG REPO
Produces:
    metrics/<ORG>/<REPO>/engagementAnalysis.json
"""
from __future__ import annotations

import argparse
import json
import numpy as np
import pandas as pd

from glob import glob
from pathlib import Path
from typing import Final
from utils.dataCleaning import load_concat

from utils.engagement import (
    get_periods,
    metric_active_chat_participation_rate,
    metric_avg_labels_per_open_issue,
    metric_committer_churn_rate,
    metric_committer_concentration_gini,
    metric_count_of_occasional_contributors,
)

# ────────────────────────── helpers ────────────────────────── #

EMPTY_DF: Final = pd.DataFrame(columns=["user", "created_at"])

def _safe_load(pattern: str | Path) -> pd.DataFrame:
    """Return concatenated XLSX or an empty DF if the file is missing."""
    matches = glob(str(pattern))
    return load_concat(matches[0]) if matches else EMPTY_DF.copy()

def _ensure_cols(df: pd.DataFrame, cols: dict[str, str]) -> None:
    """Guarantee presence & dtype for required columns."""
    for col, dtype in cols.items():
        if col not in df.columns: df[col] = pd.Series(dtype=dtype)

def _json_safe(val):
    """Turn NumPy scalars → python built‑ins, NaN → None."""
    if pd.isna(val): return None
    if isinstance(val, (np.floating, np.float32, np.float64)): return float(val)
    if isinstance(val, (np.integer, np.int32, np.int64)): return int(val)
    return val

def _series_from_window(df: pd.DataFrame, periods, metric_fn):
    """Apply `metric_fn` to each (start,end) window → [{x,y}, …]."""
    out = []
    for start, end in periods:
        window_df = df[
            (df["created_at"] >= pd.Timestamp(start, tz="UTC")) &
            (df["created_at"] <  pd.Timestamp(end,   tz="UTC"))
        ]
        y_val = metric_fn(window_df)
        out.append({"x": start.strftime("%Y-%m-%d"), "y": _json_safe(y_val)})
    return out

# ────────────────────────── main routine ────────────────────────── #

def process_engagement_metrics(org: str, repo: str) -> None:
    base = Path(__file__).resolve().parents[1] / "files"
    stem = f"{org.lower()}_{repo.lower()}"

    commits_df = _safe_load(base / f"{stem}_commits.xlsx")
    if commits_df.empty: commits_df = _safe_load(base / f"{stem}_pulls.xlsx")
    pulls_df = _safe_load(base / f"{stem}_pulls.xlsx")

    issues_df = _safe_load(base / f"{stem}_issues.xlsx")
    pr_comments_df = _safe_load(base / f"{stem}_pulls_comments.xlsx")
    issue_comments_df = _safe_load(base / f"{stem}_issues_comments.xlsx")

    comments_df = (
        pd.concat([pr_comments_df, issue_comments_df], ignore_index=True)
        if pr_comments_df.size or issue_comments_df.size
        else EMPTY_DF.copy()
    )

    for df in (commits_df, issues_df, comments_df, pulls_df):
        _ensure_cols(df, {"user": str, "created_at": "datetime64[ns, UTC]"})
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    grids = {
        "day": get_periods("day",   n=30),
        "week": get_periods("week",  n=30),
        "month": get_periods("month", n=30),
    }

    chat_part = {k: metric_active_chat_participation_rate(comments_df, commits_df, v) for k, v in grids.items()}
    churn = _json_safe(metric_committer_churn_rate(commits_df))

    def _gini_metric(win_df):
        return metric_committer_concentration_gini(
            win_df, 
            win_df["created_at"].min(), 
            win_df["created_at"].max()
        )

    gini_series = {
        k: _series_from_window(commits_df, v, _gini_metric) for k, v in grids.items()
    }

    commits_df["year"] = commits_df["created_at"].dt.year
    counts_yoy = (
        commits_df.groupby("year")["user"].nunique()
        .sort_index()
        .reset_index()
        .rename(columns={"year": "x", "user": "y"})
        .to_dict("records")
    )

    def _occasional_for_window(window_df: pd.DataFrame, end_ts: pd.Timestamp) -> int:
        """
        Count contributors who appear in *window_df* (active now)
        AND have < 3 pull requests in the trailing 365 days.
        """
        active_users = window_df["user"].unique()
        if active_users.size == 0:
            return 0

        trailing_df = pulls_df[
            (pulls_df["created_at"] >= end_ts - pd.Timedelta(days=365))
            & (pulls_df["created_at"] <  end_ts)
            & (pulls_df["user"].isin(active_users))
        ]
        pr_counts = trailing_df.groupby("user").size()
        return int((pr_counts < 3).sum())

    occasional_series = {}
    
    for gran, periods in grids.items():
        series = []
        for start, end in periods:
            window = pulls_df[
                (pulls_df["created_at"] >= pd.Timestamp(start, tz="UTC"))
                & (pulls_df["created_at"] <  pd.Timestamp(end, tz="UTC"))
            ]
            count = _occasional_for_window(window, pd.Timestamp(end, tz="UTC"))
            series.append({"x": start.strftime("%Y-%m-%d"), "y": _json_safe(count)})
        occasional_series[gran] = series
    
    results = {
        "active_chat_participation_rate": chat_part,
        "committer_churn_rate": churn,
        "committer_concentration_gini": gini_series,
        "contributor_counts_yoy": counts_yoy,
        "occasional_contributors": occasional_series
    }

    out_dir  = Path(__file__).resolve().parents[2] / "metrics" / org / repo
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "engagementAnalysis.json"
    with out_file.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    print(f"✔ results written to {out_file}")

# ────────────────────────── CLI ────────────────────────── #

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Compute engagement metrics")
    p.add_argument("org_name")
    p.add_argument("repo_name")
    args = p.parse_args()
    process_engagement_metrics(args.org_name, args.repo_name)
