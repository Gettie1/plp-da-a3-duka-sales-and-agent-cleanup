
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
    agents_df = agents.copy()
    log = []

    # Validate required columns
    required_txn_columns = [
        "txn_id", "agent_id", "txn_type", "amount", "txn_date"
    ]
    required_agent_columns = ["agent_id", "county"]

    missing_txn = [
        col for col in required_txn_columns
        if col not in clean_df.columns
    ]
    missing_agents = [
        col for col in required_agent_columns
        if col not in agents_df.columns
    ]

    if missing_txn or missing_agents:
        raise ValueError(
            f"Missing transaction columns: {missing_txn}; "
            f"Missing agent columns: {missing_agents}"
        )

    if agents_df["agent_id"].duplicated().any():
        raise ValueError("Agent register contains duplicate agent IDs.")

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
    before = len(clean_df)

    valid_agent_ids = set(agents_df["agent_id"])

    clean_df["_valid_agent"] = (
        clean_df["agent_id"].isin(valid_agent_ids)
    )

    clean_df = (
        clean_df
        .sort_values("_valid_agent", ascending=False, kind="stable")
        .drop_duplicates(subset="txn_id", keep="first")
        .drop(columns="_valid_agent")
        .copy()
    )

    record_action(
        "Resolve duplicate transaction IDs",
        before - len(clean_df),
        "Retained one record per transaction ID, preferring a registered agent."
    )

    # 3. Standardize transaction types
    original_types = clean_df["txn_type"].copy()

    standardized_types = (
        clean_df["txn_type"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map({
            "deposit": "Deposit",
            "withdrawal": "Withdrawal"
        })
    )

    changed_types = (
        original_types.astype("string") != standardized_types
    ).fillna(False)

    clean_df["txn_type"] = standardized_types

    record_action(
        "Standardize transaction types",
        changed_types.sum(),
        "Standardized transaction types to Deposit and Withdrawal."
    )

    # 4. Convert transaction amounts to numeric
    clean_df["amount"] = pd.to_numeric(
        clean_df["amount"],
        errors="coerce"
    )

    missing_amounts = clean_df["amount"].isna()
    missing_count = missing_amounts.sum()

    record_action(
        "Identify missing or invalid amounts",
        missing_count,
        "Converted invalid amount values and missing values to NaN."
    )

    # 5. Impute missing amounts using the median
    median_amount = clean_df["amount"].median()

    clean_df["amount_imputed"] = missing_amounts

    if missing_count > 0:
        if pd.isna(median_amount):
            raise ValueError(
                "Cannot impute amounts because all transaction amounts are missing."
            )

        clean_df["amount"] = clean_df["amount"].fillna(median_amount)

    record_action(
        "Impute missing amounts",
        missing_count,
        (
            f"Replaced missing amounts with the median "
            f"of KES {median_amount:.2f}."
        )
    )

    # 6. Detect suspicious KES 250,000 amounts
    suspicious_count = clean_df["amount"].eq(250000).sum()

    record_action(
        "Flag suspicious KES 250,000 amounts",
        suspicious_count,
        "Retained suspicious amounts for investigation."
    )

    # 7. Detect outliers using the IQR method
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
        "Flag statistical outliers",
        clean_df["is_outlier"].sum(),
        (
            f"Used IQR bounds of KES {lower_bound:.2f} "
            f"to KES {upper_bound:.2f}. Outliers were retained."
        )
    )

    # 8. Standardize transaction dates
    original_dates = clean_df["txn_date"].copy()

    normalized_dates = (
        original_dates.astype("string").str.replace("/", "-", regex=False)
    )

    clean_df["txn_date"] = pd.to_datetime(
        normalized_dates,
        format="mixed",
        errors="coerce"
    )

    invalid_dates = clean_df["txn_date"].isna().sum()

    record_action(
        "Standardize and validate transaction dates",
        invalid_dates,
        "Converted valid dates to datetime and standardized slash separators."
    )

    # 9. Identify unknown agents
    clean_df["unknown_agent"] = (
        ~clean_df["agent_id"].isin(valid_agent_ids)
    )

    record_action(
        "Identify unknown agents",
        clean_df["unknown_agent"].sum(),
        "Flagged transactions referencing unregistered agents."
    )

    # 10. Merge agent information
    clean_df = clean_df.merge(
        agents_df[["agent_id", "county"]],
        on="agent_id",
        how="left",
        validate="many_to_one"
    )

    record_action(
        "Merge agent register",
        clean_df["county"].isna().sum(),
        "Used a left join to retain transactions with unknown agents."
    )

    # 11. Format dates as ISO strings
    clean_df["txn_date"] = (
        clean_df["txn_date"].dt.strftime("%Y-%m-%d")
    )

    record_action(
        "Format transaction dates",
        len(clean_df),
        "Formatted transaction dates as YYYY-MM-DD."
    )

    # Return cleaned data and audit log
    cleaning_log = pd.DataFrame(log)

    return clean_df, cleaning_log
