import re


def verify_commentary(
    commentary,
    variance,
    variance_pct
):
    """
    Verify that Gemini's commentary contains
    the key financial figures calculated by Python.
    """

    if not commentary or not commentary.strip():
        return {
            "passed": False,
            "issues": ["AI commentary is empty."]
        }

    issues = []

    # -----------------------------------------------------
    # Expected values
    # -----------------------------------------------------

    expected_variance = f"{variance:,.0f}"

    if variance_pct is not None:
        expected_percentage = f"{variance_pct:.2f}"
    else:
        expected_percentage = None

    # -----------------------------------------------------
    # Check variance amount
    # -----------------------------------------------------

    variance_found = (
        expected_variance in commentary
        or str(int(round(variance))) in commentary
    )

    if not variance_found:

        issues.append(
            f"Expected variance ₹{expected_variance} "
            "was not found in the AI commentary."
        )

    # -----------------------------------------------------
    # Check variance percentage
    # -----------------------------------------------------

    if expected_percentage is not None:

        percentage_found = (
            expected_percentage in commentary
        )

        if not percentage_found:

            issues.append(
                f"Expected variance percentage "
                f"{expected_percentage}% was not found "
                "in the AI commentary."
            )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {
        "passed": len(issues) == 0,
        "issues": issues
    }