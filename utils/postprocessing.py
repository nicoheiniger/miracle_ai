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
    Exclude the timestamp itself unless explicitly mentioned in the text.
    """
    if pd.isna(timestamp):  # Handle missing timestamps
        return []

    # Convert timestamp to datetime
    timestamp_date = pd.to_datetime(timestamp).date()

    # Define range: 2 days before to 2 years after the timestamp
    start_date = timestamp_date - timedelta(days=2)
    end_date = timestamp_date + timedelta(days=365 * 2 + 2)

    # Filter extracted dates
    filtered_dates = []
    for date in extracted_dates:
        try:
            parsed_date = pd.to_datetime(date, errors="coerce").date()  # Parse date, invalid -> NaT
            if parsed_date and start_date <= parsed_date <= end_date:
                # Include only if it's not the timestamp unless explicitly mentioned
                if parsed_date != timestamp_date or str(timestamp_date) in extracted_dates:
                    filtered_dates.append(parsed_date.strftime('%Y-%m-%d'))
        except Exception:
            continue

    return filtered_dates

