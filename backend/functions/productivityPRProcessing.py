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

def processProductivityPR(org_name: str, repo_name: str) -> None:
    pulls_df = pd.read_excel(f'./files/{org_name}_{repo_name}_pulls.xlsx')
    comments_df = pd.read_excel(f'./files/{org_name}_{repo_name}_pulls_comments.xlsx')

    pulls_df['created_at'] = pd.to_datetime(pulls_df['created_at'], utc=True, errors='coerce')
    pulls_df['closed_at']  = pd.to_datetime(pulls_df['closed_at'], utc=True, errors='coerce')

    now = datetime.now(timezone.utc)

    total_opened = pulls_df['created_at'].notna().sum()
    total_closed = pulls_df['closed_at'].notna().sum()

    results = {}

    for period in ['day', 'week', 'month']:
        (last_start, last_end), (prev_start, prev_end) = get_periods(period)
        results[f"{period}_opened_last"] = count_by_period(pulls_df, 'created_at', last_start, last_end)
        results[f"{period}_opened_prev"] = count_by_period(pulls_df, 'created_at', prev_start, prev_end)
        results[f"{period}_closed_last"] = count_by_period(pulls_df, 'closed_at', last_start, last_end)
        results[f"{period}_closed_prev"] = count_by_period(pulls_df, 'closed_at', prev_start, prev_end)

    results['trend_opened_day'] = safe_divide(results['day_opened_prev'], results['day_opened_last'], 2)
    results['trend_opened_week'] = safe_divide(results['week_opened_prev'], results['week_opened_last'], 2)
    results['trend_opened_month'] = safe_divide(results['month_opened_prev'], results['month_opened_last'], 2)

    results['trend_closed_day'] = safe_divide(results['day_closed_prev'], results['day_closed_last'], 2)
    results['trend_closed_week'] = safe_divide(results['week_closed_prev'], results['week_closed_last'], 2)
    results['trend_closed_month'] = safe_divide(results['month_closed_prev'], results['month_closed_last'], 2)

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

    results['backlog_days'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m-%d")} for ts in day_points]
    results['backlog_weeks'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m-%d")} for ts in week_points]
    results['backlog_months'] = [{"y": backlog_size(ts), "x": ts.strftime("%Y-%m")} for ts in month_points]

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

    results['open_by_day'] = open_by_day[::-1]
    results['open_by_week'] = open_by_week
    results['open_by_month'] = open_by_month

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

    results['close_by_day'] = close_by_day[::-1]
    results['close_by_week'] = close_by_week
    results['close_by_month'] = close_by_month

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
    results['time_to_answer_day'] = time_to_answer_day

    time_to_answer_week = list()
    for c, value in enumerate(avg_week):
        time_to_answer_week.append({"y": value, "x": week_points[c].strftime("%Y-%m-%d")})
    results['time_to_answer_week'] = time_to_answer_week

    time_to_answer_month = list()
    for c, value in enumerate(avg_month):
        time_to_answer_month.append({"y": value, "x": month_points[c].strftime("%Y-%m-%d")})
    results['time_to_answer_month'] = time_to_answer_month

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
    results['time_to_close_day'] = time_to_close_day

    time_to_close_week = [{"y": v, "x": week_points[c].strftime("%Y-%m-%d")} for c, v in enumerate(avg_close_week)]
    results['time_to_close_week'] = time_to_close_week

    time_to_close_month = [{"y": v, "x": month_points[c].strftime("%Y-%m")} for c, v in enumerate(avg_close_month)]
    results['time_to_close_month'] = time_to_close_month

    out_dir = Path(__file__).resolve().parents[1] / "./metrics"
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