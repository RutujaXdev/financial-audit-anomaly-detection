"""
benford_analysis.py
--------------------
Applies Benford's Law to the leading digits of transaction amounts.

Benford's Law states that in most naturally-occurring numerical datasets,
the digit 1 appears as the leading digit ~30% of the time, 2 appears ~17.6%
of the time, and so on -- decreasing logarithmically through 9. Real,
untampered financial data tends to follow this distribution; manipulated,
estimated, or fabricated figures tend to deviate from it. This is a
genuine, widely-used forensic/audit analytics technique (used by the IRS,
SEC, and external auditors) for flagging populations of transactions that
merit closer manual review -- it does NOT prove fraud on its own.

Run standalone: python3 benford_analysis.py
Or import: from benford_analysis import run_benford_analysis
"""

import numpy as np
import pandas as pd
from scipy.stats import chisquare

# Expected Benford's Law distribution for leading digits 1-9
BENFORD_EXPECTED = {d: np.log10(1 + 1 / d) for d in range(1, 10)}


def leading_digit(amount: float):
    amount = abs(amount)
    if amount == 0:
        return None
    s = f"{amount:.10f}".lstrip("0").lstrip(".").lstrip("0")
    for ch in s:
        if ch.isdigit() and ch != "0":
            return int(ch)
    return None


def run_benford_analysis(csv_path: str = "financial_transactions.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["leading_digit"] = df["amount"].apply(leading_digit)
    df = df.dropna(subset=["leading_digit"])

    observed_counts = df["leading_digit"].value_counts().sort_index()
    total = observed_counts.sum()

    summary_rows = []
    for digit in range(1, 10):
        observed = observed_counts.get(digit, 0)
        observed_pct = observed / total
        expected_pct = BENFORD_EXPECTED[digit]
        deviation_pct = (observed_pct - expected_pct) / expected_pct * 100
        summary_rows.append({
            "leading_digit": digit,
            "observed_count": observed,
            "observed_pct": round(observed_pct * 100, 2),
            "expected_pct": round(expected_pct * 100, 2),
            "deviation_pct": round(deviation_pct, 1),
        })

    summary = pd.DataFrame(summary_rows)

    expected_counts = np.array([BENFORD_EXPECTED[d] * total for d in range(1, 10)])
    observed_arr = np.array([observed_counts.get(d, 0) for d in range(1, 10)])
    chi2_stat, p_value = chisquare(f_obs=observed_arr, f_exp=expected_counts)

    summary.to_csv("benford_results.csv", index=False)

    # Flag individual transactions whose leading digit is one of the
    # most over-represented digits vs. Benford's expectation (top deviation)
    worst_digits = summary.sort_values("deviation_pct", ascending=False).head(2)["leading_digit"].tolist()
    flagged = df[df["leading_digit"].isin(worst_digits)].copy()
    flagged["flag_reason"] = "Benford's Law outlier (over-represented leading digit)"
    flagged.to_csv("benford_flagged_transactions.csv", index=False)

    print("=== Benford's Law Analysis ===")
    print(summary.to_string(index=False))
    print(f"\nChi-square statistic : {chi2_stat:.2f}")
    print(f"P-value              : {p_value:.4f}")
    print("Interpretation       :", "Distribution deviates significantly from Benford's Law (p < 0.05) -- flag for review"
          if p_value < 0.05 else "Distribution is broadly consistent with Benford's Law")
    print(f"Transactions flagged  : {len(flagged)} (leading digits {worst_digits})")
    print("Saved -> benford_results.csv, benford_flagged_transactions.csv")

    return flagged


if __name__ == "__main__":
    run_benford_analysis()
