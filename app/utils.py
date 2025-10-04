from datetime import datetime, timedelta
import re

def normalize_date_phrase(phrase: str):
    phrase = phrase.lower().strip()
    if "yesterday" in phrase:
        return (datetime.now(datetime.timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    m = re.search(r"\d{4}-\d{2}-\d{2}", phrase)
    if m:
        return m.group(0)
    return None
