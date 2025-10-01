import pandas as pd
import re

# Define "uncontacted" outcomes
UNCONTACTED = {"busy", "no_answer", "failed", "unknown"}

# -----------------------
# Call Level Funnel
# -----------------------
def call_level_funnel(df: pd.DataFrame):
    total = len(df)
    uncontacted = df["outcome_norm"].isin(UNCONTACTED).sum()
    contacted = total - uncontacted
    return pd.DataFrame({
        "Metric": ["Total Dials", "Uncontacted Dials", "Contacted Dials"],
        "Count": [total, uncontacted, contacted],
        "% of Total": [f"{round(x/total*100,2)}%" for x in [total, uncontacted, contacted]]
    })

# -----------------------
# Initial Lead-Level Funnel
# -----------------------
def initial_status(group):
    outs = set(group["outcome_norm"])
    if "converted" in outs: return "converted"
    if "lost" in outs: return "lost"
    if "agent_assigned" in outs: return "agent_assigned"
    if "follow-up" in outs: return "follow-up"
    if all(o in UNCONTACTED for o in outs): return "uncontacted"
    return "other"

def initial_lead_funnel(df: pd.DataFrame):
    leads = df.groupby("mobile_number").apply(initial_status)
    counts = leads.value_counts().reset_index()
    counts.columns = ["Lead Status", "Count"]
    total = len(leads)
    counts["% of Unique Leads"] = counts["Count"].apply(lambda x: f"{round(x/total*100,2)}%")
    counts = pd.concat([pd.DataFrame({
        "Lead Status": ["Unique Leads"],
        "Count": [total],
        "% of Unique Leads": ["100%"]
    }), counts])
    return counts

# -----------------------
# Lost Lead Breakdown
# -----------------------
def lost_reason(text):
    t = str(text).lower()
    if re.search(r"wrong\s*number", t): return "Wrong Number"
    if re.search(r"not\s*interested|no interest|refuse", t): return "Not Interested"
    if re.search(r"already.*customer|enrolled|student", t): return "Already Customer"
    if re.search(r"price|cost|fee|expensive|budget", t): return "Price Concern"
    if re.search(r"call.*later|busy.*now|callback", t): return "Call Later/Timing"
    if re.search(r"location|eligibility|coverage", t): return "Location/Eligibility"
    if re.search(r"switch|port|network", t): return "Number/Network Issue"
    return "Other"

def lost_lead_breakdown(df: pd.DataFrame):
    lost_leads = df[df["outcome_norm"]=="lost"]
    if lost_leads.empty: return pd.DataFrame()
    lost_leads["Lost Reason"] = lost_leads["notes"].apply(lost_reason)
    lead_reason = lost_leads.groupby("mobile_number")["Lost Reason"].agg(
        lambda s: s.mode().iat[0] if not s.mode().empty else "Other"
    )
    table = lead_reason.value_counts().reset_index()
    table.columns = ["Lost Reason", "Count"]
    total = table["Count"].sum()
    table["% of Lost Leads"] = table["Count"].apply(lambda x: f"{round(x/total*100,2)}%")
    return table

# -----------------------
# Deep Dive Profiles
# -----------------------
def deep_dive_profiles(df: pd.DataFrame, reason="Not Interested"):
    lost_leads = df[df["outcome_norm"]=="lost"].copy()
    lost_leads["Lost Reason"] = lost_leads["notes"].apply(lost_reason)
    leads = lost_leads[lost_leads["Lost Reason"]==reason]["mobile_number"].unique()
    subset = df[df["mobile_number"].isin(leads)]
    if subset.empty: return pd.DataFrame()
    subset["is_contacted"] = ~subset["outcome_norm"].isin(UNCONTACTED)
    prof = subset.groupby("bot").agg(
        dials=("mobile_number", "count"),
        leads=("mobile_number", "nunique"),
        contact_rate=("is_contacted", lambda s: f"{round(s.mean()*100,2)}%"),
        avg_duration=("duration", "mean")
    ).reset_index()
    prof["avg_duration"] = prof["avg_duration"].round(1)
    return prof

# -----------------------
# Time-Based Impact
# -----------------------
def time_based_impact(df: pd.DataFrame):
    df["is_contacted"] = ~df["outcome_norm"].isin(UNCONTACTED)
    df["is_converted"] = df["outcome_norm"].eq("converted")
    df["hour"] = df["date"].dt.hour
    df["dow"] = df["date"].dt.day_name()

    dow = df.groupby("dow").agg(
        dials=("mobile_number","count"),
        contact_rate=("is_contacted", lambda s:f"{round(s.mean()*100,2)}%"),
        conversion_rate=("is_converted", lambda s:f"{round(s.mean()*100,2)}%")
    ).reset_index()

    hour = df.groupby("hour").agg(
        dials=("mobile_number","count"),
        contact_rate=("is_contacted", lambda s:f"{round(s.mean()*100,2)}%"),
        conversion_rate=("is_converted", lambda s:f"{round(s.mean()*100,2)}%")
    ).reset_index()

    return dow.sort_values("dials",ascending=False), hour.sort_values("dials",ascending=False)

# -----------------------
# Duration Analysis
# -----------------------
def duration_analysis(df: pd.DataFrame):
    return df[df["outcome_norm"].isin(["converted","lost"])]\
        .groupby("outcome_norm")["duration"].mean()\
        .round(2).reset_index()\
        .rename(columns={"outcome_norm":"Outcome","duration":"Avg Duration (sec)"})

# -----------------------
# Gender Analysis
# -----------------------
def infer_gender(name):
    if not isinstance(name,str) or not name.strip(): return "Unknown"
    first = name.strip().split()[0].lower()
    if re.search(r"(a|i|ee|ita|ika|shi|ni|thi)$", first): return "Female?"
    if re.search(r"(k|n|t|v|r|esh|an|it|al|esh)$", first): return "Male?"
    return "Unknown"

def gender_analysis(df: pd.DataFrame):
    leads = df.groupby("mobile_number").agg(
        gender=("name", lambda s: infer_gender(s.mode().iat[0] if not s.mode().empty else "")),
        converted=("outcome_norm", lambda s: "converted" in set(s))
    ).reset_index()
    table = leads.groupby("gender").agg(
        leads=("mobile_number","nunique"),
        conversion_rate=("converted", lambda s: f"{round(s.mean()*100,2)}%")
    ).reset_index()
    return table

# -----------------------
# Final Lead Funnel (User-defined priority)
# -----------------------
def final_status(group):
    outs = set(group["outcome_norm"])
    if "converted" in outs: return "converted"
    if "lost" in outs: return "lost"
    if "agent_assigned" in outs: return "agent_assigned"
    if "follow-up" in outs: return "follow-up"
    if "busy" in outs: return "busy"
    if "no_answer" in outs: return "no_answer"
    return "uncontacted"

def final_lead_funnel(df: pd.DataFrame):
    leads = df.groupby("mobile_number").apply(final_status)
    counts = leads.value_counts().reset_index()
    counts.columns = ["Lead Status", "Count"]
    total = len(leads)
    counts["% of Total Unique Leads"] = counts["Count"].apply(lambda x:f"{round(x/total*100,2)}%")
    return counts
