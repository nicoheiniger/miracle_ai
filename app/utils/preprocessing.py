import re
import emoji
import datetime
import pandas as pd


def preprocess_content(text):
    """
    Clean and normalize the text by:
    - Fixing character encoding issues (e.g., â€™ to ’).
    - Removing/Replacing Discord custom emojis.
    - Removing/Replacing standard emojis.
    - Removing Discord mentions (e.g., <@123456789>, <@&123456789>).
    - Replacing Discord channel mentions with placeholders.
    - Replacing Discord timestamps with readable date/time.
    - Removing special formatting (e.g., **bold**, __italic__).
    - Removing Twitter mentions (e.g. [@username])
    - Removing footnotes and references (e.g. [[1]])
    - Removing all asterisks (leading, trailing and in text)
    - Removing all underscores (that are NOT inside a URL)
    - Normalizing whitespace.
    """
    if not text or pd.isna(text):
        return ""

    # Fix encoding issues
    def fix_encoding_issues(text):
        try:
            # Attempt to decode encoding issues
            text = text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

        # Handle known corrupted characters manually
        replacements = {
            "â€™": "’",
            "Â·": "·",
            "â€“": "–",
            "â€”": "—",
            "â€œ": "“",
            "â€": "”",
            "Â": "",  # Remove stray Â characters
        }

        for bad_char, good_char in replacements.items():
            text = text.replace(bad_char, good_char)

        return text

    text = fix_encoding_issues(text)

    # Remove custom Discord emojis
    text = re.sub(r"<a?:(\w+):\d+>", "", text)  # Remove custom Discord emojis

    # Remove standard emojis
    text = emoji.replace_emoji(text, replace="")  # Remove standard emojis

    # Replace custom Discord emojis with their names
    # text = re.sub(r"<a?:(\w+):\d+>", r"\1", text)  # Replace with emoji names

    # Replace standard emojis with descriptive names
    # text = emoji.demojize(text, delimiters=(" ", " "))  # Convert emojis to descriptive text

    # Remove Discord mentions (e.g., <@123456789>, <@&123456789>, @everyone, @here)
    text = re.sub(r"<@[&]?\d+>|@everyone|@here", "", text)  # Remove user, role, and group mentions

    # Replace Discord channel mentions with a placeholder
    text = re.sub(r"<#\d+>", "[CHANNEL]", text)  # Replace channel mentions with [CHANNEL] - can be changed to link to channel if server id is available

    # Replace Discord timestamps with readable dates
    def replace_discord_timestamp(text):
        def replace_timestamp(match):
            try:
                unix_timestamp = int(match.group(1))
                return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M UTC')
            except ValueError:
                return match.group(0)  # Keep the original if conversion fails

        # Update regex to ensure all dates are captured
        return re.sub(r"<t:(\d+)(:[a-zA-Z])?>", replace_timestamp, text)

    text = replace_discord_timestamp(text)
   
    # Remove mentions like [@username]
    text = re.sub(r'\[@\w+\]', '', text)
    
    # Remove references like [[1]]
    text = re.sub(r'\[\[\d+\]\]', '', text)

       # Remove asterisks (leading, trailing, or standalone)
    text = re.sub(r"\*", "", text)

    # Remove standalone underscores (not part of words or URLs)
    text = re.sub(r"(?<!\w)_+(?!\w)", " ", text)

    # Normalize whitespace and strip trailing spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def remove_urls(text):
    """
    Remove all URLs (including bare URLs) from the text.
    """
    if not text or pd.isna(text):
        return ""

    # Enhanced regex to match both full and bare URLs
    url_pattern = r"""
        (?:http[s]?://)?               # Optional http:// or https://
        (?:www\.)?                     # Optional www.
        [a-zA-Z0-9.-]+                 # Domain name
        \.[a-zA-Z]{2,10}               # Top-level domain (e.g., .com, .xyz)
        (?:/[^\s]*)?                   # Optional path
    """

    # Replace matched URLs with an empty string
    clean_text = re.sub(url_pattern, "", text, flags=re.VERBOSE | re.IGNORECASE)
    return re.sub(r"\s+", " ", clean_text).strip()  # Normalize whitespace after removal

