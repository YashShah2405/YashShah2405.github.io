# Yash Shah Portfolio

Source for my portfolio site. It is a single `index.html` with no build step.

## Model code

The two concept case studies on the site report modeled results. The code behind them is in `sim/`:

| File | What it models |
| --- | --- |
| `sim/control_tower_sim.py` | A line with one bottleneck and material shortages. Compares first in, first out against shortage flags plus due date sequencing. |
| `sim/sensitivity.py` | The same model split into four rules across three bottleneck load levels (results in `sim/ct_results.json`). |
| `sim/fleet_launch_cpm.py` | Critical path and Monte Carlo comparison of a sequential robot deployment against the Fleet Launch Kit plan. |

Every assumption is a named constant at the top of each file. Run with Python 3 and NumPy:

```
python3 sim/control_tower_sim.py
python3 sim/sensitivity.py
python3 sim/fleet_launch_cpm.py
```

The companies in the concept studies are fictional. Their numbers come from these models, not from client work.
