"""
rca_tagging.py
----------------
Consolidates output from data_validation.py, benford_analysis.py, and
anomaly_detection.py into a single exceptions report, then assigns each
flagged transaction a root-cause category -- the final step in an audit
analytics workflow, turning raw flags into something a reviewer/manager
can act on.

Root cause categories:
  - Data Entry Error      (duplicates, missing approver, negative amounts)
  - Policy Violation Risk (just-under-limit, weekend/after-hours)
  - Statistical Outlier   (Benford's Law flags, round-number bias)

Run: python3 rca_tagging.py
Output: final_audit_exceptions.csv
"""

import pandas as pd

REASON_TO_ROOT_CAUSE = {
    "Duplicate transaction": "Data Entry Error",
    "Missing approver": "Data Entry Error",
    "Negative amount": "Data Entry Error",
    "Out-of-sequence invoice number": "Data Entry Error",
    "Just under approval limit": "Policy Violation Risk",
    "Weekend or after-hours posting": "Policy Violation Risk",
    "Benford's Law outlier (over-represented leading digit)": "Statistical Outlier",
    "Round-number amount": "Statistical Outlier",
}


def build_final_report() -> pd.DataFrame:
    frames = []
    for path in ["validation_flags.csv", "anomaly_flags.csv", "benford_flagged_transactions.csv"]:
        try:
            frames.append(pd.read_csv(path))
        except FileNotFoundError:
            print(f"Warning: {path} not found -- run its script first. Skipping.")

    if not frames:
        raise RuntimeError("No flag files found. Run data_validation.py, anomaly_detection.py, "
                            "and benford_analysis.py first.")

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined["root_cause_category"] = combined["flag_reason"].map(REASON_TO_ROOT_CAUSE)

    # A transaction can trip more than one rule -- keep one row per
    # (transaction_id, flag_reason) but preserve every distinct reason.
    combined = combined.drop_duplicates(subset=["transaction_id", "flag_reason"])

    combined.to_csv("final_audit_exceptions.csv", index=False)

    total_txns = combined["transaction_id"].nunique()
    print("=== Final Audit Exceptions Report ===")
    print(f"Unique flagged transactions : {total_txns}")
    print("\nBy root cause category:")
    print(combined.groupby("root_cause_category")["transaction_id"].nunique().to_string())
    print("\nBy flag reason:")
    print(combined.groupby("flag_reason")["transaction_id"].nunique().to_string())
    print("\nSaved -> final_audit_exceptions.csv")

    return combined


if __name__ == "__main__":
    build_final_report()
