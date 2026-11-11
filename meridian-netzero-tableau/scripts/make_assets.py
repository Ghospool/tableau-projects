"""Builds dashboard backgrounds (1600x900), icons (SVG + PNG), logo and layout.json for the Tableau guide."""
import os, re, json, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
BG = os.path.join(ROOT, "assets", "backgrounds"); IC_PNG = os.path.join(ROOT, "assets", "icons", "png"); IC_SVG = os.path.join(ROOT, "assets", "icons", "svg")
for d in (BG, IC_PNG, IC_SVG): os.makedirs(d, exist_ok=True)

NAVY, NAVY2, TEAL, GREEN, AMBER, RED, GREY, CANVAS = "#0B2545", "#13315C", "#13A89E", "#7AC74F", "#F2A541", "#D64550", "#8D99AE", "#EEF2F6"
COL = {"navy": NAVY, "white": "#FFFFFF", "teal": TEAL, "red": RED, "grey": GREY}
FD = "/usr/share/fonts/truetype/"
def font(name, size): return ImageFont.truetype(FD + name, size)
H1 = lambda s: font("google-fonts/Poppins-Medium.ttf", s); LB = lambda s: font("lato/Lato-Bold.ttf", s); LR = lambda s: font("lato/Lato-Regular.ttf", s)

# ---------------------------------------------------------------- icons
ICONS = {
 "overview": [("p", "M3 11 L12 3 L21 11 M5 9.5 L5 20 L19 20 L19 9.5 M10 20 L10 14 L14 14 L14 20")],
 "drivers": [("p", "M4 20 L21 20 M5 12 L8 12 L8 20 L5 20 Z M10.5 7 L13.5 7 L13.5 20 L10.5 20 Z M16 3.5 L19 3.5 L19 20 L16 20 Z")],
 "plan": [("p", "M9 6 L20 6 M9 12 L20 12 M9 18 L20 18 M3 6 L4.5 7.5 L7 4.5 M3 12 L4.5 13.5 L7 10.5 M3 18 L4.5 19.5 L7 16.5")],
 "co2_cloud": [("p", "M7 18 C3.5 18 3 13.5 6.5 12.8 C6.5 8.5 12 6.5 14 10 C17 8.5 21 11.5 18.5 14.5 C21.5 14.5 21.5 18 18.5 18 Z")],
 "factory": [("p", "M3 20 L3 10 L8 13 L8 10 L13 13 L13 6 L17 6 L17 20 Z M20 20 L20 13 L17 13 M6 20 L6 17 M10 20 L10 17")],
 "bolt": [("p", "M13 2 L5 13 L11 13 L10 22 L19 10 L13 10 Z")],
 "leaf": [("p", "M5 19 C5 9 11 4 20 4 C20 13 15 19 5 19 Z M5 19 L13 11")],
 "wind": [("p", "M12 12 L12 22 M12 12 L12 3 M12 12 L19.5 16 M12 12 L4.5 16"), ("c", 12, 12, 1.6)],
 "solar": [("c", 12, 12, 4), ("p", "M12 2 L12 5 M12 19 L12 22 M2 12 L5 12 M19 12 L22 12 M5 5 L7 7 M17 17 L19 19 M19 5 L17 7 M5 19 L7 17")],
 "flame": [("p", "M12 3 C13 8 18 9 18 15 C18 19 15 21 12 21 C9 21 6 19 6 15 C6 12 8 11 9 8 C10 10 11 10 12 3 Z")],
 "methane": [("p", "M12 3 C12 3 5 11 5 15 C5 19 8 21 12 21 C16 21 19 19 19 15 C19 11 12 3 12 3 Z")],
 "target": [("c", 12, 12, 9), ("c", 12, 12, 5), ("c", 12, 12, 1.3)],
 "trend_down": [("p", "M3 6 L9 12 L13 8 L21 16 M21 16 L21 10 M21 16 L15 16")],
 "dollar": [("c", 12, 12, 9.5), ("p", "M14.5 9.2 C14 8.2 13 7.7 12 7.7 C10.5 7.7 9.5 8.5 9.5 9.6 C9.5 12 14.5 11 14.5 14.4 C14.5 15.6 13.5 16.4 12 16.4 C10.8 16.4 9.8 15.9 9.3 14.9 M12 6 L12 7.7 M12 16.4 L12 18")],
 "delay": [("c", 12, 12, 9.5), ("p", "M12 7 L12 12 L16 14")],
 "warning": [("p", "M12 3 L22 20 L2 20 Z M12 9.5 L12 14 M12 17 L12 17.2")],
 "pin": [("p", "M12 21 C12 21 5 14 5 10 C5 6 8 3 12 3 C16 3 19 6 19 10 C19 14 12 21 12 21 Z"), ("c", 12, 10, 2.5)],
 "efficiency": [("p", "M3.5 18 C3.5 8 20.5 8 20.5 18 M12 18 L16 11.5 M3.5 18 L20.5 18")],
 "ccus": [("p", "M4 21 L20 21 M7 21 L7 11 L17 11 L17 21 M12 11 L12 3 M9 6 L12 3 L15 6")],
 "filter": [("p", "M3 4 L21 4 L14 12 L14 20 L10 18 L10 12 Z")],
 "info": [("c", 12, 12, 9.5), ("p", "M12 11 L12 17 M12 7.4 L12 7.6")],
 "check": [("c", 12, 12, 9.5), ("p", "M7.5 12.5 L10.5 15.5 L16.5 9")],
 "arrow_up_right": [("p", "M7 17 L17 7 M8 7 L17 7 L17 16")],
 "money_bag": [("p", "M9 3 L15 3 L13.5 7 M10.5 7 L13.5 7 C19 10 20 20 12 20.5 C4 20 5 10 10.5 7 Z M12 11 L12 17")],
}

def parse_path(d, n=24):
    """absolute M L C Q Z -> list of polylines"""
    toks = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d); i = 0; polys = []; cur = []; pos = (0, 0); start = (0, 0)
    f = lambda: float(toks[i])
    while i < len(toks):
        c = toks[i]; i += 1
        if c == "M":
            if cur: polys.append(cur)
            pos = (float(toks[i]), float(toks[i + 1])); i += 2; start = pos; cur = [pos]
        elif c == "L":
            pos = (float(toks[i]), float(toks[i + 1])); i += 2; cur.append(pos)
        elif c == "C":
            p = [(float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])) for k in range(3)]; i += 6
            for s in range(1, n + 1):
                t = s / n; a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; cc = 3 * (1 - t) * t * t; dd = t ** 3
                cur.append((a * pos[0] + b * p[0][0] + cc * p[1][0] + dd * p[2][0], a * pos[1] + b * p[0][1] + cc * p[1][1] + dd * p[2][1]))
            pos = p[2]
        elif c == "Q":
            p = [(float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])) for k in range(2)]; i += 4
            for s in range(1, n + 1):
                t = s / n; cur.append(((1 - t) ** 2 * pos[0] + 2 * (1 - t) * t * p[0][0] + t * t * p[1][0], (1 - t) ** 2 * pos[1] + 2 * (1 - t) * t * p[0][1] + t * t * p[1][1]))
            pos = p[1]
        elif c == "Z":
            cur.append(start); pos = start
    if cur: polys.append(cur)
    return polys

def icon_svg(name, color=NAVY, sw=1.8):
    parts = []
    for e in ICONS[name]:
        if e[0] == "p": parts.append(f'<path d="{e[1]}"/>')
        else: parts.append(f'<circle cx="{e[1]}" cy="{e[2]}" r="{e[3]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{"".join(parts)}</svg>')

def icon_img(name, color, px=128, sw=1.8):
    S = 16; im = Image.new("RGBA", (24 * S, 24 * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im); w = int(sw * S)
    def seg(poly):
        pts = [(x * S, y * S) for x, y in poly]; dr.line(pts, fill=color, width=w, joint="curve")
        for x, y in (pts[0], pts[-1]): dr.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=color)
    for e in ICONS[name]:
        if e[0] == "p":
            for poly in parse_path(e[1]): seg(poly)
        else:
            cx, cy, r = e[1], e[2], e[3]; seg([(cx + r * math.cos(a / 40 * 2 * math.pi), cy + r * math.sin(a / 40 * 2 * math.pi)) for a in range(41)])
    return im.resize((px, px), Image.LANCZOS)

for n in ICONS:
    open(os.path.join(IC_SVG, f"{n}.svg"), "w").write(icon_svg(n))
    for cn, c in COL.items(): icon_img(n, c).save(os.path.join(IC_PNG, f"{n}_{cn}.png"))

# logo mark + wordmark
def logo(px=256):
    S = 4; im = Image.new("RGBA", (px * S, px * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, px * S - 1, px * S - 1], radius=px * S // 4, fill=TEAL)
    lf = icon_img("leaf", "#FFFFFF", px * S * 6 // 10, sw=1.9); im.alpha_composite(lf, (px * S // 5, px * S // 5))
    return im.resize((px, px), Image.LANCZOS)
logo(256).save(os.path.join(ROOT, "assets", "logo_meridian.png"))
open(os.path.join(ROOT, "assets", "logo_meridian.svg"), "w").write(
 f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="256" height="256"><rect width="64" height="64" rx="16" fill="{TEAL}"/>'
 f'<g transform="translate(12.8 12.8) scale(1.6)" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS["leaf"][0][1]}"/></g></svg>')

# ---------------------------------------------------------------- backgrounds
W, Hh = 1600, 900
def card(img, x, y, w, h, title, fill="#FFFFFF", tcol=GREY, accent=TEAL, sub=None, icon=None, stripe=None):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x, y + 3, x + w, y + h + 3], 10, fill=(11, 37, 69, 38)); sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(sh); d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], 10, fill=fill)
    if stripe: d.rounded_rectangle([x, y, x + w, y + 5], 3, fill=stripe); d.rectangle([x, y + 3, x + w, y + 5], fill=stripe)
    d.rectangle([x + 14, y + 14, x + 17, y + 30], fill=accent)
    d.text((x + 26, y + 13), title.upper(), font=LB(13), fill=tcol)
    if sub: d.text((x + 26, y + 31), sub, font=LR(11), fill=GREY if fill == "#FFFFFF" else "#A9C4E0")
    if icon: img.alpha_composite(icon_img(icon, GREY if fill == "#FFFFFF" else "#FFFFFF", 36), (x + w - 52, y + 14))

def filter_bar(img, slots, tip):
    """clean white strip (24,88)-(1576,124) only; slot geometry is returned for the guide (nothing baked into the picture)"""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([24, 91, 1576, 127], 10, fill=(11, 37, 69, 34)); sh = sh.filter(ImageFilter.GaussianBlur(4)); img.alpha_composite(sh)
    ImageDraw.Draw(img).rounded_rectangle([24, 88, 1576, 124], 10, fill="#FFFFFF")
    out = []
    for sl in slots:
        sl2 = dict(sl); sl2.update(y=92, h=28, label_x=sl["x"], label_y=92, label_w=104, label_h=28,
                                   ctrl_x=sl["x"] + 108, ctrl_y=94, ctrl_w=sl["w"] - 114, ctrl_h=24); out.append(sl2)
    return out

def page(idx, title, subtitle, panels, kpis, layout_name, slots, tip):
    img = Image.new("RGBA", (W, Hh), CANVAS); d = ImageDraw.Draw(img)
    for xx in range(W):  # header gradient
        t = xx / W; c = tuple(int(a + (b - a) * t) for a, b in zip((11, 37, 69), (19, 49, 92))); d.line([(xx, 0), (xx, 76)], fill=c)
    d.rectangle([0, 76, W, 79], fill=TEAL)
    img.alpha_composite(logo(48), (24, 14)); d = ImageDraw.Draw(img)
    d.text((86, 12), title, font=H1(24), fill="#FFFFFF"); d.text((86, 46), subtitle, font=LR(12), fill="#9FD8D3")
    fl = filter_bar(img, slots, tip)
    lay = []
    for p in kpis + panels:
        x, y, w, h = p["box"]
        card(img, x, y, w, h, p["title"], fill=p.get("fill", "#FFFFFF"), tcol="#FFFFFF" if p.get("fill") == NAVY else NAVY2,
             accent=p.get("accent", TEAL), sub=p.get("sub"), icon=p.get("icon"), stripe=p.get("stripe"))
        lay.append(dict(id=p["id"], title=p["title"], x=x, y=y, w=w, h=h, kind=p.get("kind", "chart"), hint=p.get("hint", "")))
    img.convert("RGB").save(os.path.join(BG, f"bg_page{idx+1}_{layout_name}.png"), optimize=True)
    return lay, fl

def kpi_row(y, h, items, gap=16):
    n = len(items); w = (W - 48 - gap * (n - 1)) // n
    return [dict(id=f"k{i+1}", title=t, box=(24 + i * (w + gap), y, w, h), icon=ic, stripe=col, accent=col, kind="kpi", hint=hint) for i, (t, ic, col, hint) in enumerate(items)]

def S(label, x, w, control, field, note): return dict(id=label.lower().replace(" ", "_"), label=label, x=x, w=w, control=control, field=field, note=note)
L = {}
# PAGE 1  (filter bar y 88-124, KPI y136 h108, row2 y256 h300, row3 y568 h312)
k1 = kpi_row(136, 108, [("2027 YTD emissions (MtCO2e)", "co2_cloud", NAVY2, "SUM emissions Jan-Sep 2027 + big number + delta vs same period 2024"),
                       ("Change vs 2024 baseline", "trend_down", GREEN, "% change YTD vs 2024 YTD (green = reducing)"),
                       ("Gap to pathway (MtCO2e)", "target", RED, "YTD actual - YTD target; red when above path"),
                       ("Carbon cost exposure ($M YTD)", "dollar", AMBER, "SUM carbon_cost_usd / 1e6, YTD")])
p1 = [dict(id="a", title="Emissions vs 2030 pathway", sub="Monthly, MtCO2e: actual vs target glide path vs net-zero 2050 line", box=(24, 256, 1020, 300), hint="Dual-line + area; reference band for gap"),
      dict(id="b", title="Where the gap sits", sub="YTD variance to pathway by business unit", box=(1060, 256, 516, 300), hint="Diverging bar by BU (red = above path)"),
      dict(id="c", title="Emissions by region", sub="2027 YTD, MtCO2e", box=(24, 568, 500, 312), hint="Horizontal bar by region"),
      dict(id="d", title="Source mix by year", sub="Scope 1 & 2 categories, 2024-2027 YTD", box=(540, 568, 500, 312), hint="100% stacked bar by year x source_category"),
      dict(id="e", title="Key messages", box=(1056, 568, 520, 312), fill=NAVY, accent=AMBER, kind="text", hint="Text object: 4 insight lines (see guide)")]
sl1 = [S("Region", 130, 240, "Multiple values (dropdown)", "dim_asset.Region", "Default (All)"), S("Business Unit", 382, 240, "Multiple values (dropdown)", "dim_asset.Business Unit", "Default (All)"),
       S("Asset Type", 634, 240, "Multiple values (dropdown)", "dim_asset.Asset Type", "Default (All)"), S("Reporting month", 886, 240, "Single value (dropdown)", "Parameter p_AsOf (list Jan-Sep 2027)", "Default Sep 2027")]
L["page1"], L["page1_filters"] = page(0, "Is Meridian on track for its 2030 net-zero milestone?", "Executive overview  |  Scope 1 & 2  |  Target: -45% vs 2024 by 2030", p1, k1, "overview", sl1, "Tip: click a bar to cross-filter the page")
# PAGE 2  (KPI y136 h92, rows y240; a h640; b,d y240 h312; c,e y564 h316)
k2 = kpi_row(136, 92, [("Coal share of emissions", "factory", NAVY2, "Coal plants / total YTD"), ("Methane + flaring (kt)", "flame", AMBER, "Fugitive Methane + Flaring YTD"),
                      ("Coal plants still operating", "warning", RED, "Count of coal plants with emissions in the as-of month"), ("Top 10 assets share", "target", RED, "Pareto: top 10 assets / total"),
                      ("Scope 2 share", "bolt", GREEN, "Scope 2 / total")])
p2 = [dict(id="a", title="Top 15 emitting assets", sub="2027 YTD, ktCO2e, coloured by asset type", box=(24, 240, 520, 640), hint="Sorted horizontal bar, top-N parameter"),
      dict(id="b", title="Asset footprint map", sub="Bubble size = YTD emissions", box=(560, 240, 600, 312), hint="Symbol map lat/long, size=emissions, colour=BU"),
      dict(id="c", title="Asset type x source heatmap", sub="2027 YTD ktCO2e", box=(560, 564, 600, 316), hint="Highlight table / heatmap"),
      dict(id="d", title="Intensity trend", sub="tCO2e per unit of activity, indexed 2024 = 100", box=(1176, 240, 400, 312), hint="Line by asset type group"),
      dict(id="e", title="Methane & flaring", sub="Monthly ktCO2e", box=(1176, 564, 400, 316), hint="Area chart")]
sl2 = [S("Region", 130, 230, "Multiple values (dropdown)", "dim_asset.Region", "Default (All)"), S("Business Unit", 372, 230, "Multiple values (dropdown)", "dim_asset.Business Unit", "Default (All)"),
       S("Asset Type", 614, 230, "Multiple values (dropdown)", "dim_asset.Asset Type", "Default (All)"), S("Source", 856, 230, "Multiple values (dropdown)", "dim_source.Source Category", "Default (All)"),
       S("Top N assets", 1098, 230, "Slider (parameter)", "Parameter p_TopN", "Default 15")]
L["page2"], L["page2_filters"] = page(1, "Where do emissions come from - and where are we stuck?", "Drivers & hotspots  |  asset, region and source level", p2, k2, "drivers", sl2, "Tip: select a heatmap cell to filter the asset list")
# PAGE 3  (KPI y136 h92; row2 y240 h322; row3 y574 h306)
k3 = kpi_row(136, 92, [("Funded capex ($M)", "money_bag", NAVY2, "SUM capex of funded projects"), ("Abatement delivered (Mt/yr)", "check", GREEN, "Delivered projects annual abatement"),
                      ("Abatement at risk (Mt/yr)", "warning", RED, "Delayed projects annual abatement"), ("Avg abatement cost ($/t)", "dollar", TEAL, "Abatement-weighted MACC")])
p3 = [dict(id="a", title="Marginal abatement cost curve", sub="Width = annual abatement (Mt), height = $/tCO2e, colour = status", box=(24, 240, 780, 322), hint="Filled polygon blocks, DS4 MACC"),
      dict(id="b", title="Scenarios to 2030", sub="Business as usual vs committed plan vs accelerated vs target (company-wide, not filtered)", box=(820, 240, 756, 322), hint="Line chart by scenario + target line"),
      dict(id="c", title="Project delivery tracker", sub="Delayed & in-flight projects first", box=(24, 574, 780, 306), hint="Table with coloured status dots"),
      dict(id="d", title="Capex: planned vs actual", sub="Cumulative $M", box=(820, 574, 370, 306), hint="Dual line"),
      dict(id="e", title="Recommended actions", box=(1206, 574, 370, 306), fill=NAVY, accent=AMBER, kind="text", hint="Text object: 4 decisions for the board")]
sl3 = [S("Status", 130, 240, "Multiple values (dropdown)", "dim_project.Status", "Default: Delayed, In Execution, Planned"), S("Lever", 382, 240, "Multiple values (dropdown)", "dim_project.Lever Group", "Default (All)"),
       S("Region", 634, 240, "Multiple values (dropdown)", "dim_asset.Region (DS2)", "Default (All)"), S("Risk", 886, 240, "Multiple values (dropdown)", "dim_project.Risk Rating", "Default (All)")]
L["page3"], L["page3_filters"] = page(2, "What will it take to close the gap by 2030?", "Pathway & investment  |  abatement levers, delivery risk and scenarios", p3, k3, "investment", sl3, "Scenario chart is company-wide (not filtered)")
json.dump(L, open(os.path.join(ROOT, "assets", "layout.json"), "w"), indent=1)


# ---- navigation button images (360x72 = 180x36 @2x, transparent) : 3 pages x active/inactive
NAVD = os.path.join(ROOT, "assets", "nav_buttons"); os.makedirs(NAVD, exist_ok=True)
for key, ic, lab in [("executive", "overview", "Executive Overview"), ("drivers", "drivers", "Drivers & Hotspots"), ("pathway", "plan", "Pathway & Investment")]:
    for state in ("active", "inactive"):
        S = 4; im = Image.new("RGBA", (180 * S, 36 * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        if state == "active": dr.rounded_rectangle([0, 0, 180 * S - 1, 36 * S - 1], 18 * S, fill=TEAL)
        else: dr.rounded_rectangle([S, S, 180 * S - S - 1, 36 * S - S - 1], 18 * S, fill=(255, 255, 255, 8), outline="#4B6A91", width=S)
        im.alpha_composite(icon_img(ic, "#FFFFFF", 20 * S), (14 * S, 8 * S)); dr = ImageDraw.Draw(im)
        dr.text((42 * S, 18 * S), lab, font=LB(12 * S), fill="#FFFFFF" if state == "active" else "#C9D8EA", anchor="lm")
        im.resize((360, 72), Image.LANCZOS).save(os.path.join(NAVD, f"nav_{key}_{state}.png"))

# contact sheet of icons
names = list(ICONS); cols = 8; sheet = Image.new("RGB", (cols * 120, ((len(names) + cols - 1) // cols) * 120), "#FFFFFF"); dd = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    x, y = (i % cols) * 120, (i // cols) * 120; sheet.paste(icon_img(n, NAVY, 64), (x + 28, y + 12), icon_img(n, NAVY, 64))
    dd.text((x + 60, y + 90), n, font=LR(11), fill=NAVY, anchor="ma")
sheet.save(os.path.join(ROOT, "assets", "icons", "icon_contact_sheet.png"))
print("assets done", len(ICONS), "icons")
