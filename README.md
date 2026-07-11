# Consumer Purchase Analytics

An end-to-end workflow for enriching receipt-level purchase data, matching product descriptions to brands, measuring category trends and retention, and analyzing cross-brand customer overlap.

## Workflow

1. Collect a reference list of brands.
2. Normalize noisy product descriptions and match them to brand variants.
3. Fill and consolidate product categories.
4. Estimate category and item trends.
5. Measure retention and cross-brand overlap.
6. Identify data-quality and selection-bias risks.

## Repository structure

- `notebooks/purchase_analytics.ipynb` — cleaning, enrichment, trend, retention, and overlap analysis
- `data/` — intentionally empty; proprietary receipt data is not published

## Tools

Python, pandas, NumPy, Selenium, scikit-learn, Matplotlib, Seaborn, and Jupyter.

## Data policy

The original receipt dataset is excluded because it is large and may be proprietary. The notebook is published to demonstrate methodology; users should supply data they are authorized to analyze.
