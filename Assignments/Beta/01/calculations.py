import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROLL = "23K-0073"
R = int(ROLL[-2:])
D = sum(map(int, filter(str.isdigit, ROLL))) % 10
Q, N, P, H, B, T = 1500+25*R, 5+R%4, (4+D)/100, 4+R%4, 1200+10*R, 10-R%3
CALLS = [(k, 2000+800*(k-1), 600 if k == N else 350, 1 if k == N else 1+P)
         for k in range(1, N+1)]
EI = sum(i*w for _, i, _, w in CALLS)
EO = sum(o*w for _, _, o, w in CALLS)
ER = sum(w for _, _, _, w in CALLS)
MONTH_FACTOR = 30+4*H
MQ = Q*MONTH_FACTOR
MI, MO, MR = MQ*EI, MQ*EO, MQ*ER
QPM = Q*5*.35/120
PEAK = (QPM, QPM*ER, QPM*EI, QPM*EO, QPM*(EI+EO))
assert (R,D,Q,N,P,H,B,T) == (73,5,3325,6,.09,5,1930,9)
assert (EI,EO,ER,MQ,MI,MO) == (25620,2507.5,6.45,166250,4259325000,416871875)

with (ROOT/"models.psv").open(encoding="utf-8-sig", newline="") as stream:
    MODELS = list(csv.DictReader(stream, delimiter="|"))
route_review = {r['model']:r for r in json.loads((ROOT/'evidence/route-review-2026-11-15.json').read_bytes())}
for model in MODELS:
    for key in ("input", "output", "read", "write", "prefix", "ttft", "tps"):
        model[key] = float(model[key] or 0)
    if model["group"] == "Open":
        endpoints = route_review[model['model']]['all_routes']
        score = lambda e: EI*float(e["pricing"]["prompt"]) + EO*float(e["pricing"]["completion"])
        selected = min(endpoints, key=score)
        model["route"] = selected["name"]
        model["tools_json"] = ", ".join(
            p for p in selected.get("supported_parameters", [])
            if p in {"tools","tool_choice","response_format","structured_outputs","reasoning","include_reasoning"}
        ) or "no matching provider flags listed"
        model["price_source"] = "https://openrouter.ai/api/v1/models/"+model["model"]+"/endpoints"
        assert abs(score(selected)-(EI*model["input"]+EO*model["output"])/1e6)<1e-9
    else:
        model["route"] = model["tier"]
        model["price_source"] = (
            "https://developers.openai.com/api/docs/pricing" if model["developer"] == "OpenAI"
            else "https://ai.google.dev/gemini-api/docs/pricing" if model["developer"] == "Google"
            else "https://docs.x.ai/developers/pricing" if model["developer"] == "SpaceXAI"
            else model["source"]
        )
    model["access_date"] = "2026-11-15 (route quote); model and benchmark sources 2026-11-14" if model["group"]=="Open" else "2026-11-14"

def monthly_cost(model, hits=0, reasoning=0, caching=False):
    cost = MI*model["input"] + (MO+MR*reasoning)*model["output"]
    if caching and model["prefix"]:
        cost += MR*model["prefix"]*(hits*(model["read"]-model["input"])
                                    +(1-hits)*(model["write"]-model["input"]))
    return cost / 1e6

CONFIG = json.loads((ROOT/"evidence/qwen3-14b-config.json").read_text(encoding="utf-8"))
PARAMETERS = 14.8e9
SEQ = CALLS[-1][1]+CALLS[-1][2]
KV = 4*CONFIG["num_hidden_layers"]*CONFIG["num_key_value_heads"]*CONFIG["head_dim"]*SEQ
MEMORY = 24*2**30
FREE = MEMORY*.9 - PARAMETERS/2
CAP = math.floor(FREE/KV)
GPU_HOURLY = .89
GPU_MONTH = GPU_HOURLY*720
COMMUNITY_GPU_MONTH = .34*720
SERVICE = 30
GPU_COUNT = max(1, math.ceil(QPM*SERVICE/60/CAP))
COMPARE = MODELS[0]
OPT_IN, OPT_OUT = 6000, 250
SLOPE = MONTH_FACTOR*(OPT_IN*COMPARE["input"]+OPT_OUT*COMPARE["output"])/1e6
CONCURRENCY_SLOPE = 5*.35/120*SERVICE/60
BREAK_CAP = CAP/CONCURRENCY_SLOPE

def gpu_cost(q, gpu_month=GPU_MONTH):
    return max(1,math.ceil(q/BREAK_CAP))*gpu_month

def crossover(gpu_month=GPU_MONTH):
    if SLOPE*BREAK_CAP <= gpu_month:
        return None
    first = math.floor(gpu_month/SLOPE)+1
    return first if first <= BREAK_CAP else None

def tool_results():
    with (ROOT/"tool_latency.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    good = [r for r in rows if r["success"] == "True"]
    tools = ["OpenAQ", "Open-Meteo", "heat_index", "advisory_lookup"]
    summary = []
    for tool in tools:
        subset = [r for r in rows if r["tool"] == tool]
        successful = [r for r in good if r["tool"] == tool]
        valid = [r for r in successful if r["valid"] == "True"]
        summary.append((tool, len(subset), len(successful), len(valid), len({r["date"] for r in successful}),
                        statistics.median(float(r["seconds"]) for r in successful) if successful else None))
    qualifies = all(count >= 20 and days >= 2 for _,_,count,_,days,_ in summary[:2])
    pooled = statistics.median(float(r["seconds"]) for r in good)
    api = statistics.median(float(r["seconds"]) for r in good if r["tool"] in tools[:2])
    return summary, qualifies, pooled, api

def critical_path_proxy(summary):
    """Max of remote medians plus local medians, a proxy for the parallel path."""
    medians = [row[-1] or 0 for row in summary]
    return max(medians[:2]) + sum(medians[2:])


def latency(ttft, tps, tool_seconds, extra=0, prefill=4000, optimized_tool_seconds=None):
    start = lambda prompt: ttft + (prompt-2000)/prefill
    base = sum((start(i)+(o-1+extra)/tps)*w for _,i,o,w in CALLS) + (N-1)*tool_seconds
    first = base-(CALLS[-1][2]-1)/tps
    # One final call, after deterministic routing and the parallel tool stage.
    stage = tool_seconds if optimized_tool_seconds is None else optimized_tool_seconds
    visible = stage + start(OPT_IN) + extra/tps
    return base, first, visible+(OPT_OUT-1)/tps, visible

if __name__ == "__main__":
    print(CALLS, PEAK, (CAP,GPU_COUNT,gpu_cost(Q),SLOPE,crossover(),crossover(COMMUNITY_GPU_MONTH)))
    print(tool_results())
    for row in MODELS:
        print(row["model"],*[round(monthly_cost(row,h,caching=c),2)
                             for h,c in [(0,False),(.5,True),(.9,True)]])
