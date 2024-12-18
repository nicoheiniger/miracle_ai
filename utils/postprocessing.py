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
    Explicitly exclude the timestamp itself unless it is part of the extracted dates.
    """
    if pd.isna(timestamp):  # Handle missing timestamps
        return []

    # Parse the timestamp to ensure tz-naive for comparison
    ref_date = pd.to_datetime(timestamp).tz_localize(None)

    # Define the filtering range
    start_date = ref_date - timedelta(days=2)  # 2 days before the timestamp
    end_date = ref_date + timedelta(days=365 * 2 + 2)  # 2 years and 2 days after the timestamp

    # Safely parse and filter dates
    filtered_dates = []
    for date in extracted_dates:
        try:
            parsed_date = pd.to_datetime(date, errors="coerce").tz_localize(None)  # Parse date and ensure tz-naive
            if not pd.isna(parsed_date):  # Skip invalid dates
                if start_date <= parsed_date <= end_date:  # Check range
                    filtered_dates.append(parsed_date.strftime('%Y-%m-%d'))
        except Exception:
            continue  # Skip any unexpected parsing errors

    # Explicitly exclude the timestamp itself unless explicitly mentioned
    if ref_date.strftime('%Y-%m-%d') in filtered_dates and ref_date.strftime('%Y-%m-%d') not in extracted_dates:
        filtered_dates.remove(ref_date.strftime('%Y-%m-%d'))

    return filtered_dates



