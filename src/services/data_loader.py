import pandas as pd

def load_from_url(url: str):
    if url.endswith(".csv"):
        return pd.read_csv(url)
    elif url.endswith(".json"):
        return pd.read_json(url)
    else:
        raise ValueError("Only CSV or JSON supported")

def load_from_file(path: str):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith(".json"):
        return pd.read_json(path)
    else:
        raise ValueError("Only CSV or JSON supported")
