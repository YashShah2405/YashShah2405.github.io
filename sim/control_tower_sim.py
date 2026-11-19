"""
Line Control Tower: modeled outcome (concept project, synthetic data).

Question: on a line with one bottleneck and frequent material shortages, how much
do two planning rules reduce late orders?

  Baseline   = orders run at the bottleneck first in, first out. A shortage is found
               when the job reaches the machine, so the machine waits for material.
  Tower      = shortages are flagged a day ahead, so short jobs are skipped instead of
               blocking the machine, and ready jobs run earliest due date first.

All parameters are assumptions for a concept study. They are stated below so anyone
can change them and rerun.
"""
import numpy as np

HOURS_PER_DAY = 16          # two shifts
SIM_DAYS = 120
UTILIZATION = 0.88          # bottleneck load
MEAN_PROC_H = 3.0           # mean bottleneck hours per order
SHORTAGE_RATE = 0.22        # share of orders missing a component on arrival
SHORTAGE_DELAY_H = (8, 40)  # hours until the missing part arrives (uniform)
LEAD_TIME_DAYS = (3, 7)     # quoted due date after order release (uniform)
DOWNSTREAM_H = 6            # fixed hours after the bottleneck (test, pack)
REPLICATIONS = 400


def make_orders(rng):
    rate = UTILIZATION / MEAN_PROC_H                      # orders per hour
    horizon = SIM_DAYS * HOURS_PER_DAY
    n = rng.poisson(rate * horizon)
    arrive = np.sort(rng.uniform(0, horizon, n))
    proc = rng.lognormal(np.log(MEAN_PROC_H) - 0.18, 0.6, n)
    due = arrive + rng.uniform(*LEAD_TIME_DAYS, n) * HOURS_PER_DAY
    short = rng.random(n) < SHORTAGE_RATE
    ready = arrive + np.where(short, rng.uniform(*SHORTAGE_DELAY_H, n), 0.0)
    return arrive, proc, due, ready


def run(policy, orders):
    arrive, proc, due, ready = orders
    n = len(arrive)
    done = np.zeros(n)
    waiting = []
    t, i, finished = 0.0, 0, 0
    while finished < n:
        while i < n and arrive[i] <= t:
            waiting.append(i)
            i += 1
        if not waiting:
            t = arrive[i]
            continue
        if policy == "baseline":
            j = min(waiting, key=lambda k: arrive[k])     # first in, first out
            start = max(t, ready[j])                       # machine waits for parts
        else:
            avail = [k for k in waiting if ready[k] <= t]
            if not avail:                                  # nothing ready: jump ahead
                nxt = min(min(ready[k] for k in waiting), arrive[i] if i < n else np.inf)
                t = nxt
                continue
            j = min(avail, key=lambda k: due[k])           # earliest due date first
            start = t
        waiting.remove(j)
        t = start + proc[j]
        done[j] = t + DOWNSTREAM_H
        finished += 1
    late = done > due
    return late.mean(), np.mean(np.maximum(done - due, 0)[late]) / HOURS_PER_DAY if late.any() else 0.0


def main():
    rng = np.random.default_rng(2026)
    res = {"baseline": [], "tower": []}
    for _ in range(REPLICATIONS):
        orders = make_orders(rng)
        for p in res:
            res[p].append(run(p, orders))
    for p, rows in res.items():
        arr = np.array(rows)
        lo, hi = np.percentile(arr[:, 0], [10, 90])
        print(f"{p:9s} late orders: mean {arr[:,0].mean():.1%} (P10 {lo:.1%}, P90 {hi:.1%}); "
              f"avg lateness of late orders {arr[:,1].mean():.1f} days")


if __name__ == "__main__":
    main()
