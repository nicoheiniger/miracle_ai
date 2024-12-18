import re
from dateparser import parse
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
import pandas as pd
import spacy

nlp = spacy.load("en_core_web_sm")
# Date Parser Version 2

# Updated regex patterns to capture explicit date formats only
DATE_PATTERNS = [
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  
    # Matches dates like "12/25/2024" or "12-25-24".

    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    
    # Matches dates like "2024/12/25" or "2024-12-25".

    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[.,]?\s+\d{4}\b',  
    # Matches dates like "5th Nov 2024" or "12 Nov, 2024".

    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',    
    # Matches dates like "November 5, 2024" or "Nov 5th, 2024".

    r'\b\d{4}-\d{2}-\d{2}\b',
    # Matches ISO date format "2024-12-25".

    r'\b\d{2}/\d{2}/\d{4}\b',
    # Matches dates like "25/12/2024".

    r'\b\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}\b',
    # Matches dates like "25 Dec 2024".

    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}\b',
    # Matches dates like "Dec 25, 2024".

    r'\b\d{1,2}(st|nd|rd|th)? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
    # Matches partial dates like "25th Dec".

    r'\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b',
    # Matches dates like "December 25, 2024".

    r'\b(?:today|tomorrow|yesterday|this\s+\w+|next\s+\w+|last\s+\w+|in\s+\d+\s+\w+)\b',
    # Matches relative terms like "today", "tomorrow", "next week", "last month", or "in 3 days".
]


DAY_NAME_PATTERN = r'\b(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sun|Mon|Tue|Wed|Thu|Fri|Sat)\b'

MONTH_NAME_PATTERN = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|' \
                     r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'

# Function to extract dates
def extract_dates(text, timestamp):
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)
    if isinstance(timestamp, pd.Timestamp):
        timestamp = timestamp.to_pydatetime()

    dates = set()

    # Regex-based date extraction
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Filter out left-over Unix timestamp-like formats (e.g., <t:1730905200>)
                if '<t:' in match:
                    continue
                parsed_date = parse(match, settings={'RELATIVE_BASE': timestamp})
                if parsed_date:
                    # Only add the date if it is explicitly mentioned in the text
                    dates.add(parsed_date.strftime("%Y-%m-%d"))
            except Exception as e:
                print(f"Error parsing date '{match}': {e}")

    # SpaCy DATE entity extraction
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            try:
                # Exclude non-date entities like Unix timestamps or irrelevant entities
                if '<t:' in ent.text:
                    continue
                parsed_date = parse(ent.text, settings={'RELATIVE_BASE': timestamp})
                if parsed_date:
                    dates.add(parsed_date.strftime("%Y-%m-%d"))
            except Exception as e:
                print(f"Error parsing date '{ent.text}': {e}")

    # Add first of the month if only month is mentioned
    month_matches = re.findall(MONTH_NAME_PATTERN, text, re.IGNORECASE)
    for month in month_matches:
        try:
            month_date = parse(f"1 {month} {timestamp.year}", settings={'RELATIVE_BASE': timestamp})
            if month_date:
                dates.add(month_date.strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"Error parsing month '{month}': {e}")

    return sorted(dates)


def extract_urls(text):
    """
    Extract unique URLs from text, including bare URLs without 'http://' or 'https://'.
    """
    # Enhanced regex to match both full and bare URLs
    url_pattern = r"""
        (?:http[s]?://)?               # Optional http:// or https://
        (?:www\.)?                     # Optional www.
        [a-zA-Z0-9.-]+                 # Domain name
        \.[a-zA-Z]{2,10}               # Top-level domain (e.g., .com, .xyz)
        (?:/[^\s]*)?                   # Optional path
    """
    urls = re.findall(url_pattern, text, re.VERBOSE | re.IGNORECASE)  # Enable verbose and case-insensitive matching
    return list(set(urls))  # Remove duplicates


def extract_tickers(text):
    """
    Extract all unique words with a leading dollar sign, excluding numbers.
    Normalize tickers to uppercase to avoid duplicates like $Bubble and $bubble.
    """
    if not text or pd.isna(text):
        return ""
    
    # Match tickers starting with a dollar sign and followed by letters/word characters
    tickers = re.findall(r"\$[a-zA-Z]+\w*", text)
    
    # Normalize to uppercase and remove duplicates
    unique_tickers = list(set(ticker.upper() for ticker in tickers))
    
    # Sort the tickers alphabetically and return as a single string
    return " ".join(sorted(unique_tickers))


def generate_title(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences[0] if sentences else text  # Use the first sentence as the summary

# Function to extract locations (GPE - Geo-political entities) - could be useful later on for IRL events but needs to be fine-tuned
# def extract_locations(text):
#    doc = nlp(text)
#    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]

class CustomTokenizer:
    def to_sentences(self, text):
        # Split text into sentences using a basic regex
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def to_words(self, sentence):
        # Split sentence into words using whitespace
        return sentence.split()

def generate_summary(text, sentence_count=3):
    # Use the custom tokenizer
    parser = PlaintextParser.from_string(text, CustomTokenizer())
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join([str(sentence) for sentence in summary])