"""
Calendar Model - Handles date logic and data access
"""
from PySide6.QtCore import QDate


class CalendarModel:
    """Model: Business logic for calendar display"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_date = QDate.currentDate()
    
    def get_current_month_data(self):
        """
        Get all data needed to display current month
        Returns dict with month info and day data
        """
        year = self.current_date.year()
        month = self.current_date.month()
        
        # Get month metadata
        first_day = QDate(year, month, 1)
        days_in_month = self.current_date.daysInMonth()
        start_col = first_day.dayOfWeek() - 1  # 0 = Monday
        
        # Get transaction totals for each day
        day_data = []
        today = QDate.currentDate()
        
        for day in range(1, days_in_month + 1):
            date = QDate(year, month, day)
            totals = self.data_manager.get_day_totals_separate(date)
            is_today = (date == today)
            
            day_data.append({
                'day_number': day,
                'date': date,
                'totals': totals,
                'is_today': is_today,
                'row': (day + start_col - 1) // 7 + 1,
                'col': (day + start_col - 1) % 7
            })
        
        return {
            'month_label': self.current_date.toString('MMMM yyyy'),
            'year': year,
            'month': month,
            'days': day_data
        }
    
    def navigate_to_previous_month(self):
        """Move to previous month"""
        self.current_date = self.current_date.addMonths(-1)
    
    def navigate_to_next_month(self):
        """Move to next month"""
        self.current_date = self.current_date.addMonths(1)
    
    def get_current_date(self):
        """Get current QDate"""
        return self.current_date