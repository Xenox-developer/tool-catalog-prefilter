import copy
import json
import unittest

from fixtures import catalog,cases
from tool_lab import score,select_tools


def response(name,arguments):
    return {'done':True,'message':{'tool_calls':[{'function':{'name':name,'arguments':arguments}}]}}


class Acceptance(unittest.TestCase):
    def test_catalog_and_gold_controls(self):
        tools=catalog();self.assertEqual(len(tools),64)
        names={x['function']['name'] for x in tools};self.assertEqual(len(names),64)
        for case in cases():
            expected=case['expected'];self.assertIn(expected['name'],names)
            for args in (expected['arguments'],json.dumps(expected['arguments']),{**expected['arguments'],'limit':float(expected['arguments']['limit'])}):
                result=score(response(expected['name'],args),expected)
                self.assertTrue(result['exact']);self.assertTrue(result['name_correct']);self.assertTrue(result['valid_single_call'])

    def test_negative_controls(self):
        for case in cases():
            e=case['expected']
            bad=[response('wrong_tool',e['arguments']),response(e['name'],{'query':'WRONG','limit':e['arguments']['limit']}),
                 response(e['name'],{'query':e['arguments']['query'],'limit':True}),
                 response(e['name'],{'query':e['arguments']['query'],'limit':e['arguments']['limit']+0.5}),
                 response(e['name'],{'query':e['arguments']['query'],'limit':e['arguments']['limit']+1}),
                 response(e['name'],{**e['arguments'],'extra':0}),response(e['name'],'not json'),
                 {},{'message':{'content':'a tool call in prose'}},response(e['name'],[])]
            duplicated=response(e['name'],e['arguments']);duplicated['message']['tool_calls']*=2;bad.append(duplicated)
            for value in bad:
                self.assertFalse(score(value,e)['exact'],(case['id'],value))

    def test_retrieval_overlap_and_tie_order(self):
        def tool(name,description): return {'type':'function','function':{'name':name,'description':description,'parameters':{}}}
        tools=[tool('zeta_read','blue blue'),tool('alpha_read','blue green'),tool('beta_read','green')]
        before=copy.deepcopy(tools)
        self.assertEqual([t['function']['name'] for t in select_tools('BLUE green green',tools,2)],['alpha_read','beta_read'])
        self.assertEqual([t['function']['name'] for t in select_tools('the to return',tools,2)],['alpha_read','beta_read'])
        self.assertEqual(tools,before)
        self.assertEqual(select_tools('blue',tools,0),[])

    def test_scoring_input_not_mutated(self):
        e=cases()[0]['expected'];r=response(e['name'],e['arguments']);before=copy.deepcopy(r)
        score(r,e);self.assertEqual(r,before)

    def test_hallucinated_unavailable_gold_tool_is_not_success(self):
        e=cases()[0]['expected']
        self.assertFalse(score(response(e['name'],e['arguments']),e,['other_available_tool'])['exact'])
        self.assertFalse(score(response(e['name'],e['arguments']),e,[])['tool_available'])
        self.assertTrue(score(response(e['name'],e['arguments']),e,[e['name']])['exact'])

    def test_incomplete_and_malformed_calls(self):
        e=cases()[0]['expected']
        r=response(e['name'],e['arguments']);r['done']=False
        self.assertFalse(score(r,e)['exact'])
        for value in [None,[],{'done':True,'message':None},{'done':True,'message':{'tool_calls':[None]}},response('',e['arguments'])]:
            self.assertFalse(score(value,e)['exact'])


if __name__=='__main__':unittest.main()
