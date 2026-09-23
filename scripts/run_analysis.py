"""Reproduce every number quoted in the README / case study.

    python scripts/run_analysis.py [path/to/export.csv|xlsx]   > results.md
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import pipeline, roi  # noqa: E402
from core import stats as S  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "synthetic_survey_v2_SYNTHETIC.csv"
raw = pd.read_excel(src) if src.suffix == ".xlsx" else pd.read_csv(src)
A = pipeline.run(raw, n_boot=5000)

print(f"# Results — {src.name}\n")
print("## Cleaning flow\n"); print(A.flow.to_markdown(index=False))
print("\n## Quality audit\n"); print(f"**{A.verdict}**\n")
for c in A.checks:
    print(f"- {c.status.upper()} · {c.name}: {c.value}")
print("\n## Reliability\n"); print(A.reliability[["Construct", "Items", "Cronbach α", "Verdict"]].to_markdown(index=False))
print("\n## Correlations\n"); print(A.r.round(2).to_markdown())
m = A.trust_model
print(f"\n## Model 1 — Trust  (R²={m.r2:.3f}, adj={m.adj_r2:.3f}, F={m.f:.1f}, n={m.n})\n")
print(m.table.round(3).to_markdown(index=False))
u = A.usage_model
print(f"\n## Model 2 — Usage ~ Trust (R²={u.r2:.3f})\n"); print(u.table.round(3).to_markdown(index=False))
f = A.full_model
print(f"\n## Model 3 — Usage ~ Trust + REL + BUS (R²={f.r2:.3f})\n"); print(f.table.round(3).to_markdown(index=False))
print("\n## Hypotheses\n"); print(A.hypotheses.round(4).to_markdown(index=False))
print("\n## Mediation (5,000 bootstrap)\n")
for md in A.mediations:
    print(f"- {S.CONSTRUCTS[md.x]} → Trust → Usage: indirect={md.indirect:.3f} "
          f"[{md.ci_low:.3f}, {md.ci_high:.3f}], direct={md.c_direct:.3f} "
          f"[{md.direct_ci_low:.3f}, {md.direct_ci_high:.3f}] → {md.kind}")
print("\n## Sample profile\n")
for k, v in A.profile.items():
    print(f"- {k}: " + ", ".join(f"{i} {n}" for i, n in v.items()))
a = roi.Assumptions()
s = roi.summary(a)
from dataclasses import replace  # noqa: E402
p = roi.summary(replace(a, scale_clinics_after_12m=0))
mc = roi.monte_carlo(a, 2000)
print("\n## Business case (default assumptions)\n")
print(f"- Pilot+scale: NPV ₹{s['npv']/1e5:.1f} L, payback month {s['payback']}, gain/cost {s['roi']:.2f}×, "
      f"break-even uplift {roi.breakeven_uplift(a)*100:.1f} pp, P(NPV>0)={(mc>0).mean():.0%}")
print(f"- Pilot only: NPV ₹{p['npv']/1e5:.1f} L, payback {p['payback']}, gain/cost {p['roi']:.2f}×")
