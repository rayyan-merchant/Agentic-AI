# Live verification on 2026-11-15 (Asia/Karachi)

| Model | Successful trials | Median first visible | Median full | Full range | Tokens in/out |
|---|---:|---:|---:|---:|---|
| gpt-6-luna | 3 | 2.093 s | 3.774 s | 2.815–5.902 s | 260 in / 158–186 out |
| gpt-6.1-terra | 3 | 1.678 s | 4.183 s | 3.679–5.667 s | 260 in / 184–223 out |

Three paired trials measured simultaneous OpenAQ and Open-Meteo requests followed by local heat index and advisory retrieval. Median measured stage was 0.571 s. Station metadata was loaded before starting the timer. Each model streamed a single Responses API completion with reasoning disabled. Estimated token charges were about USD 0.0041 before account-specific adjustments.
All six completions finished within 9 s in this single-client English smoke test. The input had 260 tokens. The assignment model assumed 6,000 input tokens and 250 output tokens. A workload-matched test, heatwave-load test and bilingual quality check remain outstanding.
Authenticated PM10 discovery searched within 25 km of central Karachi. All four station latest endpoints returned HTTP 200. Their latest PM10 timestamps were in 2024, with the newest on November 7, 2024. Use the PM10 unavailable fallback. The original two-day timing CSV is unchanged.
OpenAI deployment recommendation remains a conditional Luna pilot. Exact-setting tool benchmarks, account-specific quotas and cache details, and open-weight inference-host diversity remain partial. No dashboard quota or live cache billing check was performed.
