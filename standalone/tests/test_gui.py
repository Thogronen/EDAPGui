import unittest
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeyEvent
from test_base import GUITestCase, MinimalKeyboardGUI  # Import from test_base, not EDKeys


class TestKeyboardGUI(GUITestCase):
    """Test GUI functionality"""

    def test_binding_mode(self):
        """Test binding mode toggle functionality"""
        # Initial state
        self.assertFalse(self.gui.binding_mode)
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: Off")

        # Toggle on
        self.gui.binding_toggle.click()
        self.process_events()
        self.assertTrue(self.gui.binding_mode)
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: On")

        # Toggle off
        self.gui.binding_toggle.click()
        self.process_events()
        self.assertFalse(self.gui.binding_mode)
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: Off")

    def test_key_press_handling(self):
        """Test key press event handling"""
        # Simulate key press
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier)
        self.gui.keyPressEvent(event)
        self.process_events()
        self.assertIn("Key_A", self.gui.active_keys)

    def test_key_release_handling(self):
        """Test key release handling"""
        # First press
        event_press = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier)
        self.gui.keyPressEvent(event_press)
        self.process_events()

        # Then release
        event_release = QKeyEvent(QEvent.KeyRelease, Qt.Key_A, Qt.NoModifier)
        self.gui.keyReleaseEvent(event_release)
        self.process_events()
        self.assertNotIn("Key_A", self.gui.active_keys)