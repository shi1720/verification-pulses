import argparse
import asyncio
import json
import random
from pathlib import Path
import numpy as np
from verification_pulses.api import Recorder
from verification_pulses.tasks import make_tasks, messages
from verification_pulses.dynamics import schedule
from run_calibration import MODELS

N, STEPS, CHECKS, I0 = 16,128,12,14


async def episode(recorder,task,model,name):
    seed=910000+int(task['id'].split('-')[-1])
    rng=np.random.default_rng(seed)
    state=np.array([1-task['truth']]*I0+[task['truth']]*(N-I0))
    rng.shuffle(state)
    targets=rng.integers(N,size=STEPS)
    peer_ids=rng.integers(N,size=(STEPS,3))
    flags=schedule(name,STEPS,CHECKS)
    path=[int(np.sum(state!=task['truth']))]
    records=[]
    for step in range(STEPS):
        j=int(targets[step]);peers=state[peer_ids[step]].tolist()
        meta={'task_id':task['id'],'domain':task['domain'],'truth':task['truth'],
              'schedule':name,'step':step,'target':j,'peer_ids':peer_ids[step].tolist(),
              'wrong_before':path[-1], 'wrong_peers':sum(a!=task['truth'] for a in peers)}
        if flags[step]:
            # The verifier is a deterministic source lookup, with no LLM call.
            value=task['source']['value']
            state[j]=task['values'].index(value)
            records.append({**meta,'verification':True,'source':task['source']})
        else:
            rid=f"live:{model}:{task['id']}:{name}:{step}"
            r=await recorder.call(rid,model,messages(task,peers),meta)
            if r.get('answer') is not None:
                state[j]=r['answer']
            records.append({**meta,'verification':False,'request_id':rid,
                            'valid':r.get('answer') is not None})
        path.append(int(np.sum(state!=task['truth'])))
    return {'task_id':task['id'],'domain':task['domain'],'model':model,'schedule':name,
            'n':N,'initial_wrong':I0,'steps':STEPS,'checks':CHECKS,'seed':seed,
            'wrong_counts':path,'updates':records}


async def main(args):
    tasks=make_tasks(771309,18,'heldout')
    Path('data/heldout_tasks.json').write_text(json.dumps(tasks,indent=2)+'\n')
    recorder=Recorder(Path('data/raw/trajectories.jsonl'),args.key_file,args.concurrency)
    specs=[(t,m,s) for t in tasks for m in MODELS for s in ['early','spread','late']]
    random.Random(593).shuffle(specs)
    done=0
    async def run(spec):
        nonlocal done
        row=await episode(recorder,*spec)
        name=f"{row['model']}_{row['task_id']}_{row['schedule']}.json"
        path=Path('data/raw/episodes')/name
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(row,indent=2)+'\n')
        done+=1
        print(f"episodes completed: {done}/{len(specs)}",flush=True)
    try:
        await asyncio.gather(*(run(s) for s in specs))
    finally:
        await recorder.close()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--key-file');p.add_argument('--concurrency',type=int,default=8)
    asyncio.run(main(p.parse_args()))
