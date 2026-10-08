import pandas as pd

data = [
    # Major cost overruns
    ["Sep-2026", "Marketing", "Digital Advertising", "Cost", 500000, 650000],
    ["Sep-2026", "IT", "Software Licenses", "Cost", 300000, 360000],
    ["Sep-2026", "Operations", "Maintenance", "Cost", 400000, 470000],

    # Revenue shortfalls
    ["Sep-2026", "Sales", "Product Revenue", "Revenue", 1500000, 1350000],
    ["Sep-2026", "Sales", "Service Revenue", "Revenue", 800000, 760000],

    # Favourable cost variances
    ["Sep-2026", "HR", "Recruitment", "Cost", 200000, 180000],
    ["Sep-2026", "Finance", "Audit Expenses", "Cost", 150000, 120000],
    ["Sep-2026", "IT", "Hardware", "Cost", 250000, 210000],

    # Small item with huge percentage change
    ["Sep-2026", "HR", "Employee Snacks", "Cost", 1000, 3000],

    # Zero-budget case
    ["Sep-2026", "Marketing", "New Campaign", "Cost", 0, 50000],

    # Other normal expenses
    ["Sep-2026", "Operations", "Utilities", "Cost", 250000, 245000],
    ["Sep-2026", "Operations", "Transportation", "Cost", 180000, 195000],
    ["Sep-2026", "Marketing", "Events", "Cost", 300000, 285000],
    ["Sep-2026", "Marketing", "Print Media", "Cost", 100000, 95000],
    ["Sep-2026", "HR", "Training", "Cost", 120000, 145000],
    ["Sep-2026", "IT", "Cloud Services", "Cost", 350000, 420000],
    ["Sep-2026", "Finance", "Bank Charges", "Cost", 50000, 47000],
    ["Sep-2026", "Sales", "Travel Expenses", "Cost", 220000, 275000],
    ["Sep-2026", "Sales", "Sales Incentives", "Cost", 400000, 390000],
    ["Sep-2026", "Operations", "Raw Materials", "Cost", 600000, 625000],
    ["Sep-2026", "Operations", "Packaging", "Cost", 150000, 140000],
    ["Sep-2026", "Finance", "Professional Fees", "Cost", 100000, 130000],
    ["Sep-2026", "HR", "Employee Benefits", "Cost", 250000, 240000],
    ["Sep-2026", "Marketing", "Social Media", "Cost", 180000, 225000],
    ["Sep-2026", "Sales", "Customer Discounts", "Cost", 200000, 230000],
]

columns = [
    "Period",
    "Department",
    "Line_Item",
    "Line_Type",
    "Budget",
    "Actual"
]

df = pd.DataFrame(data, columns=columns)

output_path = "data/sample_budget.xlsx"

df.to_excel(output_path, index=False)

print(f"Created: {output_path}")
print(f"Rows: {len(df)}")