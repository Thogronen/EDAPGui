import unittest
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget
from PyQt5.QtCore import Qt
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from EDKeys import KeyboardGUI  # Import the specific class we need

class MinimalKeyboardGUI(KeyboardGUI):
    """Minimal version of KeyboardGUI for testing"""

    def __init__(self, ed_keys, base_stylesheet, logger, log_handler, log_buffer):
        super().__init__(ed_keys, base_stylesheet, logger, log_handler, log_buffer)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add minimal tab widget with a single "All" tab
        self.tab_widget = QTabWidget()
        tab = QWidget()
        self.tab_widget.addTab(tab, "All")
        layout.addWidget(self.tab_widget)

        # Add binding toggle button
        self.binding_toggle = QPushButton("Binding Mode: Off")
        self.binding_toggle.setCheckable(True)
        self.binding_toggle.clicked.connect(self.toggle_binding_mode)
        layout.addWidget(self.binding_toggle)

        # Status bar for messages
        self.status_bar = self.statusBar()

    # Override methods that would create full UI
    def init_console_log_window(self): pass
    def initUI(self): pass
    def create_tabs(self): pass
    def update_all_keys(self): pass
    def run_verifications(self): pass

    def stop_global_key_logging(self):
        """Override to prevent actual key logging operations during tests"""
        if self.key_logger:
            self.key_logger = None
        self.currently_pressed_keys.clear()

class GUITestCase(unittest.TestCase):
    """Base class for GUI tests providing Qt setup and teardown."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication once for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up a fresh MinimalKeyboardGUI instance for each test."""
        self.ed_keys = Mock()
        self.ed_keys.get_bound_actions.return_value = []
        self.logger = Mock()
        self.log_buffer = Mock()
        self.log_buffer.flush_records = Mock(return_value=[])
        
        # Create minimal GUI instance
        self.gui = MinimalKeyboardGUI(
            self.ed_keys,
            "test-stylesheet",
            self.logger,
            Mock(),  # log_handler
            self.log_buffer
        )

    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'gui'):
            self.gui.close()
            self.gui = None
        QApplication.processEvents()

    def process_events(self):
        """Helper method to process Qt events."""
        QApplication.processEvents()