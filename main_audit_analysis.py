"""
main_audit_analysis.py
------------------------
Runs the full audit analytics pipeline end to end, in order:

  1. generate_data.py       -> financial_transactions.csv
  2. data_validation.py     -> validation_flags.csv
  3. benford_analysis.py    -> benford_results.csv, benford_flagged_transactions.csv
  4. anomaly_detection.py   -> anomaly_flags.csv
  5. rca_tagging.py         -> final_audit_exceptions.csv (the Power BI-ready output)

Run: python3 main_audit_analysis.py
"""

import subprocess
import sys

STEPS = [
    ("Generating synthetic transaction data", "generate_data.py"),
    ("Running data validation checks", "data_validation.py"),
    ("Running Benford's Law analysis", "benford_analysis.py"),
    ("Running rule-based anomaly detection", "anomaly_detection.py"),
    ("Building final audit exceptions report", "rca_tagging.py"),
]


def main():
    for label, script in STEPS:
        print(f"\n{'=' * 60}\nSTEP: {label} ({script})\n{'=' * 60}")
        result = subprocess.run([sys.executable, script], capture_output=False)
        if result.returncode != 0:
            print(f"\nPipeline stopped -- {script} exited with an error.")
            sys.exit(1)

    print(f"\n{'=' * 60}")
    print("Pipeline complete. Final output: final_audit_exceptions.csv")
    print("Import financial_transactions.csv + final_audit_exceptions.csv into Power BI")
    print("to build the exception-rate dashboard.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
