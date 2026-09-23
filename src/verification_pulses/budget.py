"""BasinPulse: exact check-budget calculator for a declared response model."""
import argparse
import json
import numpy as np
from .dynamics import majority3, pulse_risks, distinct_pulse_distribution, committor


def recommend(n: int, wrong: int, risk: float, distinct: bool = False):
    if not 1 <= n or not 0 <= wrong <= n or not 0 < risk < 1:
        raise ValueError("require N>=1, 0<=wrong<=N, and 0<risk<1")
    h=committor(n,majority3)
    if distinct:
        risks=np.array([distinct_pulse_distribution(n,wrong,k)@h for k in range(n+1)])
    else:
        # A union bound P(any initially wrong slot unvisited)<=wrong*(1-1/N)^K
        # bounds the required search horizon for N>1.
        limit=1 if n==1 else int(np.ceil(np.log(risk/max(wrong,1))/np.log(1-1/n)))+1
        risks=pulse_risks(n,wrong,max(1,limit),majority3)
    k=int(np.flatnonzero(risks<=risk)[0])
    return {'model':'asynchronous majority-of-three','n':n,'initial_wrong':wrong,
            'target_risk':risk,'addressing':'distinct' if distinct else 'with replacement',
            'checks':k,'exact_model_risk':float(risks[k]),
            'previous_risk':float(risks[k-1]) if k else None,
            'scope':'Pulse followed by indefinitely many ordinary updates; perfect checks. '
                    'This is a model-conditional calculation, not an empirical LLM guarantee.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n',type=int,required=True);p.add_argument('--wrong',type=int,required=True)
    p.add_argument('--risk',type=float,default=.05);p.add_argument('--distinct',action='store_true')
    args=p.parse_args();print(json.dumps(recommend(args.n,args.wrong,args.risk,args.distinct),indent=2))
