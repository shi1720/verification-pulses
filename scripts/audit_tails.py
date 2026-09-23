"""Post-analysis diagnostic frozen in protocol/diagnostic_03.md; offline only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import comb
from verification_pulses.dynamics import schedule, schedule_distribution, bernstein_response

rs=[json.loads(s) for s in Path('data/raw/calibration.jsonl').read_text().splitlines()]
rs=[r for r in rs if r['terminal']]
models=sorted({r['request']['model'] for r in rs})
x=np.arange(17)/16
basis=np.array([comb(3,j)*x**j*(1-x)**(3-j) for j in range(4)])
rng=np.random.default_rng(209231);rows=[];reps=5000
for model in models:
    rec=[r for r in rs if r['request']['model']==model]
    tasks=sorted({r['metadata']['task_id'] for r in rec})
    mat=np.full((96,4),np.nan)
    for r in rec:
        mat[tasks.index(r['metadata']['task_id']),r['metadata']['wrong_peers']]=float(r['answer']!=r['metadata']['truth'])
    assert np.isfinite(mat).all()
    a=mat[rng.integers(96,size=(reps,96))].mean(axis=1)
    g=a@basis;birth=(1-x)*g;death=x*(1-g)
    for name in ['early','spread','late']:
        p=np.zeros((reps,17));p[:,14]=1
        for checked in schedule(name,128,12):
            if checked:
                nxt=p*(1-x);nxt[:,:-1]+=p[:,1:]*x[1:]
            else:
                nxt=p*(1-birth-death)
                nxt[:,1:]+=p[:,:-1]*birth[:,:-1]
                nxt[:,:-1]+=p[:,1:]*death[:,1:]
            p=nxt
        assert np.allclose(p.sum(axis=1),1)
        for j in [0,137,reps-1]:
            reference,_=schedule_distribution(16,14,schedule(name,128,12),bernstein_response(a[j]))
            assert np.allclose(p[j],reference,atol=1e-12,rtol=0)
        for label,val in [('all_correct',p[:,0]),('all_wrong',p[:,-1]),('either_endpoint',p[:,0]+p[:,-1])]:
            lo,hi=np.quantile(val,[.025,.975])
            rows.append({'model':model,'schedule':name,'outcome':label,'lower':lo,'upper':hi,'bootstrap_replicates':reps})
pd.DataFrame(rows).to_csv('data/processed/tail_calibration_uncertainty.csv',index=False)
print(pd.DataFrame(rows).query("model.str.contains('nano') and schedule=='early'",engine='python').to_string(index=False))
