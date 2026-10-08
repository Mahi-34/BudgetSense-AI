from verifier import verify_commentary


# ---------------------------------------------------------
# Test 1 — Correct commentary
# ---------------------------------------------------------

commentary = (
    "Digital Advertising recorded an unfavourable "
    "variance of ₹150,000, representing 28.09% "
    "over budget."
)

result = verify_commentary(
    commentary=commentary,
    variance=150000,
    variance_pct=28.09
)

assert result["passed"] is True


# ---------------------------------------------------------
# Test 2 — Missing/wrong number
# ---------------------------------------------------------

bad_commentary = (
    "Digital Advertising recorded an unfavourable "
    "variance of ₹120,000, representing 20.00% "
    "over budget."
)

result = verify_commentary(
    commentary=bad_commentary,
    variance=150000,
    variance_pct=28.09
)

assert result["passed"] is False


print("ALL VERIFIER TESTS PASSED")