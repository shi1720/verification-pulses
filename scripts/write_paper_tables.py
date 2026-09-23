"""Generate manuscript numbers from complete saved analysis outputs."""
import json
from pathlib import Path
import pandas as pd

P=Path('data/processed');commands={}
def put(name,body):commands[name]=body
def model(s):return 'Mini' if 'mini' in s else 'Nano'
def rows(vals):return '\n'.join(' & '.join(v)+r'\\' for v in vals)
def f(x):return f'{x:.3f}'

results=json.loads((P/'results.json').read_text())
assert results['live'] is not None, 'The held-out experiment is not complete.'
b=pd.read_csv(P/'budgets.csv');mc=pd.read_csv(P/'independent_monte_carlo.csv')
put('DetRecoverySixteen',f'{100*(1-b.iloc[0].risk_at_deterministic):.2f}')
put('MaxMCZ',f'{abs(mc.z_error).max():.2f}')
put('BudgetRows',rows([[str(int(r.n)),str(int(r.deterministic_budget)),f(r.risk_at_deterministic),
    str(int(r.exact_95_budget)),f'{r.asymptotic_95_budget:.2f}'] for r in b.itertuples()]))
l=pd.read_csv(P/'live_summary.csv');c=pd.read_csv(P/'primary_contrasts.csv')
assert len(l)==6 and len(c)==4 and (l.n_episodes==18).all()
put('LiveRows',rows([[model(r.model),r.schedule.capitalize(),f(r.terminal_error),f(r.integrated_error),
    str(r.all_correct),str(r.all_wrong)] for r in l.itertuples()]))
put('ContrastRows',rows([[model(r.model),r.contrast.replace('-',' minus '),f(r.mean),f(r.ci_low),f(r.ci_high)] for r in c.itertuples()]))
sentences=[]
for m in l.model.unique():
    v=l[l.model==m].set_index('schedule')
    sentences.append(f"For {model(m).lower()}, mean terminal wrong fractions were {f(v.loc['early','terminal_error'])} (early), {f(v.loc['spread','terminal_error'])} (spread), and {f(v.loc['late','terminal_error'])} (late).")
assert ((c.ci_low<=0)&(c.ci_high>=0)).all(), 'Update the interpretation if regenerating with new experimental data.'
sentences.append('All four adjusted intervals include zero. The observed means therefore do not establish a schedule advantage at the declared family level. The direction of the early-minus-spread mean also differs between models. Integrated error and terminal error measure different objectives; in particular, the late pulse benefits from acting immediately before the terminal measurement.')
put('LiveResultsText',' '.join(sentences))
p=pd.read_csv(P/'prediction_audit.csv')
put('PredictionText',f"Across the six model--schedule combinations, mean absolute trajectory discrepancies ranged from {p.trajectory_mae.min():.3f} to {p.trajectory_mae.max():.3f}; absolute terminal discrepancies ranged from {abs(p.terminal_observed-p.terminal_predicted).min():.3f} to {abs(p.terminal_observed-p.terminal_predicted).max():.3f}. Appendix~\\ref{{app:experiment}} reports every comparison.")
put('PredictionTable',r'''\begin{table}[h]
\centering\small
\caption{Independently calibrated finite-state predictions and held-out means. MAE is averaged over the 129 recorded states.}
\begin{tabular}{llrrr}\toprule
Model & Schedule & Predicted final & Observed final & Trajectory MAE\\\midrule
'''+rows([[model(r.model),r.schedule.capitalize(),f(r.terminal_predicted),f(r.terminal_observed),f(r.trajectory_mae)] for r in p.itertuples()])+r'''
\bottomrule\end{tabular}\end{table}
\begin{table}[htb]
\centering\small
\caption{Post-analysis terminal-distribution audit. Entries are endpoint probabilities, not eventual absorption probabilities. Observed values are proportions of 18 episodes.}
\begin{tabular}{llrrrr}\toprule
& & \multicolumn{2}{c}{All correct} & \multicolumn{2}{c}{All wrong}\\
Model & Schedule & Predicted & Observed & Predicted & Observed\\\midrule
'''+rows([[model(r.model),r.schedule.capitalize(),f(r.all_correct_predicted),f(r.all_correct_observed),f(r.all_wrong_predicted),f(r.all_wrong_observed)] for r in p.itertuples()])+r'''
\bottomrule\end{tabular}\end{table}''')
t=pd.read_csv(P/'tail_calibration_uncertainty.csv')
t=t[(t.model.str.contains('nano'))&(t.schedule=='early')&(t.outcome=='either_endpoint')].iloc[0]
put('TailLower',f(t.lower));put('TailUpper',f(t.upper))
u=pd.read_csv(P/'usage.csv')
assert u.requests.sum()==13392
invalid=int(u.requests.sum()-u.valid.sum());extra=int(u.attempts.sum()-u.requests.sum())
put('UsageText',f"There were {int(u.requests.sum()):,} terminal requests, {int(u.valid.sum()):,} valid structured answers, and {invalid} invalid terminal outputs. The logs contain {extra} additional transport attempts. These attempts are included in Table~\\ref{{tab:usage}}.")
put('UsageRows',rows([[r.phase.capitalize(),model(r.model),f'{r.attempts:,}',f'{r.requests:,}',f'{r.input_tokens:,}',f'{r.output_tokens:,}'] for r in u.itertuples()]))
put('EstimatedCost',f'{u.estimated_uncached_usd.sum():.4f}')
Path('paper/generated.tex').write_text('% Generated from data/processed; do not edit numerical values manually.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in commands.items()))
print('Generated',len(commands),'manuscript commands from completed results.')
