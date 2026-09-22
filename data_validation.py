"""
data_validation.py
-------------------
Core data-quality / completeness checks applied to a transaction ledger
before any statistical audit testing is run. These are the checks an
auditor performs first: is the data even trustworthy and complete?

Checks performed:
  1. Exact duplicate transactions
  2. Missing approver / approval fields
  3. Negative transaction amounts
  4. Out-of-sequence invoice numbers (gaps or reversals in numbering)

Run standalone: python3 data_validation.py
Or import: from data_validation import run_validation_checks
"""

import pandas as pd
import re


def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    dup_cols = ["date", "vendor", "amount", "department"]
    dupes = df[df.duplicated(subset=dup_cols, keep=False)].copy()
    dupes["flag_reason"] = "Duplicate transaction"
    return dupes


def check_missing_approval(df: pd.DataFrame) -> pd.DataFrame:
    missing = df[df["approver"].isna()].copy()
    missing["flag_reason"] = "Missing approver"
    return missing


def check_negative_amounts(df: pd.DataFrame) -> pd.DataFrame:
    negative = df[df["amount"] < 0].copy()
    negative["flag_reason"] = "Negative amount"
    return negative


def _extract_invoice_num(inv: str) -> int:
    match = re.search(r"(\d+)", str(inv))
    return int(match.group(1)) if match else None


def check_invoice_sequence(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["invoice_num"] = tmp["invoice_number"].apply(_extract_invoice_num)
    # kind="stable" is required here: same-day transactions must keep their
    # original relative order, or the default quicksort will reorder ties
    # and create false sequence-break flags.
    tmp = tmp.sort_values("date", kind="stable")
    tmp["prev_invoice_num"] = tmp["invoice_num"].shift(1)
    tmp["seq_delta"] = tmp["invoice_num"] - tmp["prev_invoice_num"]
    # Flag any backward jump (should generally increase over time)
    out_of_seq = tmp[tmp["seq_delta"] < 0].copy()
    out_of_seq["flag_reason"] = "Out-of-sequence invoice number"
    return out_of_seq.drop(columns=["invoice_num", "prev_invoice_num", "seq_delta"])


def run_validation_checks(csv_path: str = "financial_transactions.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    results = pd.concat([
        check_duplicates(df),
        check_missing_approval(df),
        check_negative_amounts(df),
        check_invoice_sequence(df),
    ], ignore_index=True)

    results.to_csv("validation_flags.csv", index=False)

    print("=== Data Validation Summary ===")
    print(f"Total transactions checked : {len(df)}")
    print(f"Duplicate transactions      : {len(check_duplicates(df))}")
    print(f"Missing approver            : {len(check_missing_approval(df))}")
    print(f"Negative amounts            : {len(check_negative_amounts(df))}")
    print(f"Out-of-sequence invoices    : {len(check_invoice_sequence(df))}")
    print(f"Total flagged rows (raw)    : {len(results)}")
    print("Saved -> validation_flags.csv")

    return results


if __name__ == "__main__":
    run_validation_checks()
