"""Generates Client_Ready_Checklist.html"""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# (id, dashboard, title, problem, steps[], done_when)
P0 = [
 ("A1", "Dashboard 3 - P3_Scenarios", "Target label shows 71.27 instead of 17.6",
  "The red end label reads 71.27. The target is being summed over several scenario rows, so the label (and possibly the line) is multiplied.",
  ["Edit the calculated field <code>Target Mt</code> (right-click &gt; Edit) to <code>AVG([Target Tco2e]) / 1000000</code>. The target is the same on every row for a year, so AVG returns the true value however many rows are joined.",
   "Edit <code>Target Label</code> the same way: replace <code>[Target Mt]</code> by the new definition (it already refers to the field, so no change needed if you kept the name).",
   "On the sheet, right-click the right-hand axis &gt; <b>Synchronize Axis</b>, then untick <b>Show Header</b>.",
   "On the <b>AGG(Target Mt)</b> Marks tab, set Label &gt; Show mark labels &gt; Marks to label: <b>Line Ends</b>, text <code>&lt;AGG(Target Label)&gt;</code>."],
  "The red label reads <b>Target 17.6 (-42% avg)</b> and the line ends at the same height as the label."),
 ("A2", "Dashboard 2 - P2_Intensity", "Coal intensity falls to 64 (misleading)",
  "Retired coal plants still report their old activity in the simulated data, so tCO2e per MWh looks like a 36% efficiency gain. A client will read it as real.",
  ["<b>Option 1 (no data change, 2 minutes):</b> on P2_Intensity, right-click the <code>Asset Type</code> filter &gt; Edit &gt; untick <b>Coal Power Plant</b>, keep Gas CCGT, Refinery and Offshore Platform.",
   "Add a footnote under the chart (Dashboard text object, 9 pt grey): <code>Coal excluded: retired plants distort the intensity ratio.</code>",
   "<b>Option 2 (clean fix):</b> ask me to patch <code>scripts/generate_data.py</code> so activity falls to zero when a plant retires, rerun it, then in Tableau go to Data &gt; Refresh (or Edit Data Source &gt; refresh the extract). Coal then stays near 100 until retirement and drops with output."],
  "No line falls below about 85, or coal is visibly excluded with a footnote."),
 ("A3", "Dashboard 3 - P3_Tracker", "Tracker columns are cut off",
  "Only Status, Project, Lever and Region are visible. The dot, go-live dates, abatement, capex and delay columns are off to the right.",
  ["Remove <code>Lever</code> from Rows (drag it off). The lever is already part of the project name.",
   "Create <code>Project Short</code> = <code>LEFT([Project Name], 34)</code> and use it on Rows in place of <code>Project Name</code>.",
   "Format &gt; Font &gt; Worksheet: Lato 9 pt. Format &gt; Alignment: left for dimensions, right for numbers.",
   "Set <b>Fit: Entire Width</b> (toolbar). Drag header borders so widths are about: Status 60, Dot 26, Project 240, Region 105, Orig. 55, Current 55, kt/yr 55, Capex 50, Delay 40 (total under 740 px).",
   "Rename headers by double-clicking: Orig. go-live, Current go-live, Abatement (kt/yr), Capex ($M), Delay (months).",
   "On the dashboard, item &gt; Fit &gt; <b>Entire View</b> is NOT used for the tracker; keep it at the size from the guide and check no horizontal scrollbar appears."],
  "All columns, including the coloured dots and the Delay column, are visible without a horizontal scrollbar."),
 ("A4", "All dashboards - filter bar", "Year filter (and other extras) in the filter bar",
  "The KPIs use fixed YTD logic, so a Year filter can contradict them. Page 2 also has Asset Group, Asset Name; page 3 has Project Name. These make long dropdowns and duplicate each other.",
  ["On the dashboard, click each unwanted filter card &gt; click the small dropdown arrow &gt; <b>Remove from Dashboard</b> (Year on all three pages, Asset Group and Asset Name on page 2, Project Name on page 3).",
   "On the source sheet, drag the matching pill off the Filters shelf if you also want it gone from the sheet.",
   "Keep exactly these: Page 1 Region, Business Unit, Asset Type, Reporting month. Page 2 Region, Business Unit, Asset Type, Source, Top N. Page 3 Status, Lever, Region, Risk.",
   "Add Reporting month: edit parameter <code>p_AsOf</code> &gt; Allowable values <b>List</b> 1 Jan 2027 ... 1 Sep 2027, display format <code>mmm yyyy</code>; Show Parameter; float into the slot (positions in the assembly guide, Phase D)."],
  "Every page shows only the designed slicers and the KPIs respond correctly to Reporting month."),
 ("A5", "Dashboard 3 - P3_MACC", "Stray \"0.0\" labels and duplicate carbon-price label",
  "The reference lines are drawn on both panes of the dual axis, so labels show twice and zeros appear at the ends.",
  ["Right-click the <b>0 line</b> &gt; Edit &gt; Label: <b>None</b>.",
   "Right-click the <b>right-hand axis</b> pane's reference line (the second copy) &gt; <b>Remove</b>. Keep the one on the left axis.",
   "On the remaining 100 line: Edit &gt; Label: <b>Custom</b> = <code>Carbon price 2030 (High case)</code>, Position: left; tick Line only (no value).",
   "Y axis: Edit Axis &gt; Fixed -60 to 110 so the unused 120 tick disappears."],
  "One dashed line at $100 with one label; no 0.0 anywhere."),
]
P1 = [
 ("B1", "Page 2 and 3 filter bars", "Filter cards look inconsistent",
  "Different widths, default Tableau fonts and title styles.",
  ["For each filter card: dropdown arrow &gt; <b>Format Filter</b>: font Lato 10, text navy #0B2545, background white, border #CFD9E4.",
   "Arrow &gt; untick <b>Show title</b>, then place a Text label next to it (guide Phase D gives X/Y/W/H and text for each label).",
   "Set each control to the width from the guide (126 px) via Layout &gt; Width, and Y 94, Height 24."],
  "All controls are the same height, font and spacing, and each has a clear label."),
 ("B2", "Dashboard 2 - P2_TopAssets", "CCGT and Refinery colours are swapped",
  "Design standard is Coal navy, Gas CCGT teal, Refinery amber, Others grey. Your chart has Refinery teal and CCGT orange.",
  ["Click the <b>Asset Group</b> colour legend &gt; Edit Colors.",
   "Select each member and set: Coal Power Plant <code>#0B2545</code>, Gas CCGT Plant <code>#13A89E</code>, Refinery <code>#F2A541</code>, Others <code>#8D99AE</code>. OK."],
  "Colours match the legend used on page 1 messages and the guide."),
 ("B3", "Dashboards 1 and 2 - colour palette", "Default bright colours in Source Mix, Methane and Map",
  "Source Mix uses bright green/yellow/red; Methane uses yellow; the map legend is truncated.",
  ["P1_SourceMix: Color legend &gt; Edit Colors: Combustion <code>#0B2545</code>, Flaring <code>#F2A541</code>, Methane &amp; Fugitive <code>#D64550</code>, Process <code>#8D99AE</code>, Mobile <code>#13A89E</code>, Electricity (Scope 2) <code>#7AC74F</code>.",
   "P2_Methane: Fugitive Methane <code>#D64550</code>, Flaring <code>#F2A541</code> (same as above, so colours mean the same thing on every page).",
   "P2_Map: Business Unit colours: Power Generation <code>#0B2545</code>, Upstream <code>#13A89E</code>, Midstream &amp; Refining <code>#F2A541</code>, Networks <code>#8D99AE</code>, Renewables <code>#7AC74F</code>.",
   "P2_Heatmap: Color &gt; Edit Colors &gt; Custom sequential: light <code>#EEF2F6</code> to dark <code>#0B2545</code>; untick Stepped Color."],
  "Each concept has one colour across all three pages."),
 ("B4", "Dashboard 1 and 2 - numbers", "Mixed decimals (+1.73 vs 1.7; -4.8%, -19.0%)",
  "KPI and chart labels use different precision from the messages.",
  ["Create <code>Gap Mt</code> = <code>[Gap to Pathway] / 1000000</code>. On P1_KPI3 use it on Text with Number (Custom): 1 decimal, prefix <b>+</b>. It then reads +1.7.",
   "P1_Region: right-click the <code>Change vs Baseline %</code> pill on Label &gt; Format &gt; Numbers &gt; Percentage, <b>0 decimals</b>.",
   "P2_Intensity labels: Format &gt; Numbers &gt; Number, <b>0 decimals</b> (96, 94, 86).",
   "Rule of thumb for the whole workbook: Mt = 1 decimal, % = 0 decimals, $M = 0 decimals, kt = 0 decimals."],
  "No label shows more precision than the rule above."),
 ("B5", "Dashboard 1 P1_Pathway and Dashboard 2 P2_Intensity", "End labels show only values",
  "Labels read \"2.1 (Actual emissions)\" or just 95.85. They should read name first, value second.",
  ["P1_Pathway: legend &gt; right-click each entry &gt; <b>Edit Alias</b>: Actual emissions / 2030 target pathway (-45%) / Net-zero 2050 line.",
   "Marks (All) &gt; Label &gt; Show mark labels &gt; <b>Line Ends</b> &gt; Text: <code>&lt;Measure Names&gt;  &lt;SUM(Measure Values)&gt;</code> (drag Measure Names to Label first if it is not there). Number format 0.0.",
   "P2_Intensity: drag <code>Asset Type</code> to Label &gt; Line Ends &gt; Text: <code>&lt;Asset Type&gt; &lt;AGG(Intensity Index)&gt;</code>, format 0 decimals. Hide the legend.",
   "Untick <b>Allow labels to overlap other marks</b>."],
  "Each line ends with its own name and value."),
 ("B6", "Dashboard 2 - map, heatmap, methane", "Truncated legends and headers",
  "Map legend: \"Midstream &amp; R…\", \"Upst…\" with arrows; intensity legend cut; heatmap \"Statio..\".",
  ["Legends: dropdown arrow on the legend &gt; <b>Floating</b>; set width to the card width minus 32 and Layout &gt; Arrange: horizontal; or delete the legend and label directly.",
   "Heatmap headers: right-click the <code>Source Name</code> header &gt; Edit Alias: Stationary, Mobile, Flaring, Methane, SF6/other, Process, Scope 2.",
   "Heatmap: Format &gt; Font 9 pt; hide the field label for rows (right-click &gt; Hide Field Labels for Rows) so the stray sort icon disappears.",
   "Methane chart: shorten legend aliases to Methane and Flaring."],
  "No legend or header ends with an ellipsis."),
 ("B7", "Dashboard 1 - source mix axis", "Raw axis title \"% of Total Emissions Tco2E\"",
  "Default measure name leaks into the chart.",
  ["Double-click the axis title and replace it with <code>Share of emissions</code> (size 10, grey). Hide it entirely if the card subtitle already says it."],
  "Titles read like words, not field names."),
 ("B8", "Dashboard 3 - P3_Capex", "Legend overlaps title and end labels collide",
  "The legend sits on the card title; $1,935M and $1,853M overlap; the \"$190M above plan\" message is missing.",
  ["Remove the legend from the sheet and label the lines directly: Marks &gt; Label &gt; Line Ends with <code>&lt;Measure Names&gt;</code> aliased to Actual / Plan.",
   "Right-click the Actual end point &gt; Annotate &gt; Mark: <code>Actual $1,935M</code> (position left, red text); do the same for Plan with <code>Plan $1,747M</code> positioned below.",
   "Add a text annotation (right-click empty area in the plot &gt; Annotate &gt; Area): <code>Actual spend is about $190M above plan</code>, red bold 11 pt. Or insert <code>&lt;AGG(Capex Message)&gt;</code>."],
  "Two readable end labels and one red callout, no overlap with the card title."),
]
P2 = [
 ("C1", "Whole workbook", "One font",
  "Charts use Tableau Book, cards use Lato.",
  ["Format &gt; Font (menu). Set Worksheet, Title, Tooltip, Header and Pane to <b>Lato</b>. Apply to the workbook, not a single sheet.",
   "Dashboard text objects: select all (Ctrl+A in the item hierarchy) and set Lato."],
  "Zooming in on any text shows the same typeface."),
 ("C2", "All dashboards", "Footer, source and definitions",
  "No source, date or definitions. A client will ask what YTD, pathway or MACC mean.",
  ["Add a floating Text object at X 24, Y 884, W 1200, H 14 (Lato 9, grey): <code>Source: Meridian simulated data | Scope 1 and 2 | Actuals to Sep 2027 | Pathway = -45% by 2030 vs 2024 baseline | YTD = Jan to Sep</code>.",
   "Add KPI tooltips: on each KPI sheet click Tooltip on the Marks card and write a one-line definition and formula.",
   "Optionally add a hidden 4th dashboard (\"Notes and definitions\") linked from a small \"i\" icon (assets/icons/png/info_grey.png) at the top right of the header."],
  "Footer visible on every page; hovering a KPI explains it."),
 ("C3", "Dashboard 1 and 3 - text cards", "Hard-coded numbers in Key Messages and Recommended Actions",
  "If a filter changes the charts, the text still says 1.7 Mt etc.",
  ["Quick fix: add \"(company-wide, 2027 YTD)\" in the card subtitle or the first line, and note the text is not filtered.",
   "Better: make the first line dynamic. Create <code>Msg 1</code> = <code>\"We are \" + STR(ROUND([Gap to Pathway]/1000000,1)) + \" Mt above the pathway: \" + STR(ROUND([Change vs Baseline %]*100,0)) + \"% vs \" + STR(ROUND([Target Red % YTD]*100,0)) + \"% required.\"</code> and use it on Text in P1_Messages (aggregate field, no Detail pill).",
   "Keep the unchanging facts (Poland coal exit 1.85 Mt/yr, plan -32% by 2030) as typed text, with the source."],
  "Changing Reporting month does not leave a stale number in the first line."),
 ("C4", "All dashboards", "Readability and accessibility",
  "Grey subtitles are light; status uses red/green only.",
  ["Darken grey text from #8D99AE to <code>#5B6B82</code> for subtitles and axis labels; minimum font 9 pt.",
   "Keep the status text next to every red/green dot (the tracker already has it); do not rely on colour alone.",
   "Dashboard &gt; Item &gt; Alt text on the background image and each chart (one sentence each)."],
  "Passes a squint test and prints legibly in grey scale."),
 ("C5", "All dashboards", "Interaction test matrix",
  "Filters and actions interact in ways that are easy to miss.",
  ["For each page run: (a) Region = each single region, (b) Reporting month = Jan and Sep, (c) click each bar/cell then click empty space to clear.",
   "Page 1: KPIs and BU gap respond to Region; Pathway does not. Page 2: Top N changes bars from 5 to 30; heatmap click filters the asset list. Page 3: Status filter changes tracker and capex only; KPIs stay at $1,853 / 5.3 / 3.0 / $11.",
   "Press Ctrl+Alt+Z / toolbar Reset to confirm defaults return."],
  "No blank charts, no errors, KPI values match section 10 of the main guide at defaults."),
 ("C6", "Workbook", "Publish and package",
  "Final hygiene before sending.",
  ["Data source &gt; <b>Extract</b> for DS1-DS4; save a packaged workbook (<code>.twbx</code>).",
   "Hide unused sheets: right-click each sheet tab &gt; Hide (or Dashboard &gt; <b>Show Sheet Tabs</b> off on publish).",
   "Delete obsolete sheets and unused calculations (Gantt Width, MACC Cum Start, duplicate _1/_2 sheets).",
   "Dashboard 1 = default view. Export each dashboard to PDF (File &gt; Print to PDF, landscape, Fit to 1 page wide) and check clipping.",
   "Open it at 1920 x 1080 and at a laptop size; the fixed size dashboard should be centred with no scrollbars (set Dashboard background to #EEF2F6 so margins match)."],
  "Package opens cleanly on another machine."),
]

def block(prefix, items, title, colour):
    o = [f'<section><h2 style="border-color:{colour}">{title}</h2>']
    for id_, where, ttl, prob, steps, done in items:
        o.append(f'<div class="item"><label class="hd"><input type="checkbox"> <span class="id" style="background:{colour}">{id_}</span> <b>{ttl}</b></label>'
                 f'<div class="where">{where}</div><p><b>Problem:</b> {prob}</p><div class="steps">' + "".join(f'<div class="step">{s}</div>' for s in steps) + f'</div><div class="done"><b>Done when:</b> {done}</div></div>')
    o.append("</section>"); return "".join(o)

CSS = """
:root{--navy:#0B2545;--navy2:#13315C;--teal:#13A89E;--amber:#F2A541;--red:#D64550;--bg:#EEF2F6}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 Lato,'Segoe UI',Arial,sans-serif;color:#1d2b3f;background:var(--bg)}
header{background:linear-gradient(90deg,var(--navy),var(--navy2));color:#fff;padding:26px 40px;border-bottom:4px solid var(--teal)}header h1{margin:0;font-size:26px}header p{margin:6px 0 0;color:#9FD8D3}
main{max-width:1100px;margin:0 auto;padding:20px 24px 80px}section{background:#fff;border-radius:12px;padding:22px 28px;margin-bottom:22px;box-shadow:0 2px 8px rgba(11,37,69,.08)}
h2{margin:0 0 12px;color:var(--navy);font-size:21px;border-left:5px solid var(--teal);padding-left:12px}
.item{border:1px solid #e1e8f0;border-radius:10px;padding:12px 16px;margin:12px 0;background:#fcfdfe}.hd{display:flex;gap:10px;align-items:center;font-size:16px;cursor:pointer}.hd input{width:18px;height:18px}
.id{color:#fff;border-radius:6px;padding:0 8px;font-size:13px;font-weight:700}.where{color:#7a8aa0;font-size:13px;margin:2px 0 6px 28px}p{margin:6px 0 6px 28px}
.steps{counter-reset:s;margin-left:28px}.step{counter-increment:s;margin:6px 0;padding-left:32px;position:relative}.step:before{content:counter(s);position:absolute;left:0;top:1px;width:22px;height:22px;border-radius:50%;background:var(--navy);color:#fff;text-align:center;line-height:22px;font-size:12px;font-weight:700}
.done{margin:8px 0 0 28px;background:#EAF7F6;border-left:4px solid var(--teal);padding:6px 12px;border-radius:6px}code{background:#eef3f8;padding:1px 5px;border-radius:4px;font-size:13px}
.sum{display:flex;gap:12px;flex-wrap:wrap}.sum div{background:var(--navy);color:#fff;border-radius:10px;padding:10px 16px}.sum b{display:block;font-size:22px;color:var(--amber)}
.item:has(input:checked){opacity:.55;background:#f1f8f1}
"""
html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Client-ready checklist</title><style>" + CSS + "</style></head><body>"
        "<header><h1>Client-ready checklist - Meridian net-zero dashboards</h1><p>Tick each item as you fix it. Order: A = must fix, B = consistency, C = finish and governance.</p></header><main>"
        f"<section><div class='sum'><div>{len(P0)}<b>A. Must fix</b></div><div>{len(P1)}<b>B. Consistency</b></div><div>{len(P2)}<b>C. Governance</b></div></div>"
        "<p>Work in the order A, B, C. After each A item, re-check the KPIs against the QA table (section 10 of the main guide): 19.3 / -14.0% / +1.7 / $1,220 on page 1; 22.4% / 2,230 / 4 of 6 / 45.7% / 5.0% on page 2; $1,853 / 5.3 / 3.0 / $11 on page 3.</p></section>"
        + block("A", P0, "A. Must fix before a client sees it", "#D64550") + block("B", P1, "B. Consistency and polish", "#F2A541") + block("C", P2, "C. Finish, governance and publishing", "#13A89E")
        + "</main></body></html>")
open(os.path.join(ROOT, "Client_Ready_Checklist.html"), "w", encoding="utf-8").write(html); print("ok", len(P0), len(P1), len(P2))
