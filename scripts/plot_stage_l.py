"""Regenerate v2.0 scientific plots and the explanatory README banner."""
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)


def plot_results():
    summary=json.loads((ROOT/'experiments/stage_l_holdout/summary.json').read_text())
    regimes=['stationary','recurrent','abrupt','noise','bounded_shift','false_shift']
    policies=['crystal','memoryless','reuse_only','baseline']
    fig,ax=plt.subplots(figsize=(11,5.1))
    x=np.arange(len(regimes))
    w=0.2
    for i,policy in enumerate(policies):
        a=[summary[rg][policy]['mean_surplus_per_epoch'] for rg in regimes]
        ax.bar(x+(i-1.5)*w,a,w,label=policy.replace('_',' ').title())
    ax.axhline(0,linewidth=1)
    ax.set_xticks(x, [r.replace('_',' ').title() for r in regimes],rotation=12)
    ax.set_ylabel('Mean synthetic net surplus per epoch (units)')
    ax.set_title('v2.0 closed-loop results — independent 40-world holdout')
    ax.legend(ncol=4,loc='upper center',fontsize=9)
    fig.tight_layout()
    fig.savefig(ASSETS/'stage_l_results.png',dpi=160)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(10,5.0))
    regimes=['stationary','recurrent','abrupt','bounded_shift','noise']
    x=np.arange(len(regimes));width=0.32
    a=[summary[r]['crystal']['total_prediction_ops'] for r in regimes]
    b=[summary[r]['memoryless']['total_prediction_ops'] for r in regimes]
    ax.bar(x-width/2,np.array(a)/1e6,width,label='Crystal memory + verification')
    ax.bar(x+width/2,np.array(b)/1e6,width,label='Rebuild from scratch + verification')
    ax.set_xticks(x,[v.replace('_',' ').title() for v in regimes])
    ax.set_ylabel('Millions of candidate-prediction operations')
    ax.set_title('Measured search work on identical held-out worlds')
    ax.legend()
    fig.tight_layout();fig.savefig(ASSETS/'stage_l_search_cost.png',dpi=160);plt.close(fig)

    fig,ax=plt.subplots(figsize=(10,4.0))
    regimes=['stationary','recurrent','abrupt','noise','bounded_shift','unknown_shift','false_shift']
    wrong=[summary[r]['crystal']['false_certifications'] for r in regimes]
    cert=[summary[r]['crystal']['certified'] for r in regimes]
    x=np.arange(len(regimes))
    ax.bar(x-.2,cert,.4,label='Certificates issued')
    ax.bar(x+.2,wrong,.4,label='False certificates')
    ax.set_xticks(x,[v.replace('_',' ').title() for v in regimes],rotation=15)
    ax.set_title('Safety boundary: incorrect shift assumptions invalidate certificates')
    ax.set_ylabel('Episode count (40 worlds × 12 epochs)')
    ax.legend()
    fig.tight_layout();fig.savefig(ASSETS/'stage_l_shift_failure.png',dpi=160);plt.close(fig)


def banner():
    # This is a decorative abstract workflow illustration, not scientific data.
    fig=plt.figure(figsize=(14,3.6),facecolor='#0d1628')
    ax=fig.add_axes((0,0,1,1));ax.set_facecolor('#0d1628');ax.set_xlim(0,14);ax.set_ylim(0,3.6);ax.axis('off')
    nodes=[(1.2,1.15),(2.2,1.85),(3.2,1.15),(4.2,2.05),(5.2,1.15),(6.2,1.8),
           (7.3,1.15),(8.3,2.05),(9.4,1.15),(10.5,1.8),(11.4,1.2),(12.4,2.1)]
    for i in range(len(nodes)-1):
        x,y=nodes[i];xx,yy=nodes[i+1]
        ax.plot([x,xx],[y,yy],color='#2c647d',linewidth=2,alpha=.65)
        if i+2<len(nodes):
            tx,ty=nodes[i+2]
            ax.plot([x,tx],[y,ty],color='#23405d',linewidth=.65,alpha=.4)
    for i,(x,y) in enumerate(nodes):
        ax.scatter(x,y,s=100+(i%3)*45,c='#5dd4d1' if i%3 else '#aac5f1',zorder=3)
    ax.text(.42,3.02,'AGENTIC  CRYSTALLIZATION',color='white',fontsize=21,fontweight='bold')
    ax.text(.45,2.58,'v2.0  /  CERTIFIED PROCEDURES  /  RECURRENT ADAPTATION',color='#97bfd7',fontsize=10)
    ax.text(.48,.30,'PROPOSE   →   EVALUATE   →   CERTIFY   →   RETAIN   →   REVALIDATE   →   HOLD',
            color='#d0e0ef',fontsize=10.4)
    fig.savefig(ASSETS/'crystal_banner.png',dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)

if __name__=='__main__':
    plot_results();banner()
    print('Created',*[p.name for p in sorted(ASSETS.glob('stage_l_*.png'))], 'crystal_banner.png')
