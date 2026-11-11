"""Audit the declared continuation and preserve the original response prefix."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from run import ROOT,sha,verify_freeze,schedule


def audit():
    verify_freeze()
    continuation=json.loads((ROOT/'evidence/continuation.json').read_text())
    assert continuation['status']=='completed' and continuation['completed_prefix']==1 and continuation['new_planned_calls']==63
    assert continuation['pending_index'] is None
    assert sha(ROOT/'recover.py')==continuation['recovery_sha256']
    assert sha(ROOT/'TRANSPORT-AMENDMENT.md')==continuation['amendment_sha256']
    assert sha(ROOT/'evidence/frozen.json')==continuation['frozen_manifest_sha256']
    lines=(ROOT/'evidence/raw.jsonl').read_bytes().splitlines(keepends=True)
    assert hashlib.sha256(b''.join(lines[:1])).hexdigest()==continuation['original_raw_sha256']
    rows=[json.loads(x) for x in lines];planned=schedule()
    assert len(rows)==64
    for index,(row,cell) in enumerate(zip(rows,planned)):
        assert row['index']==index and all(row[k]==v for k,v in cell.items())
        assert row['resident_before']==[]
        assert row['request_sha256']==hashlib.sha256(json.dumps(row['request'],sort_keys=True).encode()).hexdigest()
        assert row['response'].get('done') is True
        if index:
            assert row['residency_probes'][-1]['models']==[]
            assert row['transport_wait_seconds']>=0
            assert datetime.fromisoformat(row['response']['created_at'].replace('Z','+00:00'))>=datetime.fromisoformat(continuation['started_utc'])
    result={'passed':True,'original_prefix_unchanged':True,'scheduled_cells_in_order':64,'cold_residency_checks':64,'replayed_calls':0,'continued_calls':63,'recovery_source_hash_verified':True}
    print(json.dumps(result));return result


if __name__=='__main__':audit()
