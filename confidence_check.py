import os
import re
import pandas as pd

def extract_confidence_from_md(md_path):
    """
    Extracts the numeric confidence value from the last line of a markdown file.
    Returns the value as a float (e.g., 100.0 for '100%'), or None if not found.
    """
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return None
        last_line = lines[-1].strip()
        match = re.search(r'(\d+(\.\d+)?)\s*%', last_line)
        if match:
            return float(match.group(1))
    return None

def collect_confidence_levels(doc_folder):
    """
    Scans all .md files in the given documentation folder, extracts the confidence level,
    and returns a pandas DataFrame with columns: 'file_name', 'confidence_level'.
    """
    records = []
    for fname in os.listdir(doc_folder):
        if fname.endswith('.md'):
            fpath = os.path.join(doc_folder, fname)
            confidence = extract_confidence_from_md(fpath)
            records.append({'file_name': fname, 'confidence_level': confidence})
    return pd.DataFrame(records)

# Example usage:
df = collect_confidence_levels('output\CalculatorCode\documentation')
df.to_csv('confidence_levels.csv', index=False)
