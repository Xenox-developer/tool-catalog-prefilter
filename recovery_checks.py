"""Focused continuation guards; no model inference or network."""
import copy
import json
import unittest
from unittest.mock import patch
import recover
from run import ROOT,schedule


class RecoveryChecks(unittest.TestCase):
    def test_only_completed_prefix(self):
        rows=[json.loads((ROOT/'evidence/raw.jsonl').read_text().splitlines()[0])]
        recover.validate_prefix(rows,schedule())
        for field,value in [('index',1),('resident_before',[{'name':'qwen2.5:7b'}]),('request_sha256','wrong'),('error','timeout')]:
            bad=copy.deepcopy(rows);bad[0][field]=value
            with self.assertRaises(ValueError):recover.validate_prefix(bad,schedule())
        with self.assertRaises(ValueError):recover.validate_prefix([],schedule())

    def test_wait_only_readiness(self):
        with patch.object(recover,'api',side_effect=[{'models':[{'name':'qwen2.5:7b'}]},{'models':[]}]) as api,patch.object(recover.time,'sleep'):
            _,probes=recover.wait_empty()
            self.assertEqual(len(probes),2)
            self.assertEqual(api.call_args_list,[unittest.mock.call('/api/ps'),unittest.mock.call('/api/ps')])
        with patch.object(recover,'api',return_value={'models':[{'name':'unrelated'}]}):
            with self.assertRaises(RuntimeError):recover.wait_empty()


if __name__=='__main__':unittest.main()
