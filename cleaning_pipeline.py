
import pandas as pd
import numpy as np


def clean_agent_data(txns, agents):
    """
    Clean agent transaction data, validate records,
    merge agent information, and generate a cleaning log.

    Parameters:
        txns: Raw agent transactions DataFrame.
        agents: Agent register DataFrame.

    Returns:
        clean_df: Cleaned and merged transaction DataFrame.
        log: DataFrame documenting cleaning actions.
    """

    clean_df = txns.copy()
    log = []

    def record_action(action, rows_affected, details):
        log.append({
            "action": action,
            "rows_affected": int(rows_affected),
            "details": details
        })

    # 1. Remove exact duplicate records
    before = len(clean_df)
    clean_df = clean_df.drop_duplicates().copy()
    record_action(
        "Remove exact duplicates",
        before - len(clean_df),
        "Removed identical transaction records."
    )

    # 2. Resolve duplicate transaction IDs
    duplicate_ids = clean_df["txn_id"].duplicated(keep=False)
    duplicate_count = int(
    clean_df["txn_id"].duplicated().sum()
)

    # Keep the record linked to a registered agent
    valid_agent_ids = set(agents["agent_id"])
    clean_df["_valid_agent"] = clean_df["agent_id"].isin(valid_agent_ids)

    clean_df = (
        clean_df.sort_values("_valid_agent", ascending=False)
        .drop_duplicates(subset="txn_id", keep="first")
        .drop(columns="_valid_agent")
        .copy()
    )

    record_action(
        "Resolve duplicate transaction IDs",
        duplicate_count,
        "Retained one record per transaction ID, preferring a registered agent."
    )

    # 3. Standardize transaction types
    clean_df["txn_type"] = (
        clean_df["txn_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    clean_df["txn_type"] = clean_df["txn_type"].map({
        "deposit": "Deposit",
        "withdrawal": "Withdrawal"
    })

    record_action(
        "Standardize transaction types",
        int(clean_df["txn_type"].isna().sum()),
        "Standardized valid values to Deposit and Withdrawal."
    )

    # 4. Convert amounts to numeric
    original_amounts = clean_df["amount"].copy()

    clean_df["amount"] = pd.to_numeric(
        clean_df["amount"],
        errors="coerce"
    )

    missing_amounts = clean_df["amount"].isna()

    record_action(
        "Identify missing or invalid amounts",
        missing_amounts.sum(),
        "Converted invalid strings and missing values to NaN."
    )

    # 5. Impute missing amounts using the median
    median_amount = clean_df["amount"].median()

    clean_df["amount_imputed"] = missing_amounts

    clean_df["amount"] = clean_df["amount"].fillna(
        median_amount
    )

    record_action(
        "Impute missing amounts",
        missing_amounts.sum(),
        f"Replaced missing amounts with median: {median_amount:.2f}."
    )

    # 6. Detect outliers using the IQR method
    q1 = clean_df["amount"].quantile(0.25)
    q3 = clean_df["amount"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    clean_df["is_outlier"] = (
        (clean_df["amount"] < lower_bound) |
        (clean_df["amount"] > upper_bound)
    )

    record_action(
        "Flag outliers",
        clean_df["is_outlier"].sum(),
        f"IQR bounds: {lower_bound:.2f} to {upper_bound:.2f}."
    )

    # 7. Standardize transaction dates
    clean_df["txn_date"] = pd.to_datetime(
        clean_df["txn_date"],
        format="mixed",
        errors="coerce"
    )

    record_action(
        "Validate transaction dates",
        clean_df["txn_date"].isna().sum(),
        "Converted transaction dates to datetime."
    )

    # 8. Identify unknown agents
    clean_df["unknown_agent"] = (
        ~clean_df["agent_id"].isin(valid_agent_ids)
    )

    record_action(
        "Identify unknown agents",
        clean_df["unknown_agent"].sum(),
        "Flagged transactions referencing unregistered agents."
    )

    # 9. Merge with the agent register
    clean_df = clean_df.merge(
        agents[["agent_id", "county"]],
        on="agent_id",
        how="left",
        validate="many_to_one"
    )

    record_action(
        "Merge agent register",
        clean_df["county"].isna().sum(),
        "Left join used to retain transactions with unknown agents."
    )

    # 10. Prepare ISO-formatted dates
    clean_df["txn_date"] = (
        clean_df["txn_date"].dt.strftime("%Y-%m-%d")
    )

    log = pd.DataFrame(log)

    return clean_df, log
