import pandas as pd
import re
import emoji

# Handle Discord Data
df_dc = pd.read_csv("data\combined_messages_20241105_191237(1).csv")
df_dc = df_dc[["Channel_Name", "Content", "Timestamp", "Embed_Title", "Embed_Description"]]
df_dc.rename(columns={"Content": "content1", "Timestamp": "timestamp", "Embed_Title": "content2", "Embed_Description": "content3"}, inplace=True)
df_dc['source'] = "discord"
df_dc['collection'] = df_dc['Channel_Name'].str.split('_').str[0]
df_dc = df_dc[["collection", "content1", "content2", "content3", "timestamp", "source"]]
df_dc['timestamp'] = pd.to_datetime(df_dc['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
df_dc['timestamp'] = pd.to_datetime(df_dc['timestamp'])

# Handle Twitter Data
df_x = pd.read_csv("data\dataset_twitter-scraper_2024-11-05_20-23-41-269(1).csv")
df_x = df_x[["username", "text", "timestamp"]]
df_x["username"] = df_x['username'].str.lstrip('@')
df_x.rename(columns={"username": "collection", "text": "content1"}, inplace=True)
df_x["content2"] = ""
df_x["content3"] = ""
df_x["source"] = "twitter"
df_x['timestamp'] = pd.to_datetime(df_x['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
df_x['timestamp'] = pd.to_datetime(df_x['timestamp'])
df_x = df_x[["collection", "content1", "content2", "content3", "timestamp", "source"]]

# Combine Data
df = pd.concat([df_dc, df_x], ignore_index=True)

# normalize text
def preprocess_content(text):
    if pd.isna(text):
        return ""
    # Remove Discord mentions like <@...> or <@&...>
    text = re.sub(r"<@[&]?\d+>", "", text)
    # Remove special formatting (e.g., **, __)
    text = re.sub(r"[\*\_]+", " ", text)
    # Replace emojis with descriptive names
    text = emoji.demojize(text, delimiters=(" ", " "))
    # Normalize whitespace and remove trailing spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Apply preprocessing to content columns
for col in ["content1", "content2", "content3"]:
    df[col] = df[col].apply(preprocess_content)

# Export
print(df.info())
# df.to_csv('output\combined_dataframe.csv', index=False)