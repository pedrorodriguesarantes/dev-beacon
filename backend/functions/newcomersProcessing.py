#!/usr/bin/env python3
"""
usage:  python newcomersProcessing.py ORG REPO
Produces: metrics/<ORG>/<REPO>/newcomerAnalysis.json
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from glob import glob
from utils.dataCleaning import *
from utils.newcomers import *

import argparse, json, math
import numpy as np
import pandas as pd

def process_newcomer_metrics(org, repo):
    base = Path(__file__).resolve().parents[1] / "files"
    pr_df = load_concat(str(base / f"{org.lower()}_{repo.lower()}_pulls.xlsx"))
    pr_comments_df = load_concat(str(base / f"{org.lower()}_{repo.lower()}_pulls_comments.xlsx"))

    day_pts = get_periods("day", n=30)
    week_pts = get_periods("week", n=30)
    month_pts = get_periods("month", n=30)

    newcomers_day = metric_newcomers_count(pr_df, day_pts),
    newcomers_week = metric_newcomers_count(pr_df, week_pts)
    newcomers_month = metric_newcomers_count(pr_df, month_pts)

    day_pts = get_periods("day", n=30, cutoff_days=90)
    week_pts = get_periods("week", n=30, cutoff_days=90)
    month_pts = get_periods("month", n=30, cutoff_days=90)

    newcomers_90retention_day = metric_retention_90d(pr_df, day_pts),
    newcomers_90retention_week = metric_retention_90d(pr_df, week_pts)
    newcomers_90retention_month = metric_retention_90d(pr_df, month_pts)

    day_pts = get_periods("day", n=30)
    week_pts = get_periods("week", n=30)
    month_pts = get_periods("month", n=30)

    newcomers_success_day = metric_onboarding_success(pr_df, day_pts)
    newcomers_success_week = metric_onboarding_success(pr_df, week_pts)
    newcomers_success_month = metric_onboarding_success(pr_df, month_pts)
    
    median_second_contribution_day = metric_median_time_to_second_contribution(pr_df, day_pts)
    median_second_contribution_week = metric_median_time_to_second_contribution(pr_df, week_pts)
    median_second_contribution_month = metric_median_time_to_second_contribution(pr_df, month_pts)

    results = {
        "newcomers_count": {
            "day": newcomers_day,
            "week": newcomers_week,
            "month": newcomers_month,
        },
        "retention_90d": {
            "week": newcomers_90retention_week,
            "month": newcomers_90retention_month,
        },
        "onboarding_success": {
            "day": newcomers_success_day,
            "week": newcomers_success_week,
            "month": newcomers_success_month,
        },
        "median_time_to_second_contribution": {
            "day": median_second_contribution_day,
            "week": median_second_contribution_week,
            "month": median_second_contribution_month,
        }
    }

    out_dir = Path(__file__).resolve().parents[2] / "metrics" / org / repo
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "newcomerAnalysis.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)
    
    print(f"✔ results written to {out_dir/'newcomerAnalysis.json'}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("org_name")
    ap.add_argument("repo_name")
    args = ap.parse_args()

    process_newcomer_metrics(args.org_name, args.repo_name)
