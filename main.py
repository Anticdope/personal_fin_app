import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from main_window import MainWindow
from themes.theme_manager import ThemeManager  # ADD THIS


def main():
    app = QApplication(sys.argv)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Initialize theme manager and load default theme
    theme_manager = ThemeManager()
    theme_manager.load_theme("light")
    
    # Create main window and pass theme manager
    window = MainWindow(theme_manager)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()