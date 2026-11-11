"""Recalculate finite task success, retrieval recall and recorded counters."""
import json
import statistics
from run import ROOT,MODELS,body,dump,sha,verify_freeze
from fixtures import cases
from tool_lab import score


def analyze():
    verify_freeze()
    state=json.loads((ROOT/'evidence/run.json').read_text())
    if state['status']!='completed':raise RuntimeError('Incomplete run; no publication-ready result')
    rows=[json.loads(line) for line in (ROOT/'evidence/raw.jsonl').read_text().splitlines()]
    case_map={c['id']:c for c in cases()};expected={(m,c,'full64') for m in MODELS for c in case_map}|{(m,c,'lexical4') for m in MODELS for c in case_map}
    assert len(rows)==64 and {(r['model'],r['case_id'],r['condition']) for r in rows}==expected
    derived=[]
    for row in rows:
        case=case_map[row['case_id']];assert row['request']==body(row,case)
        names=[x['function']['name'] for x in row['request']['tools']]
        result=score(row['response'],case['expected'],names);assert result==row['scored']
        counters={k:row['response'].get(k) for k in ['prompt_eval_count','prompt_eval_cached_count','load_duration','total_duration','prompt_eval_duration','eval_count','eval_duration','done_reason']}
        derived.append({'model':row['model'],'condition':row['condition'],'case_id':case['id'],'intent':case['intent'],'wording':case['wording'],
                        'gold_available':case['expected']['name'] in names,'tool_count':len(names),**result,**counters,
                        'definition_bytes':len(json.dumps(row['request']['tools'],sort_keys=True).encode()),'wall_seconds':row['wall_seconds']})
    summary=[]
    for model in MODELS:
        for condition in ['full64','lexical4']:
            selected=[r for r in derived if r['model']==model and r['condition']==condition]
            record={'model':model,'condition':condition,'requests':16,'intent_families':8,
                    **{k:sum(bool(x[k]) for x in selected) for k in ['exact','name_correct','valid_single_call','gold_available']}}
            for wording in ['explicit','paraphrase']:
                subset=[x for x in selected if x['wording']==wording]
                record[wording]={'requests':8,'exact':sum(x['exact'] for x in subset),'gold_available':sum(x['gold_available'] for x in subset)}
            for field in ['prompt_eval_count','definition_bytes','wall_seconds','load_duration','eval_count']:
                values=[x[field] for x in selected if type(x[field]) in (int,float)]
                record[field]={'known':len(values),'mean':statistics.mean(values) if values else None,'median':statistics.median(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None}
            record['cached_counter_known']=sum(x['prompt_eval_cached_count'] is not None for x in selected)
            summary.append(record)
    dump(ROOT/'results/summary.json',{'status':'completed','primary_unit':'8 intent families; two authored request wordings each','raw_sha256':sha(ROOT/'evidence/raw.jsonl'),'groups':summary,'observations':derived})
    print(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':analyze()
