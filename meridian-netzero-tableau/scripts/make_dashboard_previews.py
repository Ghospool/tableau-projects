"""Renders the 3 target dashboards as static HTML (real data, exact layout.json coordinates)."""
import os, json, math, base64
import pandas as pd, numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = lambda f: pd.read_csv(os.path.join(ROOT, "data", f))
OUT = os.path.join(ROOT, "Dashboard_Previews"); os.makedirs(OUT, exist_ok=True)
LAY = json.load(open(os.path.join(ROOT, "assets", "layout.json")))

NAVY, NAVY2, TEAL, GREEN, AMBER, RED, GREY = "#0B2545", "#13315C", "#13A89E", "#7AC74F", "#F2A541", "#D64550", "#8D99AE"
FONT = "Lato,'Segoe UI',Arial,sans-serif"

# ------------------------------------------------------------------ data
e = D("fact_emissions.csv"); e["date"] = pd.to_datetime(e.date)
a = D("dim_asset.csv"); s = D("dim_source.csv"); tp = D("fact_target_pathway.csv"); tp["date"] = pd.to_datetime(tp.date)
pj = D("dim_project.csv"); sp = D("fact_project_spend.csv"); sp["date"] = pd.to_datetime(sp.date)
fc = D("fact_scenario_forecast.csv"); ta = D("fact_target_annual.csv"); op = D("fact_operations.csv"); op["date"] = pd.to_datetime(op.date)
mp = D("macc_polygon.csv")
m = e.merge(a, on="asset_id").merge(s, on="source_id"); m["year"] = m.date.dt.year; m["mon"] = m.date.dt.month
y27 = m[m.year == 2027]; b24 = m[(m.year == 2024) & (m.mon <= 9)]
tot27, tot24 = y27.emissions_tco2e.sum(), b24.emissions_tco2e.sum()
pct = tp[(tp.date.dt.year == 2027) & (tp.date.dt.month <= 9)].target_reduction_pct.mean()
target_ytd = tot24 * (1 - pct); gap = tot27 - target_ytd
monthly = m.groupby("date").emissions_tco2e.sum()
GRP = {"Coal Power Plant": NAVY, "Gas CCGT Plant": TEAL, "Refinery": AMBER}
grp_col = lambda t: GRP.get(t, GREY)
BUCOL = {"Power Generation": NAVY, "Upstream Oil & Gas": TEAL, "Midstream & Refining": AMBER, "Networks & Corporate": GREY, "Renewables & New Energy": GREEN}
STCOL = {"Delayed": RED, "In Execution": TEAL, "Planned": AMBER, "Option": GREY, "Delivered": GREEN}

# ------------------------------------------------------------------ svg helpers
def T(x, y, s_, size=11, fill="#5b6b82", anchor="start", weight=400, extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s_}</text>'
def L(x1, y1, x2, y2, c="#e3e9f0", w=1, dash=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" {"stroke-dasharray=%s" % chr(34)+dash+chr(34) if dash else ""}/>'
def R(x, y, w, h, c, o=1, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{max(h,0):.1f}" fill="{c}" opacity="{o}" {extra}/>'
def PL(pts, c, w=2, dash="", fill="none", o=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="{fill}" stroke="{c}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" opacity="{o}" {"stroke-dasharray=%s" % chr(34)+dash+chr(34) if dash else ""}/>'
def SVG(w, h, body): return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="font-family:{FONT}">{body}</svg>'
def lerp(c1, c2, t):
    a1 = [int(c1[i:i+2], 16) for i in (1, 3, 5)]; a2 = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a1, a2))

def sheet(box, inner, html, kpi=False):
    x, y, w, h = box
    ox, oy, ow, oh = (16, 34, -32, -44) if kpi else (12, 44, -24, -56)
    return f'<div class="sheet" style="left:{x+ox}px;top:{y+oy}px;width:{w+ow}px;height:{h+oh}px">{html}</div>', (w + ow, h + oh)

def kpi(box, value, sub, color=NAVY, vs=32):
    x, y, w, h = box
    return (f'<div class="sheet kpi" style="left:{x+16}px;top:{y+34}px;width:{w-32}px;height:{h-44}px">'
            f'<div style="font-size:{vs}px;font-weight:700;color:{color};line-height:1.05">{value}</div>'
            f'<div style="font-size:11px;color:{GREY};margin-top:2px">{sub}</div></div>')

def card(p):  # dict from layout
    return (p["x"], p["y"], p["w"], p["h"])

# ------------------------------------------------------------------ PAGE 1
def p1():
    P = {k["id"]: k for k in LAY["page1"]}; o = []
    chg = tot27 / tot24 - 1
    o.append(kpi(card(P["k1"]), f"{tot27/1e6:.1f}", "MtCO2e, Jan-Sep 2027"))
    o.append(kpi(card(P["k2"]), f"{chg*100:.1f}%", f"vs {pct*100:.1f}% required", GREEN))
    o.append(kpi(card(P["k3"]), f"+{gap/1e6:.1f}", "MtCO2e above the 2027 pathway (YTD)", RED))
    o.append(kpi(card(P["k4"]), f"${y27.carbon_cost_usd.sum()/1e6:,.0f}", "$M carbon cost, Jan-Sep (Base price)", NAVY))
    # A: pathway
    h, ins = sheet(card(P["a"]), None, "{A}"); w, hh = ins
    Lm, Rm, Tm, Bm = 44, 16, 16, 26
    xs = lambda i: Lm + (w - Lm - Rm) * i / 83; ys = lambda v: Tm + (hh - Tm - Bm) * (1 - v / 3.0)
    b = ""
    for v in (0, 1, 2, 3): b += L(Lm, ys(v), w - Rm, ys(v)) + T(Lm - 6, ys(v) + 4, f"{v:.1f}", 10, anchor="end")
    for yr in range(2024, 2031): b += T(xs((yr - 2024) * 12), hh - 8, str(yr), 10, anchor="start")
    em = [(xs(i), ys(v / 1e6)) for i, v in enumerate(monthly.values)]
    tg = [(xs(i), ys(v / 1e6)) for i, v in enumerate(tp.target_tco2e.values)]
    nz = [(xs(i), ys(v / 1e6)) for i, v in enumerate(tp.net_zero_2050_pathway_tco2e.values)]
    b += f'<polygon points="{xs(0):.1f},{ys(0):.1f} ' + " ".join(f"{x:.1f},{y:.1f}" for x, y in em) + f' {em[-1][0]:.1f},{ys(0):.1f}" fill="{NAVY}" opacity="0.08"/>'
    b += PL(nz, GREY, 2, "2 4") + PL(tg, TEAL, 2.5, "7 4") + PL(em, NAVY, 3.2)
    ix = xs(len(monthly) - 1); b += L(ix, Tm, ix, hh - Bm, "#6b7a90", 1.2, "3 3") + T(ix + 5, Tm + 10, "Today (Sep-27)", 10, "#6b7a90")
    a1, t1 = ys(monthly.values[-1] / 1e6), ys(tp.target_tco2e.values[len(monthly) - 1] / 1e6)
    b += L(ix + 14, a1, ix + 14, t1, RED, 2) + T(ix + 20, (a1 + t1) / 2 + 4, "Gap +1.7 Mt YTD", 11, RED, weight=700)
    b += T(xs(1), ys(monthly.values[0] / 1e6) - 8, "Actual emissions", 11, NAVY, weight=700)
    b += T(xs(60), ys(tp.target_tco2e.values[60] / 1e6) + 18, "2030 target pathway (-45%)", 11, TEAL, weight=700)
    b += T(xs(62), ys(tp.net_zero_2050_pathway_tco2e.values[62] / 1e6) - 8, "Net-zero 2050 line", 10, GREY)
    b += T(10, hh / 2, "", 1)
    o.append(h.replace("{A}", SVG(w, hh, b)))
    # B: BU gap
    h, ins = sheet(card(P["b"]), None, "{B}"); w, hh = ins
    g = (y27.groupby("business_unit").emissions_tco2e.sum() - b24.groupby("business_unit").emissions_tco2e.sum() * (1 - pct)).sort_values(ascending=False) / 1e6
    mx = max(abs(g.max()), 0.7); b = ""; rowh = hh / len(g); x0 = 178
    b += L(x0, 6, x0, hh - 18, "#334", 1.2)
    for i, (bu, v) in enumerate(g.items()):
        yy = 10 + i * (rowh - 4) * 0.98 + 6; bh = min(34, rowh - 18); col = RED if v > 0 else GREEN
        b += T(x0 - 8, yy + bh / 2 + 4, bu, 11, "#33425b", "end") + R(x0, yy, (w - x0 - 60) * abs(v) / mx, bh, col, 0.9) + T(x0 + (w - x0 - 60) * abs(v) / mx + 6, yy + bh / 2 + 4, f"{v:+.2f}", 12, NAVY, weight=700)
    b += T(x0, hh - 4, "MtCO2e above (+) / below (-) pathway, 2027 YTD    Total +%.2f" % g.sum(), 10, GREY)
    o.append(h.replace("{B}", SVG(w, hh, b)))
    # C: region
    h, ins = sheet(card(P["c"]), None, "{C}"); w, hh = ins
    r27 = y27.groupby("region").emissions_tco2e.sum(); r24 = b24.groupby("region").emissions_tco2e.sum(); rc = (r27 / r24 - 1)
    r27 = r27.sort_values(ascending=False); b = ""; rowh = (hh - 18) / len(r27); x0 = 130; mx = r27.max() / 1e6
    for i, (rg, v) in enumerate(r27.items()):
        yy = 6 + i * rowh; c = lerp("#D64550", "#7AC74F", min(max((-rc[rg]) / 0.30, 0), 1)) if rc[rg] > -0.05 or True else GREEN
        b += T(x0 - 8, yy + rowh / 2 + 3, rg, 11, "#33425b", "end") + R(x0, yy + 4, (w - x0 - 90) * (v / 1e6) / mx, rowh - 12, c, 0.95) + T(x0 + (w - x0 - 90) * (v / 1e6) / mx + 6, yy + rowh / 2 + 3, f"{v/1e6:.1f}  ({rc[rg]*100:+.0f}%)", 11, NAVY, weight=700)
    b += T(x0, hh - 3, "MtCO2e, 2027 YTD (change vs 2024 YTD); green = bigger cut", 10, GREY)
    o.append(h.replace("{C}", SVG(w, hh, b)))
    # D: source mix
    h, ins = sheet(card(P["d"]), None, "{D}"); w, hh = ins
    cat = m.groupby(["year", "source_category"]).emissions_tco2e.sum().unstack().fillna(0); cat = cat.div(cat.sum(axis=1), axis=0)
    order = ["Combustion", "Flaring", "Methane & Fugitive", "Process", "Mobile", "Electricity (Scope 2)"]; cols = [NAVY, AMBER, RED, GREY, TEAL, GREEN]
    b = ""; bw = (w - 150) / 4 * 0.62; Tp, Bt = 8, 28
    for i, yr in enumerate(cat.index):
        x = 20 + i * (w - 170) / 4 + 10; yb = Tp
        for c_, col in zip(order, cols):
            v = cat.loc[yr, c_]; hgt = (hh - Tp - Bt) * v
            b += R(x, yb, bw, hgt, col, 0.95)
            if v > 0.04: b += T(x + bw / 2, yb + hgt / 2 + 4, f"{v*100:.0f}%", 10, "#fff", "middle", 700)
            yb += hgt
        b += T(x + bw / 2, hh - 10, str(yr) + (" YTD" if yr == 2027 else ""), 11, "#33425b", "middle")
    for i, (c_, col) in enumerate(zip(order, cols)):
        b += R(w - 140, 12 + i * 22, 11, 11, col) + T(w - 124, 22 + i * 22, c_, 11, "#33425b")
    o.append(h.replace("{D}", SVG(w, hh, b)))
    # E: key messages
    x, y, w_, h_ = card(P["e"])
    msgs = [("1", f"We are <b style='color:{AMBER}'>{gap/1e6:.1f} Mt above</b> the 2027 pathway: {chg*100:.0f}% vs {pct*100:.0f}% required."),
            ("2", f"The delayed <b style='color:{AMBER}'>Poland coal exit</b> alone is 1.85 Mt/yr, larger than the whole gap."),
            ("3", f"<b style='color:{AMBER}'>Methane and flaring</b> ({y27[y27.source_name.isin(['Fugitive Methane','Flaring'])].emissions_tco2e.sum()/1e6:.1f} Mt) is the cheapest abatement."),
            ("4", f"The committed plan reaches only <b style='color:{AMBER}'>-32% by 2030</b>; the target is -45%.")]
    body = "".join(f"<div style='display:flex;gap:10px;margin-bottom:12px'><div style='min-width:24px;height:24px;border-radius:12px;background:{TEAL};color:#fff;text-align:center;font-weight:700;line-height:24px'>{n}</div><div>{t_}</div></div>" for n, t_ in msgs)
    o.append(f'<div class="sheet" style="left:{x+16}px;top:{y+44}px;width:{w_-32}px;height:{h_-56}px;color:#fff;font-size:14px;line-height:1.35">{body}</div>')
    return o

# ------------------------------------------------------------------ PAGE 2
def p2():
    P = {k["id"]: k for k in LAY["page2"]}; o = []
    coal = y27[y27.asset_type == "Coal Power Plant"].emissions_tco2e.sum() / tot27
    mf = y27[y27.source_name.isin(["Fugitive Methane", "Flaring"])].emissions_tco2e.sum() / 1e3
    byasset = y27.groupby(["asset_id", "asset_name", "asset_type", "business_unit", "latitude", "longitude"]).emissions_tco2e.sum().reset_index().sort_values("emissions_tco2e", ascending=False)
    top10 = byasset.head(10).emissions_tco2e.sum() / tot27; sc2 = y27[y27.scope == 2].emissions_tco2e.sum() / tot27
    last = m[m.date == m.date.max()]; active_coal = (last[last.asset_type == "Coal Power Plant"].groupby("asset_id").emissions_tco2e.sum() > 1000).sum()
    o += [kpi(card(P["k1"]), f"{coal*100:.1f}%", "Coal share of YTD emissions", NAVY, 28), kpi(card(P["k2"]), f"{mf:,.0f}", "kt methane + flaring, YTD", AMBER, 28),
          kpi(card(P["k3"]), f"{active_coal} of 6", "of 6 coal plants still emitting in Sep-27", RED, 28), kpi(card(P["k4"]), f"{top10*100:.1f}%", "of emissions from top 10 assets", NAVY, 28),
          kpi(card(P["k5"]), f"{sc2*100:.1f}%", "Scope 2 share of YTD emissions", GREEN, 28)]
    # A top 15
    h, ins = sheet(card(P["a"]), None, "{A}"); w, hh = ins; t15 = byasset.head(15); mx = t15.emissions_tco2e.max() / 1e3; b = ""; rowh = (hh - 26) / 15; x0 = 200
    for i, r in enumerate(t15.itertuples()):
        yy = 22 + i * rowh; v = r.emissions_tco2e / 1e3
        b += T(x0 - 8, yy + rowh / 2 + 3, r.asset_name, 10.5, "#33425b", "end") + R(x0, yy + 4, (w - x0 - 70) * v / mx, rowh - 9, grp_col(r.asset_type), 0.95) + T(x0 + (w - x0 - 70) * v / mx + 6, yy + rowh / 2 + 3, f"{v:,.0f} kt", 10.5, NAVY, weight=700)
    for i, (n_, c_) in enumerate([("Coal", NAVY), ("Gas CCGT", TEAL), ("Refinery", AMBER), ("Others", GREY)]):
        b += R(x0 + i * 62, 4, 10, 10, c_) + T(x0 + 14 + i * 62, 13, n_, 10, "#33425b")
    o.append(h.replace("{A}", SVG(w, hh, b)))
    # B map
    h, ins = sheet(card(P["b"]), None, "{B}"); w, hh = ins; b = R(0, 0, w, hh, "#e9eff5")
    px = lambda lo: (lo + 135) / 300 * w; py = lambda la: (72 - la) / 92 * hh
    for lo in range(-120, 165, 30): b += L(px(lo), 0, px(lo), hh, "#d7e0ea")
    for la in range(-20, 80, 20): b += L(0, py(la), w, py(la), "#d7e0ea")
    for nm, lo, la in [("North America", -100, 52), ("Europe", 12, 58), ("Middle East", 52, 17), ("Asia Pacific", 112, -8)]: b += T(px(lo), py(la), nm.upper(), 11, "#9fb0c3", "middle", 700)
    for r in byasset.sort_values("emissions_tco2e", ascending=False).itertuples():
        b += f'<circle cx="{px(r.longitude):.1f}" cy="{py(r.latitude):.1f}" r="{max(2.0, math.sqrt(r.emissions_tco2e/1e3)*0.40):.1f}" fill="{BUCOL[r.business_unit]}" opacity="0.72" stroke="#fff" stroke-width="0.8"><title>{r.asset_name}: {r.emissions_tco2e/1e3:,.0f} kt</title></circle>'
    for i, (bu, c_) in enumerate(BUCOL.items()): b += R(8 + (i % 3) * 150, hh - 34 + (i // 3) * 15, 9, 9, c_) + T(21 + (i % 3) * 150, hh - 26 + (i // 3) * 15, bu, 10, "#33425b")
    b += T(w - 8, 14, "Tableau adds the Mapbox basemap here", 9, "#9fb0c3", "end")
    o.append(h.replace("{B}", SVG(w, hh, b)))
    # C heatmap
    h, ins = sheet(card(P["c"]), None, "{C}"); w, hh = ins
    pv = y27.pivot_table(index="asset_type", columns="source_name", values="emissions_tco2e", aggfunc="sum").fillna(0) / 1e3
    pv = pv.loc[pv.sum(axis=1).sort_values(ascending=False).index]
    cols_ = ["Stationary Combustion", "Mobile Combustion", "Flaring", "Fugitive Methane", "SF6 & Other Fugitive", "Process Emissions", "Purchased Electricity"]
    short = ["Stationary", "Mobile", "Flaring", "Methane", "SF6/other", "Process", "Scope 2"]; x0 = 130; cw = (w - x0) / 7; ch = (hh - 22) / len(pv); b = ""; vmax = pv.values.max()
    for j, c_ in enumerate(short): b += T(x0 + j * cw + cw / 2, 13, c_, 10, "#33425b", "middle", 700)
    for i, (idx, row) in enumerate(pv.iterrows()):
        b += T(x0 - 8, 22 + i * ch + ch / 2 + 4, idx, 10.5, "#33425b", "end")
        for j, c_ in enumerate(cols_):
            v = row.get(c_, 0); t_ = (v / vmax) ** 0.5 if v > 0 else 0
            b += R(x0 + j * cw + 1, 22 + i * ch + 1, cw - 2, ch - 2, lerp("#EEF2F6", NAVY, t_) if v > 0 else "#f6f8fa")
            if v >= 1: b += T(x0 + j * cw + cw / 2, 22 + i * ch + ch / 2 + 4, f"{v:,.0f}", 10, "#fff" if t_ > 0.45 else "#33425b", "middle")
    o.append(h.replace("{C}", SVG(w, hh, b)))
    # D intensity
    h, ins = sheet(card(P["d"]), None, "{D}"); w, hh = ins
    ox = op.merge(a[["asset_id", "asset_type"]], on="asset_id"); ox["year"] = ox.date.dt.year
    g_ = ox.groupby(["asset_type", "year"]).agg(em=("asset_emissions_tco2e", "sum"), ac=("activity_value", "sum")); g_["i"] = g_.em / g_.ac
    series = {t: [g_.loc[(t, y), "i"] / g_.loc[(t, 2024), "i"] * 100 for y in range(2024, 2028)] for t in ["Coal Power Plant", "Gas CCGT Plant", "Refinery", "Offshore Platform"]}
    Lm, Rm, Tm, Bm = 34, 78, 12, 26; xs = lambda i: Lm + (w - Lm - Rm) * i / 3; lo_, hi_ = 55, 105; ys = lambda v: Tm + (hh - Tm - Bm) * (1 - (v - lo_) / (hi_ - lo_)); b = ""
    for v in range(60, 101, 10): b += L(Lm, ys(v), w - Rm, ys(v)) + T(Lm - 5, ys(v) + 4, str(v), 10, anchor="end")
    b += L(Lm, ys(100), w - Rm, ys(100), "#334", 1.2) + T(Lm + 4, ys(100) - 4, "2024 = 100", 10, "#334")
    for i, yr in enumerate(range(2024, 2028)): b += T(xs(i), hh - 8, str(yr), 10, "#5b6b82", "middle")
    for (t_, vals), c_ in zip(series.items(), [NAVY, TEAL, AMBER, GREY]):
        b += PL([(xs(i), ys(v)) for i, v in enumerate(vals)], c_, 2.6) + T(xs(3) + 6, ys(vals[-1]) + 4, f"{t_.replace(' Power Plant','').replace(' Plant','')} {vals[-1]:.0f}", 10.5, c_, weight=700)
    o.append(h.replace("{D}", SVG(w, hh, b)))
    # E methane & flaring
    h, ins = sheet(card(P["e"]), None, "{E}"); w, hh = ins
    mm = m[m.source_name.isin(["Fugitive Methane", "Flaring"])].groupby(["date", "source_name"]).emissions_tco2e.sum().unstack().fillna(0) / 1e3
    n_ = len(mm); mx = (mm.sum(axis=1)).max() * 1.1; Lm, Rm, Tm, Bm = 38, 10, 10, 24; xs = lambda i: Lm + (w - Lm - Rm) * i / (n_ - 1); ys = lambda v: Tm + (hh - Tm - Bm) * (1 - v / mx); b = ""
    for v in range(0, int(mx) + 1, 100): b += L(Lm, ys(v), w - Rm, ys(v)) + T(Lm - 5, ys(v) + 4, str(v), 10, anchor="end")
    flr = mm["Flaring"].values; mth = mm["Fugitive Methane"].values
    b += f'<polygon points="' + " ".join(f"{xs(i):.1f},{ys(flr[i]):.1f}" for i in range(n_)) + f' {xs(n_-1):.1f},{ys(0):.1f} {xs(0):.1f},{ys(0):.1f}" fill="{AMBER}" opacity="0.9"/>'
    b += f'<polygon points="' + " ".join(f"{xs(i):.1f},{ys(flr[i]+mth[i]):.1f}" for i in range(n_)) + " " + " ".join(f"{xs(i):.1f},{ys(flr[i]):.1f}" for i in range(n_ - 1, -1, -1)) + f'" fill="{RED}" opacity="0.85"/>'
    for i, yr in enumerate(range(2024, 2028)): b += T(xs(i * 12), hh - 8, str(yr), 10, "#5b6b82")
    b += R(Lm + 6, 14, 10, 10, RED) + T(Lm + 20, 23, "Fugitive methane", 10, "#33425b") + R(Lm + 120, 14, 10, 10, AMBER) + T(Lm + 134, 23, "Flaring", 10, "#33425b") + T(10, 10, "kt/month", 9, GREY)
    o.append(h.replace("{E}", SVG(w, hh, b)))
    return o

# ------------------------------------------------------------------ PAGE 3
def p3():
    P = {k["id"]: k for k in LAY["page3"]}; o = []
    funded = pj[pj.funded == "Yes"]
    o += [kpi(card(P["k1"]), f"${funded.capex_usd_m.sum():,.0f}", "$M capex committed to funded projects", NAVY, 28),
          kpi(card(P["k2"]), f"{pj[pj.status=='Delivered'].annual_abatement_tco2e.sum()/1e6:.1f}", "Mt/yr abated by delivered projects", GREEN, 28),
          kpi(card(P["k3"]), f"{pj[pj.status=='Delayed'].annual_abatement_tco2e.sum()/1e6:.1f}", "Mt/yr at risk from 8 delayed projects", RED, 28),
          kpi(card(P["k4"]), f"${(pj.annual_abatement_tco2e*pj.macc_cost_usd_per_t).sum()/pj.annual_abatement_tco2e.sum():,.0f}", "per tCO2e, abatement-weighted (all projects)", TEAL, 28)]
    # A MACC
    h, ins = sheet(card(P["a"]), None, "{A}"); w, hh = ins; Lm, Rm, Tm, Bm = 44, 12, 22, 34
    xs = lambda v: Lm + (w - Lm - Rm) * v / 7; ys = lambda v: Tm + (hh - Tm - Bm) * (1 - (v + 60) / 170); b = ""
    for v in range(-60, 111, 20): b += L(Lm, ys(v), w - Rm, ys(v), "#eef2f6") + T(Lm - 5, ys(v) + 4, str(v), 10, anchor="end")
    for v in range(0, 8): b += T(xs(v), hh - 18, str(v), 10, "#5b6b82", "middle")
    b += T((w + Lm) / 2, hh - 4, "Cumulative abatement potential (MtCO2e per year)", 10.5, "#33425b", "middle") + T(6, 12, "$ per tCO2e", 10.5, "#33425b")
    for pid, g in mp.groupby("project_id"):
        x1, x2, c = g.x_cum_abatement_mt.min(), g.x_cum_abatement_mt.max(), g.y_cost_usd_per_t.max() if g.y_cost_usd_per_t.max() != 0 else g.y_cost_usd_per_t.min()
        c = g.macc_cost_usd_per_t.iloc[0]; st = g.status.iloc[0]
        y0, y1 = ys(0), ys(c); b += f'<rect x="{xs(x1):.1f}" y="{min(y0,y1):.1f}" width="{xs(x2)-xs(x1):.1f}" height="{abs(y1-y0):.1f}" fill="{STCOL[st]}" opacity="0.88" stroke="#fff" stroke-width="0.6"><title>{g.project_name.iloc[0]} | {st} | {g.abatement_mt.iloc[0]:.2f} Mt | ${c}/t</title></rect>'
        wpx = xs(x2) - xs(x1)
        if wpx > 70:
            nm = g.project_name.iloc[0].split(" (")[0]; nm = nm[: int(wpx / 5.6)]
            b += T((xs(x1) + xs(x2)) / 2, (y0 + y1) / 2 + 4, nm, 10, "#fff", "middle", 700)
    b += L(Lm, ys(0), w - Rm, ys(0), "#223", 1.4) + L(Lm, ys(100), w - Rm, ys(100), "#556", 1.2, "6 4") + T(Lm + 6, ys(100) - 5, "Carbon price 2030 (High case) $100", 10, "#556")
    for i, (st, c_) in enumerate([("Delayed", RED), ("In Execution", TEAL), ("Planned", AMBER), ("Option (unfunded)", GREY)]):
        b += R(w - 390 + i * 82 + (14 if i == 3 else 0), 4, 10, 10, c_) + T(w - 376 + i * 82 + (14 if i == 3 else 0), 13, st, 10, "#33425b")
    o.append(h.replace("{A}", SVG(w, hh, b)))
    # B scenarios
    h, ins = sheet(card(P["b"]), None, "{B}"); w, hh = ins
    sc = fc.groupby(["scenario", "year"]).emissions_tco2e.sum().unstack() / 1e6
    Lm, Rm, Tm, Bm = 40, 190, 12, 26; xs = lambda yr: Lm + (w - Lm - Rm) * (yr - 2024) / 6; lo_, hi_ = 14, 34; ys = lambda v: Tm + (hh - Tm - Bm) * (1 - (v - lo_) / (hi_ - lo_)); b = ""
    for v in range(14, 35, 4): b += L(Lm, ys(v), w - Rm, ys(v)) + T(Lm - 5, ys(v) + 4, str(v), 10, anchor="end")
    for yr in range(2024, 2031): b += T(xs(yr), hh - 8, str(yr), 10, "#5b6b82", "middle")
    names = {"0. Actual": ("Actual", NAVY), "1. Business as usual": ("Business as usual", GREY), "2. Committed plan": ("Committed plan", TEAL), "3. Accelerated (all options)": ("Accelerated", GREEN)}
    for k, (nm, c_) in names.items():
        sr = sc.loc[k].dropna(); b += PL([(xs(yr), ys(v)) for yr, v in sr.items()], c_, 3) + "".join(f'<circle cx="{xs(yr):.1f}" cy="{ys(v):.1f}" r="3" fill="{c_}"/>' for yr, v in sr.items())
        yr, v = sr.index[-1], sr.iloc[-1]; b += T(xs(yr) + 8, ys(v) + 4, f"{nm}  {v:.1f}" + (f" ({(v/30.403-1)*100:.0f}%)" if k != "0. Actual" else ""), 11, c_, weight=700)
    ty = ta.set_index("year").target_tco2e / 1e6; b += PL([(xs(yr), ys(v)) for yr, v in ty.items()], RED, 2.4, "7 4") + T(xs(2030) + 8, ys(ty[2030]) + 18, f"Target {ty[2030]:.1f} (-42% avg)", 11, RED, weight=700)
    b += f'<polygon points="{xs(2030):.1f},{ys(sc.loc["3. Accelerated (all options)",2030]):.1f} {xs(2030):.1f},{ys(ty[2030]):.1f} {xs(2030)-26:.1f},{ys(ty[2030]):.1f}" fill="{RED}" opacity="0.18"/>'
    b += T(xs(2028.9), ys(26.5), "Even with all options, a ~1.3 Mt gap remains in 2030", 11, RED, "middle", 700) + T(8, 10, "MtCO2e per year", 9, GREY)
    o.append(h.replace("{B}", SVG(w, hh, b)))
    # C tracker
    x, y, w_, h_ = card(P["c"]); pjx = pj.merge(a[["asset_id", "region"]], on="asset_id"); pjx = pjx[pjx.status.isin(["Delayed", "In Execution", "Planned"])]
    pjx["so"] = pjx.status.map({"Delayed": 1, "In Execution": 2, "Planned": 3}); pjx = pjx.sort_values(["so", "annual_abatement_tco2e"], ascending=[True, False])
    fm = lambda d: pd.to_datetime(d).strftime("%b %Y")
    rows = ""
    for r in pjx.itertuples():
        rows += (f"<tr><td><span class='dot' style='background:{STCOL[r.status]}'></span></td><td>{r.status}</td><td>{r.project_name[:32]}</td><td>{r.lever}</td><td>{r.region}</td>"
                 f"<td>{fm(r.original_golive)}</td><td>{fm(r.current_golive)}</td><td class='n'>{r.annual_abatement_tco2e/1e3:,.0f}K</td><td class='n'>${r.capex_usd_m:,.0f}</td><td class='n'>{r.delay_months}</td></tr>")
    tbl = ("<table class='trk'><thead><tr><th></th><th>Status</th><th>Project</th><th>Lever</th><th>Region</th><th>Orig.</th><th>Current</th><th class='n'>kt/yr</th><th class='n'>$M</th><th class='n'>Delay</th></tr></thead><tbody>" + rows + "</tbody></table>")
    o.append(f'<div class="sheet" style="left:{x+12}px;top:{y+44}px;width:{w_-24}px;height:{h_-56}px;overflow-y:auto">{tbl}</div>')
    # D capex
    h, ins = sheet(card(P["d"]), None, "{D}"); w, hh = ins
    fs = sp.merge(pj[["project_id", "funded"]], on="project_id"); fs = fs[fs.funded == "Yes"]
    mi = pd.date_range("2024-01-01", "2029-12-01", freq="MS"); cp = fs.groupby("date").planned_capex_usd_m.sum().reindex(mi).fillna(0).cumsum()
    ca = fs.groupby("date").actual_capex_usd_m.sum().reindex(mi).fillna(0).cumsum(); ca = ca[ca.index <= "2027-09-01"]
    Lm, Rm, Tm, Bm = 44, 12, 12, 24; xs = lambda i: Lm + (w - Lm - Rm) * i / (len(mi) - 1); ys = lambda v: Tm + (hh - Tm - Bm) * (1 - v / 2200); b = ""
    for v in range(0, 2201, 500): b += L(Lm, ys(v), w - Rm, ys(v)) + T(Lm - 5, ys(v) + 4, f"${v:,}", 9.5, anchor="end")
    for yr in range(2024, 2030): b += T(xs((yr - 2024) * 12), hh - 6, str(yr), 10, "#5b6b82")
    b += PL([(xs(i), ys(v)) for i, v in enumerate(cp.values)], GREY, 2.6) + PL([(xs(i), ys(v)) for i, v in enumerate(ca.values)], NAVY, 3.4)
    ix = xs(len(ca) - 1); b += L(ix, Tm, ix, hh - Bm, "#6b7a90", 1.2, "3 3") + T(ix + 4, Tm + 10, "Today", 10, "#6b7a90")
    var = ca.iloc[-1] - cp.loc[ca.index[-1]]
    b += T(ix - 8, ys(ca.iloc[-1]) - 8, f"Actual ${ca.iloc[-1]:,.0f}M", 11, NAVY, "end", 700) + T(ix + 8, ys(cp.loc[ca.index[-1]]) + 30, f"Plan ${cp.loc[ca.index[-1]]:,.0f}M", 11, "#6b7a90", "start", 700)
    b += T(xs(48), ys(900), f"Actual spend is about ${round(var,-1):,.0f}M", 11, RED, "middle", 700) + T(xs(48), ys(900) + 14, "above plan to date", 11, RED, "middle", 700)
    o.append(h.replace("{D}", SVG(w, hh, b)))
    # E actions
    x, y, w_, h_ = card(P["e"])
    acts = [("Fast-track the Poland coal exit", "or replace with firm capacity: 1.85 Mt/yr, the whole gap."), ("Fund the 12 unfunded options", "1.8 Mt/yr for $285M; two-thirds at negative cost."),
            ("Unblock CCGT and refinery CCUS", "1.1 Mt/yr at risk; decide by Q1 2028."), ("Plan removals / offsets", "for the residual ~1.3 Mt by 2030.")]
    body = "".join(f"<div style='display:flex;gap:9px;margin-bottom:10px'><div style='min-width:22px;height:22px;border-radius:11px;background:{AMBER};color:{NAVY};text-align:center;font-weight:700;line-height:22px;font-size:12px'>{i+1}</div><div><b style='color:{AMBER}'>{a_}</b><br><span style='font-size:12px;color:#d8e4f2'>{b_}</span></div></div>" for i, (a_, b_) in enumerate(acts))
    o.append(f'<div class="sheet" style="left:{x+14}px;top:{y+44}px;width:{w_-28}px;height:{h_-56}px;color:#fff;font-size:13px;line-height:1.3">{body}</div>')
    return o


VAL = {"region": "(All)", "business_unit": "(All)", "asset_type": "(All)", "reporting_month": "Sep 2027", "source": "(All)", "status": "3 selected", "lever": "(All)", "risk": "(All)"}
def fbar(key):
    o = []
    for f in LAY[key + "_filters"]:
        st = f"left:{f['ctrl_x']}px;top:{f['ctrl_y']}px;width:{f['ctrl_w']}px;height:{f['ctrl_h']}px"
        if f["id"] == "top_n_assets":
            o.append(f'<div class="sheet" style="{st};display:flex;align-items:center;gap:8px;font-size:11.5px;color:{NAVY};font-weight:700"><div style="flex:1;height:4px;background:#cfd9e4;border-radius:2px;position:relative"><div style="position:absolute;left:0;top:0;height:4px;width:45%;background:{TEAL};border-radius:2px"></div><div style="position:absolute;left:45%;top:-5px;width:14px;height:14px;border-radius:7px;background:{TEAL};border:2px solid #fff;box-shadow:0 0 2px #667"></div></div><span>15</span></div>')
        else:
            o.append(f'<div class="sheet" style="{st};display:flex;align-items:center;justify-content:space-between;font-size:11.5px;color:{NAVY};font-weight:700;background:#fff;border:1px solid #cfd9e4;border-radius:5px;padding:0 8px;box-sizing:border-box"><span>{VAL.get(f["id"], "(All)")}</span><span style="color:{GREY};font-size:9px">&#9660;</span></div>')
    return "".join(o)

def icon_b64(n): return "data:image/png;base64," + base64.b64encode(open(os.path.join(ROOT, "assets", "icons", "png", n + "_white.png"), "rb").read()).decode()
TABS = [("overview", "Executive Overview"), ("drivers", "Drivers &amp; Hotspots"), ("plan", "Pathway &amp; Investment")]
TIPS = {1: "Tip: click a bar to cross-filter the page", 2: "Tip: select a heatmap cell to filter the asset list", 3: "Scenario chart is company-wide (not filtered)"}
def chrome(i):
    o = []
    for k, (ic, lab) in enumerate(TABS):
        act = k == i
        o.append(f'<a class="tab" href="{PAGES[k][0]}" style="left:{1020+k*192}px;{"background:#13A89E;" if act else "border:1px solid #4B6A91;"}color:{"#fff" if act else "#C9D8EA"}"><img src="{icon_b64(ic)}" width="20" height="20">{lab}</a>')
    o.append('<div style="position:absolute;left:64px;top:96px;font-size:12px;font-weight:700;color:#13315C;letter-spacing:.3px">FILTERS</div>')
    for f in LAY[f"page{i+1}_filters"]:
        o.append(f'<div style="position:absolute;left:{f["x"]}px;top:92px;width:{f["w"]}px;height:28px;border:1px solid #D5DFEA;background:#F4F7FA;border-radius:7px"></div>'
                 f'<div style="position:absolute;left:{f["label_x"]+10}px;top:99px;font-size:10px;font-weight:700;color:#8D99AE;letter-spacing:.3px">{f["label"].upper()}</div>')
    o.append(f'<div style="position:absolute;right:40px;top:98px;font-size:11px;color:#8D99AE">{TIPS[i+1]}</div>')
    return "".join(o)

# ------------------------------------------------------------------ page shell
CSS = """
html,body{margin:0;background:#2b3442;font-family:Lato,'Segoe UI',Arial,sans-serif}
#stage{position:absolute;left:0;top:0;width:1600px;height:900px;transform-origin:0 0}
#stage img.bg{position:absolute;left:0;top:0;width:1600px;height:900px;display:block}
.sheet{position:absolute;overflow:hidden}.sheet svg{display:block}
.tab{position:absolute;top:20px;width:180px;height:36px;box-sizing:border-box;border-radius:18px;display:flex;align-items:center;gap:8px;padding-left:14px;font:700 12px Lato,'Segoe UI',Arial,sans-serif;text-decoration:none}
.nav{position:absolute;top:20px;width:180px;height:36px;border-radius:18px;cursor:pointer;display:block}
.foot{position:absolute;left:24px;top:884px;font-size:10px;color:#8D99AE}
.dot{display:inline-block;width:11px;height:11px;border-radius:6px;vertical-align:middle}
table.trk{border-collapse:collapse;width:100%;table-layout:auto;font-size:10.5px;color:#24344d}
table.trk th{position:sticky;top:0;background:#fff;text-align:left;font-weight:700;color:#5b6b82;padding:3px 5px;border-bottom:1.5px solid #cfd9e4;white-space:nowrap}
table.trk td{height:20px;line-height:14px;vertical-align:middle;padding:0 5px;border-bottom:1px solid #eef2f6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:170px}
table.trk tr:nth-child(even) td{background:#f8fafc}.n{text-align:right!important}
"""
PAGES = [("Dashboard_1_Executive_Overview.html", "bg_page1_overview.png", p1, "Executive overview"),
         ("Dashboard_2_Drivers_Hotspots.html", "bg_page2_drivers.png", p2, "Drivers & hotspots"),
         ("Dashboard_3_Pathway_Investment.html", "bg_page3_investment.png", p3, "Pathway & investment")]
for i, (fn, bg, fnc, title) in enumerate(PAGES):
    navs = "".join(f'' for k in range(3))
    html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Meridian Net-Zero - {title} (target view)</title><style>{CSS}</style></head><body>"
            f"<div id='stage'><img class='bg' src='data:image/png;base64,{base64.b64encode(open(os.path.join(ROOT,'assets','backgrounds',bg),'rb').read()).decode()}'>{navs}{''.join(fnc())}{chrome(i)}{fbar('page%d' % (i+1))}"
            f"<div class='foot'>Target view for Tableau build (filter controls shown with default values). Source: Meridian simulated data | Scope 1 &amp; 2 | Actuals to Sep 2027 | Tab buttons are clickable. Header tabs and filter slots are drawn here for reference; in Tableau they are real objects over a clean background.</div></div>"
            "<script>function fit(){var s=Math.min(innerWidth/1600,innerHeight/900);document.getElementById('stage').style.transform='scale('+s+')';}"
            "fit();addEventListener('resize',fit);</script></body></html>")
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(html); print("wrote", fn, len(html))
