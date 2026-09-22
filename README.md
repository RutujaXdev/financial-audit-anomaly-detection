# Financial Transactions Audit & Anomaly Detection

A rule-based and statistical audit-analytics pipeline that ingests a transaction ledger and flags exceptions the way a financial-statement auditor would: completeness checks, Benford's Law testing, threshold-based policy checks, and root-cause categorization.

## Pipeline

generate_data.py --> financial_transactions.csv
then
data_validation.py --> validation_flags.csv (duplicates, missing approvals, negative amounts, invoice sequence breaks)
benford_analysis.py --> benford_results.csv, benford_flagged_transactions.csv (statistical outliers)
anomaly_detection.py --> anomaly_flags.csv (just-under-limit, weekend/after-hours, round numbers)
then
rca_tagging.py --> final_audit_exceptions.csv (consolidated, root-cause tagged)

Run everything in one shot with `python3 main_audit_analysis.py`, or run each script individually.

## Results on the included dataset (6,060 transactions)

| Check | Flagged |
|---|---:|
| Duplicate transactions | 122 |
| Missing approver | 110 |
| Negative amounts | 121 |
| Out-of-sequence invoice numbers | 167 |
| Benford's Law outliers | 993 |
| Just-under-approval-limit | 287 |
| Weekend / after-hours postings | 109 |
| Round-number amounts | 246 |
| **Unique transactions flagged** | **1,886 (31%)** |

Benford's Law chi-square test: p < 0.05, meaning the amount distribution deviates significantly enough from the expected pattern to warrant manual review of the flagged population.

## Key Skills Demonstrated

Python, SQL, Power BI, statistical testing (Benford's Law), rule-based exception detection, root-cause analysis, audit analytics, data validation and quality checks.
<img width="1162" height="671" alt="image" src="https://github.com/user-attachments/assets/60dbfc66-9470-4a2b-a248-016473aa9727" />

