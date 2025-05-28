import pandas as pd
import numpy as np
import json

from datetime import datetime, timezone, timedelta

now = datetime.now(timezone.utc)

def in_range(dt, start, end):
    return (dt >= start) & (dt < end)

def safe_divide(a: float, b: float, roundBy: int) -> float:
    """Return a / b, but 0 when b is 0 (or None)."""
    return 0 if b == 0 else round(a / b, roundBy)

def get_periods(period='day'):
    if period == 'day':
        today = now.date()
        last = today - timedelta(days=1)
        before_last = today - timedelta(days=2)
        return (last, last + timedelta(days=1)), (before_last, last)
    elif period == 'week':
        # Weeks start on Monday
        this_monday = (now - timedelta(days=now.weekday())).date()
        last_start = this_monday - timedelta(days=7)
        last_end = this_monday
        before_last_start = last_start - timedelta(days=7)
        before_last_end = last_start
        return (last_start, last_end), (before_last_start, before_last_end)
    elif period == 'month':
        first = now.replace(day=1)
        last_month_end = first
        last_month_start = (first - pd.offsets.MonthBegin(1)).date()
        before_last_month_end = last_month_start
        before_last_month_start = (last_month_start - pd.offsets.MonthBegin(1)).date()
        return (last_month_start, last_month_end.date()), (before_last_month_start, before_last_month_end)
    else:
        raise ValueError('Invalid period')
    
def count_by_period(df, col, start, end):
    return df[in_range(df[col].dt.date, start, end)].shape[0]

def rolling_avg_first_answer(times, points, period):
    if not times:
        print(f"[Warning] No data available for first answer calculation in period '{period}'.")
        return [np.nan] * len(points)

    avg_times = []
    for i, end in enumerate(points):
        if period == "day":
            start = end - timedelta(days=1)
        elif period == "week":
            start = end - timedelta(weeks=1)
        elif period == "month":
            if i == 0:
                try:
                    start = min(row['first_answer_at'] for row in times) - timedelta(seconds=1)
                except ValueError:
                    print(f"[Warning] No 'first_answer_at' timestamps for period '{period}'.")
                    start = end - timedelta(days=30)  # Fallback: arbitrary 30-day window
            else:
                start = points[i - 1]
        else:
            raise ValueError("period must be 'day', 'week', or 'month'")

        valid_prs = [row for row in times if start < row['first_answer_at'] <= end]
        if valid_prs:
            avg = np.mean([row['time_to_first_answer_hours'] if period == "day" else row['time_to_first_answer_hours'] / 24 for row in valid_prs])
        else:
            avg = np.nan
        avg_times.append(avg)
    return avg_times

def rolling_avg_time_to_close(times, points, period):
    if not times:
        print(f"[Warning] No data available for time to close calculation in period '{period}'.")
        return [np.nan] * len(points)

    avg_times = []
    for i, end in enumerate(points):
        if period == "day":
            start = end - timedelta(days=1)
        elif period == "week":
            start = end - timedelta(weeks=1)
        elif period == "month":
            if i == 0:
                try:
                    start = min(row['closed_at'] for row in times) - timedelta(seconds=1)
                except ValueError:
                    print(f"[Warning] No 'closed_at' timestamps for period '{period}'.")
                    start = end - timedelta(days=30)  # Fallback: arbitrary 30-day window
            else:
                start = points[i - 1]
        else:
            raise ValueError("period must be 'day', 'week', or 'month'")

        valid_prs = [row for row in times if start < row['closed_at'] <= end]
        if valid_prs:
            avg = np.mean([row['time_to_close_hours'] if period == "day" else row['time_to_close_hours'] / 24 for row in valid_prs])
        else:
            avg = np.nan
        avg_times.append(avg)
    return avg_times
