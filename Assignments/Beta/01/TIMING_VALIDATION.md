# Tool latency validation

Qualifying experiment: COMPLETE.

| Tool | Attempts | Successful | Valid data | Successful Karachi dates | Successful median seconds |
|---|---:|---:|---:|---:|---:|
| OpenAQ | 50 | 35 | 0 | 2 | 0.743303100 |
| Open-Meteo | 70 | 70 | 70 | 2 | 0.186322450 |
| heat_index | 70 | 70 | 70 | 2 | 0.000008750 |
| advisory_lookup | 70 | 70 | 70 | 2 | 0.000001300 |

Successful pooled median: 0.000009400 s. Successful API-only median: 0.244081 s.

HTTP 200 counts toward timing when the request succeeded. Data validity is tracked independently. Original November 14 records passed a byte-for-byte SHA-256 check.

Counts by Karachi date, tool, status and validity:

- 2026-11-14, Open-Meteo, 200, True: 30
- 2026-11-14, OpenAQ, 200, False: 15
- 2026-11-14, OpenAQ, 401, False: 15
- 2026-11-14, advisory_lookup, local, True: 30
- 2026-11-14, heat_index, local, True: 30
- 2026-11-15, Open-Meteo, 200, True: 40
- 2026-11-15, OpenAQ, 200, False: 20
- 2026-11-15, advisory_lookup, local, True: 40
- 2026-11-15, heat_index, local, True: 40
