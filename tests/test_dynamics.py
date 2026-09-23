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
    assert minimum_fuel(majority3,.95,.5,peak=1/9)==np.inf
    assert np.isfinite(minimum_fuel(majority3,.95,.5,peak=.112))


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


def test_asymmetric_boundary_and_fixed_count_variance():
    # The theorem is not confined to a symmetric 1/2 boundary. This cubic is
    # a valid [0,1]-valued response with its sole interior crossing at b.
    b=.37;c=1.4;x0=.83
    def response(x):return x+c*x*(1-x)*(x-b)
    slope=c*b*(1-b)
    errors=[]
    for n in [256,1024,4096]:
        ks=np.arange(int(n*log(x0/b)-np.sqrt(n)),int(n*log(x0/b)+2*np.sqrt(n)))
        exact=pulse_risks(n,int(n*x0),int(ks[-1]),response)[ks]
        errors.append(np.max(abs(exact-critical_window(n,ks,x0,b,slope))))
    assert errors[2]<errors[1]<errors[0]
    assert errors[-1]<.03
    n=19;i0=16;k=13
    p=pulse_distribution(n,i0,k);r=np.arange(n+1);survival=(1-1/n)**k
    variance=i0*survival*(1-survival)+i0*(i0-1)*((1-2/n)**k-survival**2)
    assert p@r**2-(p@r)**2==pytest.approx(variance,abs=1e-12)


def test_identical_drift_different_innovation_variance():
    x=sp.symbols('x');g=3*x**2-2*x**3
    ar=(1-x)*g;dr=x*(1-g)
    af=x**2*(1-x);df=x*(1-x)**2
    assert sp.expand(ar-dr-af+df)==0
    assert (ar+dr).subs(x,sp.Rational(1,2))==sp.Rational(1,2)
    assert (af+df).subs(x,sp.Rational(1,2))==sp.Rational(1,4)
