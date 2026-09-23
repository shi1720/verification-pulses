from verification_pulses.budget import recommend
from verification_pulses.dynamics import *
import numpy as np


def test_budget_certificate_and_distinct_targets():
    for n in [8,16,64]:
        d=recommend(n,7*n//8,.05)
        assert d['exact_model_risk']<=.05<d['previous_risk']
        unique=recommend(n,7*n//8,.05,True)
        assert unique['checks']<=d['checks']
        assert distinct_pulse_distribution(n,7*n//8,n)[0]==1
    assert recommend(1,1,.05)['checks']==1
    assert recommend(8,0,.05)['checks']==0


def test_herding_threshold():
    # g_a=(1-a)x+a majority3(x); the directed-reset saddle node is
    # u_c=a/(8+a), x=3/4, for every a>0.
    for a in [.1,.3,.7,1.]:
        g=lambda x:(1-a)*x+a*majority3(x)
        u=a/(8+a)
        assert abs((1-u)*g(.75)-.75)<1e-13
        dx=1e-5
        assert abs(((1-u)*g(.75+dx)-(.75+dx)-(1-u)*g(.75-dx)+(.75-dx))/(2*dx))<1e-8
        assert abs(minimum_fuel(g,.875,.5)-np.log(1.75))<1e-10
