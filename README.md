# Factory-to-Customer Shipping Route Efficiency Analysis — Nassau Candy Distributor

## Overview
This project analyzes factory-to-customer shipment efficiency for Nassau Candy Distributor. It converts order and shipment records into route-level intelligence across factories, states, regions, and ship modes.

## Dataset
- Records: 10,194
- Unique orders: 8,549
- States: 59
- Regions: 4
- Ship modes: 4
- Products: 15
- Factories mapped from the supplied product-factory correlation: 5

## Key findings
- Mean calculated Order-to-Ship lead time: **1320.8 days**
- Median: **1274 days**
- Minimum / maximum: **904 / 1642 days**
- Highest-volume region: **Pacific (3,253 records)**
- Highest-volume ship mode: **Standard Class (6,120 records)**

## Important data-quality note
The supplied Order Date and Ship Date produce lead times from 904 to 1642 days. These values are unusually large for normal parcel shipping. The project does **not** silently alter or invent dates. Results should therefore be interpreted as analytics on the supplied date fields, and the date issue should be resolved with the source system before operational SLA decisions are made.

## Methodology
1. Validate and parse dates.
2. Calculate `ShippingLeadTime = Ship Date - Order Date`.
3. Remove only invalid negative lead times (none were found).
4. Map each product to its supplied factory.
5. Define routes as Factory → Customer State and Factory → Customer Region.
6. Calculate shipment volume, mean/median lead time, and variability.
7. Benchmark routes and identify high-volume/high-lead-time bottlenecks.
8. Compare ship modes and regions.
9. Provide drill-down and configurable delay-threshold analysis in Streamlit.

## KPIs
- Shipping Lead Time
- Average Lead Time
- Route Volume
- Delay Frequency (user-defined threshold)
- Route Efficiency Score

## Streamlit
Run:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Interpretation
Route efficiency scores are relative to the currently filtered dataset. Delay frequency is threshold-dependent. This is descriptive operational analytics, not a prediction of future shipping performance.

## Files
- `streamlit_app.py` — interactive dashboard
- `Nassau_Candy_Route_Cleaned.csv` — processed dataset
- `factory_state_routes.csv` — factory/state route metrics
- `route_performance.csv` — factory/region/state/ship-mode metrics
- `ship_mode_metrics.csv` — ship-mode summary
- `region_metrics.csv` — regional summary
- `Nassau_Candy_Research_Paper.docx` — research paper
- `Nassau_Candy_Executive_Summary.docx` — executive summary
- `Project_Feedback_Video_Script.txt` — feedback video script
