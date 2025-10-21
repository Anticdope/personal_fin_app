"""
Spending View - Pure UI display with chart
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import Qt


class SpendingView(QWidget):
    """View: Pure UI for displaying spending pie chart"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create chart view
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
    
    def display_spending(self, spending_data):
        """
        Display spending as pie chart
        spending_data: list of dicts with category, amount, color
        """
        # Create chart
        if spending_data and len(spending_data) > 0:
            # Has data - create pie chart
            series = QPieSeries()
            
            for item in spending_data:
                slice = series.append(
                    f"{item['category']}\n${item['amount']:.2f}", 
                    item['amount']
                )
                slice.setColor(QColor(item['color']))
                slice.setLabelVisible(True)
            
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Spending by Category")
            chart.legend().setVisible(False)
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Apply theme colors
            self._apply_chart_theme(chart)
            
            self.chart_view.setChart(chart)
        else:
            # No data - show empty chart
            chart = QChart()
            chart.setTitle("No spending data for this month")
            
            # Apply theme colors
            self._apply_chart_theme(chart)
            
            self.chart_view.setChart(chart)
    
    def _apply_chart_theme(self, chart):
        """Apply theme colors to chart"""
        if self.dark_mode:
            chart.setBackgroundBrush(QColor("#2D2D2D"))
            chart.setTitleBrush(QColor("#E0E0E0"))
        else:
            chart.setBackgroundBrush(QColor("white"))
            chart.setTitleBrush(QColor("#2C3E50"))
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode
        
        # Re-apply theme to existing chart if available
        if self.chart_view.chart():
            self._apply_chart_theme(self.chart_view.chart())