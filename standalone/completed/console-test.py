import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QComboBox, QPushButton
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt5.QtCore import Qt
import logging

class TestConsoleLogWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Console Log")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.level_selector = QComboBox()
        self.level_selector.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_selector.setCurrentText("INFO")
        self.level_selector.currentTextChanged.connect(self.apply_filter)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        self.add_log_button = QPushButton("Add Log Entry")
        self.add_log_button.clicked.connect(self.add_test_log)

        layout.addWidget(self.level_selector)
        layout.addWidget(self.log_display)
        layout.addWidget(self.add_log_button)

        self.setLayout(layout)

        self.full_log = []
        
        # Add some initial log entries
        self.add_test_log("DEBUG", "Initial DEBUG message")
        self.add_test_log("INFO", "Initial INFO message")
        self.add_test_log("WARNING", "Initial WARNING message")
        self.add_test_log("ERROR", "Initial ERROR message")
        self.add_test_log("CRITICAL", "Initial CRITICAL message")

        self.apply_filter()

    def add_test_log(self, level=None, custom_message=None):
        if level is None:
            level = self.level_selector.currentText()
        message = custom_message or f"Test log message - {level}"
        self.full_log.append((message, level))
        self.apply_filter()

    def apply_filter(self):
        selected_level = self.level_selector.currentText()
        selected_level_num = self.get_level_num(selected_level)

        self.log_display.clear()
        for message, level in self.full_log:
            if self.get_level_num(level) >= selected_level_num:
                self.add_colored_text(message, level)

    def get_level_num(self, level_name):
        level_dict = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_dict.get(level_name, logging.INFO)

    def add_colored_text(self, text, level):
        color = self.get_color_for_level(level)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setFont(QFont("Courier"))
        self.log_display.moveCursor(QTextCursor.End)
        self.log_display.setCurrentCharFormat(fmt)
        self.log_display.insertPlainText(f"[{level}] {text}\n")
        self.log_display.moveCursor(QTextCursor.End)

    def get_color_for_level(self, level):
        colors = {
            "DEBUG": "#808080",
            "INFO": "#000000",
            "WARNING": "#FFA500",
            "ERROR": "#FF0000",
            "CRITICAL": "#8B0000"
        }
        return colors.get(level, "#000000")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestConsoleLogWindow()
    window.show()
    sys.exit(app.exec_())