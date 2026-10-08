import io
import pandas as pd

from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo


def create_excel_report(
    data,
    department_summary,
    top_variances,
    ai_results,
    analyst_notes,
    data_source,
):
    """
    Creates a professionally formatted Excel management report.
    """

    output = io.BytesIO()

    # =========================================================
    # FINANCIAL SUMMARY
    # =========================================================

    total_budget = data["Budget"].sum()
    total_actual = data["Actual"].sum()
    total_variance = total_actual - total_budget

    variance_percentage = (
        (total_variance / total_budget) * 100
        if total_budget != 0
        else 0
    )

    summary_df = pd.DataFrame(
        {
            "Metric": [
                "Data Source",
                "Rows Analyzed",
                "Departments",
                "Periods",
                "Total Budget",
                "Total Actual",
                "Net Variance",
                "Overall Variance %",
            ],
            "Value": [
                data_source,
                len(data),
                data["Department"].nunique(),
                data["Period"].nunique(),
                total_budget,
                total_actual,
                total_variance,
                variance_percentage,
            ],
        }
    )

    # =========================================================
    # TOP 3 VARIANCES
    # =========================================================

    top_export = top_variances.copy()

    top_export["Variance_%"] = top_export["Variance_%"].round(2)

    top_export["Analyst Note"] = ""
    top_export["AI Commentary"] = ""
    top_export["Verification"] = ""

    # Add available AI results
    for index, row in top_export.iterrows():

        key = (
            f"{row['Department']}_"
            f"{row['Line_Item']}_{index}"
        )

        ai_result = None

        # Current ai_results is a list
        if isinstance(ai_results, list):

            for item in ai_results:

                if (
                    item.get("department") == row["Department"]
                    and item.get("line_item") == row["Line_Item"]
                ):
                    ai_result = item
                    break

        # Also support dictionary format
        elif isinstance(ai_results, dict):

            ai_result = ai_results.get(key)

        if ai_result:

            # Analyst note
            top_export.at[
                index,
                "Analyst Note"
            ] = ai_result.get(
                "analyst_note",
                ai_result.get("Analyst_Note", "")
            )

            # AI commentary
            top_export.at[
                index,
                "AI Commentary"
            ] = ai_result.get(
                "commentary",
                ai_result.get("Commentary", "")
            )

            # Verification
            if "verification" in ai_result:

                verification = ai_result["verification"]

                if isinstance(verification, dict):

                    verified = verification.get(
                        "passed",
                        False
                    )

                    top_export.at[
                        index,
                        "Verification"
                    ] = (
                        "Verified"
                        if verified
                        else "Verification Failed"
                    )

            elif "verified" in ai_result:

                top_export.at[
                    index,
                    "Verification"
                ] = (
                    "Verified"
                    if ai_result["verified"]
                    else "Verification Failed"
                )

            elif "Verification" in ai_result:

                top_export.at[
                    index,
                    "Verification"
                ] = ai_result["Verification"]

    # =========================================================
    # AI COMMENTARY
    # =========================================================

    ai_rows = []

    if isinstance(ai_results, list):

        for item in ai_results:

            verification = item.get(
                "verification",
                {}
            )

            if isinstance(verification, dict):

                verified = verification.get(
                    "passed",
                    False
                )

                verification_text = (
                    "Verified"
                    if verified
                    else "Verification Failed"
                )

            else:

                verification_text = str(
                    verification
                )

            ai_rows.append(
                {
                    "Department": item.get(
                        "department",
                        ""
                    ),
                    "Line Item": item.get(
                        "line_item",
                        ""
                    ),
                    "AI Commentary": item.get(
                        "commentary",
                        ""
                    ),
                    "Verification": verification_text,
                }
            )

    elif isinstance(ai_results, dict):

        for item in ai_results.values():

            verified = item.get(
                "verified",
                False
            )

            ai_rows.append(
                {
                    "Department": item.get(
                        "department",
                        ""
                    ),
                    "Line Item": item.get(
                        "line_item",
                        ""
                    ),
                    "AI Commentary": item.get(
                        "commentary",
                        ""
                    ),
                    "Verification": (
                        "Verified"
                        if verified
                        else "Verification Failed"
                    ),
                }
            )

    ai_df = pd.DataFrame(ai_rows)

    if ai_df.empty:

        ai_df = pd.DataFrame(
            columns=[
                "Department",
                "Line Item",
                "AI Commentary",
                "Verification",
            ]
        )

    # =========================================================
    # ANALYST NOTES
    # =========================================================

    notes_rows = []

    for index, (_, row) in enumerate(
        top_variances.iterrows()
    ):

        key = (
            f"{row['Department']}_"
            f"{row['Line_Item']}_{index}"
        )

        note = ""

        if isinstance(analyst_notes, dict):

            note = analyst_notes.get(
                key,
                ""
            )

            # Also check note_key format
            if not note:

                note = analyst_notes.get(
                    f"note_{key}",
                    ""
                )

        notes_rows.append(
            {
                "Department": row["Department"],
                "Line Item": row["Line_Item"],
                "Analyst Note": note,
            }
        )

    notes_df = pd.DataFrame(notes_rows)

    # =========================================================
    # WRITE EXCEL
    # =========================================================

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False
        )

        department_summary.to_excel(
            writer,
            sheet_name="Department Summary",
            index=False
        )

        top_export.to_excel(
            writer,
            sheet_name="Top 3 Variances",
            index=False
        )

        ai_df.to_excel(
            writer,
            sheet_name="AI Commentary",
            index=False
        )

        notes_df.to_excel(
            writer,
            sheet_name="Analyst Notes",
            index=False
        )

        data.to_excel(
            writer,
            sheet_name="Detailed Data",
            index=False
        )

        # =====================================================
        # COMMON STYLING
        # =====================================================

        workbook = writer.book

        header_fill = PatternFill(
            "solid",
            fgColor="1F4E78"
        )

        header_font = Font(
            bold=True,
            color="FFFFFF"
        )

        title_font = Font(
            bold=True,
            size=16
        )

        thin_border = Border(
            bottom=Side(
                style="thin",
                color="D9E1F2"
            )
        )

        favourable_fill = PatternFill(
            "solid",
            fgColor="E2F0D9"
        )

        unfavourable_fill = PatternFill(
            "solid",
            fgColor="FCE4D6"
        )

        verified_fill = PatternFill(
            "solid",
            fgColor="E2F0D9"
        )

        failed_fill = PatternFill(
            "solid",
            fgColor="F4CCCC"
        )

        # =====================================================
        # STYLE EACH SHEET
        # =====================================================

        for ws in workbook.worksheets:

            # Freeze first row
            ws.freeze_panes = "A2"

            # Header styling
            for cell in ws[1]:

                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )

                cell.border = thin_border

            # Header height
            ws.row_dimensions[1].height = 25

            # Auto-size columns
            for column_cells in ws.columns:

                column_letter = get_column_letter(
                    column_cells[0].column
                )

                max_length = 0

                for cell in column_cells:

                    try:

                        value_length = len(
                            str(cell.value)
                        )

                        max_length = max(
                            max_length,
                            value_length
                        )

                    except Exception:

                        pass

                ws.column_dimensions[
                    column_letter
                ].width = min(
                    max(max_length + 2, 12),
                    55
                )

            # Wrap text
            for row in ws.iter_rows():

                for cell in row:

                    cell.alignment = Alignment(
                        vertical="top",
                        wrap_text=True
                    )

        # =====================================================
        # EXECUTIVE SUMMARY
        # =====================================================

        ws = workbook[
            "Executive Summary"
        ]

        ws.freeze_panes = "A2"

        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 30

        # Currency rows
        currency_metrics = {
            "Total Budget",
            "Total Actual",
            "Net Variance",
        }

        for row in range(
            2,
            ws.max_row + 1
        ):

            metric = ws.cell(
                row=row,
                column=1
            ).value

            if metric in currency_metrics:

                ws.cell(
                    row=row,
                    column=2
                ).number_format = '₹#,##0'

            if metric == "Overall Variance %":

                ws.cell(
                    row=row,
                    column=2
                ).number_format = '0.00%'

        # =====================================================
        # DEPARTMENT SUMMARY
        # =====================================================

        ws = workbook[
            "Department Summary"
        ]

        for column in range(
            2,
            ws.max_column + 1
        ):

            header = ws.cell(
                row=1,
                column=column
            ).value

            if header in [
                "Budget",
                "Actual",
                "Variance",
            ]:

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    ws.cell(
                        row=row,
                        column=column
                    ).number_format = '₹#,##0'

            if header in [
                "Variance_%",
                "Variance %",
            ]:

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    ws.cell(
                        row=row,
                        column=column
                    ).number_format = '0.00%'

        # =====================================================
        # TOP 3 VARIANCES
        # =====================================================

        ws = workbook[
            "Top 3 Variances"
        ]

        # Currency
        for column in [
            "Budget",
            "Actual",
            "Variance",
            "Absolute_Variance",
        ]:

            for cell in ws[1]:

                if cell.value == column:

                    col = cell.column

                    for row in range(
                        2,
                        ws.max_row + 1
                    ):

                        ws.cell(
                            row=row,
                            column=col
                        ).number_format = '₹#,##0'

        # Percentage
        for cell in ws[1]:

            if cell.value == "Variance_%":

                col = cell.column

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    ws.cell(
                        row=row,
                        column=col
                    ).number_format = '0.00%'

    

        # Find Status column
        status_col = None
        verification_col = None

        for cell in ws[1]:

            if cell.value == "Status":
                status_col = cell.column

            if cell.value == "Verification":
                verification_col = cell.column

        if status_col:

            for row in range(
                2,
                ws.max_row + 1
            ):

                cell = ws.cell(
                    row=row,
                    column=status_col
                )

                if cell.value == "Favourable":

                    cell.fill = favourable_fill

                elif cell.value == "Unfavourable":

                    cell.fill = unfavourable_fill

        if verification_col:

            for row in range(
                2,
                ws.max_row + 1
            ):

                cell = ws.cell(
                    row=row,
                    column=verification_col
                )

                if cell.value == "Verified":

                    cell.fill = verified_fill

                elif cell.value == "Verification Failed":

                    cell.fill = failed_fill

        # Make AI commentary wider
        for column in ws.columns:

            for cell in column:

                if cell.value in [
                    "AI Commentary",
                    "Analyst Note",
                ]:

                    ws.column_dimensions[
                        get_column_letter(
                            cell.column
                        )
                    ].width = 55

        # =====================================================
        # AI COMMENTARY
        # =====================================================

        ws = workbook[
            "AI Commentary"
        ]

        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 75
        ws.column_dimensions["D"].width = 22

        verification_col = None

        for cell in ws[1]:

            if cell.value == "Verification":

                verification_col = cell.column

        if verification_col:

            for row in range(
                2,
                ws.max_row + 1
            ):

                cell = ws.cell(
                    row=row,
                    column=verification_col
                )

                if cell.value == "Verified":

                    cell.fill = verified_fill

                elif cell.value == "Verification Failed":

                    cell.fill = failed_fill

        # =====================================================
        # ANALYST NOTES
        # =====================================================

        ws = workbook[
            "Analyst Notes"
        ]

        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 28
        ws.column_dimensions["C"].width = 70

        # =====================================================
        # DETAILED DATA
        # =====================================================

        ws = workbook[
            "Detailed Data"
        ]

        for cell in ws[1]:

            if cell.value in [
                "Budget",
                "Actual",
                "Variance",
            ]:

                column = cell.column

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    ws.cell(
                        row=row,
                        column=column
                    ).number_format = '₹#,##0'

            if cell.value == "Variance_%":

                column = cell.column

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    ws.cell(
                        row=row,
                        column=column
                    ).number_format = '0.00%'

            if cell.value == "Status":

                column = cell.column

                for row in range(
                    2,
                    ws.max_row + 1
                ):

                    status_cell = ws.cell(
                        row=row,
                        column=column
                    )

                    if status_cell.value == "Favourable":

                        status_cell.fill = favourable_fill

                    elif status_cell.value == "Unfavourable":

                        status_cell.fill = unfavourable_fill

    output.seek(0)

    return output