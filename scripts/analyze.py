"""Rebuild all tables and figures from raw data; never calls an API."""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy.integrate import solve_ivp
from scipy.stats import beta
from verification_pulses.dynamics import *

OUT=Path('data/processed');FIG=Path('figures')
COLORS={'early':'#176B87','spread':'#C35A29','late':'#8059A6'}
LABELS={'early':'Early pulse','spread':'Spread checks','late':'Late pulse'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
 'axes.spines.right':False,'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':8,
 'pdf.fonttype':42,'ps.fonttype':42,'savefig.bbox':'tight','figure.dpi':140})


def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'));fig.savefig(FIG/(name+'.png'),dpi=220);plt.close(fig)


def terminal_records(path):
    out={}
    for s in path.read_text().splitlines():
        r=json.loads(s)
        if r.get('terminal'):out[r['request_id']]=r
    return list(out.values())


def theoretical_figures():
    # Classical bifurcation and equal-fuel continuous schedules.
    fig=plt.figure(figsize=(7.3,5.6));grid=fig.add_gridspec(2,2)
    axs=[fig.add_subplot(grid[0,0]),fig.add_subplot(grid[0,1]),fig.add_subplot(grid[1,:])]
    us=np.linspace(0,1/9,250)
    roots=np.array([majority_equilibria(u) for u in us])
    axs[0].plot([0,.18],[0,0],c=COLORS['early'],lw=2)
    axs[0].plot(us,roots[:,2],c=COLORS['spread'],lw=2)
    axs[0].plot(us,roots[:,1],c='#666666',ls='--')
    axs[0].scatter([1/9],[.75],c='black',s=20,zorder=5)
    axs[0].annotate(r'$u_c=1/9$',(1/9,.75),(.115,.87),fontsize=9)
    axs[0].set(xlabel='Constant verification fraction u',ylabel='Equilibrium wrong fraction',title='A  Saddle-node bifurcation',xlim=(0,.18),ylim=(-.04,1.05))
    x=np.linspace(0,1,500)
    for u in [0,.08,.14]:axs[1].plot(x,(1-u)*majority3(x)-x,label=f'u = {u:.2f}')
    axs[1].axhline(0,c='#999999',lw=.8)
    axs[1].set(xlabel='Wrong fraction x',ylabel='dx/dt',title='B  Drift under verification')
    axs[1].legend(frameon=False)
    t=np.linspace(0,8,1601);B=.75;x0=.875
    for name in ['early','spread','late']:
        cuts=[0,B,8] if name=='early' else ([0,8-B,8] if name=='late' else [0,8])
        rates=[1,0] if name=='early' else ([0,1] if name=='late' else [B/8])
        ys=[];ts=[];init=x0
        for lo,hi,u in zip(cuts[:-1],cuts[1:],rates):
            tt=t[(t>=lo)&(t<=hi)]
            sol=solve_ivp(lambda _,y:(1-u)*majority3(y)-y,[lo,hi],[init],dense_output=True,rtol=1e-10,atol=1e-12)
            ys.extend(sol.sol(tt)[0]);ts.extend(tt);init=sol.y[0,-1]
        axs[2].plot(ts,ys,label=LABELS[name],c=COLORS[name],lw=2)
    axs[2].axhline(.5,c='#999999',ls=':',lw=1)
    axs[2].set(xlabel='Time (update sweeps)',ylabel='Wrong fraction x',title='C  Equal total verification: B = 0.75',ylim=(0,1.02))
    axs[2].legend(frameon=True,facecolor='white',framealpha=1,edgecolor='none')
    fig.tight_layout(w_pad=2,h_pad=2);save(fig,'01_bifurcation')

    budget_rows=[];curve_rows=[]
    fig=plt.figure(figsize=(7.3,5.6));grid=fig.add_gridspec(2,2)
    axs=[fig.add_subplot(grid[0,0]),fig.add_subplot(grid[0,1]),fig.add_subplot(grid[1,:])]
    for n in [16,64,256,1024,4096]:
        i0=7*n//8;rs=pulse_risks(n,i0,2*n)
        k95=int(np.flatnonzero(rs<=.05)[0])
        kdet=math.ceil(n*math.log(1.75))
        budget_rows.append({'n':n,'i0':i0,'deterministic_budget':kdet,'risk_at_deterministic':rs[kdet],
            'exact_95_budget':k95,'asymptotic_95_budget':asymptotic_budget(n,7/8),
            'risk_at_075n':rs[3*n//4]})
        ks=np.arange(len(rs));scaled=(ks-n*math.log(1.75))/np.sqrt(n)
        keep=(scaled>=-3)&(scaled<=5)
        axs[0].plot(scaled[keep],rs[keep],label=f'N = {n}',lw=1.5)
        for k in ks[keep]:curve_rows.append({'n':n,'checks':k,'scaled':scaled[k],'exact_risk':rs[k],
            'asymptotic_risk':critical_window(n,k,7/8)})
    ss=np.linspace(-3,5,201)
    axs[0].plot(ss,critical_window(10000,10000*math.log(1.75)+ss*100,7/8),c='black',ls='--',lw=2,label='Critical-window limit')
    axs[0].set(xlabel=r'$(K-N\log(7/4))/\sqrt{N}$',ylabel='Eventual wrong-consensus probability',title='A  Finite-population scaling',ylim=(0,1))
    axs[0].legend(frameon=False,fontsize=7)
    bdf=pd.DataFrame(budget_rows);bdf.to_csv(OUT/'budgets.csv',index=False)
    pd.DataFrame(curve_rows).to_csv(OUT/'critical_window.csv',index=False)
    axs[1].plot(bdf.n,bdf.exact_95_budget/bdf.n,'o-',c=COLORS['early'],label='Exact 95% recovery budget')
    axs[1].plot(bdf.n,bdf.asymptotic_95_budget/bdf.n,'s--',c=COLORS['late'],label='Two-term approximation')
    axs[1].axhline(math.log(1.75),c='#777777',ls=':',label='Mean-field threshold')
    axs[1].set(xscale='log',xlabel='Population N',ylabel='Checks per slot',title='B  Recovery budgets')
    axs[1].legend(frameon=False,fontsize=7)
    n=16;i0=14;h=committor(n);ks=np.arange(33)
    axs[2].plot(ks,pulse_risks(n,i0,32),c=COLORS['early'],label='Random targets, with replacement')
    unique=[distinct_pulse_distribution(n,i0,int(k))@h if k<=n else 0 for k in ks]
    axs[2].plot(ks,unique,c=COLORS['spread'],label='Distinct targets')
    axs[2].axhline(.05,c='#777777',ls=':')
    axs[2].set(xlabel='Number of checks K',ylabel='Eventual wrong-consensus probability',title='C  Random versus distinct targets (N = 16)',ylim=(0,1))
    axs[2].legend(frameon=False,fontsize=7)
    fig.tight_layout(w_pad=2,h_pad=2);save(fig,'02_finite_population')

    fig,axs=plt.subplots(1,2,figsize=(7.3,3.0))
    fuel=[]
    peaks=np.r_[np.linspace(.112,.15,60),np.linspace(.155,1,100)]
    for eps in [0.,.05,.15]:
        vals=np.array([minimum_fuel(majority3,.875,.5,a,eps) for a in peaks])
        axs[0].plot(peaks,np.minimum(vals,8),label=fr'Verifier error $\epsilon={eps:.2f}$')
        for a,v in zip(peaks,vals):fuel.append({'peak':a,'epsilon':eps,'fuel':v})
    axs[0].set(xlabel='Peak verification fraction',ylabel='Infimum fuel to reach x = 0.5',title='A  Peak capacity matters',ylim=(0,5),xlim=(.1,1))
    axs[0].legend(frameon=False)
    qs=np.linspace(.01,.99,150);xs=np.linspace(.01,1,150)
    Q,X=np.meshgrid(qs,xs)
    C=Q*(1-Q)*X**2*(2*(1+Q)*X-3)
    axs[1].contourf(Q,X,C,levels=[-1,0,1],colors=['#DDECF1','#EBDFF3'])
    axs[1].contour(Q,X,C,levels=[0],colors='black',linewidths=1)
    axs[1].text(.25,.45,'Early check gives\nlower terminal error',fontsize=9,ha='center')
    axs[1].text(.8,.94,'Late better',fontsize=8,ha='center')
    axs[1].set(xlabel='Fraction q retained by one check',ylabel='Starting wrong fraction',title='B  Operation order can reverse')
    pd.DataFrame(fuel).to_csv(OUT/'peak_fuel.csv',index=False)
    fig.tight_layout(w_pad=2);save(fig,'03_capacity_and_order')
    return budget_rows


def calibration():
    rows=terminal_records(Path('data/raw/calibration.jsonl'))
    models=sorted({r['request']['model'] for r in rows})
    summaries=[];params={};rng=np.random.default_rng(88291)
    fig,axs=plt.subplots(1,2,figsize=(7.3,3.1))
    xx=np.linspace(0,1,301)
    for ax,model in zip(axs,models):
        rs=[r for r in rows if r['request']['model']==model]
        ids=sorted({r['metadata']['task_id'] for r in rs})
        mat=np.full((len(ids),4),np.nan)
        for r in rs:
            if r.get('answer') is not None:
                mat[ids.index(r['metadata']['task_id']),r['metadata']['wrong_peers']]=float(r['answer']!=r['metadata']['truth'])
        a=np.nanmean(mat,axis=0);params[model]=a.tolist()
        ids_boot=rng.integers(len(ids),size=(10000,len(ids)))
        boot=np.nanmean(mat[ids_boot],axis=1)
        curves=np.array([bernstein_response(v)(xx) for v in boot])
        lo,hi=np.quantile(curves,[.025,.975],axis=0)
        ax.fill_between(xx,lo,hi,alpha=.2,color=COLORS['early'])
        ax.plot(xx,bernstein_response(a)(xx),c=COLORS['early'],lw=2,label='Calibrated response')
        ax.plot(xx,majority3(xx),c='#777777',ls=':',label='Majority-of-three')
        ax.plot(xx,xx,c='black',ls='--',lw=1,label='Identity')
        eq=equilibria(a)
        for e in eq:ax.scatter([e['x']],[e['x']],facecolor=COLORS['early'] if e['stable'] else 'white',edgecolor='black',s=32,zorder=5)
        ax.set(xlabel='Population wrong fraction x',ylabel='Probability of writing wrong value g(x)',title=model.replace('-2025-04-14',''),xlim=(0,1),ylim=(0,1))
        ax.legend(frameon=False,fontsize=7)
        for k in range(4):
            n=int(np.isfinite(mat[:,k]).sum());w=int(np.nansum(mat[:,k]))
            ci=[0. if w==0 else float(beta.ppf(.025,w,n-w+1)),1. if w==n else float(beta.ppf(.975,w+1,n-w))]
            summaries.append({'model':model,'wrong_peers':k,'wrong':w,'valid':n,'attempted':len(ids),'rate':a[k], 'ci_low':ci[0],'ci_high':ci[1]})
        Path(OUT/(model+'_equilibria.json')).write_text(json.dumps(eq,indent=2)+'\n')
    fig.tight_layout(w_pad=2);save(fig,'04_calibrated_response')
    pd.DataFrame(summaries).to_csv(OUT/'calibration.csv',index=False)
    Path(OUT/'response_parameters.json').write_text(json.dumps(params,indent=2)+'\n')
    return params


def trajectories(params):
    files=sorted(Path('data/raw/episodes').glob('*.json'))
    if len(files)!=108:
        print(f'Live analysis deferred: {len(files)}/108 complete episodes.');return None
    episodes=[json.loads(p.read_text()) for p in files]
    metrics=[];summaries=[];contrasts=[];predictions=[]
    for r in episodes:
        x=np.array(r['wrong_counts'])/r['n']
        metrics.append({k:r[k] for k in ['task_id','model','schedule','domain']}|{
            'terminal_error':x[-1],'integrated_error':x[:-1].mean(),
            'all_wrong_terminal':int(x[-1]==1),'all_correct_terminal':int(x[-1]==0),
            'invalid_calls':sum(not t.get('valid',True) for t in r['updates']),
            'llm_calls':sum(not t['verification'] for t in r['updates']),
            'checks':sum(t['verification'] for t in r['updates'])})
    df=pd.DataFrame(metrics);df.to_csv(OUT/'episode_metrics.csv',index=False)
    models=sorted(params);rng=np.random.default_rng(737391)
    fig,axs=plt.subplots(2,2,figsize=(8.4,6.0))
    for c,m in enumerate(models):
        sub=df[df.model==m]
        for name in ['early','spread','late']:
            er=[r for r in episodes if r['model']==m and r['schedule']==name]
            paths=np.array([r['wrong_counts'] for r in er])/16
            mean=paths.mean(axis=0)
            boot=paths[rng.integers(18,size=(10000,18))].mean(axis=1)
            lo,hi=np.quantile(boot,[.025,.975],axis=0)
            ax=axs[0,c];tt=np.arange(129)/16
            ax.plot(tt,mean,c=COLORS[name],lw=2,label=LABELS[name]);ax.fill_between(tt,lo,hi,color=COLORS[name],alpha=.10)
            final_dist,pred=schedule_distribution(16,14,schedule(name,128,12),bernstein_response(params[m]))
            ax.plot(tt,pred,c=COLORS[name],ls='--',lw=1,alpha=.85)
            predictions.append({'model':m,'schedule':name,'terminal_predicted':pred[-1],
                'terminal_observed':mean[-1],'trajectory_mae':np.mean(abs(mean-pred)),
                'all_correct_predicted':final_dist[0],'all_correct_observed':np.mean(paths[:,-1]==0),
                'all_wrong_predicted':final_dist[-1],'all_wrong_observed':np.mean(paths[:,-1]==1)})
            rec=sub[sub.schedule==name]
            summaries.append({'model':m,'schedule':name,'n_episodes':len(rec),
                'terminal_error':rec.terminal_error.mean(),'integrated_error':rec.integrated_error.mean(),
                'all_correct':int(rec.all_correct_terminal.sum()),'all_wrong':int(rec.all_wrong_terminal.sum()),
                'invalid_calls':int(rec.invalid_calls.sum()),'llm_calls':int(rec.llm_calls.sum()),'checks':int(rec.checks.sum())})
        axs[0,c].set(xlabel='Update sweeps',ylabel='Wrong fraction',title=m.replace('-2025-04-14',''),ylim=(0,1.03))
        axs[0,c].legend(frameon=False,fontsize=7)
        pivot=sub.pivot(index='task_id',columns='schedule',values='terminal_error')
        ax=axs[1,c]
        for j,name in enumerate(['early','late']):
            delta=(pivot[name]-pivot['spread']).to_numpy()
            boot=delta[rng.integers(18,size=(10000,18))].mean(axis=1)
            # Four primary model x schedule comparisons; Bonferroni 98.75% each.
            lo,hi=np.quantile(boot,[.00625,.99375])
            contrasts.append({'model':m,'contrast':name+'-spread','mean':delta.mean(),
                              'ci_low':lo,'ci_high':hi,'confidence':.9875,'tasks':18})
            ax.scatter(np.full(18,j)+np.linspace(-.12,.12,18),delta,color=COLORS[name],alpha=.5,s=18)
            ax.errorbar(j+.22,delta.mean(),yerr=[[delta.mean()-lo],[hi-delta.mean()]],fmt='D',color='black',capsize=3)
        ax.axhline(0,c='#777777',ls='--',lw=1)
        ax.set(xticks=[0,1],xticklabels=['Early minus spread','Late minus spread'],ylabel='Paired terminal-error difference',ylim=(-1.08,1.08))
    fig.tight_layout(h_pad=2,w_pad=2);save(fig,'05_live_schedules')
    pd.DataFrame(summaries).to_csv(OUT/'live_summary.csv',index=False)
    pd.DataFrame(contrasts).to_csv(OUT/'primary_contrasts.csv',index=False)
    pd.DataFrame(predictions).to_csv(OUT/'prediction_audit.csv',index=False)
    return {'summaries':summaries,'contrasts':contrasts,'predictions':predictions}


def monte_carlo():
    rng=np.random.default_rng(3411);rows=[];reps=50000;n=16
    for name in ['early','spread','late']:
        # Direct slot simulation, independent of the birth-death recursion.
        states=np.zeros((reps,n),dtype=np.int8);states[:,:14]=1
        ar=np.arange(reps)
        for flag in schedule(name,128,12):
            target=rng.integers(n,size=reps)
            if flag:states[ar,target]=0
            else:
                peers=rng.integers(n,size=(reps,3))
                answer=(states[ar[:,None],peers].sum(axis=1)>=2)
                states[ar,target]=answer
        x=states.mean(axis=1)
        _,path=schedule_distribution(n,14,schedule(name,128,12))
        rows.append({'schedule':name,'replicates':reps,'mc_mean':x.mean(),
            'mc_se':x.std(ddof=1)/np.sqrt(reps),'exact_mean':path[-1],
            'z_error':(x.mean()-path[-1])/(x.std(ddof=1)/np.sqrt(reps))})
    pd.DataFrame(rows).to_csv(OUT/'independent_monte_carlo.csv',index=False)
    return rows


def usage():
    rows=[]
    for path in sorted(Path('data/raw').glob('*.jsonl')):
        for line in path.read_text().splitlines():
            r=json.loads(line);u=r.get('response',{}).get('usage',{})
            rows.append({'phase':path.stem,'model':r['request']['model'],'http_status':r.get('http_status'),
                'terminal':r.get('terminal',False),'valid':r.get('answer') is not None,
                'input_tokens':u.get('prompt_tokens',0),'output_tokens':u.get('completion_tokens',0)})
    df=pd.DataFrame(rows)
    agg=df.groupby(['phase','model']).agg(attempts=('terminal','size'),requests=('terminal','sum'),
        valid=('valid','sum'),input_tokens=('input_tokens','sum'),output_tokens=('output_tokens','sum')).reset_index()
    agg['estimated_uncached_usd']=[(r.input_tokens*(.4 if 'mini' in r.model else .1)+r.output_tokens*(1.6 if 'mini' in r.model else .4))/1e6 for r in agg.itertuples()]
    agg.to_csv(OUT/'usage.csv',index=False)
    return agg.to_dict(orient='records')


if __name__=='__main__':
    OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
    result={'budgets':theoretical_figures(),'params':calibration()}
    result['live']=trajectories(result['params']);result['monte_carlo']=monte_carlo();result['usage']=usage()
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
