import flet as ft
import datetime
import calendar
from collections import defaultdict

# Simple in-memory storage for entries
entries = []


def main(page):
    page.title = "記帳 App"

    # --- Controls ---
    # Use Year/Month/Day dropdowns because DatePicker may not be selectable in some environments
    today = datetime.date.today()
    years = [today.year - 2, today.year - 1, today.year, today.year + 1]
    year_dd = ft.Dropdown(label="年", width=100, options=[ft.dropdown.Option(str(y)) for y in years], value=str(today.year))
    month_dd = ft.Dropdown(label="月", width=100, options=[ft.dropdown.Option(str(m)) for m in range(1, 13)], value=str(today.month))
    # day options depend on month/year
    def build_days(y, m):
        _, ndays = calendar.monthrange(y, m)
        return [ft.dropdown.Option(str(d)) for d in range(1, ndays + 1)]

    day_dd = ft.Dropdown(label="日", width=100, options=build_days(today.year, today.month), value=str(today.day))

    def get_selected_date():
        try:
            y = int(year_dd.value)
            m = int(month_dd.value)
            d = int(day_dd.value)
            return datetime.date(y, m, d)
        except Exception:
            return today

    # update day options when year or month change
    def _on_year_month_change(e=None):
        try:
            y = int(year_dd.value)
            m = int(month_dd.value)
            day_dd.options = build_days(y, m)
            # ensure current day value is valid
            if int(day_dd.value) > len(day_dd.options):
                day_dd.value = day_dd.options[-1].value
        except Exception:
            pass
        page.update()

    year_dd.on_change = _on_year_month_change
    month_dd.on_change = _on_year_month_change

    category_dd = ft.Dropdown(
        label="類別",
        width=200,
        options=[
            ft.dropdown.Option("食物"),
            ft.dropdown.Option("交通"),
            ft.dropdown.Option("娛樂"),
            ft.dropdown.Option("購物"),
            ft.dropdown.Option("其他"),
        ],
        value="食物",
    )

    payment_dd = ft.Dropdown(
        label="付款方式",
        width=200,
        options=[
            ft.dropdown.Option("現金"),
            ft.dropdown.Option("信用卡"),
            ft.dropdown.Option("行動支付"),
            ft.dropdown.Option("轉帳"),
        ],
        value="現金",
    )

    amount_tf = ft.TextField(label="支出金額", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    note_tf = ft.TextField(label="備註", width=400)

    save_btn = ft.ElevatedButton("儲存")

    # --- Stats displays ---
    totals_text = ft.Text("今日/本月/今年 總花費：0 / 0 / 0")
    category_column = ft.Column()

    # --- Pie chart placeholder ---
    # Using ft.Chart if available in this Flet version. If not available it will be replaced by a simple legend.
    try:
        pie_chart = ft.Chart(width=300, height=300, chart_type=ft.ChartType.PIE, data=[])
    except Exception:
        pie_chart = ft.Container(content=ft.Text("無法顯示圖表（Chart 不支援）"))

    # --- Entries table (details) ---
    entries_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("日期")),
        ft.DataColumn(ft.Text("類別")),
        ft.DataColumn(ft.Text("付款方式")),
        ft.DataColumn(ft.Text("金額")),
        ft.DataColumn(ft.Text("備註")),
    ], rows=[])

    # --- Helper functions ---
    def update_stats():
        today = get_selected_date()
        daily = monthly = yearly = 0.0
        per_cat = defaultdict(float)

        for e in entries:
            amt = e.get("amount", 0.0)
            d = e.get("date")
            # totals relative to the selected date in the date picker
            if d == today:
                daily += amt
            if d.year == today.year and d.month == today.month:
                monthly += amt
            if d.year == today.year:
                yearly += amt
            per_cat[e.get("category", "其他")] += amt

        totals_text.value = f"今日/本月/今年 總花費：{daily:.2f} / {monthly:.2f} / {yearly:.2f}"

        # update category breakdown list
        category_column.controls.clear()
        for cat, v in sorted(per_cat.items(), key=lambda x: -x[1]):
            category_column.controls.append(ft.Row([
                ft.Container(width=12, height=12, bgcolor=_category_color(cat)),
                ft.Text(f" {cat}: {v:.2f}")
            ], alignment=ft.MainAxisAlignment.START))

        # update entries table (sorted by date desc)
        try:
            rows = []
            for e in sorted(entries, key=lambda x: (x.get("date"),), reverse=True):
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(e.get("date").strftime("%Y-%m-%d"))),
                    ft.DataCell(ft.Text(e.get("category"))),
                    ft.DataCell(ft.Text(e.get("payment"))),
                    ft.DataCell(ft.Text(f"{e.get('amount'):.2f}")),
                    ft.DataCell(ft.Text(e.get("note")))
                ]))
            entries_table.rows = rows
        except Exception:
            pass

        # update pie chart data if supported
        try:
            if isinstance(pie_chart, ft.Chart):
                chart_data = []
                for cat, v in per_cat.items():
                    chart_data.append(ft.ChartData(label=cat, value=v))
                pie_chart.data = chart_data
        except Exception:
            pass

        page.update()

    def _category_color(cat):
        # simple deterministic colors for categories (return hex string; flet accepts color strings)
        mapping = {
            "食物": "#FF6384",
            "交通": "#36A2EB",
            "娛樂": "#FFCE56",
            "購物": "#8BC34A",
            "其他": "#9E9E9E",
        }
        return mapping.get(cat, "#CCCCCC")

    # --- Save handler ---
    def on_save(e):
        try:
            amount = float(amount_tf.value or 0)
        except Exception:
            amount = 0.0

        entry = {
            "date": get_selected_date(),
            "category": category_dd.value or "其他",
            "payment": payment_dd.value or "現金",
            "amount": amount,
            "note": note_tf.value or "",
        }
        entries.append(entry)

        # clear inputs
        amount_tf.value = ""
        note_tf.value = ""
        amount_tf.focus()

        update_stats()

    save_btn.on_click = on_save

    # Layout
    input_card = ft.Card(content=ft.Container(padding=10, content=ft.Column([
        ft.Row([ft.Column([ft.Text("日期"), ft.Row([year_dd, month_dd, day_dd])]), category_dd, payment_dd], alignment=ft.MainAxisAlignment.START),
        ft.Row([amount_tf, save_btn], alignment=ft.MainAxisAlignment.START),
        note_tf,
    ])))

    stats_card = ft.Card(content=ft.Container(padding=10, content=ft.Column([
        totals_text,
        ft.Text("各類別花費："),
        category_column,
    ])))

    chart_card = ft.Card(content=ft.Container(padding=10, content=ft.Column([
        ft.Text("花費細項圓餅圖："),
        pie_chart,
    ])))

    table_card = ft.Card(content=ft.Container(padding=10, content=ft.Column([
        ft.Text("明細（依日期排序）："),
        entries_table,
    ])))

    # place input and stats side-by-side (horizontally scrollable); put chart next, and entries table at the bottom
    top_row = ft.Row([input_card, stats_card], spacing=10, scroll=ft.ScrollMode.AUTO)

    page.add(
        ft.Column(
            [
                top_row,
                chart_card,
                table_card,  # move the detailed entries table to the bottom to avoid horizontal overflow
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )
    )

    # initial update
    update_stats()


ft.app(target=main, view=ft.AppView.WEB_BROWSER)  # 直接在瀏覽器跑起來