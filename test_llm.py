from llm import generate_variance_commentary


print("\nTEST 1 — Marketing")
print("-" * 50)

marketing_commentary = generate_variance_commentary(
    department="Marketing",
    line_item="Digital Advertising",
    line_type="Cost",
    budget=534000,
    actual=684000,
    variance=150000,
    variance_pct=28.09,
    status="Unfavourable",
    analyst_note="Festival campaign was launched earlier than planned."
)

print(marketing_commentary)


print("\nTEST 2 — IT")
print("-" * 50)

it_commentary = generate_variance_commentary(
    department="IT",
    line_item="Cloud Services",
    line_type="Cost",
    budget=360000,
    actual=472000,
    variance=112000,
    variance_pct=31.11,
    status="Unfavourable",
    analyst_note=""
)

print(it_commentary)