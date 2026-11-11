"""Frozen, sequential loopback-only measurement. Never executes proposed tools."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import time
import urllib.request

from fixtures import catalog,cases
from tool_lab import select_tools,score

ROOT=Path(__file__).resolve().parent
MODELS=['qwen2.5:7b','qwen3:8b']
SEED=20261111
BASE='http://127.0.0.1:11434'
SYSTEM=('You are a read-only tool router. Select exactly ONE available function matching the requested application and search object. '
        'Call it natively with query set to the quoted search text verbatim and limit set to the requested maximum count. '
        'Do not call several functions, invent tools, execute a real service or answer the search request in prose. '
        'If no suitable function is available, explain that briefly without a tool call. Do not substitute a different application.')


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def api(route,data=None,timeout=90):
    if route not in ['/api/tags','/api/show','/api/chat','/api/ps','/api/version']:
        raise ValueError('Unsupported fixed loopback route')
    payload=json.dumps(data,allow_nan=False).encode() if data is not None else None
    request=urllib.request.Request(BASE+route,data=payload,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=timeout) as response:return json.load(response)


def schedule():
    rng=random.Random(SEED);result=[]
    for model in MODELS:
        ordered=cases();rng.shuffle(ordered)
        for case in ordered:
            conditions=['full64','lexical4'];rng.shuffle(conditions)
            for condition in conditions:result.append({'model':model,'case_id':case['id'],'condition':condition})
    return result


def tools_for(case,condition):
    tools=catalog()
    return tools if condition=='full64' else select_tools(case['request'],tools,4)


def body(cell,case):
    return {'model':cell['model'],'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':case['request']}],
            'tools':tools_for(case,cell['condition']),'stream':False,'think':False,'keep_alive':0,
            'options':{'temperature':0,'seed':SEED,'num_ctx':16384,'num_predict':160}}


def freeze():
    if (ROOT/'evidence/frozen.json').exists():raise FileExistsError('Protocol already frozen; create a new namespace for a new run')
    models=api('/api/tags')['models'];available={m['name']:m for m in models}
    if any(model not in available for model in MODELS):raise RuntimeError('Required preinstalled model unavailable; no pulls allowed')
    dump(ROOT/'evidence/catalog.json',catalog());dump(ROOT/'evidence/cases.json',cases());dump(ROOT/'evidence/schedule.json',schedule())
    info={model:available[model] for model in MODELS}
    for model in MODELS:
        shown=api('/api/show',{'model':model})
        info[model]['capabilities']=shown.get('capabilities')
        info[model]['model_info']=shown.get('model_info')
        if 'tools' not in (shown.get('capabilities') or []):raise RuntimeError('Native tool support missing')
    dump(ROOT/'evidence/models.json',info)
    dump(ROOT/'evidence/versions.json',{'ollama':api('/api/version'),'python':subprocess.check_output(['python3','--version'],text=True).strip(),
        'invariant':subprocess.check_output(['invariant','--version'],text=True).strip()})
    files=['PROTOCOL.md','fixtures.py','tool_lab.py','run.py','analyze.py','verify.py','tests/test_acceptance.py','tests/run_checks.py','evidence/invariant.json',
           'evidence/catalog.json','evidence/cases.json','evidence/schedule.json','evidence/models.json','evidence/versions.json']
    value={'schema_version':1,'created_at':datetime.now(timezone.utc).isoformat(),'planned_calls':64,
           'files':{name:sha(ROOT/name) for name in files}}
    dump(ROOT/'evidence/frozen.json',value)
    print(json.dumps({'frozen_files':len(files),'planned_calls':64}))


def verify_freeze():
    value=json.loads((ROOT/'evidence/frozen.json').read_text())
    for name,digest in value['files'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('Frozen file changed: '+name)
    return value


def measure():
    verify_freeze()
    if (ROOT/'evidence/run.json').exists() or (ROOT/'evidence/raw.jsonl').exists():raise FileExistsError('Never replay uncertain measured requests')
    pinned=json.loads((ROOT/'evidence/models.json').read_text())
    current={m['name']:m['digest'] for m in api('/api/tags')['models']}
    if any(current.get(model)!=pinned[model]['digest'] for model in MODELS):raise RuntimeError('Model digest changed')
    case_map={c['id']:c for c in cases()};started=time.time()
    state={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'tested_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'planned_calls':64}
    dump(ROOT/'evidence/run.json',state)
    try:
        with (ROOT/'evidence/raw.jsonl').open('x') as out:
            for index,cell in enumerate(schedule()):
                case=case_map[cell['case_id']];request=body(cell,case)
                resident=api('/api/ps').get('models',[])
                # Do not evict another user's loaded model or silently claim a cold run.
                if resident:raise RuntimeError('A model remains resident; cold-start contract not satisfied')
                row={**cell,'index':index,'request':request,'resident_before':resident,
                     'request_sha256':hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()}
                before=time.perf_counter()
                try:
                    response=api('/api/chat',request)
                    row.update(response=response,wall_seconds=time.perf_counter()-before)
                    row['scored']=score(response,case['expected'],[t['function']['name'] for t in request['tools']])
                except Exception as error:
                    row.update(error=type(error).__name__,error_detail=str(error)[:300],wall_seconds=time.perf_counter()-before)
                    out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
                    raise
                out.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');out.flush()
                print(json.dumps({'completed':index+1,'total':64,'model':cell['model'],'condition':cell['condition']}),flush=True)
        state['status']='completed'
    except Exception as error:
        state.update(status='incomplete',error=type(error).__name__,detail=str(error)[:500]);raise
    finally:
        state.update(wall_seconds=time.time()-started,finished_utc=datetime.now(timezone.utc).isoformat())
        dump(ROOT/'evidence/run.json',state)
    from analyze import analyze
    analyze()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','measure']);args=parser.parse_args()
    freeze() if args.command=='freeze' else measure()
