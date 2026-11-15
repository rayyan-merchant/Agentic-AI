# SaafHawa Q1 — independent verification and remaining evidence

Roll 23K-0073. Verified on 15 November 2026. This addendum distinguishes source-backed specifications, computations, archived experimental data, and measurements that **have not** been performed. It does not replace the original assignment PDF.

## 1. Fresh Jupyter and workbook audit — completed

- Clean Linux Jupyter rerun: all 4 executable cells completed, saved in `Assignment_Beta_Question_no_1_23K-0073.ipynb`.
- Repaired a portability defect: original graph code required `C:/Windows/Fonts/segoeui.ttf`; `plots.py` now uses an installed DejaVu fallback, then PIL's default font if needed.
- Workbook `SaafHawa.xlsx` was imported and checked without changing formulas. All 12 rows match Python's three displayed billing scenarios, a total of 36 numerical reconciliations. Peak traffic, input/output monthly totals, GPU memory ceiling and step-model values match. No Excel formula-error values appeared.
- Original user's assumptions: R=73, D=5, Q=3,325/day, N=6, p=.09, H=5, B=$1,930, T=9 s. Derived monthly queries 166,250; input 4,259,325,000; output 416,871,875. These are *calculated*, not measurements.

## 2. Public model, rate-limit and cache sources

**OpenAI:** Pricing confirms standard short-context rates of $0.10 input / $0.50 output per million for GPT-6 Luna; $1.00 / $5.00 for GPT-6.1 Terra, with the documented cache read/write prices. Build RPM 5,000 for each, combined TPM 2,000,000 for Luna and 1,000,000 for Terra. At 312.76 expected peak RPM and 1,363,890.76 combined visible TPM, Luna clears the published Build limits; Terra needs a higher tier on the baseline workload. Model availability and any project-specific limits must still be checked using the actual paid account. Sources:

- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/docs/guides/rate-limits
- https://developers.openai.com/api/docs/guides/prompt-caching
- https://developers.openai.com/api/docs/models/gpt-6.1-terra

**Anthropic:** Claude Haiku 5.5 is listed with 1M context and up to 128K output. The documented caching minimum for Haiku 5.5 is 512 tokens, and Anthropic's rate-limit scheme separates RPM, input TPM and output TPM, with cached reads generally excluded from counted input TPM. The actual new paid team's allotment was not observable in this session. Sources:

- https://platform.claude.com/docs/en/models/overview
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- https://platform.claude.com/docs/en/api/rate-limits

**Google Gemini:** The official rate-limit documentation requires an authorized AI Studio project to check its live RPM and input TPM. Implicit caching thresholds are model-dependent, so this submission conservatively credits zero cache savings for the selected Gemini rows whose 1,500-token stable prefix was not verified eligible. Sources:

- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/caching

**xAI Grok 4.7:** Official docs give T0 150 RPS and 50M TPM. xAI defines RPS as RPM/48 (with a 2 RPS minimum). Therefore the correct *implied* baseline RPM is 7,200, not 9,000. The earlier 9,000 figure came from multiplying 150 by 60, but is inconsistent with the documented burst-derivation rule. Source data and report have been corrected. Sources:

- https://docs.x.ai/developers/rate-limits
- https://docs.x.ai/developers/grok-4-7

**Public benchmark gaps remain:** Model and reasoning-setting matching is essential. Current BFCL leaderboard snapshots do not provide complete exact-model function-use benchmarks for every proprietary selection. Absence of a matched score is noted as UNVERIFIED; scores from unrelated predecessors must not be copied as if they evaluated these models. Source: https://gorilla.cs.berkeley.edu/leaderboard

## 3. Direct host versus gateway prices — checked, diversity still partial

`DIRECT_HOST_COMPARISON.csv` records six open-model slugs, their selected gateway route, and published **direct** DeepInfra Standard/Flex prices. The un-cached monthly costs agree with the lowest available direct price to the cent for all six under the corresponding tier assumptions. This is a price cross-check, *not* proof that the selected OpenRouter route actually ran at the Flex service class.

Caution: prices for five routes align with DeepInfra's 20%-discounted Flex tier (the sixth aligns with the published standard price). According to DeepInfra, Flex is best-effort and requests may wait for available capacity; a discounted Flex price cannot be treated as guaranteeing the 9-second SLA. The direct host and gateway price may be equal without proving equal latency. Provider diversity remains **PARTIAL** because the selected cheapest offers still use DeepInfra as the underlying host. If '4 providers' means four **underlying inference hosts** rather than model developers, this version does not yet prove compliance; alternate eligible routes will be more expensive and require verified quotes.

Sources include:

- https://deepinfra.com/llama
- https://deepinfra.com/Qwen/Qwen3-14B
- https://deepinfra.com/pricing
- https://deepinfra.com/mistralai/Mistral-Small-3.2-24B-Instruct-2506
- https://deepinfra.com/glm
- https://deepinfra.com/blog/deepseek-v4-1-flash-model-overview-integration

## 4. Completed two-day timing; PM10 remains unverified

Archived timing CSV and responses were retained without changing timestamps. This review reproduced its medians: OpenAQ 35 successful 200 responses from 50 attempts across Nov 14–15, 2026; Open-Meteo 70/70 successful; local heat index 70/70; local advisory lookup 70/70. Pooled successful median: 0.000009400 s. API-only median: 0.244081 s. The pooled value is dominated by extremely fast local functions and is **not** the physical end-to-end tool stage.

None of the successful OpenAQ rows contains the necessary **fresh paired PM2.5 and PM10** values. The archived Karachi discovery from Nov 15 listed PM10 at OpenAQ locations 1894633 (last station activity Feb 28 2024), 3089895 (Oct 25 2024), 3182341 (Oct 28 2024) and 3213801 (Nov 7 2024). The valid local 2026 station offers fresh PM2.5 but no PM10. The absence of a current pollutant reading is a data-coverage issue, not an HTTP timing failure.

`live_path_probe.py --discover-pm10` uses the official `parameters_id=1` filter, with a 25-km Karachi search, to conduct a fresh check under a local OpenAQ API key. The historical results cannot establish current PM10 availability. Do not fill in a missing PM10 value or present stale measurements as current. Sources:

- https://docs.openaq.org/api/operations/locations_get_v3_locations_get
- https://docs.openaq.org/resources/locations
- https://docs.openaq.org/resources/latest

## 5. Live 9-second test — not run here

No OpenAI or OpenAQ API key was available in this environment and outbound DNS was disabled. As a result the real concurrent OpenAQ+Open-Meteo stage and streamed paid model responses could **not** be measured. The workbook and report's 6.25-second Luna and 7.77-second Terra optimized totals remain **modeled estimates**, not confirmed production latency. The modeled 30-second self-host service time is also not a measured throughput benchmark.

The included `live_path_probe.py` can test the actual concurrent stage and stream a real final answer for both candidates through OpenAI Responses when run locally with credentials. It logs time to first visible output and full completion separately, and records actual token usage. It does not print or save API keys. Compare its actual token counts with the modeled 6,000-input / 250-output profile before claiming that result validates the assignment's optimized workload. One or a few trials do not establish peak-load reliability.

Run locally **only after setting credentials outside the repository**:

```powershell
python -m pip install requests
python live_path_probe.py --discover-pm10
python live_path_probe.py --samples 3 --run-paid
```

For a controlled full-length latency test, supply a genuinely representative and appropriately long final-stage context, then measure its billed input/output tokens. Do not achieve an apparent workload match using arbitrary filler and call it a SaafHawa benchmark.

Official stream event reference: https://developers.openai.com/api/docs/guides/streaming-responses

## Status after this pass

**COMPLETE:** Clean Jupyter run, Python–Excel reconciliation, archived two-day tool timing, direct underlying-host quote cross-check, xAI rate correction and source links.

**PARTIAL:** Exact-model published benchmark coverage; account-specific RPM/TPM and cache bills; four distinct *underlying* open inference hosts if required; fresh PM10 coverage; actual self-host throughput.

**BLOCKED:** End-to-end paid-model and concurrent remote-tool timing from the intended network until the user runs `live_path_probe.py` with valid local keys, and any subsequent peak-load validation.
