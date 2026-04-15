"""Generate a professional multi-sheet workout system workbook.

Usage:
    python workout_system_generator.py
    python workout_system_generator.py --output My_Workout_System.xlsx
"""

from __future__ import annotations

import argparse
from datetime import date

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

# Theme colors (premium but simple)
NAVY = "1F2A44"
SLATE = "4A5568"
LIGHT_BG = "F7FAFC"
WHITE = "FFFFFF"
GREEN = "2F855A"
RED = "C53030"
BLUE = "2B6CB0"

THIN_BORDER = Border(
    left=Side(style="thin", color="D1D5DB"),
    right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"),
    bottom=Side(style="thin", color="D1D5DB"),
)


def style_title(ws, cell: str, text: str) -> None:
    ws[cell] = text
    ws[cell].font = Font(name="Calibri", size=20, bold=True, color=NAVY)
    ws[cell].alignment = Alignment(horizontal="left", vertical="center")


def style_header_row(ws, row: int, min_col: int, max_col: int) -> None:
    for col in range(min_col, max_col + 1):
        c = ws.cell(row=row, column=col)
        c.font = Font(name="Calibri", bold=True, color=WHITE)
        c.fill = PatternFill(fill_type="solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = THIN_BORDER


def apply_card_style(ws, row: int, label_col: int = 2, value_col: int = 3) -> None:
    label = ws.cell(row=row, column=label_col)
    value = ws.cell(row=row, column=value_col)

    label.font = Font(name="Calibri", bold=True, color=SLATE)
    label.fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
    label.border = THIN_BORDER
    label.alignment = Alignment(horizontal="left")

    value.font = Font(name="Calibri", bold=True, color=NAVY)
    value.fill = PatternFill(fill_type="solid", fgColor=WHITE)
    value.border = THIN_BORDER
    value.alignment = Alignment(horizontal="center")


def build_dashboard(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "Dashboard"

    style_title(ws, "B2", "Simple Workout System")
    ws["B3"] = f"Generated on {date.today().isoformat()}"
    ws["B3"].font = Font(size=10, color=SLATE, italic=True)

    labels = [
        ("Planned Workouts", "=COUNTIF('Workout Plan'!C4:C104,\"<>Rest\")"),
        ("Completed Workouts", "=COUNTIF('Workout Log'!C4:C504,\"Yes\")"),
        (
            "Current Streak",
            "=IF(C7=0,0,MAX(FREQUENCY(IF('Workout Log'!C4:C504=\"Yes\",ROW('Workout Log'!C4:C504)),IF('Workout Log'!C4:C504<>\"Yes\",ROW('Workout Log'!C4:C504)))))",
        ),
        ("Weight Lost", "=IFERROR('Progress'!C6-'Progress'!C7,0)"),
    ]

    start_row = 5
    for i, (label, formula) in enumerate(labels):
        r = start_row + i
        ws.cell(row=r, column=2, value=label)
        ws.cell(row=r, column=3, value=formula)
        apply_card_style(ws, r)

    ws["B11"] = "Quick Notes"
    ws["B11"].font = Font(bold=True, color=SLATE)
    ws["B12"] = "Stay consistent: 3 workouts/week beats 1 perfect week."
    ws["B12"].alignment = Alignment(wrap_text=True)

    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 26


def build_workout_plan(wb: Workbook) -> None:
    ws = wb.create_sheet("Workout Plan")
    style_title(ws, "B2", "Workout Plan")

    headers = ["Day", "Workout", "Primary Focus", "Planned Duration (min)"]
    for idx, header in enumerate(headers, start=2):
        ws.cell(row=3, column=idx, value=header)

    style_header_row(ws, 3, 2, 5)

    plan = [
        ("Monday", "Upper Body", "Push + Pull", 45),
        ("Tuesday", "Rest", "Recovery", 0),
        ("Wednesday", "Lower Body", "Squat + Hinge", 45),
        ("Thursday", "Rest", "Mobility", 0),
        ("Friday", "Upper Body", "Push + Pull", 45),
        ("Saturday", "Lower Body", "Squat + Hinge", 45),
        ("Sunday", "Rest", "Recovery", 0),
    ]

    for r, row_data in enumerate(plan, start=4):
        for c, value in enumerate(row_data, start=2):
            cell = ws.cell(row=r, column=c, value=value)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center")

    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 24


def build_workout_log(wb: Workbook) -> None:
    ws = wb.create_sheet("Workout Log")
    style_title(ws, "B2", "Workout Log")

    headers = ["Date", "Workout Completed", "Notes", "Energy (1-10)"]
    for idx, header in enumerate(headers, start=2):
        ws.cell(row=3, column=idx, value=header)

    style_header_row(ws, 3, 2, 5)

    for row in range(4, 504):
        for col in range(2, 6):
            ws.cell(row=row, column=col).border = THIN_BORDER

    yes_no = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(yes_no)
    yes_no.add("C4:C503")

    energy = DataValidation(type="whole", operator="between", formula1=1, formula2=10, allow_blank=True)
    ws.add_data_validation(energy)
    energy.add("E4:E503")

    complete_green = FormulaRule(
        formula=['$C4="Yes"'],
        fill=PatternFill(fill_type="solid", fgColor="E6FFFA"),
        font=Font(color=GREEN),
    )
    missed_red = FormulaRule(
        formula=['$C4="No"'],
        fill=PatternFill(fill_type="solid", fgColor="FFF5F5"),
        font=Font(color=RED),
    )

    ws.conditional_formatting.add("B4:E503", complete_green)
    ws.conditional_formatting.add("B4:E503", missed_red)

    ws.freeze_panes = "B4"
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 38
    ws.column_dimensions["E"].width = 14


def build_progress(wb: Workbook) -> None:
    ws = wb.create_sheet("Progress")
    style_title(ws, "B2", "Progress")

    ws["B5"] = "Starting Weight"
    ws["B6"] = "Current Weight"
    ws["B7"] = "Weight Lost"
    for r in (5, 6, 7):
        ws[f"B{r}"].font = Font(bold=True, color=SLATE)
        ws[f"B{r}"].fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
        ws[f"B{r}"].border = THIN_BORDER
        ws[f"C{r}"].border = THIN_BORDER

    ws["C7"] = "=IFERROR(C5-C6,0)"
    ws["C7"].font = Font(bold=True, color=BLUE)

    ws["E4"] = "Date"
    ws["F4"] = "Weight"
    style_header_row(ws, 4, 5, 6)

    for row in range(5, 105):
        ws.cell(row=row, column=5).border = THIN_BORDER
        ws.cell(row=row, column=6).border = THIN_BORDER

    chart = LineChart()
    chart.title = "Weight Trend"
    chart.style = 10
    chart.y_axis.title = "Weight"
    chart.x_axis.title = "Date"

    data = Reference(ws, min_col=6, min_row=4, max_row=104)
    categories = Reference(ws, min_col=5, min_row=5, max_row=104)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.height = 7
    chart.width = 12

    ws.add_chart(chart, "B10")

    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 12


def build_instructions(wb: Workbook) -> None:
    ws = wb.create_sheet("Instructions")
    style_title(ws, "B2", "How To Use")

    instructions = [
        "1) Set your starting and current weight in the Progress sheet.",
        "2) Follow the weekly split in Workout Plan.",
        "3) Log every training day in Workout Log (Yes/No + notes).",
        "4) Review Dashboard metrics weekly to track consistency and results.",
        "5) Duplicate this file monthly to keep a clean historical record.",
    ]

    for idx, text in enumerate(instructions, start=4):
        ws.cell(row=idx, column=2, value=text)
        ws.cell(row=idx, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    ws.column_dimensions["B"].width = 90


def create_workbook(output_path: str) -> None:
    wb = Workbook()
    build_dashboard(wb)
    build_workout_plan(wb)
    build_workout_log(wb)
    build_progress(wb)
    build_instructions(wb)
    wb.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a professional workout system workbook.")
    parser.add_argument(
        "--output",
        default="Workout_System_Professional.xlsx",
        help="Output xlsx filename (default: Workout_System_Professional.xlsx)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_workbook(args.output)
    print(f"Workbook created: {args.output}")


if __name__ == "__main__":
    main()