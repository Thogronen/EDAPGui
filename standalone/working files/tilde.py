import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeyEvent

# For Windows
import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32

# Windows key codes
VK_OEM_3 = 0xC0  # Backtick
VK_OEM_7 = 0xDE  # Single quote

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

class KeyTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Key Test')
        self.setGeometry(300, 300, 200, 150)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.backtick_button = QPushButton('`')
        self.single_quote_button = QPushButton("'")

        layout.addWidget(self.backtick_button)
        layout.addWidget(self.single_quote_button)

        self.setFocusPolicy(Qt.StrongFocus)

    def nativeEvent(self, eventType, message):
        msg = ctypes.wintypes.MSG.from_address(message.__int__())
        if msg.message == WM_KEYDOWN:
            if msg.wParam == VK_OEM_3:  # Backtick
                self.backtick_button.setStyleSheet("background-color: green;")
                print("Backtick pressed")
                return True, 0
            elif msg.wParam == VK_OEM_7:  # Single quote
                self.single_quote_button.setStyleSheet("background-color: green;")
                print("Single quote pressed")
                return True, 0
        elif msg.message == WM_KEYUP:
            if msg.wParam == VK_OEM_3:  # Backtick
                self.backtick_button.setStyleSheet("")
                print("Backtick released")
                return True, 0
            elif msg.wParam == VK_OEM_7:  # Single quote
                self.single_quote_button.setStyleSheet("")
                print("Single quote released")
                return True, 0
        return False, 0

    def keyPressEvent(self, event):
        # This is just for debugging, the actual handling is in nativeEvent
        print(f"Qt KeyPress - Key: {event.key()}, Text: {event.text()}")

    def keyReleaseEvent(self, event):
        # This is just for debugging, the actual handling is in nativeEvent
        print(f"Qt KeyRelease - Key: {event.key()}, Text: {event.text()}")

def main():
    app = QApplication(sys.argv)
    ex = KeyTestWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()