import pandas as pd

from engine import (
    validate_data,
    calculate_variance,
    get_top_variances
)


# ---------------------------------------------------------
# TEST 1: VALID DATA
# ---------------------------------------------------------

def test_valid_data():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["Advertising"],
        "Line_Type": ["Cost"],
        "Budget": [500000],
        "Actual": [650000]
    })

    errors = validate_data(df)

    assert errors == []

    print("TEST 1 PASSED: Valid data accepted")


# ---------------------------------------------------------
# TEST 2: VARIANCE CALCULATION
# ---------------------------------------------------------

def test_variance_calculation():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["Advertising"],
        "Line_Type": ["Cost"],
        "Budget": [500000],
        "Actual": [650000]
    })

    result = calculate_variance(df)

    assert result.loc[0, "Variance"] == 150000
    assert result.loc[0, "Variance_%"] == 30
    assert result.loc[0, "Status"] == "Unfavourable"

    print("TEST 2 PASSED: Variance calculation correct")


# ---------------------------------------------------------
# TEST 3: REVENUE LOGIC
# ---------------------------------------------------------

def test_revenue_logic():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Sales"],
        "Line_Item": ["Product Revenue"],
        "Line_Type": ["Revenue"],
        "Budget": [1500000],
        "Actual": [1350000]
    })

    result = calculate_variance(df)

    assert result.loc[0, "Variance"] == -150000
    assert result.loc[0, "Variance_%"] == -10
    assert result.loc[0, "Status"] == "Unfavourable"

    print("TEST 3 PASSED: Revenue logic correct")


# ---------------------------------------------------------
# TEST 4: ZERO BUDGET
# ---------------------------------------------------------

def test_zero_budget():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["New Campaign"],
        "Line_Type": ["Cost"],
        "Budget": [0],
        "Actual": [50000]
    })

    result = calculate_variance(df)

    assert result.loc[0, "Variance"] == 50000
    assert pd.isna(result.loc[0, "Variance_%"])

    print("TEST 4 PASSED: Zero-budget case handled")


# ---------------------------------------------------------
# TEST 5: MISSING COLUMN
# ---------------------------------------------------------

def test_missing_column():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["Advertising"],
        "Budget": [500000],
        "Actual": [650000]
    })

    errors = validate_data(df)

    assert len(errors) > 0
    assert "Line_Type" in errors[0]

    print("TEST 5 PASSED: Missing column detected")


# ---------------------------------------------------------
# TEST 6: NEGATIVE BUDGET
# ---------------------------------------------------------

def test_negative_budget():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["Advertising"],
        "Line_Type": ["Cost"],
        "Budget": [-500000],
        "Actual": [650000]
    })

    errors = validate_data(df)

    assert any("negative" in error.lower() for error in errors)

    print("TEST 6 PASSED: Negative budget detected")


# ---------------------------------------------------------
# TEST 7: DUPLICATE ROW
# ---------------------------------------------------------

def test_duplicate_rows():

    df = pd.DataFrame({
        "Period": ["Sep-2026", "Sep-2026"],
        "Department": ["Marketing", "Marketing"],
        "Line_Item": ["Advertising", "Advertising"],
        "Line_Type": ["Cost", "Cost"],
        "Budget": [500000, 500000],
        "Actual": [650000, 650000]
    })

    errors = validate_data(df)

    assert any("duplicate" in error.lower() for error in errors)

    print("TEST 7 PASSED: Duplicate row detected")


# ---------------------------------------------------------
# TEST 8: INVALID LINE TYPE
# ---------------------------------------------------------

def test_invalid_line_type():

    df = pd.DataFrame({
        "Period": ["Sep-2026"],
        "Department": ["Marketing"],
        "Line_Item": ["Advertising"],
        "Line_Type": ["Unknown"],
        "Budget": [500000],
        "Actual": [650000]
    })

    errors = validate_data(df)

    assert any("line_type" in error.lower() for error in errors)

    print("TEST 8 PASSED: Invalid Line_Type detected")


# ---------------------------------------------------------
# TEST 9: TOP VARIANCE RANKING
# ---------------------------------------------------------

def test_top_variances():

    df = pd.DataFrame({
        "Period": ["Sep-2026", "Sep-2026", "Sep-2026"],
        "Department": ["Marketing", "IT", "HR"],
        "Line_Item": [
            "Advertising",
            "Software",
            "Training"
        ],
        "Line_Type": [
            "Cost",
            "Cost",
            "Cost"
        ],
        "Budget": [
            500000,
            300000,
            100000
        ],
        "Actual": [
            650000,
            360000,
            150000
        ]
    })

    calculated = calculate_variance(df)

    top = get_top_variances(calculated, top_n=2)

    assert len(top) == 2

    # Largest variance should be Advertising
    assert top.iloc[0]["Line_Item"] == "Advertising"

    print("TEST 9 PASSED: Top variance ranking correct")


# ---------------------------------------------------------
# RUN ALL TESTS
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\nRunning BudgetSense AI Engine Tests...\n")

    test_valid_data()
    test_variance_calculation()
    test_revenue_logic()
    test_zero_budget()
    test_missing_column()
    test_negative_budget()
    test_duplicate_rows()
    test_invalid_line_type()
    test_top_variances()

    print("\n----------------------------------------")
    print("ALL TESTS PASSED")
    print("----------------------------------------")