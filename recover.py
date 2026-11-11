"""Continue a known readiness-only stop, never replay a model request."""
import hashlib
import json
import subprocess
import time
from datetime import datetime,timezone

from fixtures import cases
from run import ROOT,MODELS,api,body,dump,schedule,sha,verify_freeze
from tool_lab import score


def validate_prefix(rows,planned):
    case_map={c['id']:c for c in cases()}
    if not 0<len(rows)<len(planned):raise ValueError('Expected a nonempty, incomplete prefix')
    for index,row in enumerate(rows):
        cell=planned[index]
        if row.get('index')!=index or any(row.get(k)!=v for k,v in cell.items()):raise ValueError('Not the scheduled prefix')
        if row.get('resident_before')!=[] or 'error' in row or row.get('response',{}).get('done') is not True:raise ValueError('Uncertain prior response')
        if row['request']!=body(cell,case_map[cell['case_id']]):raise ValueError('Prior request changed')
        if row['request_sha256']!=hashlib.sha256(json.dumps(row['request'],sort_keys=True).encode()).hexdigest():raise ValueError('Prior request hash changed')
    return case_map


def wait_empty():
    started=time.perf_counter();observed=[]
    while True:
        resident=api('/api/ps').get('models',[])
        observed.append({'elapsed_seconds':time.perf_counter()-started,'models':resident})
        if not resident:return time.perf_counter()-started,observed
        if any(m.get('name') not in MODELS for m in resident):raise RuntimeError('Unrelated model resident; never evict')
        if time.perf_counter()-started>=30:raise RuntimeError('Cold readiness did not clear')
        time.sleep(0.5)


def recover():
    verify_freeze();path=ROOT/'evidence/run.json';state=json.loads(path.read_text())
    if state.get('status')!='incomplete' or state.get('detail')!='A model remains resident; cold-start contract not satisfied':raise ValueError('Not the known readiness-only stop')
    continuation_path=ROOT/'evidence/continuation.json'
    if continuation_path.exists():raise FileExistsError('Never replay a prior continuation')
    raw=ROOT/'evidence/raw.jsonl';rows=[json.loads(x) for x in raw.read_text().splitlines()]
    planned=schedule();case_map=validate_prefix(rows,planned)
    pinned=json.loads((ROOT/'evidence/models.json').read_text());current={m['name']:m['digest'] for m in api('/api/tags')['models']}
    if any(current.get(m)!=pinned[m]['digest'] for m in MODELS):raise RuntimeError('Model identity changed')
    dump(ROOT/'evidence/initial-stop.json',state)
    continuation={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'completed_prefix':len(rows),'new_planned_calls':len(planned)-len(rows),
                  'original_raw_sha256':sha(raw),'frozen_manifest_sha256':sha(ROOT/'evidence/frozen.json'),
                  'recovery_sha256':sha(ROOT/'recover.py'),'amendment_sha256':sha(ROOT/'TRANSPORT-AMENDMENT.md'),
                  'tested_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'pending_index':None}
    dump(continuation_path,continuation)
    try:
        with raw.open('a') as out:
            for index in range(len(rows),len(planned)):
                cell=planned[index];case=case_map[cell['case_id']];request=body(cell,case)
                wait_seconds,probes=wait_empty()
                row={**cell,'index':index,'request':request,'resident_before':[],
                     'request_sha256':hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest(),
                     'transport_wait_seconds':wait_seconds,'residency_probes':probes}
                continuation['pending_index']=index;dump(continuation_path,continuation)
                before=time.perf_counter()
                try:
                    response=api('/api/chat',request)
                    row.update(response=response,wall_seconds=time.perf_counter()-before)
                    row['scored']=score(response,case['expected'],[t['function']['name'] for t in request['tools']])
                except Exception as error:
                    row.update(error=type(error).__name__,error_detail=str(error)[:300],wall_seconds=time.perf_counter()-before)
                    out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush();raise
                out.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');out.flush()
                continuation.update(pending_index=None,completed_total=index+1);dump(continuation_path,continuation)
                print(json.dumps({'completed':index+1,'total':64,'model':cell['model'],'condition':cell['condition']}),flush=True)
        continuation['status']='completed';state['status']='completed'
        state['transport_amendment']='TRANSPORT-AMENDMENT.md';state['initial_stop']='evidence/initial-stop.json'
        state.pop('error',None);state.pop('detail',None)
    except Exception as error:
        continuation.update(status='incomplete',error=type(error).__name__,detail=str(error)[:300]);raise
    finally:
        continuation['finished_utc']=datetime.now(timezone.utc).isoformat();dump(continuation_path,continuation)
        state['continuation_status']=continuation['status'];state['finished_utc']=continuation['finished_utc']
        state.setdefault('original_driver_wall_seconds',state['wall_seconds'])
        state['wall_seconds']=(datetime.fromisoformat(state['finished_utc'])-datetime.fromisoformat(state['started_utc'])).total_seconds()
        dump(path,state)
    from analyze import analyze
    analyze()


if __name__=='__main__':recover()
