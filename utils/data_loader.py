import pandas as pd

def normalize_outcome(value: str) -> str:
    if not isinstance(value, str):
        return "other"
    v = value.strip().lower()
    mapping = {
        "busy":"busy",
        "no_answer":"no_answer",
        "no answer":"no_answer",
        "failed":"failed",
        "unknown":"unknown",
        "follow-up":"follow-up",
        "follow up":"follow-up",
        "assign to live agent":"agent_assigned",
        "assigned to agent":"agent_assigned",
        "agent_assigned":"agent_assigned",
        "agent assigned":"agent_assigned",
        "converted":"converted",
        "lost":"lost"
    }
    return mapping.get(v, v)

def load_and_clean_data(files):
    dfs = []
    for f in files:
        if f.name.endswith(".csv"):
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True).drop_duplicates()

    # Normalize columns
    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]

    # Date parsing
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.NaT

    if "outcome" in df.columns:
        df["outcome_norm"] = df["outcome"].astype(str).apply(normalize_outcome)
    else:
        df["outcome_norm"] = "other"

    if "mobile_number" in df.columns:
        df["mobile_number"] = df["mobile_number"].astype(str)
    else:
        df["mobile_number"] = "unknown"

    if "name" not in df.columns:
        df["name"] = ""

    if "notes" not in df.columns:
        df["notes"] = ""

    if "duration" not in df.columns:
        df["duration"] = 0

    return df
