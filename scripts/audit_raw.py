"""Audit saved requests and independently reconstruct every held-out state.

No API calls. Fails rather than silently accepting an incomplete experiment.
The replay uses response JSON, not the derived answer or wrong-count fields.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import numpy as np


def load(path):
    return json.loads(Path(path).read_text())


def answer(row):
    try:
        c = row['response']['choices'][0]
        o = json.loads(c['message']['content'])
        if c['finish_reason'] == 'stop' and o in ({'answer': 'A'}, {'answer': 'B'}):
            return int(o['answer'] == 'B')
    except (KeyError, TypeError, ValueError, IndexError):
        pass
    return None


def check_reports(row, task, peers):
    p = row['request']
    assert len(p['messages']) == 2
    assert [m['role'] for m in p['messages']] == ['system', 'user']
    assert p['store'] is False and p['temperature'] == .7
    assert p['max_completion_tokens'] == 40
    assert p['response_format']['json_schema']['strict'] is True
    # Exact prompt schema: all ordinary evidence must be the three prior reports.
    lines = p['messages'][1]['content'].splitlines()
    assert lines[:5] == [task['question'], 'Available values:',
        'A: '+task['values'][0], 'B: '+task['values'][1],
        'Prior assistant reports (no source record is available in this step):']
    assert lines[5:8] == [f'Report {i+1}: The recorded value is {task["values"][v]}.'
                           for i,v in enumerate(peers)]
    assert lines[8:] == ['Which value should be written to the shared register? Return answer A or B.']


def main():
    terminals = {}; totals = {}; retries = 0
    for phase, expected in [('pilot',96),('calibration',768),('trajectories',12528)]:
        rows = [json.loads(s) for s in Path(f'data/raw/{phase}.jsonl').read_text().splitlines()]
        final = [r for r in rows if r['terminal']]
        assert len(final) == expected, (phase,len(final),expected)
        assert len({r['request_id'] for r in final}) == expected
        assert all(r['attempt'] in (0,1,2) for r in rows)
        for r in rows:
            expected_sha = hashlib.sha256(json.dumps(r['request'],sort_keys=True).encode()).hexdigest()
            assert expected_sha == r['request_sha256']
            assert answer(r) == r.get('answer')
            if r.get('http_status') == 200:
                assert r['response']['model'] == r['request']['model']
                assert r['response']['usage']['total_tokens'] == sum(r['response']['usage'][k]
                    for k in ['prompt_tokens','completion_tokens'])
        terminals[phase] = {r['request_id']:r for r in final}
        totals[phase] = {'terminal':len(final),'attempts':len(rows),
                        'invalid':sum(answer(r) is None for r in final),
                        'code_revisions':sorted({r.get('git_revision','not recorded in development pilot') for r in rows})}
        if phase!='pilot':
            assert all(r['git_revision'].startswith('d7247ff') for r in rows)
        retries += len(rows)-len(final)
    model_names = {r['request']['model'] for r in terminals['calibration'].values()}
    tasks_by_split = {s:{t['id']:t for t in load(f'data/{s}_tasks.json')}
                      for s in ['pilot','calibration','heldout']}
    ids = [{t['record'] for t in ts.values()} for ts in tasks_by_split.values()]
    assert all(not ids[i]&ids[j] for i in range(3) for j in range(i+1,3))
    for phase in ['pilot','calibration']:
        tasks=tasks_by_split[phase]
        for r in terminals[phase].values():
            t=tasks[r['metadata']['task_id']];k=r['metadata']['wrong_peers']
            peers=[1-t['truth']]*k+[t['truth']]*(3-k)
            random.Random(f'{phase}:{t["id"]}:{k}').shuffle(peers)
            check_reports(r,t,peers)
        assert Counter((r['request']['model'],r['metadata']['wrong_peers']) for r in terminals[phase].values()) == Counter({(m,k):len(tasks) for m in model_names for k in range(4)})
    files=sorted(Path('data/raw/episodes').glob('*.json'))
    assert len(files)==108
    seen=set();used=set();metric_rows=[];checks=0
    for path in files:
        ep=load(path);t=tasks_by_split['heldout'][ep['task_id']]
        key=(ep['task_id'],ep['model'],ep['schedule']);assert key not in seen;seen.add(key)
        assert (ep['n'],ep['initial_wrong'],ep['steps'],ep['checks'])==(16,14,128,12)
        rng=np.random.default_rng(910000+int(t['id'].split('-')[-1]))
        state=np.array([1-t['truth']]*14+[t['truth']]*2);rng.shuffle(state)
        targets=rng.integers(16,size=128);peers=rng.integers(16,size=(128,3))
        expected_checks={'early':set(range(12)), 'late':set(range(116,128)),
                         'spread':{int((j+.5)*128/12) for j in range(12)}}[ep['schedule']]
        history=[int(sum(state!=t['truth']))]
        assert len(ep['updates'])==128
        for k,u in enumerate(ep['updates']):
            assert u['step']==k and u['target']==targets[k]
            assert u['peer_ids']==peers[k].tolist()
            assert u['wrong_before']==history[-1]
            assert u['wrong_peers']==sum(state[peers[k]]!=t['truth'])
            assert u['verification']==(k in expected_checks)
            if k in expected_checks:
                assert u['source']==t['source'];state[targets[k]]=t['truth'];checks+=1
            else:
                rid=u['request_id'];assert rid not in used;used.add(rid)
                r=terminals['trajectories'][rid]
                check_reports(r,t,state[peers[k]].tolist())
                assert r['metadata']=={kk:vv for kk,vv in u.items() if kk not in ('verification','request_id','valid')}
                v=answer(r);assert u['valid']==(v is not None)
                if v is not None:state[targets[k]]=v
            history.append(int(sum(state!=t['truth'])))
        assert history==ep['wrong_counts']
        metric_rows.append({'task_id':ep['task_id'],'model':ep['model'],'schedule':ep['schedule'],
            'terminal_error':history[-1]/16,'integrated_error':sum(history[:-1])/(128*16)})
    assert len(used)==12528 and checks==1296
    assert seen=={(t,m,s) for t in tasks_by_split['heldout'] for m in model_names for s in ['early','spread','late']}
    if Path('data/processed/episode_metrics.csv').exists():
        import pandas as pd
        a=pd.DataFrame(metric_rows).set_index(['task_id','model','schedule']).sort_index()
        b=pd.read_csv('data/processed/episode_metrics.csv').set_index(['task_id','model','schedule']).sort_index()
        assert np.allclose(a,b[a.columns],atol=1e-15,rtol=0)
    out={'status':'passed','phases':totals,'episodes_replayed':len(files),
         'ordinary_updates_replayed':len(used),'verified_updates_replayed':checks,
         'transport_retry_attempts':retries,'distinct_task_records':sum(map(len,tasks_by_split.values()))}
    Path('data/processed/raw_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
