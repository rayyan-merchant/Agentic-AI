SaafHawa — Agentic AI Assignment Beta, Question 1
Student roll number: 23K-0073

SUBMISSION FILES
- SaafHawa.pdf: final Q1 report, including model table, calculations, plots,
  GPU configuration screenshot, and live verification summary.
- SaafHawa.xlsx: formula-based calculation workbook.
- Assignment_Beta_Question_no_1_23K-0073.ipynb: executed calculation notebook.
- tool_latency.csv: unmodified two-day raw timing log (November 14–15, 2026).
- AI_USE.md: AI-use declaration.

SUPPORTING MATERIAL
- master_model_matrix.csv and DIRECT_HOST_COMPARISON.csv: source-backed model evidence.
- TIMING_VALIDATION.md: summary and qualification checks.
- live_test_results/: six paid-model smoke-trial rows, report and PM10 coverage checks.
- evidence/: original configuration screenshot, route evidence and API response logs.
- AUDIT.md and EVIDENCE_UPDATE_2026-11-15.md: limitations and verification notes.
- calculations.py, plots.py, models.psv: necessary imports and inputs for the notebook.
- collect.py, live_path_probe.py: timing methods and reproduction scripts; they require
  API keys in environment variables and valid network access for new requests.

REPRODUCING THE NOTEBOOK
From this extracted folder, install Python plus Jupyter and Pillow, open the
.ipynb file, and choose Run All. Keep calculations.py, plots.py, models.psv,
tool_latency.csv and evidence/ at the same paths because the notebook imports them.

The live English tests used 260-token input prompts, not the modeled 6,000-token
optimized workload. No workload-matched 9-second guarantee is claimed.
