import numpy as np, json, importlib
import control_tower_sim as m

def run(policy, orders):
    arrive, proc, due, ready = orders
    n=len(arrive); done=np.zeros(n); waiting=[]; t=0.0; i=0; fin=0
    seq, skip = policy
    while fin<n:
        while i<n and arrive[i]<=t: waiting.append(i); i+=1
        if not waiting: t=arrive[i]; continue
        key = (lambda k: due[k]) if seq=="edd" else (lambda k: arrive[k])
        if skip:
            avail=[k for k in waiting if ready[k]<=t]
            if not avail:
                t=min(min(ready[k] for k in waiting), arrive[i] if i<n else np.inf); continue
            j=min(avail,key=key); start=t
        else:
            j=min(waiting,key=key); start=max(t,ready[j])
        waiting.remove(j); t=start+proc[j]; done[j]=t+m.DOWNSTREAM_H; fin+=1
    return (done>due).mean()

pols={"FIFO, wait for parts":("fifo",False),"FIFO + shortage flags":("fifo",True),
      "Due date first, wait for parts":("edd",False),"Due date first + shortage flags":("edd",True)}
out={}
for util in (0.80,0.88,0.94):
    m.UTILIZATION=util
    rng=np.random.default_rng(11)
    acc={p:[] for p in pols}
    for _ in range(250):
        o=m.make_orders(rng)
        for p,v in pols.items(): acc[p].append(run(v,o))
    out[util]={p:round(float(np.mean(a))*100,1) for p,a in acc.items()}
    print(util,out[util])
json.dump(out,open("ct_results.json","w"),indent=1)
