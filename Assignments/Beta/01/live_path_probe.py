"""Optional SaafHawa live latency probe. No secrets or fabricated results.

Required environment: OPENAQ_API_KEY for OpenAQ; OPENAI_API_KEY to run paid tests.
Run only with --run-paid when you authorize API charges.
"""
import argparse
import concurrent.futures
import csv
import json
import os
import statistics
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from collect import aq_valid, heat_index, KB

ROOT = Path(__file__).resolve().parent

def load_local_keys():
    """Load the two supported keys from the adjacent local .env file."""
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name, separator, value = line.partition("=")
        name = name.strip()
        value = value.strip()
        if separator and name in {"OPENAQ_API_KEY", "OPENAI_API_KEY"} and value:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            os.environ.setdefault(name, value)

OUT = ROOT / 'live_test_results'
KARACHI = timezone(timedelta(hours=5))
MODELS = ['gpt-6-luna', 'gpt-6.1-terra']
FIELDS = ['timestamp', 'sample_id', 'model', 'stage_status', 'openaq_http',
          'openaq_seconds', 'openmeteo_http', 'openmeteo_seconds',
          'parallel_tool_seconds', 'aq_dual_valid', 'model_http',
          'time_first_visible_seconds', 'full_completion_seconds',
          'model_seconds', 'input_tokens', 'output_tokens',
          'generated_characters', 'model_error', 'notes']


def get_aq(station, key, sensors):
    t = time.perf_counter()
    try:
        r = requests.get(f'https://api.openaq.org/v3/locations/{station}/latest',
                         headers={'X-API-Key': key}, timeout=15)
        elapsed = time.perf_counter() - t
        valid = r.status_code == 200 and aq_valid(r.json(), sensors, datetime.now(timezone.utc))
        return {'status': r.status_code, 'seconds': elapsed, 'valid': bool(valid),
                'body': r.json() if r.status_code == 200 else {}, 'error': ''}
    except Exception as e:
        return {'status': None, 'seconds': time.perf_counter()-t, 'valid': False,
                'body': {}, 'error': type(e).__name__}


def get_weather():
    t=time.perf_counter()
    try:
        r=requests.get('https://api.open-meteo.com/v1/forecast',
                       params={'latitude':24.86,'longitude':67.01,'timezone':'Asia/Karachi',
                       'current':'temperature_2m,relative_humidity_2m,wind_speed_10m'}, timeout=15)
        body=r.json() if r.status_code==200 else {}
        cur=body.get('current',{})
        units=body.get('current_units',{})
        try:
            tm=datetime.fromisoformat(cur['time']).replace(tzinfo=KARACHI)
            fresh=abs(datetime.now(KARACHI)-tm)<=timedelta(minutes=30)
        except (KeyError,ValueError,TypeError):
            fresh=False
        good=(fresh and units.get('temperature_2m')=='°C'
              and units.get('relative_humidity_2m')=='%'
              and units.get('wind_speed_10m')=='km/h'
              and all(k in cur for k in ('temperature_2m','relative_humidity_2m','wind_speed_10m')))
        return {'status':r.status_code,'seconds':time.perf_counter()-t,'body':cur,
                'valid':bool(good),'error':''}
    except Exception as e:
        return {'status':None,'seconds':time.perf_counter()-t,'body':{},'valid':False,
                'error':type(e).__name__}


def station_info(station,key):
    r=requests.get(f'https://api.openaq.org/v3/locations/{station}',
                   headers={'X-API-Key':key}, timeout=15)
    r.raise_for_status()
    obj=r.json()['results'][0]
    return {s['id']:(s['parameter']['name'],s['parameter']['units']) for s in obj['sensors']}


def discover_pm10(key):
    OUT.mkdir(exist_ok=True)
    result=[]
    for page in range(1,15):
        r=requests.get('https://api.openaq.org/v3/locations',
            headers={'X-API-Key':key},
            params={'coordinates':'24.8607,67.0011','radius':25000,
                    'parameters_id':1, 'limit':100,'page':page},timeout=20)
        r.raise_for_status()
        rows=r.json().get('results',[])
        for entry in rows:
            pm10=[x for x in entry.get('sensors',[])
                  if x.get('parameter',{}).get('name')=='pm10']
            if not pm10:continue
            result.append({'id':entry['id'],'name':entry.get('name'),
                           'last_station_reported':entry.get('datetimeLast'),
                           'distance_m':entry.get('distance'),
                           'pm10_sensors':pm10})
        if len(rows)<100:break
    path=OUT/'pm10_filtered_discovery.json'
    path.write_text(json.dumps({'checked_at':datetime.now(KARACHI).isoformat(),
                                'parameter_id':1, 'candidates':result},indent=2))
    print('PM10 candidates (station activity alone does not prove fresh PM10):',len(result),path)


def stream_openai(model,context,api_key,seconds_timeout=120):
    payload={'model':model,'input':context,'reasoning':{'effort':'none'},
             'stream':True,'max_output_tokens':350,
             'store':False}
    t=time.perf_counter()
    first=None; output=[]; usage={}; completed=False; error=''; code=None
    try:
        with requests.post('https://api.openai.com/v1/responses',
             json=payload, headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json'},
             timeout=(12,seconds_timeout),stream=True) as r:
            code=r.status_code
            if code!=200:
                return {'http':code,'first':None,'complete':None,'usage':{},'chars':0,
                        'error':'HTTP '+str(code)+'; body withheld to avoid exposing account details'}
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith('data: '): continue
                data=line[6:]
                if data=='[DONE]':break
                try:event=json.loads(data)
                except json.JSONDecodeError:continue
                kind=event.get('type')
                if kind=='response.output_text.delta' and event.get('delta'):
                    if first is None:first=time.perf_counter()-t
                    output.append(event['delta'])
                elif kind=='response.completed':
                    completed=True
                    usage=(event.get('response') or {}).get('usage') or {}
                    break
                elif kind in ('response.failed','error'):
                    error=kind+': '+str(event.get('message') or event.get('error') or '')[:120]
                    break
    except Exception as e:
        error=type(e).__name__
    return {'http':code,'first':first,'complete':time.perf_counter()-t if completed else None,
            'usage':usage,'chars':sum(map(len,output)),'error':error or ('' if completed else 'not completed')}


def trial(station,key,models,api_key,run_paid):
    sensors=station_info(station,key)
    t=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f1=pool.submit(get_aq,station,key,sensors)
        f2=pool.submit(get_weather)
        aq=f1.result(); weather=f2.result()
    if weather['valid']:
        cur=weather['body']
        heat=heat_index(cur['temperature_2m'],cur['relative_humidity_2m'])
    else:heat=None
    advisory=KB['heat']
    stage=time.perf_counter()-t
    air='PM10 unavailable; do not infer it from PM2.5.' if not aq['valid'] else 'PM2.5 and PM10 available; see retained station source.'
    facts={'station_id':station,'openaq_response_status':aq['status'],
           'openaq_dual_pollutant_valid':aq['valid'], 'air_quality_note':air,
           'weather':weather['body'] if weather['valid'] else 'unavailable',
           'heat_index_c':round(heat,2) if heat is not None else None,
           'official_advisory':advisory}
    prompt=("You are SaafHawa, a Karachi environmental information assistant. "
        "Give a concise, accurate answer in the user's requested language. "
        "Use only the supplied JSON data; never make up pollution values. "
        "State clearly that PM10 is unavailable where applicable, and do not diagnose conditions. "
        "User request: 'Tell me the current air quality and heat precautions in Karachi in English.'\n"
        "Verified tool response: "+json.dumps(facts,ensure_ascii=False)+"\n"
        "Answer in about 150 to 220 words. Only cite the given advisory URL.")
    rows=[]
    for model in models:
        r=stream_openai(model,prompt,api_key) if run_paid else {'http':None,'first':None,
            'complete':None,'usage':{},'chars':0,'error':'PAID TEST NOT RUN'}
        usage=r['usage']
        rows.append({'timestamp':datetime.now(KARACHI).isoformat(),
            'sample_id':uuid.uuid4().hex,'model':model,
            'stage_status':'complete' if aq['status']==200 and weather['valid'] else 'partial',
            'openaq_http':aq['status'],'openaq_seconds':aq['seconds'],
            'openmeteo_http':weather['status'],'openmeteo_seconds':weather['seconds'],
            'parallel_tool_seconds':stage,'aq_dual_valid':aq['valid'],
            'model_http':r['http'],
            'time_first_visible_seconds':None if r['first'] is None else stage+r['first'],
            'full_completion_seconds':None if r['complete'] is None else stage+r['complete'],
            'model_seconds':r['complete'],
            'input_tokens':usage.get('input_tokens'),
            'output_tokens':usage.get('output_tokens'),
            'generated_characters':r['chars'],'model_error':r['error'],
            'notes':'Actual prompt token count may be far below 6000; cannot validate the 6000-token modeled scenario without workload-matched prompt.'})
    return rows


def main():
    load_local_keys()
    parser=argparse.ArgumentParser(description='Real concurrent tool and model latency, with no simulated timings')
    parser.add_argument('--samples',type=int,default=2)
    parser.add_argument('--location',type=int,default=4932783)
    parser.add_argument('--run-paid',action='store_true',help='Authorize paid GPT-6 API calls to both candidate models')
    parser.add_argument('--discover-pm10',action='store_true')
    a=parser.parse_args()
    key=os.environ.get('OPENAQ_API_KEY')
    if not key:
        parser.error('Set OPENAQ_API_KEY in your local environment (never commit or paste it).')
    if a.discover_pm10:
        discover_pm10(key); return
    api_key=os.environ.get('OPENAI_API_KEY')
    if a.run_paid and not api_key:
        parser.error('--run-paid requires OPENAI_API_KEY. No paid calls were made.')
    if a.samples<1 or a.samples>20:parser.error('samples must be 1..20')
    OUT.mkdir(exist_ok=True)
    path=OUT/'parallel_e2e_trials.csv'
    present=path.exists()
    with path.open('a',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        if not present:writer.writeheader()
        for i in range(a.samples):
            for item in trial(a.location,key,MODELS,api_key,a.run_paid):
                writer.writerow(item)
            f.flush()
            print(f'Completed real parallel tool trial {i+1}/{a.samples} (paid={a.run_paid})')
    print('Saved:',path)
    rows=list(csv.DictReader(path.open()))
    for model in MODELS:
        completions=[float(x['full_completion_seconds']) for x in rows if x['model']==model and x['full_completion_seconds']]
        if completions:
            print(model,'real end-to-end median',statistics.median(completions),
                  'range',min(completions),max(completions),'n',len(completions))
        else:print(model,'end-to-end not verified (missing paid trials)')

if __name__=='__main__':main()
