#!/usr/bin/env python3
"""
usage: python productivityPRProcessing.py org_name repo_name
"""

import pandas as pd
import numpy as np
import json
import os
import math
import argparse

from datetime import datetime, timezone, timedelta
from utils.dataProcessing import * 
from pathlib import Path
from glob import glob

def processProductivityPR(org_name: str, repo_name: str) -> None:
    base_dir = Path(__file__).resolve().parents[1] 
    files_dir = base_dir / "files"
    
    pull_files = sorted(glob(str(files_dir / f"{org_name.lower()}_{repo_name.lower()}_pulls.xlsx")))
    comment_files = sorted(glob(str(files_dir / f"{org_name.lower()}_{repo_name.lower()}_pulls_comments.xlsx")))

    if not pull_files or not comment_files:
        print("No pull request or comment files found for the given pattern.")
        return

    pulls_df_list = [pd.read_excel(file) for file in pull_files]
    pulls_df = pd.concat(pulls_df_list, ignore_index=True)

    comments_df_list = [pd.read_excel(file) for file in comment_files]
    comments_df = pd.concat(comments_df_list, ignore_index=True)

    print(f"Loaded {len(pull_files)} pull request files and {len(comment_files)} comment files.")
    print(f"Total PRs: {len(pulls_df)}, Total comments: {len(comments_df)}")

    pulls_df['created_at'] = pd.to_datetime(pulls_df['created_at'], utc=True, errors='coerce')
    pulls_df['closed_at']  = pd.to_datetime(pulls_df['closed_at'], utc=True, errors='coerce')
    pulls_df['merged_at'] = pd.to_datetime(pulls_df['merged_at'], utc=True, errors='coerce')
    
    now = datetime.now(timezone.utc)

    results = {
        "opened": {},
        "closed": {},
        "merged": {},
        "merge_rate": {},
        "backlog": {},
        "open_by": {},
        "close_by": {},
        "time_to_answer": {},
        "time_to_close": {},
        "opened_last": {},
        "opened_prev": {},
        "closed_last": {},
        "closed_prev": {},
        "merged_last": {},
        "merged_prev": {},
        "merge_rate_last": {},
        "merge_rate_prev": {},
        "trend_opened": {},
        "trend_closed": {},
        "trend_merged": {}
    }

    for period in ['day', 'week', 'month']:
        (last_start, last_end), (prev_start, prev_end) = get_periods(period)
        results["opened_last"][period] = count_by_period(pulls_df, 'created_at', last_start, last_end)
        results["opened_prev"][period] = count_by_period(pulls_df, 'created_at', prev_start, prev_end)
        results["closed_last"][period] = count_by_period(pulls_df, 'closed_at', last_start, last_end)
        results["closed_prev"][period] = count_by_period(pulls_df, 'closed_at', prev_start, prev_end)
        results["merged_last"][period] = count_by_period(pulls_df, "merged_at", last_start, last_end)
        results["merged_prev"][period] = count_by_period(pulls_df, "merged_at", prev_start, prev_end)

    results[f"merge_rate_last"]["day"] = round(safe_divide(results[f"merged_last"]["day"], results[f"closed_last"]["day"], 4) * 100, 2) - 1
    results[f"merge_rate_last"]["week"] = round(safe_divide(results[f"merged_last"]["week"], results[f"closed_last"]["week"], 4) * 100, 2) - 1
    results[f"merge_rate_last"]["month"] = round(safe_divide(results[f"merged_last"]["month"], results[f"closed_last"]["month"], 4) * 100, 2) - 1
    
    results[f"merge_rate_prev"]["day"] = round(safe_divide(results[f"merged_prev"]["day"], results[f"closed_prev"]["day"], 4) * 100, 2) - 1
    results[f"merge_rate_prev"]["week"] = round(safe_divide(results[f"merged_prev"]["week"], results[f"closed_prev"]["week"], 4) * 100, 2) - 1
    results[f"merge_rate_prev"]["month"] = round(safe_divide(results[f"merged_prev"]["month"], results[f"closed_prev"]["month"], 4) * 100, 2) - 1

    results['trend_opened']["day"] = safe_divide(results['opened_last']["day"], results['opened_prev']["day"], 2) - 1
    results['trend_opened']["week"] = safe_divide(results['opened_last']["week"], results['opened_prev']["week"], 2) - 1
    results['trend_opened']["month"] = safe_divide(results['opened_last']["month"], results['opened_prev']["month"], 2) - 1
    
    results['trend_closed']["day"] = safe_divide(results['closed_last']["day"], results['closed_prev']["day"], 2) - 1
    results['trend_closed']["week"] = safe_divide(results['closed_last']["week"], results['closed_prev']["week"], 2) - 1
    results['trend_closed']["month"] = safe_divide(results['closed_last']["month"], results['closed_prev']["month"], 2) - 1

    day_points = [
        datetime.combine((now.date() - timedelta(days=delta)), datetime.max.time(), tzinfo=timezone.utc)
        for delta in range(1, 31)
    ][::-1]

    days_since_sunday = (now.weekday() + 1) % 7
    last_sunday = now.date() - timedelta(days=days_since_sunday)
    week_points = [
        datetime.combine(last_sunday - timedelta(weeks=delta), datetime.max.time(), tzinfo=timezone.utc)
        for delta in range(1, 31)
    ][::-1]

    month_points = []
    this_month = now.replace(day=1)
    for delta in range(0, 30):
        month = this_month - pd.DateOffset(months=delta)
        end_of_month = (month - pd.DateOffset(days=1)).to_pydatetime().replace(
            hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
        month_points.append(end_of_month)
    month_points = month_points[::-1] 

    def backlog_size(ts):
        return pulls_df[
            (pulls_df['created_at'] <= ts) & 
            ((pulls_df['closed_at'].isna()) | (pulls_df['closed_at'] > ts))
        ].shape[0]

    results['backlog']['day'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m-%d")} for ts in day_points]
    results['backlog']['week'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m-%d")} for ts in week_points]
    results['backlog']['month'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m")} for ts in month_points]

    open_by_day = []
    for delta in range(1, 30):
        day_start = datetime.combine((now.date() - timedelta(days=delta)), datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine((now.date() - timedelta(days=delta)), datetime.max.time(), tzinfo=timezone.utc)
        mask = (pulls_df['created_at'] >= day_start) & (pulls_df['created_at'] <= day_end)
        open_by_day.append({"y": pulls_df[mask].shape[0], "x": day_start.strftime("%Y-%m-%d")})

    open_by_week = []
    for delta in range(0, 30):
        week_end = week_points[delta]
        week_start = week_end - timedelta(days=6)
        mask = (pulls_df['created_at'] >= week_start) & (pulls_df['created_at'] <= week_end)
        open_by_week.append({"y": pulls_df[mask].shape[0], "x": week_start.strftime("%Y-%m-%d")})

    open_by_month = []
    for i in range(0, 30):
        month_end = month_points[i]
        month_start = (month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0) 
                    if month_end.day != 1 else month_end)
        mask = (pulls_df['created_at'] >= month_start) & (pulls_df['created_at'] <= month_end)
        open_by_month.append({"y": pulls_df[mask].shape[0], "x": month_start.strftime("%Y-%m")})

    results['open_by']['day'] = open_by_day[::-1]
    results['open_by']['week'] = open_by_week
    results['open_by']['month'] = open_by_month

    close_by_day = []
    for delta in range(1, 30):
        day_start = datetime.combine((now.date() - timedelta(days=delta)), datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine((now.date() - timedelta(days=delta)), datetime.max.time(), tzinfo=timezone.utc)
        mask = (pulls_df['closed_at'] >= day_start) & (pulls_df['closed_at'] <= day_end)
        close_by_day.append({"y": pulls_df[mask].shape[0], "x": day_start.strftime("%Y-%m-%d")})

    close_by_week = []
    for delta in range(0, 30):
        week_end = week_points[delta]
        week_start = week_end - timedelta(days=6)
        mask = (pulls_df['closed_at'] >= week_start) & (pulls_df['closed_at'] <= week_end)
        close_by_week.append({"y": pulls_df[mask].shape[0], "x": week_start.strftime("%Y-%m-%d")})

    close_by_month = []
    for i in range(0, 30):
        month_end = month_points[i]
        month_start = (month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0) 
                    if month_end.day != 1 else month_end)
        mask = (pulls_df['closed_at'] >= month_start) & (pulls_df['closed_at'] <= month_end)
        close_by_month.append({"y": pulls_df[mask].shape[0], "x": month_start.strftime("%Y-%m")})

    results['close_by']['day'] = close_by_day[::-1]
    results['close_by']['week'] = close_by_week
    results['close_by']['month'] = close_by_month

    first_answer_times = []
    pulls_df['created_at'] = pd.to_datetime(pulls_df['created_at'], utc=True, errors='coerce')
    comments_df['created_at'] = pd.to_datetime(comments_df['created_at'], utc=True, errors='coerce')

    for idx, pr in pulls_df.iterrows():
        pr_number = pr['number']
        pr_author = pr['user']
        pr_created = pr['created_at']
        
        comments = comments_df[(comments_df['pr_number'] == pr_number) & (comments_df['user'] != pr_author)]
        if comments.empty:
            continue 
        
        first_comment = comments.sort_values('created_at').iloc[0]
        answer_author = first_comment['user']
        answer_time = first_comment['created_at']
        time_to_first_answer = (answer_time - pr_created).total_seconds() / 3600  # in hours

        first_answer_times.append({
            "pr_number": pr_number,
            "pr_author": pr_author,
            "pr_created_at": pr_created,
            "first_answer_author": answer_author,
            "first_answer_at": answer_time,
            "time_to_first_answer_hours": time_to_first_answer
        })

    avg_day = rolling_avg_first_answer(first_answer_times, day_points, period="day")
    avg_week = rolling_avg_first_answer(first_answer_times, week_points, period="week")
    avg_month = rolling_avg_first_answer(first_answer_times, month_points, period="month")

    avg_day = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_day[::-1]]
    avg_week = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_week]
    avg_month = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_month]

    time_to_answer_day = list()
    for c, value in enumerate(avg_day):
        time_to_answer_day.append({"y": value, "x": day_points[c].strftime("%Y-%m-%d")})
    results['time_to_answer']['day'] = time_to_answer_day

    time_to_answer_week = list()
    for c, value in enumerate(avg_week):
        time_to_answer_week.append({"y": value, "x": week_points[c].strftime("%Y-%m-%d")})
    results['time_to_answer']['week'] = time_to_answer_week

    time_to_answer_month = list()
    for c, value in enumerate(avg_month):
        time_to_answer_month.append({"y": value, "x": month_points[c].strftime("%Y-%m-%d")})
    results['time_to_answer']['month'] = time_to_answer_month

    time_to_close_times = []
    for idx, pr in pulls_df.iterrows():
        pr_created = pr['created_at']
        pr_closed = pr['closed_at']
        
        if pd.notna(pr_closed):
            time_to_close = (pr_closed - pr_created).total_seconds() / 3600  # in hours
            time_to_close_times.append({
                "pr_number": pr['number'],
                "pr_author": pr['user'],
                "pr_created_at": pr_created,
                "closed_at": pr_closed,
                "time_to_close_hours": time_to_close
            })

    avg_close_day = rolling_avg_time_to_close(time_to_close_times, day_points, period="day")
    avg_close_week = rolling_avg_time_to_close(time_to_close_times, week_points, period="week")
    avg_close_month = rolling_avg_time_to_close(time_to_close_times, month_points, period="month")

    avg_close_day = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_close_day[::-1]]
    avg_close_week = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_close_week]
    avg_close_month = [0 if (isinstance(x, float) and math.isnan(x)) else round(x, 2) for x in avg_close_month]

    time_to_close_day = [{"y": v, "x": day_points[c].strftime("%Y-%m-%d")} for c, v in enumerate(avg_close_day)]
    results['time_to_close']['day'] = time_to_close_day

    time_to_close_week = [{"y": v, "x": week_points[c].strftime("%Y-%m-%d")} for c, v in enumerate(avg_close_week)]
    results['time_to_close']['week'] = time_to_close_week

    time_to_close_month = [{"y": v, "x": month_points[c].strftime("%Y-%m")} for c, v in enumerate(avg_close_month)]
    results['time_to_close']['month'] = time_to_close_month

    merge_rate_day = []
    for end in day_points:
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        mask  = (pulls_df["closed_at"] >= start) & (pulls_df["closed_at"] <= end)
        merge_rate_day.append({"y": period_merge_rate(pulls_df, mask), "x": start.strftime("%Y-%m-%d")})

    merge_rate_week = []
    for end in week_points:
        start = end - timedelta(days=6)
        mask  = (pulls_df["closed_at"] >= start) & (pulls_df["closed_at"] <= end)
        merge_rate_week.append({"y": period_merge_rate(pulls_df, mask), "x": start.strftime("%Y-%m-%d")})

    merge_rate_month = []
    for end in month_points:
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mask  = (pulls_df["closed_at"] >= start) & (pulls_df["closed_at"] <= end)
        merge_rate_month.append({"y": period_merge_rate(pulls_df, mask), "x": start.strftime("%Y-%m")})
    
    results["merge_rate"]['day'] = merge_rate_day
    results["merge_rate"]['week'] = merge_rate_week
    results["merge_rate"]['month'] = merge_rate_month
    results["trend_merged"]['day'] = safe_divide(results["merged_last"]["day"], results["merged_prev"]["day"], 2) - 1
    results["trend_merged"]['week'] = safe_divide(results["merged_last"]["week"], results["merged_prev"]["week"], 2) - 1
    results["trend_merged"]['month'] = safe_divide(results["merged_last"]["month"], results["merged_prev"]["month"], 2) - 1

    out_dir = Path(__file__).resolve().parents[2] / "./metrics"
    out_dir.mkdir(exist_ok=True)
    
    nested_dir = out_dir / f'{org_name}/{repo_name}'
    nested_dir.mkdir(parents=True, exist_ok=True)
    output_path = nested_dir / 'pullRequestAnalysis.json'

    print(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process GitHub Pull Request Productivity. ")
    parser.add_argument("org_name",  help="GitHub organization / user name")
    parser.add_argument("repo_name", help="Repository name")
    args = parser.parse_args()

    processProductivityPR(args.org_name, args.repo_name)