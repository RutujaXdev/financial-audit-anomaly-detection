"""
anomaly_detection.py
----------------------
Rule-based exception testing -- the kind of deterministic checks an audit
analytics team runs alongside statistical tests like Benford's Law.

Rules implemented:
  1. "Just under the limit"  -- amounts sitting suspiciously close (within 5%)
     below a department's approval threshold, a classic sign of transaction
     structuring to avoid secondary sign-off.
  2. Weekend / after-hours postings -- transactions posted outside normal
     business hours or on a weekend.
  3. Round-number bias -- amounts that are suspiciously "clean" (e.g. exactly
     1000, 2500, 5000), which can indicate estimated rather than actual figures.

Run standalone: python3 anomaly_detection.py
Or import: from anomaly_detection import run_anomaly_detection
"""

import pandas as pd


def flag_just_under_limit(df: pd.DataFrame, threshold_pct: float = 0.90) -> pd.DataFrame:
    mask = (df["amount"] > 0) & (df["amount"] >= df["approval_limit"] * threshold_pct) & \
           (df["amount"] < df["approval_limit"])
    flagged = df[mask].copy()
    flagged["flag_reason"] = "Just under approval limit"
    return flagged


def flag_weekend_after_hours(df: pd.DataFrame) -> pd.DataFrame:
    weekend = df["day_of_week"].isin(["Saturday", "Sunday"])
    hour = pd.to_datetime(df["posting_time"], format="%H:%M").dt.hour
    after_hours = (hour >= 20) | (hour < 7)
    flagged = df[weekend | after_hours].copy()
    flagged["flag_reason"] = "Weekend or after-hours posting"
    return flagged


def flag_round_numbers(df: pd.DataFrame) -> pd.DataFrame:
    round_mask = (df["amount"] % 100 == 0) & (df["amount"] != 0)
    flagged = df[round_mask].copy()
    flagged["flag_reason"] = "Round-number amount"
    return flagged


def run_anomaly_detection(csv_path: str = "financial_transactions.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    results = pd.concat([
        flag_just_under_limit(df),
        flag_weekend_after_hours(df),
        flag_round_numbers(df),
    ], ignore_index=True)

    results.to_csv("anomaly_flags.csv", index=False)

    print("=== Rule-Based Anomaly Detection Summary ===")
    print(f"Just-under-limit transactions : {len(flag_just_under_limit(df))}")
    print(f"Weekend/after-hours postings   : {len(flag_weekend_after_hours(df))}")
    print(f"Round-number amounts           : {len(flag_round_numbers(df))}")
    print(f"Total flagged rows (raw)       : {len(results)}")
    print("Saved -> anomaly_flags.csv")

    return results


if __name__ == "__main__":
    run_anomaly_detection()
