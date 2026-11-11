"""Builds data/macc_polygon.csv: 4 corner points per non-delivered project, ordered by cost (Tableau Polygon mark)."""
import pandas as pd, os
root = os.path.join(os.path.dirname(__file__), "..")
p = pd.read_csv(os.path.join(root, "data", "dim_project.csv"))
p = p[p.status != "Delivered"].sort_values(["macc_cost_usd_per_t", "project_id"]).reset_index(drop=True)
p["abatement_mt"] = p.annual_abatement_tco2e / 1e6
p["x_end"] = p.abatement_mt.cumsum(); p["x_start"] = p.x_end - p.abatement_mt
p["cum_rank"] = p.index + 1
rows = []
for _, r in p.iterrows():
    for i, (x, y) in enumerate([(r.x_start, 0), (r.x_start, r.macc_cost_usd_per_t), (r.x_end, r.macc_cost_usd_per_t), (r.x_end, 0)], 1):
        rows.append(dict(project_id=r.project_id, project_name=r.project_name, lever=r.lever, status=r.status, funded=r.funded,
                         cost_rank=r.cum_rank, point_order=i, x_cum_abatement_mt=round(x, 4), y_cost_usd_per_t=y,
                         abatement_mt=round(r.abatement_mt, 4), macc_cost_usd_per_t=r.macc_cost_usd_per_t, capex_usd_m=r.capex_usd_m))
out = pd.DataFrame(rows); out.to_csv(os.path.join(root, "data", "macc_polygon.csv"), index=False)
print(len(p), "projects", len(out), "rows; total Mt", round(p.abatement_mt.sum(), 2), "cost range", p.macc_cost_usd_per_t.min(), p.macc_cost_usd_per_t.max())
print(p.groupby("status").abatement_mt.sum().round(2).to_dict())
print(p.head(3)[["project_name","macc_cost_usd_per_t","abatement_mt"]].to_string())
