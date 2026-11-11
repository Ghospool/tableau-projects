# Meridian Energy: Net-Zero Pathway (Tableau)

**Question answered:** Is Meridian Energy Group on track for its 2030 target of -45% Scope 1+2 emissions versus 2024, and what would close the gap?

**Live dashboard:** [Tableau Public](https://public.tableau.com/app/profile/gospel.ayodele.iyioku/viz/Meridian_NetZero_Tableau/ExecutiveOverview)

## Dashboards
1. **Executive Overview** - YTD emissions, change vs 2024 baseline, gap to pathway, carbon cost.
2. **Drivers & Hotspots** - top assets, regional footprint, intensity trend, source heatmap, methane and flaring.
3. **Pathway & Investment** - marginal abatement cost curve, scenarios to 2030, delivery tracker, capex plan vs actual.

## Key findings (data as of 30 Sep 2027)
- 2027 YTD emissions are 19.3 Mt, -14.0% vs 2024 YTD, against -21.7% required: a gap of about 1.7 Mt.
- The delayed Poland coal exit (1.85 Mt/yr) is larger than the whole gap.
- The committed plan reaches about -32% by 2030, short of the -45% target; accelerating all options reaches about -38%.

## Data
Fully **synthetic** (seeded generator, seed 2027). Star schema of 11 CSVs in `data/` (about 30,000 rows): emissions, operations, project spend, target pathway, scenarios, carbon price, and asset, source, project and date dimensions. `macc_polygon.csv` draws the abatement cost curve.

Regenerate with `python scripts/generate_data.py`.

## Method
Relationships (not joins) across four data sources; calculated fields, parameters (`p_AsOf`, `p_BaselineYear`, `p_TopN`), table calculations and LODs; polygon-based MACC; fixed 1600x900 dashboards with custom backgrounds and navigation.

## Limitations
- Simulated data; no real company, asset or price is represented.
- Scope 1 and 2 only; no Scope 3.
- Scenario and abatement costs are illustrative assumptions.

## Contents
| Path | What it is |
|---|---|
| `Meridian_NetZero_Tableau.twbx` | Packaged Tableau workbook |
| `data/` | CSV star schema |
| `scripts/` | Python generators for data, assets and guides |
| `assets/` | Dashboard backgrounds, logo, navigation images
