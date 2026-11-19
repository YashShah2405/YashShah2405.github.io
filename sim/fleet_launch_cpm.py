"""
Fleet Launch Kit: modeled outcome (concept project, assumed task durations).

Compares a sequential deployment against the Fleet Launch Kit plan, where the site
readiness scorecard and customer samples arrive at kickoff so the lab build, the
site survey and customer site fixes run in parallel.

Durations are triangular (low, likely, high) in weeks. They are assumptions for a
concept study, stated here so anyone can change them and rerun.
"""
import numpy as np

BASELINE = {   # task: (low, likely, high), predecessors
    "Kickoff and requirements": ((0.8, 1.0, 1.5), []),
    "Site survey":              ((0.8, 1.0, 1.5), ["Kickoff and requirements"]),
    "Lab build and tuning":     ((2.5, 3.0, 4.5), ["Site survey"]),
    "Ship and install":         ((0.8, 1.0, 1.5), ["Lab build and tuning"]),
    "Site fixes found at install": ((1.0, 1.5, 3.0), ["Ship and install"]),
    "Commissioning and SAT":    ((1.0, 1.5, 2.5), ["Site fixes found at install"]),
    "Ramp to target rate":      ((0.8, 1.0, 2.0), ["Commissioning and SAT"]),
}

KIT = {
    "Kickoff with readiness scorecard": ((0.8, 1.0, 1.5), []),
    "Site survey (scorecard)":  ((0.3, 0.5, 1.0), ["Kickoff with readiness scorecard"]),
    "Lab build from customer samples": ((2.5, 3.0, 4.5), ["Kickoff with readiness scorecard"]),
    "Customer site fixes":      ((1.0, 1.5, 3.0), ["Site survey (scorecard)"]),
    "Ship and install":         ((0.8, 1.0, 1.5), ["Lab build from customer samples", "Customer site fixes"]),
    "Commissioning and SAT (pre-agreed script)": ((0.8, 1.0, 1.5), ["Ship and install"]),
    "Ramp to target rate":      ((0.8, 1.0, 2.0), ["Commissioning and SAT (pre-agreed script)"]),
}


def finish(plan, dur):
    end = {}
    for task, (_, preds) in plan.items():          # dicts are in topological order
        start = max((end[p] for p in preds), default=0.0)
        end[task] = start + dur[task]
    return end


def schedule(plan):
    likely = {t: d[1] for t, (d, _) in plan.items()}
    end = finish(plan, likely)
    out = []
    for t, (d, _) in plan.items():
        out.append((t, round(end[t] - d[1], 2), d[1]))
    return out, max(end.values())


def monte_carlo(plan, rng, n=20000):
    totals = np.empty(n)
    for k in range(n):
        dur = {t: rng.triangular(*d) for t, (d, _) in plan.items()}
        totals[k] = max(finish(plan, dur).values())
    return np.percentile(totals, [50, 80])


def main():
    rng = np.random.default_rng(7)
    for name, plan in (("Baseline", BASELINE), ("Launch Kit", KIT)):
        rows, total = schedule(plan)
        p50, p80 = monte_carlo(plan, rng)
        print(f"{name}: likely {total:.1f} wk, P50 {p50:.1f} wk, P80 {p80:.1f} wk")
        for t, s, d in rows:
            print(f"   {t:45s} start {s:4.1f}  dur {d:3.1f}")


if __name__ == "__main__":
    main()
