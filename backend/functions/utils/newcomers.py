from datetime import datetime, timezone, timedelta
from pathlib import Path
from glob import glob
from utils.dataCleaning import *

import argparse, json, math
import numpy as np
import pandas as pd

LOOKAHEAD_90D = timedelta(days=90)
LOOKAHEAD_6M = timedelta(days=182)
SUSTAINED_N = 4
TODAY = datetime.now(timezone.utc)

def get_periods(period='day', n=30, cutoff_days=0):
    now = datetime.now(timezone.utc)
    periods = []

    if period == 'day':
        today = now.date()
        start_day = today - timedelta(days=cutoff_days + n)
        for i in range(n):
            start = start_day + timedelta(days=i)
            end = start + timedelta(days=1)
            periods.append((start, end))

    elif period == 'week':
        this_monday = (now - timedelta(days=now.weekday())).date()
        start_monday = this_monday - timedelta(weeks=cutoff_days // 7 + n)
        for i in range(n):
            start = start_monday + timedelta(weeks=i)
            end = start + timedelta(weeks=1)
            periods.append((start, end))

    elif period == 'month':
        current = now.replace(day=1)
        start_month = current - pd.DateOffset(months=cutoff_days // 30 + n)
        current_month = pd.Timestamp(start_month)
        for _ in range(n):
            start = (current_month).date()
            end = (current_month + pd.offsets.MonthBegin(1)).date()
            periods.append((start, end))
            current_month += pd.offsets.MonthBegin(1)

    else:
        raise ValueError("Invalid period")

    return periods


def first_contribution(df: pd.DataFrame, date_col="created_at"):
    return df.groupby("user")[date_col].min()

def metric_newcomers_count(contrib_df, pts):
    out = []
    first_dates = pd\
        .to_datetime(first_contribution(contrib_df))\
        .apply(lambda dt: dt.timestamp())

    for start_date, end_date in pts:
        start_ts, end_ts = pd.Timestamp(start_date).timestamp(), pd.Timestamp(end_date).timestamp()
        count = first_dates[
            (first_dates >= start_ts) & 
            (first_dates <= end_ts)
        ].size

        out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": count })

    return out

def metric_retention_90d(contrib_df, pts, lookahead=timedelta(days=90)):
    contrib_df['created_at'] = pd.to_datetime(contrib_df['created_at'], utc=True)
    first_contribs = first_contribution(contrib_df)
    out = []

    for start_date, end_date in pts:
        start_ts = pd.Timestamp(start_date, tz='UTC')
        end_ts = pd.Timestamp(end_date, tz='UTC')
        cohort_users = first_contribs[(first_contribs >= start_ts) & (first_contribs < end_ts)].index

        if len(cohort_users) == 0:
            out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": None })
            continue

        retention_start = start_ts + lookahead
        retained_users = contrib_df[
            (contrib_df['user'].isin(cohort_users)) &
            (contrib_df['created_at'] >= retention_start)
        ]['user'].nunique()

        retention_rate = retained_users / len(cohort_users) * 100
        out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": round(retention_rate, 2) })

    return out

def metric_onboarding_success(pr_df, pts):
    pr_df['created_at'] = pd.to_datetime(pr_df['created_at'], utc=True)
    pr_df['merged_at'] = pd.to_datetime(pr_df['merged_at'], utc=True)
    first_prs = pr_df.sort_values(by='created_at').groupby('user').first()
    out = []

    for start_date, end_date in pts:
        start_ts = pd.Timestamp(start_date, tz='UTC')
        end_ts = pd.Timestamp(end_date, tz='UTC')
        cohort = first_prs[ (first_prs['created_at'] >= start_ts) & (first_prs['created_at'] < end_ts) ]

        if cohort.empty:
            out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": None })
            continue

        accepted = cohort['merged_at'].notna().sum()
        success_rate = accepted / len(cohort) * 100
        out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": str(round(success_rate, 2)) })

    return out


def metric_median_time_to_second_contribution(df, pts):
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    out = []
    df_sorted = df.sort_values(by='created_at')
    user_contribs = df_sorted.groupby('user')['created_at'].apply(list)

    for start_date, end_date in pts:
        start_ts = pd.Timestamp(start_date, tz='UTC')
        end_ts = pd.Timestamp(end_date, tz='UTC')
        cohort = user_contribs[ user_contribs.apply(lambda lst: len(lst) >= 2 and start_ts <= lst[0] < end_ts)]

        if cohort.empty:
            out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": None })
            continue

        deltas = [ (contribs[1] - contribs[0]).days for contribs in cohort.values]
        median_delta = str(int(round(np.median(deltas), 2))) if deltas else None
        out.append({ "x": start_date.strftime('%Y-%m-%d'), "y": median_delta })

    return out
