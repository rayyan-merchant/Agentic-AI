# Requirements audit

Evidence cut-off: 15 November 2026, Asia/Karachi. The assignment and this package concern roll 23K-0073.

| Requirement | Status | Evidence or action remaining |
|---|---|---|
| Original Question 1 read and numbered checklist extracted | COMPLETE | REQUIREMENTS.md traces PDF pages 1–6. |
| Student details and all parameters on page 1 | COMPLETE | Roll, digit sum and substitutions verified. |
| Scenario steps and municipal use addressed | COMPLETE | Report covers intake, data acquisition, calculation, advisory retrieval and language fidelity. |
| Section 1 minimum model/developer counts | COMPLETE | Six closed models from four developers and six open models from six developers. |
| Section 1 provider diversity on open side | PARTIAL | Lowest observed public offers represented by one underlying host at the refreshed lowest quotes through one gateway. Expand live route investigation if the instructor counts inference hosts instead of model developers. |
| 1.1 Parameter counts and MoE breakdown | PARTIAL | Dense rows and proprietary nondisclosures recorded. GLM-4.6 active base estimated from its actual config. Exact active accounting and optional next-token prediction head are still unverified. |
| 1.2 Context and output limits | COMPLETE | Exact route caps used for open models. Grok documentation gives a context bound rather than a separate fixed cap. |
| 1.3 Prices and cheapest open routes | COMPLETE | Public route JSON and cost-based comparison of the observed offers. Confirm availability from the intended deployment account. |
| 1.4 New paid RPM and TPM | PARTIAL | OpenAI and xAI public figures accounted for. Retrieve Google, Anthropic and open route quotas from the intended paid accounts. |
| 1.5 TTFT and decode throughput | PARTIAL | Two matched candidate rows. Others need matching provider measurements or published data. |
| 1.6 Two benchmarks including tools | PARTIAL | Six BFCL scores and additional benchmark evidence on the open side, with mode mismatches flagged. Several closed rows lack a tool score and others lack a second result. Collect public evaluations for each exact model and disclose the setting. |
| 1.7 Native tools, JSON and reasoning settings | PARTIAL | Official settings and route flags captured. Confirm supported overrides and schema enforcement with paid test accounts. |
| 1.8 Licensing | COMPLETE | Proprietary, commercial and conditional licences identified. |
| 1 master table, provenance, key uncertainties | PARTIAL | Master CSV has route/model URLs and dates. Some per-field settings and provider disclosures remain unresolved as listed above. |
| 2.1 Retry-adjusted tokens and traffic | COMPLETE | Arithmetic, notebook and Excel reconciled. |
| 2.2 Cache and API cost | PARTIAL | 12 quotes, base, cold, 50%, 90%, savings and budget applied. Verify Gemini/Grok/GLM eligibility and other unverified cache policy fields. Measure matched reasoning averages where required. |
| 2.3 Peak traffic and rate-limit comparison | PARTIAL | Demand derived. Account-specific headroom requires the quotas listed above. |
| 2.4 Config inspection and screenshot | COMPLETE | Direct HF JSON and Chrome screenshot available. |
| 2.4.1–4 Weight memory, KV, theoretical concurrency and GPU count | COMPLETE | FP16/INT8/4-bit calculations, reserve and realistic caveats included. Throughput is unmeasured. |
| 2.5 GPU pricing and break-even | COMPLETE | Paid Runpod listing and reproducible step model with conditional no-crossover proof. Revisit after the latency comparison qualifies. |
| 2.6 Actual local timings and raw log | COMPLETE | Heat index and advisory lookup executed 70 times each across the two Karachi dates. |
| 2.6 Open-Meteo timing across two dates | COMPLETE | 30 valid responses on November 14 and 40 on November 15. |
| 2.6 Authenticated OpenAQ timings across two dates | COMPLETE | 15 successful responses on November 14 and 20 on November 15 at location 4932783. Excluded 15 unauthorized attempts. |
| OpenAQ fresh PM2.5 and PM10 coverage | PARTIAL | Fresh PM2.5 was verified at Climate Action Center. No PM10 sensor at this location. Day 2 discovery again found four stations listing both pollutants. The latest station-level activity among those four was November 7, 2024. Use PM10 unavailable until a timely monitored source exists. |
| 2.6 Pooled median and two-candidate latency | COMPLETE | Two-day pooled median drives the sequential baseline. The optimized scenario models the parallel critical path from measured component medians. |
| Production parallel-path and loaded LLM validation | PARTIAL | Three paid trials per model completed. The workload-matched, heatwave-load and multilingual tests remain unverified. |
| Technical recommendation | COMPLETE | Conditional API pilot recommendation. Real latency, multilingual quality and availability remain gates. |
| PDF and editable Word | COMPLETE | Word report and matching PDF include the live verification supplement. |
| Executable notebook | COMPLETE | Generated from clean-scope Python execution with displayed outputs. See README for running it in Jupyter. |
| Formula workbook | COMPLETE | Microsoft Excel recalculated it and checked traffic, caching, memory and crossover values. |
| Raw CSV, response evidence and validation summary | COMPLETE | Includes actual successes and failures, dates and evidence paths. Original log prefix verified byte-for-byte. The successful timing experiment is distinct from incomplete pollution coverage. |
| AI declaration, README, audit, ZIP | COMPLETE | Package uses an explicit allowlist and integrity check. |

The experiment meets the timing requirement. Model evidence and PM10 coverage limitations remain. Promote pending rows only when verified evidence is available.

## Independent re-check (15 November 2026)

- **COMPLETE — clean Jupyter execution:** A clean Linux Python kernel initially failed due to the hard-coded Windows font in `plots.py`. A cross-platform font fallback was added. All four code cells then executed successfully; the saved notebook includes the fresh outputs.
- **COMPLETE — workbook reconciliation:** Original formula workbook retained. Traffic, tokens, GPU capacity and 12×3 model-cost values agree with Python (36/36 comparisons). No spreadsheet formula errors appeared in the scanned values.
- **COMPLETE — direct host price comparison:** `DIRECT_HOST_COMPARISON.csv` pairs the six gateway quotes with direct DeepInfra Standard/Flex quotes and source URLs. This verifies prices but **does not establish 4 distinct underlying open-model inference providers** at the cheapest price.
- **COMPLETE — xAI published rate-unit correction:** Grok 4.7 T0 limit is 150 RPS; xAI defines RPS as RPM/48, so the implied RPM is 7,200, not the previously noted 9,000. Source matrix and report updated. The original peak request requirement is far lower regardless.
- **PARTIAL — benchmark and quotas:** Exact-setting public function-call benchmarks remain unavailable for several closed models; Gemini and some Claude/new-route account limits must be checked on intended paid-account dashboards.
- **PARTIAL — PM10 coverage:** Current authenticated discovery and latest endpoints confirmed four candidate stations with stale PM10, newest November 7, 2024. See live_test_results/LIVE_RESULTS.md.
- **COMPLETE — paid smoke test:** Three trials per model on a short English prompt. All six completed under 9 seconds. Peak-load verification remains PARTIAL. See live_test_results/LIVE_RESULTS.md.
