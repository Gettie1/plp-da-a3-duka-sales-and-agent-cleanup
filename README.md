# Duka Sales Analysis and Mobile Money Agent Data Cleanup

## Project Overview

This project contains two data analytics engagements completed using Python and Pandas.

1. **Duka Electronics Sales Analysis:** Explores sales performance, revenue trends, product performance and branch-level results. It also produces an Excel branch summary and a filtered CSV of premium online orders from Nairobi and Mombasa.
2. **Mobile Money Agent Data Cleanup:** Investigates and cleans agent transaction records, addresses data quality issues, merges transactions with the agent register and generates quality reports and summary tables.

## Technologies Used

- Python
- Pandas
- NumPy
- Jupyter Notebook
- Excel
- OpenPyXL

## Repository Structure

```text
plp-da-a3-duka-sales-and-agent-cleanup/
│
├── generate_data.py
├── requirements.txt
├── README.md
├── duka_sales_exploration.ipynb
├── agent_cleanup.ipynb
├── cleaning_pipeline.py
│
├── excel/
│   └── duka_branch_summary.xlsx
│
└── outputs/
    ├── premium_online_coast_capital.csv
    └── agent_transactions_clean.csv
```

## Setup and Installation

Clone the repository:

```bash
git clone https://github.com/Gettie1/plp-da-a3-duka-sales-and-agent-cleanup.git
```

Navigate into the project folder:

```bash
cd plp-da-a3-duka-sales-and-agent-cleanup
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Regenerating the Data

Run the data generation script:

```bash
python generate_data.py
```

This generates the raw datasets required for both engagements:

- `duka_sales.csv`
- `agents.csv`
- `agent_transactions.csv`

The raw generated CSV files are not included in the repository and can be regenerated using the script.

## Running the Notebooks

Open Jupyter Notebook:

```bash
jupyter notebook
```

Run the notebooks in the following order:

1. `duka_sales_exploration.ipynb` — explores Duka Electronics sales data, calculates revenue metrics and generates the premium online orders export.
2. `agent_cleanup.ipynb` — profiles and cleans agent transactions, validates the results and generates the cleaned transaction export.

Run each notebook from top to bottom after regenerating the data.

## Engagement 1: Duka Electronics Sales Analysis

### Executive Summary

The analysis covered 1,000 sales orders with a total revenue of **KES 71,792,500**. Nairobi generated the highest branch revenue at **KES 26,106,100** from 376 orders. Mombasa followed with **KES 14,003,700** from 186 orders. Nakuru generated **KES 11,970,400** from 162 orders, while Kisumu generated **KES 10,868,100** from 159 orders. Eldoret recorded **KES 8,844,200** from 117 orders.

### Deliverables

- Sales exploration notebook.
- Derived sales metrics and business analysis.
- Excel branch summary workbook containing branch revenue calculations, region lookup and PivotTable analysis.
- Filtered premium online orders from Nairobi and Mombasa saved in `outputs/premium_online_coast_capital.csv`.

## Engagement 2: Mobile Money Agent Data Cleanup

### Overview

The original transaction dataset contained **612 records** and the agent register contained **20 agents**. Data profiling identified missing amounts, duplicate transaction IDs, inconsistent transaction types, inconsistent date formats, suspicious transaction values and unknown agent references.

A reusable cleaning function, `clean_agent_data(txns, agents)`, was implemented in `cleaning_pipeline.py`.

### Cleaning Results

| Metric | Result |
|---|---:|
| Original transaction records | 612 |
| Cleaned transaction records | 600 |
| Duplicate transaction IDs after cleaning | 0 |
| Missing amounts imputed | 20 |
| IQR outliers flagged | 53 |
| Unknown agent transactions retained | 7 |

### Cleaning Operations

- Removed exact duplicate records.
- Resolved duplicate transaction IDs.
- Standardized transaction types to Deposit and Withdrawal.
- Converted transaction amounts to numeric values.
- Imputed missing amounts using the median.
- Detected and flagged outliers using the IQR method.
- Standardized transaction dates to ISO format.
- Identified unknown agent references.
- Merged transaction records with agent county information.

### Deliverables

- `cleaning_pipeline.py` — reusable data-cleaning function and cleaning log.
- `agent_cleanup.ipynb` — data profiling, audit table, validation, county summaries, weekly pivot and Data Quality Report.
- `outputs/agent_transactions_clean.csv` — cleaned transaction dataset.

## Data Quality and Privacy

The agent data assessment covers six dimensions:

1. Completeness
2. Uniqueness
3. Consistency
4. Validity
5. Accuracy
6. Referential Integrity

Potentially suspicious transactions are retained and flagged for investigation rather than automatically deleted. The project also considers appropriate safeguards for personal data under Kenya's Data Protection Act, 2019.

## Author

**Getrude Cheptoo**

Software Engineering Student | Data Analytics Learner

GitHub: [@Gettie1](https://github.com/Gettie1)