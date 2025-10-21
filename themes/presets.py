"""
Theme Presets - Different visual styles for the application
"""

THEME_PRESETS = {
    "Light (Default)": """
/* Light Theme - Default */
QWidget {
    background-color: #F5F5F5;
    color: #212121;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 10px;
    margin: 5px;
}

#cardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 15px;
    margin: 5px;
}

#paneLabel {
    font-size: 18px;
    font-weight: bold;
    color: #1976D2;
}

QPushButton#primaryButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #1565C0;
}
""",

    "Dark (Default)": """
/* Dark Theme - Default */
QWidget {
    background-color: #212121;
    color: #E0E0E0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #2C2C2C;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 10px;
    margin: 5px;
}

#cardFrame {
    background-color: #2C2C2C;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 15px;
    margin: 5px;
}

#paneLabel {
    font-size: 18px;
    font-weight: bold;
    color: #64B5F6;
}

QPushButton#primaryButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #2196F3;
}
""",

    "Card Style - Light": """
/* Card Style - Light with elevated shadows */
QWidget {
    background-color: #FAFAFA;
    color: #212121;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
}

#cardFrame {
    background-color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 20px;
    margin: 8px;
}

#paneLabel {
    font-size: 20px;
    font-weight: bold;
    color: #1976D2;
    padding: 5px;
}

QPushButton#primaryButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #1565C0;
}

QPushButton#navButton {
    background-color: #FFFFFF;
    color: #1976D2;
    border: 2px solid #1976D2;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #E3F2FD;
}
""",

    "Card Style - Dark": """
/* Card Style - Dark with elevated cards */
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #1E1E1E;
    border: none;
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
}

#cardFrame {
    background-color: #1E1E1E;
    border: none;
    border-radius: 12px;
    padding: 20px;
    margin: 8px;
}

#paneLabel {
    font-size: 20px;
    font-weight: bold;
    color: #64B5F6;
    padding: 5px;
}

QPushButton#primaryButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #2196F3;
}

QPushButton#navButton {
    background-color: #1E1E1E;
    color: #64B5F6;
    border: 2px solid #64B5F6;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #263238;
}
""",

    "Panel Style - Light": """
/* Panel Style - Light with clear borders */
QWidget {
    background-color: #ECEFF1;
    color: #263238;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #FFFFFF;
    border: 2px solid #90A4AE;
    border-radius: 6px;
    padding: 15px;
    margin: 8px;
}

#cardFrame {
    background-color: #F5F7FA;
    border: 2px solid #CFD8DC;
    border-radius: 6px;
    padding: 15px;
    margin: 8px;
}

#paneLabel {
    font-size: 18px;
    font-weight: bold;
    color: #455A64;
    background-color: #CFD8DC;
    padding: 8px;
    border-radius: 4px;
}

QPushButton#primaryButton {
    background-color: #546E7A;
    color: white;
    border: 2px solid #455A64;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #455A64;
}

QPushButton#navButton {
    background-color: #FFFFFF;
    color: #546E7A;
    border: 2px solid #90A4AE;
    border-radius: 4px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #ECEFF1;
    border: 2px solid #546E7A;
}
""",

    "Panel Style - Dark": """
/* Panel Style - Dark with clear borders */
QWidget {
    background-color: #263238;
    color: #ECEFF1;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #37474F;
    border: 2px solid #546E7A;
    border-radius: 6px;
    padding: 15px;
    margin: 8px;
}

#cardFrame {
    background-color: #37474F;
    border: 2px solid #546E7A;
    border-radius: 6px;
    padding: 15px;
    margin: 8px;
}

#paneLabel {
    font-size: 18px;
    font-weight: bold;
    color: #CFD8DC;
    background-color: #455A64;
    padding: 8px;
    border-radius: 4px;
}

QPushButton#primaryButton {
    background-color: #546E7A;
    color: white;
    border: 2px solid #78909C;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #607D8B;
}

QPushButton#navButton {
    background-color: #37474F;
    color: #CFD8DC;
    border: 2px solid #78909C;
    border-radius: 4px;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #455A64;
    border: 2px solid #90A4AE;
}
""",

    "Material Style - Light": """
/* Material Style - Light with soft shadows */
QWidget {
    background-color: #FAFAFA;
    color: #212121;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 16px;
    margin: 8px;
}

#cardFrame {
    background-color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 16px;
    margin: 6px;
}

#paneLabel {
    font-size: 18px;
    font-weight: 500;
    color: #1976D2;
    padding: 4px;
}

QPushButton#primaryButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: 500;
    text-transform: uppercase;
}

QPushButton#primaryButton:hover {
    background-color: #1976D2;
}

QPushButton#navButton {
    background-color: transparent;
    color: #2196F3;
    border: none;
    border-radius: 50%;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #E3F2FD;
}

QLineEdit#formInput {
    background-color: transparent;
    border: none;
    border-bottom: 2px solid #BDBDBD;
    border-radius: 0px;
    padding: 8px 4px;
}

QLineEdit#formInput:focus {
    border-bottom: 2px solid #2196F3;
}
""",

    "Material Style - Dark": """
/* Material Style - Dark with soft shadows */
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

#paneSection {
    background-color: #1E1E1E;
    border: none;
    border-radius: 8px;
    padding: 16px;
    margin: 8px;
}

#cardFrame {
    background-color: #2C2C2C;
    border: none;
    border-radius: 8px;
    padding: 16px;
    margin: 6px;
}

#paneLabel {
    font-size: 18px;
    font-weight: 500;
    color: #64B5F6;
    padding: 4px;
}

QPushButton#primaryButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: 500;
    text-transform: uppercase;
}

QPushButton#primaryButton:hover {
    background-color: #42A5F5;
}

QPushButton#navButton {
    background-color: transparent;
    color: #64B5F6;
    border: none;
    border-radius: 50%;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#navButton:hover {
    background-color: #263238;
}

QLineEdit#formInput {
    background-color: transparent;
    border: none;
    border-bottom: 2px solid #616161;
    border-radius: 0px;
    padding: 8px 4px;
    color: #E0E0E0;
}

QLineEdit#formInput:focus {
    border-bottom: 2px solid #2196F3;
}
"""
}