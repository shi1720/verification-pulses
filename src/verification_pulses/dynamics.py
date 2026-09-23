"""Exact scalar and finite-population dynamics (no language model calls)."""
from __future__ import annotations
from math import comb, log, sqrt
import numpy as np
from numpy.polynomial import Polynomial
from scipy.integrate import quad
from scipy.special import ndtr, ndtri, logsumexp


def majority3(x):
    x = np.asarray(x)
    return x*x*(3-2*x)


def bernstein_response(coefficients):
    a = np.asarray(coefficients, dtype=float)
    n = len(a)-1
    if np.any((a < 0) | (a > 1)):
        raise ValueError("response probabilities must lie in [0,1]")
    def response(x):
        x = np.asarray(x)
        return sum(a[k]*comb(n,k)*x**k*(1-x)**(n-k) for k in range(n+1))
    return response


def response_polynomial(coefficients):
    n = len(coefficients)-1
    p = Polynomial([0.])
    for k, a in enumerate(coefficients):
        p += a*comb(n,k)*Polynomial([0.,1.])**k*Polynomial([1.,-1.])**(n-k)
    return p


def equilibria(coefficients, u=0., epsilon=0.):
    p = (1-u)*response_polynomial(coefficients)+Polynomial([u*epsilon,-1.])
    results = []
    for z in p.roots():
        if abs(z.imag) < 1e-8 and -1e-9 <= z.real <= 1+1e-9:
            x = float(np.clip(z.real, 0, 1))
            results.append({"x":x, "slope":float(p.deriv()(x)), "stable":bool(p.deriv()(x)<0)})
    return sorted(results, key=lambda r:r["x"])


def majority_equilibria(u):
    roots = [0.]
    if 0 <= u <= 1/9:
        d = sqrt(max(0., 9-8/(1-u)))
        roots.extend([(3-d)/4, (3+d)/4])
    return roots


def minimum_fuel(response, x0, boundary, peak=1., epsilon=0.):
    if not 0 <= epsilon < boundary < x0 <= 1 or not 0 < peak <= 1:
        raise ValueError("require 0 <= epsilon < boundary < x0 <= 1 and 0 < peak <= 1")
    denominator = lambda x: x-(1-peak)*response(x)-peak*epsilon
    grid = np.linspace(boundary, x0, 10001)
    if np.min(denominator(grid)) <= 0:
        return np.inf
    return quad(lambda x: peak/denominator(x), boundary, x0, epsabs=1e-11, epsrel=1e-11)[0]


def transition_rates(n, response=majority3, u=0., epsilon=0.):
    x = np.arange(n+1)/n
    p = (1-u)*response(x)+u*epsilon
    return (1-x)*p, x*(1-p)


def propagate(dist, birth, death):
    out = dist*(1-birth-death)
    out[1:] += dist[:-1]*birth[:-1]
    out[:-1] += dist[1:]*death[1:]
    return out


def committor(n, response=majority3):
    """Probability of hitting N before 0; endpoints are stopping boundaries.

    With nonzero endpoint mutation this is a first-hit probability, NOT an
    eventual absorbing-consensus probability.
    """
    birth, death = transition_rates(n, response)
    if np.any(birth[1:n] <= 0) or np.any(death[1:n] <= 0):
        raise ValueError("strictly positive interior transition rates required")
    lw = np.r_[0., np.cumsum(np.log(death[1:n])-np.log(birth[1:n]))]
    w = np.exp(lw-logsumexp(lw))
    return np.r_[0., np.cumsum(w)]


def pulse_distribution(n, i0, checks):
    p = np.zeros(n+1); p[i0] = 1.
    birth, death = transition_rates(n, u=1.)
    for _ in range(checks):
        p = propagate(p,birth,death)
    return p


def pulse_risks(n, i0, max_checks, response=majority3):
    h = committor(n,response)
    p = np.zeros(n+1); p[i0]=1.
    birth,death=transition_rates(n,u=1.)
    out=[]
    for k in range(max_checks+1):
        out.append(float(p@h))
        p=propagate(p,birth,death)
    return np.asarray(out)


def critical_window(n, checks, x0, boundary=.5, slope=.5):
    tau=log(x0/boundary)
    pulse_var=boundary*(1-boundary/x0)-boundary**2*tau
    escape_var=boundary*(1-boundary)/slope
    s=(np.asarray(checks)-n*tau)/sqrt(n)
    return ndtr(-boundary*s/sqrt(pulse_var+escape_var))


def asymptotic_budget(n, x0, risk=.05, boundary=.5, slope=.5):
    tau=log(x0/boundary)
    v=boundary*(1-boundary/x0)-boundary**2*tau+boundary*(1-boundary)/slope
    return n*tau+sqrt(n*v)/boundary*ndtri(1-risk)


def schedule(name, steps, checks):
    if not 0 <= checks <= steps:
        raise ValueError("invalid check budget")
    s=np.zeros(steps,dtype=bool)
    if checks == 0:
        return s
    if name == "early":
        s[:checks]=True
    elif name == "late":
        s[-checks:]=True
    elif name == "spread":
        s[np.floor((np.arange(checks)+.5)*steps/checks).astype(int)]=True
    else:
        raise ValueError(name)
    assert s.sum()==checks
    return s


def schedule_distribution(n, i0, flags, response=majority3, epsilon=0.):
    p=np.zeros(n+1);p[i0]=1
    ordinary=transition_rates(n,response)
    verified=transition_rates(n,response,u=1,epsilon=epsilon)
    path=[i0/n]
    for check in flags:
        p=propagate(p,*(verified if check else ordinary))
        path.append(float(p@np.arange(n+1)/n))
    return p,np.asarray(path)
