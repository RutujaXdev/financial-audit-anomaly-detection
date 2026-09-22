# Financial Transactions Audit & Anomaly Detection

A rule-based and statistical audit-analytics pipeline that ingests a
transaction ledger and flags exceptions the way a financial-statement
auditor would: completeness checks, Benford's Law testing, threshold-based
policy checks, and root-cause categorization.

## Pipeline

```
generate_data.py  -->  financial_transactions.csv
        |
        v
data_validation.py    -->  validation_flags.csv       (duplicates, missing approvals,
                                                         negative amounts, invoice
                                                         sequence breaks)
benford_analysis.py   -->  benford_results.csv,
                            benford_flagged_transactions.csv  (statistical outliers)
anomaly_detection.py  -->  anomaly_flags.csv           (just-under-limit, weekend/
                                                         after-hours, round numbers)
        |
        v
rca_tagging.py        -->  final_audit_exceptions.csv  (consolidated, root-cause tagged)
```

Run everything in one shot with `python3 main_audit_analysis.py`, or run
each script individually.

## Results on the included dataset (6,060 transactions)

| Check                         | Flagged |
|--------------------------------|--------:|
| Duplicate transactions          |     122 |
| Missing approver                |     110 |
| Negative amounts                |     121 |
| Out-of-sequence invoice numbers |     167 |
| Benford's Law outliers          |     993 |
| Just-under-approval-limit       |     287 |
| Weekend / after-hours postings  |     109 |
| Round-number amounts            |     246 |
| **Unique transactions flagged** | **1,886 (31%)** |

Benford's Law chi-square test: p < 0.05, meaning the amount distribution
deviates significantly enough from the expected pattern to warrant manual
review of the flagged population (this is a screening signal, not proof of
anything — say this in an interview, it's the technically correct framing).

## Resume bullets (ready to paste, using the real output numbers above)

```
Financial Transactions Audit & Anomaly Detection | Python, SQL, Power BI
– Accomplished exception-testing coverage across 6,000+ simulated ledger
  transactions, as measured by 1,886 flagged records (31%), by building a
  Python pipeline combining Benford's Law statistical testing with
  rule-based policy checks (approval-limit thresholds, posting-time
  analysis, round-number bias).
– Accomplished root-cause classification of every flagged exception, as
  measured by categorization into Data Entry Error, Policy Violation Risk,
  and Statistical Outlier buckets, by engineering a consolidation script
  that merges validation, statistical, and rule-based flag sources.
– Accomplished a client-ready exception dashboard, as measured by
  drill-down views by department, vendor, and root-cause category, by
  designing a Power BI report on top of the final audit exceptions output.
```

Pick 2 of these 3 for your resume (space is tight) — I'd keep bullets 1 and 2,
since they show both the technical build and the audit-specific judgment
(root-cause categorization) EY's JD is looking for.

## Step-by-step: what to actually do right now

1. **Create a public GitHub repo** — name it something like
   `financial-audit-anomaly-detection`.
2. **Upload these 6 files** to the repo root:
   `generate_data.py`, `data_validation.py`, `benford_analysis.py`,
   `anomaly_detection.py`, `rca_tagging.py`, `main_audit_analysis.py`,
   plus this `README.md`.
3. **Do NOT upload the CSV outputs** (`financial_transactions.csv`,
   `final_audit_exceptions.csv`, etc.) unless you want to — they're
   synthetic data, fine to include, but the code is what matters. If you
   do include them, add a one-line note in the README that the dataset is
   synthetically generated (`generate_data.py` creates it) — an EY
   reviewer who opens the repo will respect that transparency, and hiding
   it is a worse look if asked in an interview.
4. **Add the GitHub link** to your resume's Projects section using the
   bullets above.
5. **Before your interview** (do this later, not now): actually run
   `python3 main_audit_analysis.py` yourself once, open
   `final_audit_exceptions.csv`, and skim this README so you can talk
   through what Benford's Law means and why "just under the limit" is a
   red flag, in your own words. You don't need to be an expert — you need
   to be able to say what each check does and why an auditor would run it.
6. **Optional, if you have 20 extra minutes later:** open
   `financial_transactions.csv` and `final_audit_exceptions.csv` in Power
   BI, build a simple bar chart of exception count by `root_cause_category`
   and by `department`. A screenshot of that in your GitHub README makes
   the project look finished, not just a script.

## Honesty note for interviews

This is a **synthetic dataset with anomalies deliberately seeded in** —
say that plainly if asked ("I generated a synthetic ledger with known
anomaly patterns so I could validate that my detection logic actually
catches them"). That's a legitimate and common way to build/test an audit
analytics tool, and framing it that way is more credible than implying it's
real company data.
