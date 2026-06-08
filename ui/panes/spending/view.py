"""
Spending View - Pure UI display with chart
Emits chart_clicked signal when the user clicks anywhere on the chart.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import Qt, Signal


class SpendingView(QWidget):
    """View: Pure UI for displaying spending pie chart"""

    chart_clicked = Signal()  # Emitted when user clicks the chart

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.chart_view = ClickableChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.clicked.connect(self.chart_clicked.emit)
        layout.addWidget(self.chart_view)

    def display_spending(self, spending_data):
        """
        Display spending as pie chart.
        spending_data: list of dicts with category, amount, color
        """
        if spending_data:
            series = QPieSeries()
            for item in spending_data:
                slc = series.append(
                    f"{item['category']}\n${item['amount']:.2f}",
                    item['amount']
                )
                slc.setColor(QColor(item['color']))
                slc.setLabelVisible(True)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Spending by Category  •  Click for details")
            chart.legend().setVisible(False)
            chart.setAnimationOptions(QChart.SeriesAnimations)
        else:
            chart = QChart()
            chart.setTitle("No spending data for this month")

        self._apply_chart_theme(chart)
        self.chart_view.setChart(chart)

    def _apply_chart_theme(self, chart):
        if self.dark_mode:
            chart.setBackgroundBrush(QColor("#2D2D2D"))
            chart.setTitleBrush(QColor("#E0E0E0"))
        else:
            chart.setBackgroundBrush(QColor("white"))
            chart.setTitleBrush(QColor("#2C3E50"))

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        if self.chart_view.chart():
            self._apply_chart_theme(self.chart_view.chart())


class ClickableChartView(QChartView):
    """QChartView subclass that emits a signal on mouse press."""

    clicked = Signal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()