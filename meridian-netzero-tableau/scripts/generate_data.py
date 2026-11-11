"""
Meridian Energy Group - Net-Zero Pathway simulation (as-of 30 Sep 2027)
Generates a star-schema of CSVs for Tableau.   Run:  python generate_data.py
Deterministic (seeded) - rerun gives identical data.
"""
import numpy as np, pandas as pd, os, sys, zlib

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2027)

AS_OF = pd.Timestamp("2027-09-01")            # last actual month
MONTHS = pd.date_range("2024-01-01", "2030-12-01", freq="MS")
ACT_MONTHS = MONTHS[MONTHS <= AS_OF]
T = {m: i for i, m in enumerate(MONTHS)}
def M(s): return pd.Timestamp(s + "-01")

REGIONS = {"UK & North Sea": (56.0, 1.5, 2.5), "Continental Europe": (50.0, 8.0, 4.0),
           "North America": (35.0, -98.0, 9.0), "Middle East": (25.0, 50.0, 4.0),
           "Asia Pacific": (8.0, 108.0, 12.0)}
COUNTRY = {"UK & North Sea": ["United Kingdom", "Norway"], "Continental Europe": ["Germany", "Netherlands", "Poland", "Spain"],
           "North America": ["USA", "Canada"], "Middle East": ["UAE", "Saudi Arabia", "Oman"],
           "Asia Pacific": ["Indonesia", "Australia", "Malaysia", "Vietnam"]}

# type: (BU, count, base monthly tCO2e, region weights, sources{name:share}, activity unit, intensity tCO2e/unit)
TYPES = {
 "Coal Power Plant":   ("Power Generation", 6, 150000, None, {"Stationary Combustion": .97, "Process Emissions": .01, "Purchased Electricity": .01, "Mobile Combustion": .01}, "MWh", 0.95),
 "Gas CCGT Plant":     ("Power Generation", 14, 55000, [.2, .3, .3, .1, .1], {"Stationary Combustion": .98, "Fugitive Methane": .01, "Mobile Combustion": .01}, "MWh", 0.38),
 "Refinery":           ("Midstream & Refining", 4, 85000, [.1, .3, .3, .2, .1], {"Stationary Combustion": .55, "Process Emissions": .15, "Flaring": .08, "Fugitive Methane": .04, "Purchased Electricity": .17, "Mobile Combustion": .01}, "bbl", 0.045),
 "Offshore Platform":  ("Upstream Oil & Gas", 24, 14000, [.3, 0, .3, .2, .2], {"Stationary Combustion": .50, "Flaring": .25, "Fugitive Methane": .20, "Mobile Combustion": .05}, "boe", 0.03),
 "Gas Processing":     ("Midstream & Refining", 10, 12000, [.1, .1, .5, .2, .1], {"Stationary Combustion": .55, "Flaring": .12, "Fugitive Methane": .15, "Process Emissions": .13, "Purchased Electricity": .05}, "boe", 0.02),
 "Compressor Station": ("Midstream & Refining", 20, 4000, [.1, .2, .5, .1, .1], {"Stationary Combustion": .85, "Fugitive Methane": .12, "Purchased Electricity": .03}, "MMscf", 0.9),
 "Wind Farm":          ("Renewables & New Energy", 28, 300, [.3, .3, .2, .05, .15], {"Purchased Electricity": .6, "Mobile Combustion": .4}, "MWh", 0.0005),
 "Solar PV Park":      ("Renewables & New Energy", 24, 200, [.1, .2, .25, .25, .2], {"Purchased Electricity": .6, "Mobile Combustion": .4}, "MWh", 0.0006),
 "Grid & Networks":    ("Networks & Corporate", 8, 6000, [.2, .3, .2, .1, .2], {"Fugitive Methane": .0, "SF6 & Other Fugitive": .45, "Purchased Electricity": .55}, "MWh", 0.004),
 "Buildings & Fleet":  ("Networks & Corporate", 12, 3000, [.2, .25, .25, .15, .15], {"Mobile Combustion": .5, "Purchased Electricity": .4, "Stationary Combustion": .1}, "Operating unit", 1.5),
}
COAL_REGIONS = ["UK & North Sea", "Continental Europe", "Continental Europe", "Asia Pacific", "Asia Pacific", "North America"]

# ---------------- dim_source ----------------
SRC = [("Stationary Combustion", 1, "Combustion"), ("Mobile Combustion", 1, "Mobile"), ("Flaring", 1, "Flaring"),
       ("Fugitive Methane", 1, "Methane & Fugitive"), ("SF6 & Other Fugitive", 1, "Methane & Fugitive"),
       ("Process Emissions", 1, "Process"), ("Purchased Electricity", 2, "Electricity (Scope 2)")]
dim_source = pd.DataFrame(SRC, columns=["source_name", "scope", "source_category"])
dim_source.insert(0, "source_id", [f"S{i+1:02d}" for i in range(len(dim_source))])
src_id = dict(zip(dim_source.source_name, dim_source.source_id))

# ---------------- dim_asset ----------------
rows = []; n = 0
for t, (bu, cnt, base, rw, srcs, unit, inten) in TYPES.items():
    for k in range(cnt):
        n += 1
        reg = COAL_REGIONS[k] if t == "Coal Power Plant" else rng.choice(list(REGIONS), p=rw)
        la, lo, sp = REGIONS[reg]
        lat = float(np.clip(la + rng.normal(0, sp * .45), -40, 70)); lon = lo + rng.normal(0, sp * .6)
        b = base * rng.lognormal(0, .25)
        rows.append(dict(asset_id=f"A{n:03d}", asset_name=f"{reg.split()[0] if reg!='UK & North Sea' else 'North Sea'} {t.split()[0]} {k+1:02d}",
                         asset_type=t, business_unit=bu, region=reg, country=rng.choice(COUNTRY[reg]),
                         latitude=round(lat, 4), longitude=round(lon, 4), commissioning_year=int(rng.integers(1985, 2023)),
                         ownership_pct=int(rng.choice([100, 100, 100, 80, 65, 50])), _base=b, _unit=unit, _int=inten))
dim_asset = pd.DataFrame(rows)
dim_asset["asset_name"] = dim_asset.groupby("asset_type").cumcount().add(1).astype(str).str.zfill(2).radd(dim_asset.asset_type + " ") + " - " + dim_asset.country

# ---------------- projects ----------------
LEV = {  # lever: (group, capex $ per annual tCO2e, MACC $/t, duration months)
 "Coal Retirement": ("Fuel Switch & Retirement", 35, -20, 12), "Biomass Co-firing": ("Fuel Switch & Retirement", 90, 45, 14),
 "Efficiency Upgrade": ("Efficiency", 120, -40, 10), "CCUS": ("CCUS", 600, 95, 36), "Hydrogen Blending": ("Hydrogen", 900, 180, 24),
 "Electrification": ("Electrification", 350, 70, 22), "Methane LDAR": ("Methane & Flaring", 25, -30, 9),
 "Flare Gas Recovery": ("Methane & Flaring", 140, 15, 14), "Renewable PPA": ("Renewable Power", 5, 8, 6),
 "Fleet Electrification": ("Electrification", 400, 85, 12)}
LEV_SRC = {"Coal Retirement": None, "Biomass Co-firing": ["Stationary Combustion"], "Efficiency Upgrade": ["Stationary Combustion"],
           "CCUS": ["Stationary Combustion"], "Hydrogen Blending": ["Stationary Combustion"], "Electrification": ["Stationary Combustion"],
           "Methane LDAR": ["Fugitive Methane"], "Flare Gas Recovery": ["Flaring"], "Renewable PPA": ["Purchased Electricity"],
           "Fleet Electrification": ["Mobile Combustion"]}
RANDOM_LEVERS = {"Gas CCGT Plant": [("Efficiency Upgrade", .04, .5), ("CCUS", .85, .12), ("Hydrogen Blending", .10, .15)],
                 "Refinery": [("Efficiency Upgrade", .10, .6), ("CCUS", .60, .3), ("Renewable PPA", .85, .6)],
                 "Offshore Platform": [("Flare Gas Recovery", .70, .35), ("Methane LDAR", .50, .45), ("Electrification", .80, .12)],
                 "Gas Processing": [("Methane LDAR", .50, .6), ("Flare Gas Recovery", .65, .4), ("Renewable PPA", .9, .5)],
                 "Compressor Station": [("Electrification", .90, .3), ("Methane LDAR", .45, .6)],
                 "Grid & Networks": [("Renewable PPA", .9, .7)], "Buildings & Fleet": [("Fleet Electrification", .6, .55), ("Renewable PPA", .95, .6)]}
projs = []
def P(asset_idx, lever, red, golive, status=None, orig=None, extra=None):
    a = dim_asset.loc[asset_idx]; grp, cpt, macc, dur = LEV[lever]
    srcs = LEV_SRC[lever] or list(TYPES[a.asset_type][4])
    base_yr = a._base * 12 * sum(TYPES[a.asset_type][4].get(s, 0) for s in srcs)
    ab = red * base_yr
    gl = M(golive); st = gl - pd.DateOffset(months=dur)
    projs.append(dict(asset_id=a.asset_id, lever=lever, lever_group=grp, target_sources="|".join(srcs), reduction_pct=red,
                      annual_abatement_tco2e=round(ab), capex_usd_m=round(ab * cpt / 1e6 * rng.uniform(.9, 1.15), 1),
                      macc_cost_usd_per_t=round(macc * rng.uniform(.8, 1.25)), start_date=st, current_golive=gl,
                      original_golive=M(orig) if orig else gl, status_override=status, **(extra or {})))

coal = dim_asset.index[dim_asset.asset_type == "Coal Power Plant"].tolist()
P(coal[0], "Coal Retirement", 1.0, "2025-12", extra=dict(project_name="Coal exit - UK"))
P(coal[1], "Coal Retirement", 1.0, "2026-09", extra=dict(project_name="Coal exit - Germany"))
P(coal[2], "Coal Retirement", 1.0, "2028-06", status="Delayed", orig="2026-12", extra=dict(project_name="Coal exit - Poland (grid-security delay)"))
P(coal[3], "Coal Retirement", 1.0, "2028-12", status="Planned", extra=dict(project_name="Coal exit - Indonesia"))
P(coal[4], "Biomass Co-firing", .20, "2027-03", extra=dict(project_name="Biomass co-firing - Vietnam"))
P(coal[5], "Coal Retirement", 1.0, "2029-06", status="Option", extra=dict(project_name="Coal exit - US Midwest (unfunded)"))
refs = dim_asset.index[dim_asset.asset_type == "Refinery"].tolist()
P(refs[0], "CCUS", .60, "2028-09", status="Delayed", orig="2027-06", extra=dict(project_name="Refinery CCUS hub - flagship"))
P(refs[1], "Efficiency Upgrade", .10, "2026-06", extra=dict(project_name="Refinery heat integration"))
P(refs[2], "CCUS", .55, "2029-09", status="Option", extra=dict(project_name="Refinery CCUS - phase 2 (unfunded)"))
used = {(p["asset_id"], p["lever"]) for p in projs}
for i, a in dim_asset.iterrows():
    for lever, red, prob in RANDOM_LEVERS.get(a.asset_type, []):
        if (a.asset_id, lever) in used or rng.random() > prob: continue
        gl = M("2024-09") + pd.DateOffset(months=int(rng.integers(0, 58)))
        P(i, lever, round(red * rng.uniform(.85, 1.05), 2), gl.strftime("%Y-%m"), extra=dict(project_name=None))
dim_project = pd.DataFrame(projs)
dim_project = dim_project.merge(dim_asset[["asset_id", "asset_name", "asset_type", "business_unit", "region"]], on="asset_id")

def status_of(r):
    if r.status_override: return r.status_override
    if r.current_golive <= AS_OF: return "Delivered"
    if r.start_date <= AS_OF:
        return "In Execution"
    return "Planned" if (zlib.crc32((r.asset_id + r.lever).encode()) % 100) < 55 else "Option"
dim_project["status"] = dim_project.apply(status_of, axis=1)
# make ~6 random in-execution projects delayed
cand = dim_project.index[(dim_project.status == "In Execution")]
for i in rng.choice(cand, size=min(6, len(cand)), replace=False):
    gl = dim_project.at[i, "current_golive"]
    dim_project.at[i, "original_golive"] = AS_OF - pd.DateOffset(months=int(rng.integers(1, 6)))
    dim_project.at[i, "current_golive"] = max(gl, AS_OF + pd.DateOffset(months=int(rng.integers(4, 12))))
    dim_project.at[i, "status"] = "Delayed"
# "Planned" funded projects must start in the future and Options too
dim_project["delay_months"] = ((dim_project.current_golive.dt.year - dim_project.original_golive.dt.year) * 12 +
                               dim_project.current_golive.dt.month - dim_project.original_golive.dt.month).clip(lower=0)
dim_project["funded"] = np.where(dim_project.status == "Option", "No", "Yes")
dim_project["risk_rating"] = np.where(dim_project.status == "Delayed", "High",
                              np.where(dim_project.lever.isin(["CCUS", "Hydrogen Blending", "Electrification"]), "Medium", "Low"))
dim_project["rag_status"] = dim_project.status.map({"Delivered": "Green", "In Execution": "Green", "Planned": "Amber", "Delayed": "Red", "Option": "Grey"})
dim_project = dim_project.sort_values(["status", "capex_usd_m"], ascending=[True, False]).reset_index(drop=True)
dim_project["project_id"] = [f"P{i+1:03d}" for i in range(len(dim_project))]
dim_project["project_name"] = dim_project.apply(lambda r: r.project_name if isinstance(r.project_name, str) else f"{r.lever} - {r.asset_name}", axis=1)
dim_project["abatement_lost_to_delay_tco2e"] = np.where(
    dim_project.status.isin(["Delayed", "Delivered"]),
    (dim_project.annual_abatement_tco2e / 12 * dim_project.delay_months.where(dim_project.status == "Delayed", 0)).round(), 0)
dim_project["capex_per_tonne_usd"] = (dim_project.capex_usd_m * 1e6 / dim_project.annual_abatement_tco2e.clip(lower=1)).round(0)

RAMP = 3
def ramp(proj_row, t_idx_array):
    g = T[proj_row.current_golive]
    return np.clip((t_idx_array - g + 1) / RAMP, 0, 1)

# ---------------- emissions engine ----------------
tix = np.arange(len(MONTHS))
season = {"Power Generation": 1 + .10 * np.cos((MONTHS.month.values - 1) / 12 * 2 * np.pi),
          "default": 1 + .04 * np.cos((MONTHS.month.values - 1) / 12 * 2 * np.pi)}
growth = {"Power Generation": 1.008, "default": 1.004}

def simulate(scenario_filter):
    """returns DataFrame asset-source-month emissions + activity for MONTHS under project set filter"""
    pr = dim_project[scenario_filter(dim_project)]
    out_e, out_a = [], []
    rng2 = np.random.default_rng(99)
    for _, a in dim_asset.iterrows():
        bu = a.business_unit
        s = season.get(bu, season["default"]); g = growth.get(bu, growth["default"]) ** (tix / 12)
        act = s * g * rng2.lognormal(0, .03, len(MONTHS))
        if a.asset_type in ("Wind Farm", "Solar PV Park"): act = (1 + .25 * np.cos((MONTHS.month.values - (1 if a.asset_type == "Wind Farm" else 6)) / 12 * 2 * np.pi)) * rng2.lognormal(0, .08, len(MONTHS))
        ap = pr[pr.asset_id == a.asset_id]
        for sname, share in TYPES[a.asset_type][4].items():
            if share <= 0: continue
            keep = np.ones(len(MONTHS))
            for _, p in ap.iterrows():
                if sname in p.target_sources.split("|"):
                    keep *= 1 - p.reduction_pct * ramp(p, tix)
            e = a._base * share * act * keep * rng2.lognormal(0, .025, len(MONTHS))
            out_e.append(pd.DataFrame(dict(date=MONTHS, asset_id=a.asset_id, source_id=src_id[sname], emissions_tco2e=e.round(1), _keep=keep)))
        act_out = act.copy()  # retired plants stop generating: activity falls with the retirement ramp
        for _, p in ap[ap.lever == "Coal Retirement"].iterrows():
            act_out = act_out * (1 - p.reduction_pct * ramp(p, tix))
        out_a.append(pd.DataFrame(dict(date=MONTHS, asset_id=a.asset_id, activity_value=(a._base / a._int * act_out).round(0), activity_unit=a._unit)))
    return pd.concat(out_e, ignore_index=True), pd.concat(out_a, ignore_index=True)

committed = lambda d: d.status != "Option"
em, act = simulate(committed)

# ---------------- carbon price ----------------
P0 = {"UK & North Sea": (55, 115), "Continental Europe": (70, 140), "North America": (25, 75), "Middle East": (5, 25), "Asia Pacific": (15, 55)}
SCN = {"Low": .7, "Base": 1.0, "High": 1.35}
cp = []
for sc, f in SCN.items():
    for r, (p0, p1) in P0.items():
        path = p0 + (p1 - p0) * (tix / (len(MONTHS) - 1)) ** 1.1
        cp.append(pd.DataFrame(dict(date=MONTHS, region=r, scenario=sc, carbon_price_usd_per_t=(path * f * rng.lognormal(0, .02, len(MONTHS))).round(2))))
fact_carbon_price = pd.concat(cp, ignore_index=True)
base_price = fact_carbon_price[fact_carbon_price.scenario == "Base"][["date", "region", "carbon_price_usd_per_t"]]

# ---------------- fact_emissions (actuals) ----------------
fe = em[em.date <= AS_OF].drop(columns="_keep").merge(dim_asset[["asset_id", "region"]], on="asset_id").merge(base_price, on=["date", "region"])
fe["carbon_cost_usd"] = (fe.emissions_tco2e * fe.carbon_price_usd_per_t).round(0)
fe["data_quality"] = rng.choice(["Measured (CEMS)", "Calculated", "Estimated"], size=len(fe), p=[.5, .35, .15])
fe = fe.drop(columns=["region", "carbon_price_usd_per_t"])
fe.insert(0, "record_id", np.arange(1, len(fe) + 1))
fact_operations = act[act.date <= AS_OF].merge(fe.groupby(["date", "asset_id"], as_index=False).emissions_tco2e.sum(), on=["date", "asset_id"])
fact_operations["emissions_intensity"] = (fact_operations.emissions_tco2e / fact_operations.activity_value.replace(0, np.nan)).round(5)
fact_operations = fact_operations.rename(columns={"emissions_tco2e": "asset_emissions_tco2e"})

# ---------------- target pathway ----------------
base24 = fe[fe.date.dt.year == 2024].emissions_tco2e.sum() / 12
pct_t = 0.45 * tix / (len(MONTHS) - 1)
fact_target = pd.DataFrame(dict(date=MONTHS, baseline_monthly_tco2e=round(base24), target_reduction_pct=pct_t.round(4),
                                target_tco2e=(base24 * (1 - pct_t)).round()))
fact_target["net_zero_2050_pathway_tco2e"] = (base24 * (1 - (tix / (26 * 12 + len(MONTHS) - 1)))).round()

# ---------------- project spend ----------------
sp = []
dp = dim_project
for _, p in dp.iterrows():
    if p.status == "Option": continue
    s_i = max(T.get(p.start_date, 0) if p.start_date >= MONTHS[0] else 0, 0)
    e_plan = T[p.original_golive] if p.original_golive in T else len(MONTHS) - 1
    e_act = T[p.current_golive] if p.current_golive in T else len(MONTHS) - 1
    if e_plan <= s_i: e_plan = s_i + 1
    if e_act <= s_i: e_act = s_i + 1
    def curve(n): w = np.sin(np.linspace(.15, np.pi - .15, n)); return w / w.sum()
    pw = curve(e_plan - s_i + 1); aw = curve(e_act - s_i + 1)
    over = 1 + (rng.uniform(.0, .22) if p.status != "Delayed" else rng.uniform(.12, .35))
    for k in range(e_plan - s_i + 1):
        sp.append((p.project_id, MONTHS[s_i + k], "plan", p.capex_usd_m * pw[k]))
    for k in range(e_act - s_i + 1):
        sp.append((p.project_id, MONTHS[s_i + k], "act", p.capex_usd_m * over * aw[k]))
spd = pd.DataFrame(sp, columns=["project_id", "date", "k", "v"])
fp = spd.pivot_table(index=["project_id", "date"], columns="k", values="v", aggfunc="sum").reset_index().fillna(0)
fp.columns.name = None
fp = fp.rename(columns={"plan": "planned_capex_usd_m", "act": "actual_capex_usd_m"})
fp.loc[fp.date > AS_OF, "actual_capex_usd_m"] = np.nan          # no actuals in the future
fp = fp.merge(dp[["project_id", "annual_abatement_tco2e", "current_golive"]], on="project_id")
r = np.clip((fp.date.map(T) - fp.current_golive.map(T) + 1) / RAMP, 0, 1)
fp["abatement_realized_tco2e"] = np.where(fp.date <= AS_OF, (fp.annual_abatement_tco2e / 12 * r).round(), np.nan)
fact_project_spend = fp.drop(columns=["annual_abatement_tco2e", "current_golive"])
for c in ["planned_capex_usd_m", "actual_capex_usd_m"]: fact_project_spend[c] = fact_project_spend[c].round(3)

# ---------------- scenario forecast (annual) ----------------
def agg(df, scn):
    d = df.merge(dim_asset[["asset_id", "business_unit", "region"]], on="asset_id").merge(dim_source[["source_id", "scope"]], on="source_id")
    d["year"] = d.date.dt.year
    g = d.groupby(["year", "business_unit", "region", "scope"], as_index=False).emissions_tco2e.sum()
    g["scenario"] = scn; return g
bau, _ = simulate(lambda d: d.status == "__none__")
acc, _ = simulate(lambda d: d.status != "__none__")
orig_dp = dim_project.copy()
fact_forecast = pd.concat([agg(bau, "1. Business as usual"), agg(em, "2. Committed plan"), agg(acc, "3. Accelerated (all options)")])
fact_forecast = fact_forecast[fact_forecast.year >= 2027]
hist = agg(fe.copy(), "0. Actual"); hist = hist[hist.year <= 2026]          # full-year actuals 2024-2026
fact_forecast = pd.concat([hist, fact_forecast], ignore_index=True)
fact_forecast["emissions_tco2e"] = fact_forecast.emissions_tco2e.round(0)

# ---------------- dim_date ----------------
dim_date = pd.DataFrame(dict(date=MONTHS, year=MONTHS.year, quarter="Q" + MONTHS.quarter.astype(str), month_num=MONTHS.month,
                             month_name=MONTHS.strftime("%b"), year_month=MONTHS.strftime("%Y-%m"),
                             is_actual=np.where(MONTHS <= AS_OF, "Actual", "Forecast")))

# ---------------- write ----------------
dim_asset_out = dim_asset.drop(columns=["_base", "_unit", "_int"])
dim_project_out = dim_project.drop(columns=["status_override", "target_sources"]).assign(target_sources=dim_project.target_sources)
dim_project_out = dim_project_out[["project_id", "project_name", "asset_id", "lever", "lever_group", "target_sources", "reduction_pct",
    "annual_abatement_tco2e", "capex_usd_m", "capex_per_tonne_usd", "macc_cost_usd_per_t", "start_date", "original_golive", "current_golive",
    "delay_months", "abatement_lost_to_delay_tco2e", "status", "rag_status", "funded", "risk_rating"]]
fact_target_annual = fact_target.assign(year=fact_target.date.dt.year).groupby("year", as_index=False).agg(
    target_tco2e=("target_tco2e", "sum"), baseline_tco2e=("baseline_monthly_tco2e", "sum"))
fact_target_annual["target_reduction_pct_avg"] = (1 - fact_target_annual.target_tco2e / fact_target_annual.baseline_tco2e).round(4)
files = dict(fact_target_annual=fact_target_annual, dim_asset=dim_asset_out, dim_source=dim_source, dim_project=dim_project_out, dim_date=dim_date,
             fact_emissions=fe, fact_operations=fact_operations, fact_project_spend=fact_project_spend,
             fact_target_pathway=fact_target, fact_carbon_price=fact_carbon_price, fact_scenario_forecast=fact_forecast)
for k, v in files.items():
    v.to_csv(os.path.join(OUT, k + ".csv"), index=False, date_format="%Y-%m-%d")
    print(f"{k:24s}{len(v):>8,} rows")
print("total rows", sum(len(v) for v in files.values()))
