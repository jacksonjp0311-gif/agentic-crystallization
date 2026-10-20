"""Generate three non-misleading result figures directly from Stage M summary."""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
summary=json.loads((root/'experiments/stage_m_holdout/summary.json').read_text())
assets=root/'assets';assets.mkdir(exist_ok=True)

# Utilities include experimental computation, validation and memory costs.
regimes=['stationary','recurrent','abrupt','gradual','inverted_drift','misleading_feedback']
policies=['crystal','memoryless','periodic','fixed_reuse']
fig,ax=plt.subplots(figsize=(12.3,6.1))
x=np.arange(len(regimes));width=.2
for i,p in enumerate(policies):
    y=[summary[r][p]['mean_surplus_per_epoch'] for r in regimes]
    ax.bar(x+(i-1.5)*width,y,width,label=p.replace('_',' ').title())
ax.axhline(0,lw=.8)
ax.set_xticks(x,[r.replace('_','\n') for r in regimes]);ax.set_ylabel('Mean synthetic net task surplus / epoch')
ax.set_title('Stage M: comparative utility under feedback and distribution shift')
ax.legend(ncol=4,loc='upper right',fontsize=9)
ax.text(.02,.01,'Synthetic parity tasks; not Pegasus or real-world returns',transform=ax.transAxes,fontsize=9)
fig.tight_layout();fig.savefig(assets/'stage_m_policy_utility.png',dpi=160);plt.close(fig)

regimes=['inverted_drift','misleading_feedback','abrupt','gradual']
fig,ax=plt.subplots(figsize=(10.8,5.6))
x=np.arange(len(regimes));width=.22
for i,p in enumerate(('crystal','memoryless','periodic')):
    y=[summary[r][p]['harmful_blocks'] for r in regimes]
    ax.bar(x+(i-1)*width,y,width,label=p.replace('_',' ').title())
ax.set_xticks(x,[r.replace('_','\n') for r in regimes]);ax.set_ylabel('Harmful deployment blocks (24 worlds x 12 epochs)')
ax.set_title('Delayed and falsified feedback: harm before detection still counts')
ax.legend();fig.tight_layout();fig.savefig(assets/'stage_m_safety.png',dpi=160);plt.close(fig)

regimes=['stationary','recurrent','abrupt','inverted_drift']
fig,ax=plt.subplots(figsize=(11,5.6))
x=np.arange(len(regimes));width=.22
for i,p in enumerate(('crystal','memoryless','periodic')):
    y=[summary[r][p]['total_queries'] for r in regimes]
    ax.bar(x+(i-1)*width,y,width,label=p.replace('_',' ').title())
ax.set_xticks(x,[r.replace('_','\n') for r in regimes]);ax.set_ylabel('Charged exploratory/validation observations')
ax.set_title('Validation and rediscovery cost across adaptation policies')
ax.legend();fig.tight_layout();fig.savefig(assets/'stage_m_observation_cost.png',dpi=160);plt.close(fig)
print('Saved 3 Stage M figures')
