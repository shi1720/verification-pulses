from fractions import Fraction
from itertools import product
from math import log
import numpy as np
import pytest
import sympy as sp
from verification_pulses.dynamics import (
    majority3, bernstein_response, majority_equilibria, minimum_fuel,
    transition_rates, propagate, committor, pulse_distribution, pulse_risks,
    schedule, critical_window)


def test_symbolic_saddle_node_and_operation_commutator():
    x,u,q=sp.symbols('x u q')
    g=3*x*x-2*x**3
    f=(1-u)*g-x
    assert sp.simplify(f.subs({u:sp.Rational(1,9),x:sp.Rational(3,4)}))==0
    assert sp.simplify(sp.diff(f,x).subs({u:sp.Rational(1,9),x:sp.Rational(3,4)}))==0
    assert sp.simplify(g.subs(x,q*x)-q*g-q*(1-q)*x*x*(2*(1+q)*x-3))==0


def test_equilibria_and_full_peak_fuel():
    for u in [0,.03,.1,1/9,.12,1]:
        for r in majority_equilibria(u):
            assert abs((1-u)*majority3(r)-r)<1e-12
    for x0 in [.6,.875,1.]:
        assert minimum_fuel(majority3,x0,.5)==pytest.approx(log(2*x0))
    assert minimum_fuel(majority3,.95,.5,peak=.1)==np.inf


def test_independent_exhaustive_slot_enumeration():
    # Enumerate actual update target and ordered three peer indices, independent
    # of the count-chain formula. Includes self-selection and repeated peers.
    for n in range(2,8):
        b,d=transition_rates(n)
        for i in range(n+1):
            state=[1]*i+[0]*(n-i)
            totals={-1:0,0:0,1:0}
            for target in range(n):
                for peers in product(range(n),repeat=3):
                    new=int(sum(state[j] for j in peers)>=2)
                    totals[new-state[target]]+=1
            den=n**4
            assert float(Fraction(totals[1],den))==pytest.approx(b[i])
            assert float(Fraction(totals[-1],den))==pytest.approx(d[i])


def test_pulse_distribution_exhaustive_and_moments():
    n=4;i0=3;k=5
    counts=np.zeros(n+1)
    for targets in product(range(n),repeat=k):
        state=[1]*i0+[0]*(n-i0)
        for j in targets:state[j]=0
        counts[sum(state)]+=1
    p=pulse_distribution(n,i0,k)
    assert np.allclose(p,counts/n**k)
    assert p@np.arange(n+1)==pytest.approx(i0*(1-1/n)**k)


def test_committor_independent_linear_solve():
    for n in [4,16,64]:
        b,d=transition_rates(n)
        a=np.diag(b[1:n]+d[1:n])+np.diag(-b[1:n-1],1)+np.diag(-d[2:n],-1)
        rhs=np.zeros(n-1);rhs[-1]=b[n-1]
        direct=np.r_[0,np.linalg.solve(a,rhs),1]
        h=committor(n)
        assert np.max(abs(h-direct))<1e-12
        assert np.allclose(h,1-h[::-1])
        assert np.all(np.diff(pulse_risks(n,n,4*n))<=1e-12)


def test_mass_and_schedules():
    for name in ['early','spread','late']:
        s=schedule(name,128,12)
        assert s.sum()==12
    rng=np.random.default_rng(7)
    for _ in range(30):
        a=rng.uniform(size=4);g=bernstein_response(a)
        b,d=transition_rates(16,g,u=.23,epsilon=.07)
        p=rng.dirichlet(np.ones(17));out=propagate(p,b,d)
        assert np.min(out)>=0
        assert sum(out)==pytest.approx(1.)


def test_critical_window_converges_to_exact():
    errors=[]
    for n in [64,256,1024]:
        i0=7*n//8
        ks=np.arange(int(n*log(1.75)-2*np.sqrt(n)),int(n*log(1.75)+3*np.sqrt(n)))
        exact=pulse_risks(n,i0,int(ks[-1]))[ks]
        errors.append(np.max(abs(exact-critical_window(n,ks,7/8))))
    assert errors[2]<errors[1]<errors[0]
    assert errors[-1]<.025
