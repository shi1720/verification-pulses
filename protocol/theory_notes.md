# Derivations and claim boundaries

Let g be the probability that an ordinary update writes a wrong value when
the population wrong fraction is x. Random replacement gives
dx/dt = (1-u)g(x) + u epsilon - x, with time in update sweeps and u the
fraction of updates spent on verification. Thus the fuel is integral u dt,
not elapsed time, successful corrections, or language-model tokens.

## General minimum-fuel crossing

Assume b < x0 <= h, g(b)=b, g(h)=h, and g(x)>x on (b,h).
Take epsilon < b and peak a in (0,1]. Define
D_a(x)=x-(1-a)g(x)-a epsilon.
If D_a>0 on [b,x0], the infimum fuel to enter x<b is
integral_b^x0 a/D_a(x) dx. Full-rate control attains the cost to reach b;
an arbitrarily small extension crosses it. The infimum for strict crossing
is generally not attained. Set W'=a/D_a. Then
dW/dt + u = (a-u)(g(x)-x)/D_a(x) >= 0.
Clip W to constants above x0 and below b to cover paths with excursions.
For a=1 the expression is log((x0-epsilon)/(b-epsilon)). If D_a vanishes
at an interior barrier, bounded controls cannot cross it in finite time.
This is a scalar minimum-fuel specialization, not a new general control principle.

## Finite-N exact certificate

An ordinary update has upward probability (1-x)g(x) and downward probability
x(1-g(x)). The two are positive in the interior. Standard birth-death scale
weights give the committor h_N(i) for hitting N before 0. This is eventual
wrong-consensus probability only when g(0)=0 and g(1)=1. A verification pulse
is a pure-death chain with death probability i/N. Its exact distribution pi_K
and the committor give R_N(K)=sum_i pi_K(i)h_N(i). This is computable without
Monte Carlo and avoids replacing expected contamination by a basin label.

## Critical-window law (fixed check count)

Assume g is C^3, absorbing endpoints, g(x)<x for 0<x<b and g(x)>x for
b<x<1, and lambda=g'(b)-1>0. Let i0=floor(N x0), b<x0<=1,
tau=log(x0/b), and K=floor(N tau+s sqrt(N)).
Pure-death occupancy CLT gives sqrt(N)(I_K/N-b) => Normal(-b s, v_p),
v_p=b(1-b/x0)-b^2 tau. A martingale derivation uses drift -x and
one-step innovation variance x(1-x), NOT the Poisson-clock variance x.

The exact birth-death scale ratios satisfy
d/dx log[d(x)/a(x)] at b = -lambda/[b(1-b)].
Laplace expansion of their products shows
h_N(floor(Nb+z sqrt(N))) -> Phi(z/sqrt(v_d)),
v_d=b(1-b)/lambda. This convergence is locally uniform in z; tightness
of the pulse CLT plus boundedness extends it to the mixture. Therefore
R_N(K) -> Phi(-b s/sqrt(v_p+v_d)). Quantile inversion yields
K_delta = N tau + sqrt(N(v_p+v_d))/b * Phi^{-1}(1-delta)+o(sqrt(N)).
The two variances come from duplicate verification targets and autonomous
re-amplification after the pulse. Do not use this asymptotic formula as an
exact small-population safety guarantee; the recurrence is the certificate.

For majority-of-three g=3x^2-2x^3: b=1/2, lambda=1/2, v_d=1/2.
Constant u has a saddle node at u=1/9, x=3/4. This polynomial bifurcation
is elementary and belongs to classical majority dynamics.

## No universal operation-order claim

For D(x)=3x^2-2x^3 and V(x)=q x,
D(V(x))-V(D(x))=q(1-q)x^2[2(1+q)x-3].
Its sign can change; an early weak check is not always superior to a late
check for a fixed two-operation horizon. Minimum-fuel escape is a different
objective from terminal contamination, and both must be reported.
