"""
generate_data.py
-----------------
Generates a synthetic financial transactions dataset that mimics a company's
general ledger / expense feed. Intentionally seeds realistic audit anomalies
(round-number bias, just-under-approval-limit transactions, weekend/after-hours
postings, duplicate entries, missing approvals, out-of-sequence invoices) so
the downstream audit-analytics scripts have real patterns to detect.

Run: python3 generate_data.py
Output: financial_transactions.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_TRANSACTIONS = 6000

DEPARTMENTS = ["Procurement", "Marketing", "IT", "Operations", "HR", "Finance", "Sales"]
VENDORS = [f"Vendor_{i:03d}" for i in range(1, 61)]
APPROVERS = [f"Approver_{i:02d}" for i in range(1, 16)]
CATEGORIES = ["Travel", "Supplies", "Consulting", "Software", "Equipment", "Utilities", "Misc"]

# Each department has an approval limit above which a transaction needs
# secondary sign-off. Used later to flag "just under the limit" behavior.
APPROVAL_LIMITS = {
    "Procurement": 50000,
    "Marketing": 25000,
    "IT": 40000,
    "Operations": 30000,
    "HR": 15000,
    "Finance": 60000,
    "Sales": 20000,
}

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days


def random_datetime(weekday_only: bool = True):
    dt = start_date + timedelta(days=np.random.randint(0, date_range_days))
    if weekday_only:
        # Redraw until we land on a Mon-Fri date; normal business postings
        # should overwhelmingly occur on weekdays.
        while dt.weekday() >= 5:
            dt = start_date + timedelta(days=np.random.randint(0, date_range_days))
    hour = np.random.choice(range(8, 19), p=_business_hour_probs())
    minute = np.random.randint(0, 60)
    return dt.replace(hour=hour, minute=minute)


def random_weekend_datetime():
    dt = start_date + timedelta(days=np.random.randint(0, date_range_days))
    while dt.weekday() < 5:
        dt = start_date + timedelta(days=np.random.randint(0, date_range_days))
    hour = np.random.randint(0, 24)
    minute = np.random.randint(0, 60)
    return dt.replace(hour=hour, minute=minute)


def _business_hour_probs():
    hours = list(range(8, 19))  # 8am - 6pm
    weights = np.array([2, 4, 6, 8, 6, 3, 5, 8, 7, 5, 3])  # rough workday curve
    return weights / weights.sum()


def benford_amount():
    """
    Draw an amount whose leading digit roughly follows Benford's Law,
    which is the naturally-occurring pattern in real, untampered
    financial data. A minority of amounts are deliberately generated
    OUTSIDE this pattern later to simulate manipulated/round-number entries.
    """
    magnitude = np.random.choice([2, 3, 4, 5], p=[0.25, 0.40, 0.25, 0.10])
    base = 10 ** (magnitude - 1)
    # log-uniform draw within the magnitude naturally approximates Benford
    value = base * (10 ** np.random.uniform(0, 1))
    return round(value, 2)


rows = []

for i in range(1, N_TRANSACTIONS + 1):
    dept = np.random.choice(DEPARTMENTS)
    limit = APPROVAL_LIMITS[dept]
    dt = random_datetime()

    amount = benford_amount()

    # --- Seed anomaly patterns (roughly 12% of records) ---
    anomaly_roll = np.random.rand()

    if anomaly_roll < 0.04:
        # Just-under-the-approval-limit ("structuring") pattern
        amount = round(limit * np.random.uniform(0.90, 0.995), 2)
    elif anomaly_roll < 0.08:
        # Round-number bias (common sign of estimated/fabricated entries)
        amount = float(np.random.choice([1000, 2500, 5000, 7500, 10000, 15000, 20000]))
    elif anomaly_roll < 0.10:
        # After-hours / weekend posting
        if np.random.rand() < 0.5:
            dt = random_weekend_datetime()
        else:
            dt = dt.replace(hour=np.random.choice([21, 22, 23, 0, 1]))
    elif anomaly_roll < 0.115:
        # Negative amount (credit memo miscoded as expense, or data entry error)
        amount = -abs(round(np.random.uniform(50, 5000), 2))

    approver = np.random.choice(APPROVERS)
    # ~2% of transactions missing approver entirely
    if np.random.rand() < 0.02:
        approver = None

    rows.append({
        "transaction_id": f"TXN-{i:06d}",
        "date": dt.strftime("%Y-%m-%d"),
        "posting_time": dt.strftime("%H:%M"),
        "day_of_week": dt.strftime("%A"),
        "department": dept,
        "vendor": np.random.choice(VENDORS),
        "category": np.random.choice(CATEGORIES),
        "amount": amount,
        "approval_limit": limit,
        "approver": approver,
    })

df = pd.DataFrame(rows)

# Assign invoice numbers in true chronological order so they are
# sequential by date, then deliberately inject a small number of
# genuine backward jumps (~2% of rows) to simulate real-world
# invoice-sequence exceptions worth flagging.
df = df.sort_values("date").reset_index(drop=True)
invoice_numbers = list(range(100000, 100000 + len(df)))

n_jumps = int(len(df) * 0.02)
jump_positions = np.random.choice(range(5, len(df)), size=n_jumps, replace=False)
for pos in jump_positions:
    invoice_numbers[pos] = invoice_numbers[pos - 3] - np.random.randint(1, 4)

df["invoice_number"] = [f"INV-{n}" for n in invoice_numbers]

# Inject ~1% exact duplicate transactions (same vendor/amount/date re-posted)
dup_sample = df.sample(frac=0.01, random_state=1).copy()
dup_sample["transaction_id"] = dup_sample["transaction_id"] + "-D"
df = pd.concat([df, dup_sample], ignore_index=True)

df.to_csv("financial_transactions.csv", index=False)
print(f"Generated {len(df)} transactions -> financial_transactions.csv")
