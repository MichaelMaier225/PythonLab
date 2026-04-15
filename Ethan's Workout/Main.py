"""Generate a polished multi-sheet workout workbook.

Usage:
    python Main.py
    python Main.py --output My_Workout_System.xlsx
"""

from __future__ import annotations

import argparse
from datetime import date

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

# Theme colors
NAVY = "1F2A44"
SLATE = "4A5568"
LIGHT_BG = "F7FAFC"
WHITE = "FFFFFF"
GREEN = "2F855A"
RED = "C53030"
BLUE = "2B6CB0"
MUTED_GREEN = "E6FFFA"
MUTED_RED = "FFF5F5"
HEADER_BG = "2D3748"
ROW_ALT = "F8FAFC"

THIN_BORDER = Border(
    left=Side(style="thin", color="D1D5DB"),
    right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"),
    bottom=Side(style="thin", color="D1D5DB"),
)


def configure_sheet(ws, freeze_panes: str | None = None) -> None:
    """Apply workbook-wide visual defaults to a worksheet."""
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    if freeze_panes:
        ws.freeze_panes = freeze_panes


def style_title(ws, cell: str, text: str) -> None:
    ws[cell] = text
    ws[cell].font = Font(name="Calibri", size=21, bold=True, color=NAVY)
    ws[cell].alignment = Alignment(horizontal="left", vertical="center")


def style_header_row(ws, row: int, min_col: int, max_col: int) -> None:
    for col in range(min_col, max_col + 1):
        c = ws.cell(row=row, column=col)
        c.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
        c.fill = PatternFill(fill_type="solid", fgColor=HEADER_BG)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = THIN_BORDER


def stripe_data_rows(ws, start_row: int, end_row: int, min_col: int, max_col: int) -> None:
    """Apply alternating row fills for readability."""
    for row in range(start_row, end_row + 1):
        if row % 2 == 0:
            for col in range(min_col, max_col + 1):
                cell = ws.cell(row=row, column=col)
                cell.fill = PatternFill(fill_type="solid", fgColor=ROW_ALT)


def apply_card_style(ws, row: int, label_col: int = 2, value_col: int = 3) -> None:
    label = ws.cell(row=row, column=label_col)
    value = ws.cell(row=row, column=value_col)

    label.font = Font(name="Calibri", bold=True, color=SLATE)
    label.fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
    label.border = THIN_BORDER
    label.alignment = Alignment(horizontal="left", vertical="center")

    value.font = Font(name="Calibri", bold=True, color=NAVY)
    value.fill = PatternFill(fill_type="solid", fgColor=WHITE)
    value.border = THIN_BORDER
    value.alignment = Alignment(horizontal="center", vertical="center")


def build_dashboard(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "Dashboard"
    configure_sheet(ws)

    style_title(ws, "B2", "Ethan's Workout System")
    ws["B3"] = f"Generated on {date.today().strftime('%B %d, %Y')}"
    ws["B3"].font = Font(size=10, color=SLATE, italic=True)

    labels = [
        ("Planned Workouts", "=COUNTIF('Workout Plan'!$C$4:$C$104,\"<>Rest\")"),
        ("Completed Workouts", "=COUNTIF('Workout Log'!$C$4:$C$504,\"Yes\")"),
        ("Completion Rate", "=IFERROR(C6/C5,0)"),
        (
            "Weight Change",
            "=IF(OR('Progress'!C5=\"\",'Progress'!C6=\"\"),\"Set your weight\",'Progress'!C7)",
        ),
    ]

    for i, (label, formula) in enumerate(labels, start=5):
        ws.cell(row=i, column=2, value=label)
        ws.cell(row=i, column=3, value=formula)
        apply_card_style(ws, i)

    ws["C7"].number_format = "0%"
    ws["C8"].number_format = "0.0"

    ws["B10"] = "Quick Notes"
    ws["B10"].font = Font(bold=True, color=SLATE)
    ws["B10"].alignment = Alignment(horizontal="left")
    ws.merge_cells("B11:C13")
    ws["B11"] = "Stay consistent: 3 workouts/week done every week beats one perfect week."
    ws["B11"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["B11"].fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
    ws["B11"].border = THIN_BORDER

    ws["E5"] = "At-a-Glance"
    ws["E5"].font = Font(bold=True, color=SLATE)
    ws["E6"] = "Last Workout"
    ws["F6"] = "=LOOKUP(2,1/('Workout Log'!$B$4:$B$504<>\"\"),'Workout Log'!$B$4:$B$504)"
    ws["E7"] = "Avg Energy"
    ws["F7"] = "=IFERROR(AVERAGE('Workout Log'!$E$4:$E$504),\"\")"
    ws["E8"] = "This Month Sessions"
    ws["F8"] = "=COUNTIFS('Workout Log'!$B$4:$B$504,\">=\"&EOMONTH(TODAY(),-1)+1,'Workout Log'!$B$4:$B$504,\"<=\"&EOMONTH(TODAY(),0),'Workout Log'!$C$4:$C$504,\"Yes\")"

    for row in range(6, 9):
        ws[f"E{row}"].font = Font(bold=True, color=SLATE)
        ws[f"E{row}"].fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
        ws[f"E{row}"].border = THIN_BORDER
        ws[f"F{row}"].border = THIN_BORDER
        ws[f"F{row}"].alignment = Alignment(horizontal="center")

    ws["F6"].number_format = "mmm d, yyyy"
    ws["F7"].number_format = "0.0"

    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["E"].width = 21
    ws.column_dimensions["F"].width = 22


def build_workout_plan(wb: Workbook) -> None:
    ws = wb.create_sheet("Workout Plan")
    configure_sheet(ws, freeze_panes="B4")
    style_title(ws, "B2", "Workout Plan")

    headers = ["Day", "Workout", "Primary Focus", "Planned Duration (min)", "Intensity"]
    for idx, header in enumerate(headers, start=2):
        ws.cell(row=3, column=idx, value=header)

    style_header_row(ws, 3, 2, 6)

    plan = [
        ("Monday", "Upper Body", "Push + Pull", 45, "Moderate"),
        ("Tuesday", "Rest", "Recovery", 0, "Low"),
        ("Wednesday", "Lower Body", "Squat + Hinge", 45, "Hard"),
        ("Thursday", "Rest", "Mobility", 0, "Low"),
        ("Friday", "Upper Body", "Push + Pull", 45, "Moderate"),
        ("Saturday", "Lower Body", "Squat + Hinge", 45, "Hard"),
        ("Sunday", "Conditioning", "Cardio + Core", 30, "Moderate"),
    ]

    for row_number, row_data in enumerate(plan, start=4):
        for col, value in enumerate(row_data, start=2):
            cell = ws.cell(row=row_number, column=col, value=value)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center")

    stripe_data_rows(ws, 4, 104, 2, 6)

    duration_coloring = ColorScaleRule(
        start_type="num",
        start_value=0,
        start_color="E2E8F0",
        mid_type="num",
        mid_value=30,
        mid_color="BEE3F8",
        end_type="num",
        end_value=60,
        end_color="63B3ED",
    )
    ws.conditional_formatting.add("E4:E104", duration_coloring)

    workout_list = DataValidation(
        type="list",
        formula1='"Upper Body,Lower Body,Conditioning,Active Recovery,Rest"',
        allow_blank=True,
    )
    ws.add_data_validation(workout_list)
    workout_list.add("C4:C104")

    intensity_list = DataValidation(type="list", formula1='"Low,Moderate,Hard"', allow_blank=True)
    ws.add_data_validation(intensity_list)
    intensity_list.add("F4:F104")

    ws.auto_filter.ref = "B3:F104"
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 23
    ws.column_dimensions["E"].width = 23
    ws.column_dimensions["F"].width = 13


def build_workout_log(wb: Workbook) -> None:
    ws = wb.create_sheet("Workout Log")
    configure_sheet(ws, freeze_panes="B4")
    style_title(ws, "B2", "Workout Log")

    headers = ["Date", "Workout Completed", "Notes", "Energy (1-10)", "Duration (min)"]
    for idx, header in enumerate(headers, start=2):
        ws.cell(row=3, column=idx, value=header)

    style_header_row(ws, 3, 2, 6)

    for row in range(4, 504):
        for col in range(2, 7):
            cell = ws.cell(row=row, column=col)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center")

    stripe_data_rows(ws, 4, 503, 2, 6)

    yes_no = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(yes_no)
    yes_no.add("C4:C503")

    energy = DataValidation(type="whole", operator="between", formula1=1, formula2=10, allow_blank=True)
    ws.add_data_validation(energy)
    energy.add("E4:E503")

    duration = DataValidation(type="whole", operator="between", formula1=0, formula2=180, allow_blank=True)
    ws.add_data_validation(duration)
    duration.add("F4:F503")

    complete_green = FormulaRule(
        formula=['$C4="Yes"'],
        fill=PatternFill(fill_type="solid", fgColor=MUTED_GREEN),
        font=Font(color=GREEN),
    )
    missed_red = FormulaRule(
        formula=['$C4="No"'],
        fill=PatternFill(fill_type="solid", fgColor=MUTED_RED),
        font=Font(color=RED),
    )

    ws.conditional_formatting.add("B4:F503", complete_green)
    ws.conditional_formatting.add("B4:F503", missed_red)
    ws.conditional_formatting.add(
        "E4:E503",
        ColorScaleRule(
            start_type="num",
            start_value=1,
            start_color="FEB2B2",
            end_type="num",
            end_value=10,
            end_color="9AE6B4",
        ),
    )

    ws.auto_filter.ref = "B3:F503"
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 44
    ws.column_dimensions["E"].width = 13
    ws.column_dimensions["F"].width = 14


def build_progress(wb: Workbook) -> None:
    ws = wb.create_sheet("Progress")
    configure_sheet(ws)
    style_title(ws, "B2", "Progress")

    ws["B5"] = "Starting Weight"
    ws["B6"] = "Current Weight"
    ws["B7"] = "Weight Lost"
    for r in (5, 6, 7):
        ws[f"B{r}"].font = Font(bold=True, color=SLATE)
        ws[f"B{r}"].fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)
        ws[f"B{r}"].border = THIN_BORDER
        ws[f"B{r}"].alignment = Alignment(horizontal="left")

        ws[f"C{r}"].border = THIN_BORDER
        ws[f"C{r}"].alignment = Alignment(horizontal="center")
        ws[f"C{r}"].number_format = "0.0"

    ws["C7"] = "=IFERROR(C5-C6,0)"
    ws["C7"].font = Font(bold=True, color=BLUE)

    ws["E4"] = "Date"
    ws["F4"] = "Weight"
    ws["G4"] = "Weekly Δ"
    style_header_row(ws, 4, 5, 7)

    for row in range(5, 105):
        ws.cell(row=row, column=5).border = THIN_BORDER
        ws.cell(row=row, column=6).border = THIN_BORDER
        ws.cell(row=row, column=7).border = THIN_BORDER
        ws.cell(row=row, column=6).number_format = "0.0"
        ws.cell(row=row, column=7, value=f"=IF(F{row}=\"\",\"\",IFERROR(F{row-1}-F{row},\"\"))")
        ws.cell(row=row, column=7).number_format = "+0.0;-0.0;0"

    stripe_data_rows(ws, 5, 104, 5, 7)

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
    ws.column_dimensions["G"].width = 12


def build_instructions(wb: Workbook) -> None:
    ws = wb.create_sheet("Instructions")
    configure_sheet(ws)
    style_title(ws, "B2", "How To Use")

    instructions = [
        "1) Enter starting and current weight in the Progress sheet (cells C5 and C6).",
        "2) Customize the Workout Plan tab based on your weekly schedule.",
        "3) Log each day in Workout Log: date, completion status, notes, energy, and duration.",
        "4) Check Dashboard for completion rate, recent training, and average energy.",
        "5) Update this workbook weekly and duplicate monthly for archived progress.",
    ]

    for idx, text in enumerate(instructions, start=4):
        ws.cell(row=idx, column=2, value=text)
        ws.cell(row=idx, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=idx, column=2).border = THIN_BORDER
        if idx % 2 == 0:
            ws.cell(row=idx, column=2).fill = PatternFill(fill_type="solid", fgColor=LIGHT_BG)

    ws.column_dimensions["B"].width = 100


def create_workbook(output_path: str) -> None:
    wb = Workbook()
    build_dashboard(wb)
    build_workout_plan(wb)
    build_workout_log(wb)
    build_progress(wb)
    build_instructions(wb)
    wb.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a polished workout workbook.")
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
