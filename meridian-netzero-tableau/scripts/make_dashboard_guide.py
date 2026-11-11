"""Generates Dashboard_Assembly_Guide.html (step-by-step per dashboard) from assets/layout.json."""
import os, json
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LAY = json.load(open(os.path.join(ROOT, "assets", "layout.json")))
Image.new("RGBA", (180, 36), (0, 0, 0, 0)).save(os.path.join(ROOT, "assets", "transparent_nav_button_180x36.png"))

# card id -> (object name, kind, dashboard-level settings)
PAGES = [
 dict(key="page1", n=1, bg="bg_page1_overview.png", name="Dashboard 1 - Executive Overview", preview="Dashboard_1_Executive_Overview.html",
  items={
   "k1": ("P1_KPI1", "Sheet (KPI text)", "Entire View. No legend."),
   "k2": ("P1_KPI2", "Sheet (KPI text)", "Entire View. Hide the KPI2 Colour legend."),
   "k3": ("P1_KPI3", "Sheet (KPI text)", "Entire View. Hide the Gap Status legend."),
   "k4": ("P1_KPI4", "Sheet (KPI text)", "Entire View."),
   "a": ("P1_Pathway", "Sheet", "Entire View. Hide the Measure Names legend (lines are labelled). Hide title."),
   "b": ("P1_BU_Gap", "Sheet", "Entire View. Hide the Gap Status legend."),
   "c": ("P1_Region", "Sheet", "Entire View. Hide the colour legend."),
   "d": ("P1_SourceMix", "Sheet", "Width = card width - 24 - 140 (chart only). Keep its Source Category legend as a separate floating legend, see step below."),
   "e": ("P1_Messages", "Sheet (or Text object)", "White Lato 13-14pt text on the dark card. Sheet background None."),
  },
  extras=[
   ("Legend: Source Category", "Floating legend (click P1_SourceMix &gt; dropdown &gt; Legends &gt; Source Category, then float it)", 1056-140-24+0-0, None),
  ],
  filters=[("Region", "dim_asset Region", "Single-value dropdown, All default; apply to DS1 sheets"), ("Business Unit", "dim_asset Business Unit", "Multi-value dropdown")],
  actions=[("Filter", "Select on P1_Region", "Target: P1_BU_Gap and P1_SourceMix only (not P1_Pathway: the target line is not region-specific)", "Select"),
           ("Highlight", "Hover on P1_BU_Gap", "Fields: Business Unit; Target: P1_BU_Gap, P1_Pathway", "Hover")],
  checks=["P1_KPI1 = 19.3, KPI2 = -14.0% (green), KPI3 = +1.7 (red), KPI4 = $1,220",
          "Navy actual line sits above the teal target line; red 'Gap +1.7 Mt YTD' callout at 'Today'",
          "Business-unit gaps: Upstream +0.57, Midstream & Refining +0.55, Power +0.53, Networks +0.06, Renewables +0.03",
          "Regions: North America 7.4, Continental Europe 5.7, Asia Pacific 2.5, UK & North Sea 2.4, Middle East 1.3-1.4",
          "Source mix bars total 100%, combustion about 76%"]),
 dict(key="page2", n=2, bg="bg_page2_drivers.png", name="Dashboard 2 - Drivers &amp; Hotspots", preview="Dashboard_2_Drivers_Hotspots.html",
  items={
   "k1": ("P2_KPI1", "Sheet (KPI text)", "Coal share, format 0.0%."),
   "k2": ("P2_KPI2", "Sheet (KPI text)", "Methane + flaring kt, format #,##0."),
   "k3": ("P2_KPI3", "Sheet (KPI text)", "Coal plants still operating (4 of 6)."),
   "k4": ("P2_KPI4", "Sheet (KPI text)", "Top 10 assets share, table calc: keep Asset Name on Detail."),
   "k5": ("P2_KPI5", "Sheet (KPI text)", "Scope 2 share, format 0.0%."),
   "a": ("P2_TopAssets", "Sheet", "Entire View. Hide the legend and the p_TopN control inside the sheet (placed separately below)."),
   "b": ("P2_Map", "Sheet", "Entire View. Hide the size legend and the map controls (Map &gt; Map Options)."),
   "c": ("P2_Heatmap", "Sheet", "Entire View. Hide the colour legend."),
   "d": ("P2_Intensity", "Sheet", "Entire View. Hide the legend (line-end labels)."),
   "e": ("P2_Methane", "Sheet", "Entire View. Hide the legend or keep it in the sheet top-left."),
  },
  extras=[],
  filters=[("Region", "dim_asset Region", "Dropdown, same as page 1 (set 'Apply to worksheets &gt; All using related data sources')"),
           ("p_TopN", "Parameter control", "Slider; place inside the Top Assets card header: X 380, Y 210, W 150, H 30")],
  actions=[("Highlight", "Select on P2_TopAssets", "Fields: Asset Name; Target: P2_Map", "Select"),
           ("Filter", "Select on P2_Heatmap", "Target: P2_TopAssets (filters by Asset Type or Source); Clearing: Show all values", "Select")],
  checks=["KPIs: 22.4%, 2,230, 4 of 6, 45.7%, 5.0%",
          "Top-15 bars: Poland coal 1,392 kt first, then Malaysia 1,058, Indonesia 1,043, Netherlands refinery 1,026",
          "Heatmap darkest cells: Gas CCGT x Stationary (6,161) and Coal x Stationary (4,188)",
          "Intensity: coal falls to about 64 by 2027 (simulation quirk, see note in guide), CCGT 96, refinery 86",
          "Methane + flaring about 2.2 Mt YTD, with flaring (amber) in the lower band"]),
 dict(key="page3", n=3, bg="bg_page3_investment.png", name="Dashboard 3 - Pathway &amp; Investment", preview="Dashboard_3_Pathway_Investment.html",
  items={
   "k1": ("P3_KPI1", "Sheet (KPI text)", "Funded capex $M, format $#,##0."),
   "k2": ("P3_KPI2", "Sheet (KPI text)", "Abatement Delivered Mt, 1 decimal, green."),
   "k3": ("P3_KPI3", "Sheet (KPI text)", "Abatement At Risk Mt, 1 decimal, red."),
   "k4": ("P3_KPI4", "Sheet (KPI text)", "Wtd Avg MACC, $0."),
   "a": ("P3_MACC", "Sheet (DS4 MACC)", "Entire View. Hide the legend inside the sheet and use the floating legend step below."),
   "b": ("P3_Scenarios", "Sheet (DS3)", "Entire View. Hide the legend (line-end labels)."),
   "c": ("P3_Tracker", "Sheet", "Fit: Entire Width; keep scrolling enabled (do NOT use Entire View, it would shrink the font)."),
   "d": ("P3_Capex", "Sheet", "Entire View. Hide the legend (Plan / Actual labelled)."),
   "e": ("P3_Actions", "Sheet (or Text object)", "White Lato 12-13pt text on the dark card."),
  },
  extras=[],
  filters=[],
  actions=[("Highlight", "Select on P3_Tracker", "Fields: Project Name; Target: P3_MACC (works because both sheets use the same field name)", "Select"),
           ("Filter", "Select on P3_MACC", "Target: P3_Tracker; Clearing: Show all values", "Select")],
  checks=["KPIs: $1,853, 5.3, 3.0, $11",
          "MACC: total width about 7 Mt; Poland coal exit widest block (red, about -$20/t); CCUS blocks on the right at $85-100",
          "Scenarios in 2030: BAU 31.6, Committed 20.7, Accelerated 18.9, Target 17.6; red gap shading",
          "Tracker: 8 Delayed rows first (Poland coal 1,850K, 18 months), coloured dots visible",
          "Capex: actual $1,935M vs planned $1,747M at Sep-27; tooltip says about $190M above plan"]),
]

def inner(p):
    k = p["kind"] == "kpi"; t = p["kind"] == "text"
    if k: return p["x"] + 16, p["y"] + 34, p["w"] - 32, p["h"] - 44
    if t: return p["x"] + 16, p["y"] + 44, p["w"] - 32, p["h"] - 56
    return p["x"] + 12, p["y"] + 44, p["w"] - 24, p["h"] - 56

def section(pg):
    lay = LAY[pg["key"]]; n = pg["n"]; o = [f'<section id="d{n}"><h2>{pg["name"]}</h2>']
    o.append(f'<p>Target look: <a href="Dashboard_Previews/{pg["preview"]}" target="_blank">open the preview</a>. Background file: <code>assets/backgrounds/{pg["bg"]}</code>.</p>')
    # Phase A
    o.append('<h3>Phase A - Create the canvas</h3><div class="steps">')
    o.append(f'<div class="step">Click the <b>New Dashboard</b> tab icon (bottom bar). Rename the dashboard <code>{pg["name"].replace("&amp;","&")}</code> (double-click the tab).</div>')
    o.append('<div class="step">Left pane &gt; <b>Size</b> &gt; <b>Fixed size</b> &gt; Custom: <b>Width 1600, Height 900</b>. Untick <b>Show dashboard title</b>.</div>')
    o.append('<div class="step">Set <b>Layout</b> tab (bottom-left) to show the Item hierarchy. Dashboard &gt; Format &gt; Shading: <code>#EEF2F6</code>.</div>')
    o.append(f'<div class="step">Drag an <b>Image</b> object (Objects &gt; Image) onto the canvas as <b>Floating</b> (click the Floating icon at the bottom-left of the object list, or drop while holding Shift). Choose <code>{pg["bg"]}</code>. In the Layout tab set <b>X 0, Y 0, W 1600, H 900</b>, tick <b>Fit image</b> and untick <b>Center image</b>; Border none, Background none.</div>')
    o.append('<div class="step">In the Item hierarchy (Layout tab) make sure this image is the <b>bottom-most</b> item. Every item you add later is above it. Do not lock it yet.</div></div>')
    # Phase B
    o.append('<h3>Phase B - Place the sheets (one by one, floating)</h3><p>For each row: drag the sheet from the left list onto the canvas, hold <b>Shift</b> while dropping (or click the sheet then the Floating icon), then in the <b>Layout</b> tab type X, Y, Width and Height. Then for the dashboard item: <b>Layout</b> tab &gt; Background: None, Border: None; and right-click the item &gt; untick <b>Show title</b>, <b>Fit &gt; Entire View</b> (unless noted).</p>')
    o.append('<table><tr><th>#</th><th>Sheet / object</th><th>Type</th><th>X</th><th>Y</th><th>W</th><th>H</th><th>Settings</th></tr>')
    for i, p in enumerate(lay, 1):
        nm, ty, st = pg["items"][p["id"]]; x, y, w, h = inner(p)
        o.append(f'<tr><td>{i}</td><td><b>{nm}</b><br><small>card: {p["title"]}</small></td><td>{ty}</td><td>{x}</td><td>{y}</td><td>{w}</td><td>{h}</td><td>{st}</td></tr>')
    o.append('</table>')
    o.append('<div class="tip">Order tip: place KPI cards first, then the big charts, then dark text cards. After every 2-3 items, check the Item hierarchy still has the background at the bottom.</div>')
    # source mix legend
    if pg["key"] == "page1":
        d = [p for p in lay if p["id"] == "d"][0]
        o.append(f'<h4>Extra: P1_SourceMix legend</h4><p>The chart above is {d["w"]-24-140} px wide to leave room for a legend. Resize the P1_SourceMix item to <b>W {d["w"]-24-140}</b>, then float its Source Category legend at <b>X {d["x"]+d["w"]-150}, Y {d["y"]+60}, W 130, H 150</b>; font 10, no border or background.</p>')
    if pg["key"] == "page2":
        a = [p for p in lay if p["id"] == "a"][0]; b = [p for p in lay if p["id"] == "b"][0]
        o.append(f'<h4>Extra: floating controls and legends</h4><table><tr><th>Item</th><th>X</th><th>Y</th><th>W</th><th>H</th><th>How</th></tr>'
                 f'<tr><td>Asset Group legend (P2_TopAssets)</td><td>{a["x"]+16}</td><td>{a["y"]+a["h"]-34}</td><td>{a["w"]-32}</td><td>26</td><td>Legend dropdown &gt; Floating; Layout: horizontal</td></tr>'
                 f'<tr><td>Business Unit legend (P2_Map)</td><td>{b["x"]+16}</td><td>{b["y"]+b["h"]-40}</td><td>{b["w"]-32}</td><td>34</td><td>Floating, horizontal, 10pt</td></tr></table>')
    if pg["key"] == "page3":
        a = [p for p in lay if p["id"] == "a"][0]
        o.append(f'<h4>Extra: P3_MACC legend</h4><p>Float the P3_MACC <b>Status</b> legend at <b>X {a["x"]+a["w"]-390}, Y {a["y"]+8}, W 370, H 28</b>, horizontal, 10pt, no border.</p>')
    # Phase C
    tabs = [("Executive Overview", 1020, "Dashboard 1 - Executive Overview", "executive"), ("Drivers &amp; Hotspots", 1212, "Dashboard 2 - Drivers &amp; Hotspots", "drivers"), ("Pathway &amp; Investment", 1404, "Dashboard 3 - Pathway &amp; Investment", "pathway")]
    o.append('<h3>Phase C - Navigation buttons (top right of the header; the background is left empty on purpose)</h3>')
    o.append('<p>Best method: use the ready-made pill images in <code>assets/nav_buttons/</code> (360x72 px, transparent, icon + label, active and inactive versions) as the face of Tableau <b>Navigation</b> buttons. They match the design exactly.</p>')
    o.append('<table><tr><th>Button</th><th>Navigate to</th><th>Image file</th><th>X</th><th>Y</th><th>W</th><th>H</th></tr>')
    for k, (t, x, tgt, key) in enumerate(tabs):
        st = "active" if k == n - 1 else "inactive"
        o.append(f'<tr><td><b>{t}</b></td><td>{tgt.replace("&amp;","&")}</td><td><code>nav_{key}_{st}.png</code></td><td>{x}</td><td>20</td><td>180</td><td>36</td></tr>')
    o.append('</table><div class="steps">')
    o.append('<div class="step">Objects &gt; <b>Navigation</b>; drop it as <b>Floating</b> anywhere on the canvas. In the dialog, choose <b>Choose sheet</b> = the target dashboard from the table.</div>')
    o.append('<div class="step">Right-click the button (or its dropdown arrow) &gt; <b>Format Button</b>. Under <b>Button style</b> choose <b>Image</b>, click <b>Select image...</b> and pick the file from the table. Tick <b>Fit image</b>.</div>')
    o.append('<div class="step">Still in Format Button: set Background <b>None</b> and Border <b>None</b>. Untick any title/text.</div>')
    o.append('<div class="step">Layout tab: type <b>X, Y, W, H</b> from the table (Y 20, W 180, H 36).</div>')
    o.append('<div class="step">Repeat for the other two buttons. On this dashboard the <b>current page uses the _active image</b>, the other two use _inactive. Copy the three buttons to the next dashboard and just swap which one is active (Format Button &gt; Select image) and the navigation target.</div>')
    o.append('<div class="step">Optional: Edit Button &gt; Tooltip, e.g. "Go to Drivers &amp; Hotspots".</div></div>')
    o.append('<div class="tip"><b>Fallback (no images):</b> Format Button &gt; Button style <b>Text</b>, Lato bold 12; active = teal #13A89E fill with white text, inactive = no fill, border #4B6A91, text #C9D8EA.</div>')
    fl = LAY[pg["key"] + "_filters"]
    o.append('<h3>Phase D - Filters (slicers) in the filter bar</h3>')
    o.append('<p>The white strip under the header (X 24, Y 88, W 1552, H 36) is empty. Put <b>two objects per filter</b>: (1) a small <b>Text object</b> as the label, then (2) the <b>filter / parameter control</b> to its right. Optional: a Text object "FILTERS" at X 40, Y 96, W 70, H 20 (Lato bold 12, navy) and a right-aligned hint text at the far right of the strip.</p>')
    o.append('<table><tr><th>Slot</th><th>Field</th><th>Control type</th><th>Default</th><th>Label object (X, Y, W, H)</th><th>Control (X, Y, W, H)</th></tr>')
    for sl in fl:
        o.append(f'<tr><td><b>{sl["label"]}</b></td><td>{sl["field"]}</td><td>{sl["control"]}</td><td>{sl["note"]}</td><td>{sl["label_x"]}, {sl["label_y"]}, {sl["label_w"]}, {sl["label_h"]}<br><small>text: {sl["label"].upper()}, Lato bold 10, grey #8D99AE</small></td><td>{sl["ctrl_x"]}, {sl["ctrl_y"]}, {sl["ctrl_w"]}, {sl["ctrl_h"]}</td></tr>')
    o.append('</table><div class="tip">Control look: filter title <b>hidden</b>, dropdown (compact), font Lato 10 bold navy, background white, border #CFD9E4. Optional slot backgrounds: float a Blank object with border #D5DFEA behind each label + control.</div><div class="steps">')
    if pg["key"] == "page1":
        o.append('<div class="step">Region, Business Unit, Asset Type: go to sheet <b>P1_Region</b>, drag the field to <b>Filters</b> (all values), right-click the pill &gt; <b>Show Filter</b>. Repeat on the same sheet for the other two fields, then delete the extra filter cards from that sheet.</div>')
        o.append('<div class="step">Reporting month: right-click parameter <code>p_AsOf</code> &gt; Edit &gt; Allowable values <b>List</b>: 1 Jan 2027 ... 1 Sep 2027 (type each date); Display format <code>mmm yyyy</code>; Current value 1 Sep 2027. Then right-click &gt; <b>Show Parameter</b> on any sheet.</div>')
        o.append('<div class="step">On the dashboard, click each filter card &gt; its arrow &gt; <b>Multiple Values (dropdown)</b> (Reporting month: Single Value dropdown). Then arrow &gt; <b>Apply to Worksheets &gt; Selected Worksheets...</b> and tick all P1 sheets <b>except P1_Pathway</b> (the target and net-zero lines are company-wide).</div>')
        o.append('<div class="step">Arrow &gt; untick <b>Show Title</b>. Float each card to the X/Y/W/H above. Format: Lato 10, text navy, background white.</div>')
    elif pg["key"] == "page2":
        o.append('<div class="step">Add Region, Business Unit, Asset Type (dim_asset) and Source Category (dim_source) to <b>Filters</b> on <b>P2_TopAssets</b> (all values), then <b>Show Filter</b> for each.</div>')
        o.append('<div class="step">Parameter <code>p_TopN</code>: right-click &gt; <b>Show Parameter</b> on P2_TopAssets. On the dashboard set its control to <b>Slider</b> (arrow &gt; Slider), hide the title, show the value.</div>')
        o.append('<div class="step">For each filter card: arrow &gt; <b>Multiple Values (dropdown)</b>; <b>Apply to Worksheets &gt; Selected Worksheets</b>: all P2 sheets (KPIs, TopAssets, Map, Heatmap, Intensity, Methane). Hide titles and float to the X/Y/W/H above.</div>')
        o.append('<div class="step">The Top-N rank is calculated <i>after</i> the filters, so with Asset Type = Refinery the slider shows the top N refineries.</div>')
    else:
        o.append('<div class="step">On <b>P3_Tracker</b> add Status, Lever Group (dim_project), Region (dim_asset) and Risk Rating (dim_project) to Filters and choose <b>Show Filter</b> for each. Set Status default to Delayed, In Execution, Planned.</div>')
        o.append('<div class="step">Arrow &gt; <b>Multiple Values (dropdown)</b>; <b>Apply to Worksheets &gt; Selected Worksheets</b>: Lever, Region and Risk apply to P3_KPI1-4, P3_Tracker and P3_Capex; <b>Status applies ONLY to P3_Tracker and P3_Capex</b> (its default hides Delivered projects, which would zero out the Abatement delivered KPI and cut funded capex). Hide titles and float to the X/Y/W/H above.</div>')
        o.append('<div class="warn">P3_MACC (DS4) and P3_Scenarios (DS3) are separate data sources, so these filters do not change them. The scenario card says "company-wide, not filtered". To cross-filter the MACC, use the actions in Phase E (selecting a tracker row highlights its block).</div>')
    o.append('<div class="step">Test: change a filter and check the KPIs, charts and tables respond. Use Ctrl+Alt+Z (Revert) or the toolbar Reset to return to defaults.</div></div>')
    o.append('<h3>Phase E - Interactivity (Dashboard &gt; Actions &gt; Add Action)</h3><table><tr><th>Type</th><th>Run on</th><th>Source / target</th><th></th></tr>')
    for ty, run, tgt, tr in pg["actions"]: o.append(f'<tr><td>{ty}</td><td>{tr}</td><td>{run}: {tgt}</td><td></td></tr>')
    o.append('</table>')
    o.append('<h3>Phase F - Finish and check</h3><div class="steps">')
    o.append('<div class="step">Right-click the background image in the Item hierarchy &gt; <b>Lock</b> position (optional, prevents accidental moves).</div>')
    o.append('<div class="step">Press <b>F7</b> (presentation mode). Click each nav button, each filter and each chart once.</div>')
    o.append(f'<div class="step">Compare with the <a href="Dashboard_Previews/{pg["preview"]}" target="_blank">target preview</a>. Tick off the checks below.</div></div>')
    o.append('<ul class="chk">' + "".join(f'<li><label><input type="checkbox"> {c}</label></li>' for c in pg["checks"]) + '</ul>')
    o.append('</section>')
    return "".join(o)

CSS = """
:root{--navy:#0B2545;--navy2:#13315C;--teal:#13A89E;--amber:#F2A541;--red:#D64550;--bg:#EEF2F6}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 Lato,'Segoe UI',Arial,sans-serif;color:#1d2b3f;background:var(--bg)}
header{background:linear-gradient(90deg,var(--navy),var(--navy2));color:#fff;padding:26px 40px;border-bottom:4px solid var(--teal)}
header h1{margin:0;font-size:26px}header p{margin:6px 0 0;color:#9FD8D3}
.wrap{display:flex;max-width:1500px;margin:0 auto}nav{position:sticky;top:0;align-self:flex-start;width:230px;padding:20px;font-size:14px}
nav a{display:block;padding:7px 10px;color:var(--navy2);text-decoration:none;border-radius:6px}nav a:hover{background:#dbe6f1}
main{flex:1;padding:20px 30px 80px;min-width:0}section{background:#fff;border-radius:12px;padding:26px 30px;margin-bottom:22px;box-shadow:0 2px 8px rgba(11,37,69,.08)}
h2{margin:0 0 10px;color:var(--navy);font-size:22px;border-left:5px solid var(--teal);padding-left:12px}h3{color:var(--navy2);margin:24px 0 6px}h4{color:var(--navy2);margin:16px 0 4px}
code{background:#eef3f8;padding:1px 5px;border-radius:4px;font-size:13px}table{border-collapse:collapse;width:100%;margin:8px 0 14px;font-size:13.5px}
th{background:var(--navy);color:#fff;text-align:left;padding:6px 9px}td{border-bottom:1px solid #e3e9f0;padding:6px 9px;vertical-align:top}small{color:#7a8aa0}
.steps{counter-reset:s}.step{counter-increment:s;margin:9px 0;padding-left:38px;position:relative}.step:before{content:counter(s);position:absolute;left:0;top:0;width:26px;height:26px;border-radius:50%;background:var(--navy);color:#fff;text-align:center;line-height:26px;font-weight:700;font-size:13px}
.tip{background:#FFF7E8;border-left:4px solid var(--amber);padding:9px 14px;border-radius:6px;margin:10px 0}.warn{background:#FDECEE;border-left:4px solid var(--red);padding:9px 14px;border-radius:6px;margin:10px 0}
ul.chk{list-style:none;padding-left:4px}ul.chk li{margin:5px 0}@media(max-width:900px){nav{display:none}}
"""
common = '''<section id="start"><h2>Before you start</h2><div class="steps">
<div class="step">All 28 sheets are built and tested against section 10 of the main guide (<a href="START_HERE_Tableau_Build_Guide.html">START_HERE guide</a>): P1 (4 KPI sheets, 4 charts, P1_Messages), P2 (5 KPI sheets, 5 charts), P3 (4 KPI sheets, 4 charts, P3_Actions).</div>
<div class="step">On every sheet: Format &gt; Shading &gt; None for Worksheet and Pane, no borders, title hidden. This is what makes sheets sit on the white cards.</div>
<div class="step">Install the font <b>Lato</b> (and Poppins for the title if you edit backgrounds) so Tableau text matches the images.</div>
<div class="step">Create the 3 dashboards in order 1, 2, 3 so navigation buttons can point to existing dashboards.</div></div>
<h3>The same routine for every dashboard</h3>
<table><tr><th>Phase</th><th>What you do</th></tr><tr><td>A</td><td>Create a fixed 1600x900 dashboard and float the background image at 0,0.</td></tr>
<tr><td>B</td><td>Float every sheet at the exact X, Y, W, H in the table (card position plus padding).</td></tr>
<tr><td>C</td><td>Add three navigation buttons in the empty top-right of the header (the background has none baked in).</td></tr><tr><td>D</td><td>Add label text objects and slicers into the empty white filter strip.</td></tr>
<tr><td>E</td><td>Add interactivity (actions).</td></tr><tr><td>F</td><td>Test in presentation mode and compare with the preview.</td></tr></table>
<div class="warn"><b>Common mistakes:</b> (1) using a Tiled item (always Floating); (2) leaving "Show title" on; (3) using Entire View on the tracker; (4) the background image not at the bottom of the Item hierarchy; (5) dashboard size left on Automatic.</div>
<div class="tip"><b>Exact positions:</b> when you add a sheet as floating, Tableau shows Layout tab fields <b>Position: X, Y</b> and <b>Size: Width, Height</b> (pixels). Type the numbers, press Tab. The padding rule is: charts X+12 / Y+44 / W-24 / H-56; KPI cards X+16 / Y+34 / W-32 / H-44; text cards X+16 / Y+44 / W-32 / H-56 (card = background rectangle).</div></section>'''
html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Meridian - Dashboard assembly guide</title><style>{CSS}</style></head><body>"
        "<header><h1>Dashboard assembly guide - step by step</h1><p>How to build the 3 Meridian dashboards in Tableau from the finished sheets</p></header><div class='wrap'><nav>"
        "<a href='#start'>Before you start</a><a href='#d1'>Dashboard 1 - Executive</a><a href='#d2'>Dashboard 2 - Drivers</a><a href='#d3'>Dashboard 3 - Investment</a>"
        "<a href='START_HERE_Tableau_Build_Guide.html'>Back to main guide</a></nav><main>" + common + "".join(section(p) for p in PAGES) + "</main></div></body></html>")
open(os.path.join(ROOT, "Dashboard_Assembly_Guide.html"), "w", encoding="utf-8").write(html); print("ok", len(html))
