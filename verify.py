"""Independent scoring and lexical shortlist reconstruction; no model/network."""
import json
import math
import re
from pathlib import Path
from collections import Counter
from run import ROOT,verify_freeze,dump


def main():
    verify_freeze()
    rows=[json.loads(x) for x in (ROOT/'evidence/raw.jsonl').read_text().splitlines()]
    cases={c['id']:c for c in json.loads((ROOT/'evidence/cases.json').read_text())}
    catalog=json.loads((ROOT/'evidence/catalog.json').read_text())
    stop=set('a an the and or to of in on for with our by from at as is it this that use search find look up exact text return most results preserve quoted verbatim'.split())
    def words(s):return set(re.findall('[a-z0-9]+',s.lower()))-stop
    counts=Counter();keys=set()
    for row in rows:
        key=row['model'],row['case_id'],row['condition'];assert key not in keys;keys.add(key)
        case=cases[row['case_id']]
        terms=words(case['request'])
        ranked=sorted(catalog,key=lambda t:(-len(terms&words(t['function']['name']+' '+t['function']['description'])),t['function']['name']))
        wanted=catalog if row['condition']=='full64' else ranked[:4]
        assert wanted==row['request']['tools']
        response=row['response'];calls=response.get('message',{}).get('tool_calls',[])
        exact=False
        if response.get('done') is True and isinstance(calls,list) and len(calls)==1:
            function=calls[0].get('function',{})
            arguments=function.get('arguments')
            if isinstance(arguments,str):
                try:arguments=json.loads(arguments)
                except ValueError:arguments=None
            if isinstance(arguments,dict) and set(arguments)=={'query','limit'}:
                limit=arguments['limit'];valid=type(limit) in (int,float) and math.isfinite(limit) and limit==int(limit) and 1<=limit<=20
                exact=bool(valid and type(arguments['query']) is str and function.get('name')==case['expected']['name'] and function.get('name') in {t['function']['name'] for t in wanted} and arguments['query']==case['expected']['arguments']['query'] and limit==case['expected']['arguments']['limit'])
        assert exact==row['scored']['exact'],key
        counts[(row['model'],row['condition'])]+=exact
        assert row['resident_before']==[]
    assert len(rows)==64
    summary=json.loads((ROOT/'results/summary.json').read_text())
    for group in summary['groups']:assert counts[(group['model'],group['condition'])]==group['exact']
    result={'passed':True,'measured_calls':64,'distinct_cells':len(keys),'independently_scored_calls':64,'independently_reconstructed_catalogs':64,'gold_labels_used_in_retrieval':False,
            'counts':[{'model':model,'condition':condition,'exact':value,'requests':16} for (model,condition),value in counts.items()]}
    dump(ROOT/'results/verification.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
