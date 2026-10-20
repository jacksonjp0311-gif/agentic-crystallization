"""Generate Stage K evidence efficiency and safety figures from sealed summaries."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def build(summary_path:Path, asset_dir:Path):
    asset_dir.mkdir(parents=True,exist_ok=True)
    rows=json.loads(Path(summary_path).read_text())
    chosen=[r for r in rows if r['regime'] in ('stationary_easy','stationary_near_tie','bounded_shift','gradual_shift')]
    labels=['Easy','Near tie','Bounded shift','Gradual shift']
    x=np.arange(len(chosen))
    width=.27
    fig,ax=plt.subplots(figsize=(10.2,4.9),layout='constrained')
    for i,(p,label) in enumerate((('fixed','Fixed budget'),('finite','Finite-checkpoint sequential'),('unbounded','Unbounded alpha spending'))):
        heights=[r[p+'_mean_observations'] for r in chosen]
        ax.bar(x+(i-1)*width,heights,width,label=label)
    ax.set_title('Stage K — outcome evaluations required per synthetic world')
    ax.set_ylabel('Evaluated procedure outcomes')
    ax.set_xticks(x,labels)
    ax.set_ylim(0,42500)
    ax.legend(loc='upper left',fontsize=9)
    fig.savefig(asset_dir/'stage_k_evidence.png',dpi=175)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(10.2,4.9),layout='constrained')
    regimes=['stationary_easy','stationary_near_tie','bounded_shift','gradual_shift','violated_shift']
    names=['Easy','Near tie','Bounded','Gradual','False bound']
    rr=[next(r for r in rows if r['regime']==s) for s in regimes]
    x=np.arange(len(rr));w=.26
    for i,(p,label) in enumerate((('fixed','Fixed budget'),('finite','Sequential finite'),('unbounded','Sequential unbounded'))):
        ax.bar(x+(i-1)*w,[100*r[p+'_cert_rate'] for r in rr],w,label=label)
    ax.set_xticks(x,names)
    ax.set_ylabel('Worlds with best-action certificate (%)')
    ax.set_ylim(0,112)
    ax.set_title('Certification frequency is not certificate correctness')
    ax.legend(loc='upper center',ncol=3,fontsize=9)
    fig.savefig(asset_dir/'stage_k_certification.png',dpi=175)
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10.8,4.25),layout='constrained')
    names=['Easy','Near tie','Bounded','Gradual','False bound']
    vals=[r['finite_wrong_cert_count'] for r in rr]
    axes[0].bar(names,vals)
    axes[0].set_ylabel('Incorrect best-action certificates / 400 worlds')
    axes[0].set_title('Wrong certificates: violated assumptions exposed')
    axes[0].tick_params(axis='x',rotation=25)
    pct=[r['paired_mean_evidence_reduction']*100 if r['paired_mean_evidence_reduction'] is not None else 0 for r in rr]
    axes[1].bar(names,pct)
    axes[1].set_ylim(0,110)
    axes[1].set_ylabel('Mean observation reduction (%)')
    axes[1].set_title('Reduced evidence does not imply validity')
    axes[1].tick_params(axis='x',rotation=25)
    fig.savefig(asset_dir/'stage_k_safety_counterexample.png',dpi=175)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--summary',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();build(Path(a.summary),Path(a.out))
