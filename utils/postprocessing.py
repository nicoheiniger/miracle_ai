import re
import pandas as pd
from datetime import timedelta

def clean_urls(urls):
    """
    Removes trailing punctuation from URLs in a list.
    """
    if not urls:
        return []
    return [re.sub(r"[)\]>]+$", "", url) for url in urls]  # Remove trailing ), >, or ]

def filter_dates(extracted_dates, timestamp):
    """
    Filter extracted dates to only keep those within 2 days before and 2 years after the given timestamp.
    """
    # Ensure timestamp is tz-naive for comparison
    if pd.isna(timestamp):  # Handle missing timestamps
        return []

    start_date = pd.to_datetime(timestamp).tz_localize(None) - timedelta(days=2)  # 2 days before
    end_date = start_date + timedelta(days=365 * 2 + 2)  # 2 years after the original timestamp (+ 2 days buffer)

    # Safely parse and filter dates
    filtered_dates = []
    for date in extracted_dates:
        try:
            parsed_date = pd.to_datetime(date, errors="coerce")  # Parse date, invalid -> NaT
            if not pd.isna(parsed_date):  # Skip invalid dates
                parsed_date = parsed_date.tz_localize(None)  # Ensure tz-naive
                if start_date <= parsed_date <= end_date:  # Check range
                    filtered_dates.append(parsed_date.strftime('%Y-%m-%d'))
        except Exception:
            continue  # Skip any unexpected parsing errors
    return filtered_dates
