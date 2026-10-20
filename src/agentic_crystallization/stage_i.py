"""v1.7 certificate audit; synthetic finite actions and known bounded perturbations."""
import argparse,csv,json,random,hashlib
from pathlib import Path
from .stability import certify_action, choose_with_fallback

def run(out:Path,seeds=range(500),n_actions=6,eps=.15):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for seed in seeds:
        rng=random.Random(170000+seed)
        truth={f'a{i}':rng.uniform(-1,1) for i in range(n_actions)}
        qhat={a:v+rng.uniform(-eps,eps) for a,v in truth.items()}
        errors={a:eps for a in truth}
        c=certify_action(qhat,errors)
        true_best=max(truth.values());chosen=c['action']
        correct=(truth[chosen]>=true_best-1e-12)
        fallback=max(qhat,key=qhat.get) # same estimate, not an independent baseline
        rows.append({'seed':seed,'eps':eps,'certified':int(c['certified']),
                     'correct':int(correct),'true_regret':round(true_best-truth[chosen],12),
                     'gap':round(c['gap'],12),'margin':round(c['margin'],12),
                     'actions':n_actions})
    with (out/'runs.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    assert all(not int(r['certified']) or int(r['correct']) for r in rows), 'certificate violation'
    result={'seeds':len(rows),'actions':n_actions,'error_bound':eps,
            'certified':sum(int(r['certified']) for r in rows),
            'uncertified':sum(not int(r['certified']) for r in rows),
            'violations':sum(int(r['certified']) and not int(r['correct']) for r in rows),
            'mean_regret':sum(r['true_regret'] for r in rows)/len(rows),
            'interpretation':'Known bounded perturbation sanity check; zero violations follow from proved inequality, not evidence of calibrated real-world bounds.'}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps({'source':'agentic_crystallization.stability','seed_start':min(seeds),'seed_end':max(seeds),'n_actions':n_actions,'eps':eps,'oracle':'known random truth, bounded independent perturbation','status':'synthetic'},indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='experiments/stage_i');p.add_argument('--seeds',type=int,default=500);p.add_argument('--eps',type=float,default=.15)
    args=p.parse_args();print(json.dumps(run(Path(args.out),range(args.seeds),eps=args.eps),indent=2))
