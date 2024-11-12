import unittest
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication
from test_base import GUITestCase
from EDKeys import ConsoleLogWindow


class TestConsoleLogging(GUITestCase):
    """Test console logging functionality"""

    def setUp(self):
        super().setUp()
        self.console = ConsoleLogWindow(self.gui)
        self.console.level_selector.setCurrentText("TRACE")  # Show all levels

    def test_log_levels(self):
        """Test different log levels appear in log output"""
        self.console.log_display.clear()

        test_messages = {
            "TRACE": "Test trace message",
            "DEBUG": "Test debug message",
            "INFO": "Test info message",
            "WARNING": "Test warning message",
            "ERROR": "Test error message"
        }

        for level, message in test_messages.items():
            self.console.log_signal.emit(message, level)
            self.process_events()

        log_content = self.console.log_display.toPlainText()
        for level, message in test_messages.items():
            self.assertIn(message, log_content, f"Message for level {level} not found")

    def test_level_filtering(self):
        """Test log level filtering"""
        self.console.level_selector.setCurrentText("WARNING")
        self.process_events()

        # Send messages of different levels
        self.console.log_signal.emit("Debug message", "DEBUG")
        self.console.log_signal.emit("Warning message", "WARNING")
        self.process_events()

        log_content = self.console.log_display.toPlainText()
        self.assertNotIn("Debug message", log_content)
        self.assertIn("Warning message", log_content)