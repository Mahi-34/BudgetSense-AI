import pandas as pd


# =========================================================
# 1. VALIDATE INPUT DATA
# =========================================================

def validate_data(df):
    """
    Checks whether the uploaded budget data is valid.

    Returns:
        A list of validation errors.
        Empty list means the data is valid.
    """

    errors = []

    required_columns = [
        "Period",
        "Department",
        "Line_Item",
        "Line_Type",
        "Budget",
        "Actual"
    ]

    # -----------------------------------------------------
    # Check required columns
    # -----------------------------------------------------

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing columns: {', '.join(missing_columns)}"
        )

        # Cannot continue if required columns are missing
        return errors

    # -----------------------------------------------------
    # Check missing values
    # -----------------------------------------------------

    if df[required_columns].isnull().any().any():
        errors.append(
            "Dataset contains missing values."
        )

    # -----------------------------------------------------
    # Check numeric columns
    # -----------------------------------------------------

    if not pd.api.types.is_numeric_dtype(df["Budget"]):
        errors.append(
            "Budget column must contain numbers."
        )

    if not pd.api.types.is_numeric_dtype(df["Actual"]):
        errors.append(
            "Actual column must contain numbers."
        )

    # -----------------------------------------------------
    # Check negative values
    # -----------------------------------------------------

    # Only perform numeric comparison if the column
    # actually contains numeric values.

    if pd.api.types.is_numeric_dtype(df["Budget"]):
        if (df["Budget"] < 0).any():
            errors.append(
                "Budget cannot contain negative values."
            )

    if pd.api.types.is_numeric_dtype(df["Actual"]):
        if (df["Actual"] < 0).any():
            errors.append(
                "Actual cannot contain negative values."
            )

    # -----------------------------------------------------
    # Check duplicate rows
    # -----------------------------------------------------

    if df.duplicated().any():
        errors.append(
            "Dataset contains duplicate rows."
        )

    # -----------------------------------------------------
    # Check Line_Type
    # -----------------------------------------------------

    valid_types = {
        "Revenue",
        "Cost"
    }

    invalid_types = (
        set(df["Line_Type"].dropna())
        - valid_types
    )

    if invalid_types:
        errors.append(
            f"Invalid Line_Type values: "
            f"{', '.join(map(str, invalid_types))}"
        )

    return errors


# =========================================================
# 2. CALCULATE VARIANCE
# =========================================================

def calculate_variance(df):
    """
    Calculates:

    - Variance in rupees
    - Variance percentage
    - Favourable / Unfavourable status
    """

    result = df.copy()

    # -----------------------------------------------------
    # Absolute variance
    # -----------------------------------------------------

    result["Variance"] = (
        result["Actual"] - result["Budget"]
    )

    # -----------------------------------------------------
    # Variance percentage
    # -----------------------------------------------------

    result["Variance_%"] = (
        result["Variance"]
        / result["Budget"]
        * 100
    )

    # Avoid division by zero
    result.loc[
        result["Budget"] == 0,
        "Variance_%"
    ] = pd.NA

    # -----------------------------------------------------
    # Determine favourable / unfavourable
    # -----------------------------------------------------

    def determine_status(row):

        # -----------------------------
        # COST
        # -----------------------------

        if row["Line_Type"] == "Cost":

            if row["Actual"] > row["Budget"]:
                return "Unfavourable"

            elif row["Actual"] < row["Budget"]:
                return "Favourable"

            else:
                return "No Variance"

        # -----------------------------
        # REVENUE
        # -----------------------------

        elif row["Line_Type"] == "Revenue":

            if row["Actual"] > row["Budget"]:
                return "Favourable"

            elif row["Actual"] < row["Budget"]:
                return "Unfavourable"

            else:
                return "No Variance"

        return "Unknown"

    result["Status"] = result.apply(
        determine_status,
        axis=1
    )

    return result


# =========================================================
# 3. FIND TOP MATERIAL VARIANCES
# =========================================================

def get_top_variances(df, top_n=3):
    """
    Returns the most financially significant variances.

    Ranking is based on absolute rupee impact.

    The same Department + Line Item combination
    is shown only once so that management sees
    different business areas requiring attention.
    """

    result = df.copy()

    # -----------------------------------------------------
    # Calculate absolute financial impact
    # -----------------------------------------------------

    result["Absolute_Variance"] = (
        result["Variance"].abs()
    )

    # -----------------------------------------------------
    # Rank by largest financial impact
    # -----------------------------------------------------

    result = result.sort_values(
        by="Absolute_Variance",
        ascending=False
    )

    # -----------------------------------------------------
    # Keep only the largest variance for each
    # Department + Line Item combination
    # -----------------------------------------------------

    result = result.drop_duplicates(
        subset=[
            "Department",
            "Line_Item"
        ],
        keep="first"
    )

    # -----------------------------------------------------
    # Return top N
    # -----------------------------------------------------

    return result.head(top_n)


# =========================================================
# 4. COMPLETE BUDGET ANALYSIS
# =========================================================

def analyze_budget(df, top_n=3):
    """
    Runs the complete BudgetSense AI financial engine.

    Steps:
    1. Validate data
    2. Calculate variance
    3. Identify material variances
    """

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    errors = validate_data(df)

    if errors:

        return {
            "valid": False,
            "errors": errors,
            "data": None,
            "top_variances": None
        }

    # -----------------------------------------------------
    # Calculate variance
    # -----------------------------------------------------

    calculated_data = calculate_variance(df)

    # -----------------------------------------------------
    # Find top material variances
    # -----------------------------------------------------

    top_variances = get_top_variances(
        calculated_data,
        top_n
    )

    return {
        "valid": True,
        "errors": [],
        "data": calculated_data,
        "top_variances": top_variances
    }


# =========================================================
# 5. TEST THE ENGINE
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # Final BudgetSense AI dataset
    # -----------------------------------------------------

    file_path = (
        "data/"
        "BudgetSense_Final_Clean_Dataset.xlsx"
    )

    # -----------------------------------------------------
    # Load Excel file
    # -----------------------------------------------------

    df = pd.read_excel(file_path)

    print(
        f"\nDataset loaded successfully."
    )

    print(
        f"Total rows: {len(df)}"
    )

    # -----------------------------------------------------
    # Run analysis
    # -----------------------------------------------------

    result = analyze_budget(df)

    # -----------------------------------------------------
    # Handle validation failure
    # -----------------------------------------------------

    if not result["valid"]:

        print("\nVALIDATION FAILED")

        for error in result["errors"]:
            print("-", error)

    # -----------------------------------------------------
    # Successful analysis
    # -----------------------------------------------------

    else:

        print("\nVALIDATION PASSED")

        # -------------------------------------------------
        # Display calculated results
        # -------------------------------------------------

        print(
            "\nCalculated Variances:"
        )

        print(
            result["data"][
                [
                    "Department",
                    "Line_Item",
                    "Line_Type",
                    "Budget",
                    "Actual",
                    "Variance",
                    "Variance_%",
                    "Status"
                ]
            ].to_string(index=False)
        )

        # -------------------------------------------------
        # Display top material variances
        # -------------------------------------------------

        print(
            "\nTOP 3 MATERIAL VARIANCES:"
        )

        print(
            result["top_variances"][
                [
                    "Department",
                    "Line_Item",
                    "Budget",
                    "Actual",
                    "Variance",
                    "Variance_%",
                    "Status"
                ]
            ].to_string(index=False)
        )