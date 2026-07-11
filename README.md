# Brand Retention and Consumer Purchase Behavior

A personal project focused on a straightforward consumer question: which brands retain customers, and which brands tend to share the same buyers?

The analysis transforms noisy receipt descriptions into brand-level purchase histories, then measures category trends, repeat purchasing, and cross-brand customer overlap.

## Analytical workflow

1. Collect a public reference list of brands.
2. Normalize receipt descriptions and resolve brand-name variants.
3. Fill and consolidate product categories.
4. Measure item and category purchasing trends.
5. Compare customer retention across brands.
6. Calculate directional brand-to-brand customer overlap.
7. Audit unmatched records and potential selection bias.

## Repository structure

```text
src/
  scrape_brands.py       public brand-reference collection
  brand_matching.py      receipt normalization and enrichment
analysis/
  category_trends.py     item and category momentum
  retention.py           repeat-purchase behavior
  brand_overlap.py       shared-customer analysis
notebooks/
  purchase_analytics.ipynb
```

## Data policy

The original receipt-level source data is not published. The repository presents the analytical methodology and separated code structure without redistributing consumer records.

## Tools

Python · pandas · NumPy · Selenium · scikit-learn · Matplotlib · Seaborn
