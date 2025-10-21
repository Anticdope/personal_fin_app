"""
Dashboard Model - Handles pane state management
"""

class DashboardModel:
    """Model: Manages dashboard pane state"""
    
    def __init__(self):
        self.top_panes = []
        self.bottom_panes = []
        self.current_top_index = 0
        self.current_bottom_index = 0
        self.current_year = None
        self.current_month = None
    
    def set_panes(self, top_panes, bottom_panes):
        """Set the list of available panes"""
        self.top_panes = top_panes
        self.bottom_panes = bottom_panes
    
    def get_top_pane(self):
        """Get current top pane"""
        if 0 <= self.current_top_index < len(self.top_panes):
            return self.top_panes[self.current_top_index]
        return None
    
    def get_bottom_pane(self):
        """Get current bottom pane"""
        if 0 <= self.current_bottom_index < len(self.bottom_panes):
            return self.bottom_panes[self.current_bottom_index]
        return None
    
    def can_go_prev_top(self):
        """Check if can navigate to previous top pane"""
        return self.current_top_index > 0
    
    def can_go_next_top(self):
        """Check if can navigate to next top pane"""
        return self.current_top_index < len(self.top_panes) - 1
    
    def can_go_prev_bottom(self):
        """Check if can navigate to previous bottom pane"""
        return self.current_bottom_index > 0
    
    def can_go_next_bottom(self):
        """Check if can navigate to next bottom pane"""
        return self.current_bottom_index < len(self.bottom_panes) - 1
    
    def go_prev_top(self):
        """Navigate to previous top pane"""
        if self.can_go_prev_top():
            self.current_top_index -= 1
            return True
        return False
    
    def go_next_top(self):
        """Navigate to next top pane"""
        if self.can_go_next_top():
            self.current_top_index += 1
            return True
        return False
    
    def go_prev_bottom(self):
        """Navigate to previous bottom pane"""
        if self.can_go_prev_bottom():
            self.current_bottom_index -= 1
            return True
        return False
    
    def go_next_bottom(self):
        """Navigate to next bottom pane"""
        if self.can_go_next_bottom():
            self.current_bottom_index += 1
            return True
        return False
    
    def get_pane_name(self, pane):
        """Get display name for a pane"""
        if hasattr(pane, 'get_pane_name'):
            return pane.get_pane_name()
        return "Pane"
    
    def set_current_period(self, year, month):
        """Set the current year/month being displayed"""
        self.current_year = year
        self.current_month = month