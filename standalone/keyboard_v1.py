import xml.etree.ElementTree as ET
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QEvent, QSize
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

# Simplified SCANCODE dictionary
SCANCODE = {
    # Function Keys
    'DIK_F1': 0x3B, 'DIK_F2': 0x3C, 'DIK_F3': 0x3D, 'DIK_F4': 0x3E,
    'DIK_F5': 0x3F, 'DIK_F6': 0x40, 'DIK_F7': 0x41, 'DIK_F8': 0x42,
    'DIK_F9': 0x43, 'DIK_F10': 0x44, 'DIK_F11': 0x57, 'DIK_F12': 0x58,
    'DIK_F13': 0x64, 'DIK_F14': 0x65, 'DIK_F15': 0x66,

    # Numeric Keys
    'DIK_0': 0x0B, 'DIK_1': 0x02, 'DIK_2': 0x03, 'DIK_3': 0x04, 'DIK_4': 0x05,
    'DIK_5': 0x06, 'DIK_6': 0x07, 'DIK_7': 0x08, 'DIK_8': 0x09, 'DIK_9': 0x0A,

    # Numpad Keys
    'DIK_NUMPAD0': 0x52, 'DIK_NUMPAD1': 0x4F, 'DIK_NUMPAD2': 0x50, 'DIK_NUMPAD3': 0x51,
    'DIK_NUMPAD4': 0x4B, 'DIK_NUMPAD5': 0x4C, 'DIK_NUMPAD6': 0x4D, 'DIK_NUMPAD7': 0x47,
    'DIK_NUMPAD8': 0x48, 'DIK_NUMPAD9': 0x49,

    # Alphabet Keys
    'DIK_A': 0x1E, 'DIK_B': 0x30, 'DIK_C': 0x2E, 'DIK_D': 0x20, 'DIK_E': 0x12,
    'DIK_F': 0x21, 'DIK_G': 0x22, 'DIK_H': 0x23, 'DIK_I': 0x17, 'DIK_J': 0x24,
    'DIK_K': 0x25, 'DIK_L': 0x26, 'DIK_M': 0x32, 'DIK_N': 0x31, 'DIK_O': 0x18,
    'DIK_P': 0x19, 'DIK_Q': 0x10, 'DIK_R': 0x13, 'DIK_S': 0x1F, 'DIK_T': 0x14,
    'DIK_U': 0x16, 'DIK_V': 0x2F, 'DIK_W': 0x11, 'DIK_X': 0x2D, 'DIK_Y': 0x15,
    'DIK_Z': 0x2C,

    # Control Keys
    'DIK_ESCAPE': 0x01, 'DIK_TAB': 0x0F, 'DIK_LSHIFT': 0x2A, 'DIK_RSHIFT': 0x36,
    'DIK_LCONTROL': 0x1D, 'DIK_RCONTROL': 0x9D, 'DIK_BACK': 0x0E, 'DIK_BACKSPACE': 0x0E,
    'DIK_RETURN': 0x1C, 'DIK_NUMPADENTER': 0x9C, 'DIK_LMENU': 0x38, 'DIK_LALT': 0x38,
    'DIK_SPACE': 0x39, 'DIK_CAPITAL': 0x3A, 'DIK_CAPSLOCK': 0x3A, 'DIK_NUMLOCK': 0x45,
    'DIK_SCROLL': 0x46, 'DIK_RMENU': 0xB8, 'DIK_RALT': 0xB8,

    # Symbol Keys
    'DIK_MINUS': 0x0C, 'DIK_EQUALS': 0x0D, 'DIK_LBRACKET': 0x1A, 'DIK_RBRACKET': 0x1B,
    'DIK_SEMICOLON': 0x27, 'DIK_APOSTROPHE': 0x28, 'DIK_TILDE': 0x29, 'DIK_BACKSLASH': 0x2B,
    'DIK_COMMA': 0x33, 'DIK_PERIOD': 0x34, 'DIK_SLASH': 0x35, 'DIK_MULTIPLY': 0x37,
    'DIK_NUMPADSTAR': 0x37, 'DIK_SUBTRACT': 0x4A, 'DIK_ADD': 0x4E, 'DIK_DECIMAL': 0x53,
    'DIK_NUMPADEQUALS': 0x8D, 'DIK_NUMPADMINUS': 0x4A, 'DIK_NUMPADPLUS': 0x4E,
    'DIK_NUMPADPERIOD': 0x53, 'DIK_NUMPADSLASH': 0xB5,

    # KataKana Keys
    'DIK_KANA': 0x70, 'DIK_ABNT_C1': 0x73, 'DIK_CONVERT': 0x79, 'DIK_NOCONVERT': 0x7B,
    'DIK_YEN': 0x7D, 'DIK_OEM_102': 0x56, 'DIK_ABNT_C2': 0x7E, 'DIK_PREVTRACK': 0x90,
    'DIK_KANJI': 0x94, 'DIK_STOP': 0x95, 'DIK_AX': 0x96, 'DIK_UNLABELED': 0x97,
    'DIK_NUMPADCOMMA': 0xB3, 'DIK_CIRCUMFLEX': 0x90,

    # App Keys
    'DIK_NEXTTRACK': 0x99, 'DIK_MUTE': 0xA0, 'DIK_CALCULATOR': 0xA1, 'DIK_PLAYPAUSE': 0xA2,
    'DIK_MEDIASTOP': 0xA4, 'DIK_VOLUMEDOWN': 0xAE, 'DIK_VOLUMEUP': 0xB0, 'DIK_WEBHOME': 0xB2,
    'DIK_SYSRQ': 0xB7, 'DIK_PAUSE': 0xC5, 'DIK_APPS': 0xDD, 'DIK_POWER': 0xDE,
    'DIK_SLEEP': 0xDF, 'DIK_WAKE': 0xE3, 'DIK_WEBSEARCH': 0xE5, 'DIK_WEBFAVORITES': 0xE6,
    'DIK_WEBREFRESH': 0xE7, 'DIK_WEBSTOP': 0xE8, 'DIK_WEBFORWARD': 0xE9, 'DIK_WEBBACK': 0xEA,
    'DIK_MYCOMPUTER': 0xEB, 'DIK_MAIL': 0xEC, 'DIK_MEDIASELECT': 0xED,

    # Arrow Keypad
    'DIK_HOME': 0xC7, 'DIK_UP': 0xC8, 'DIK_PRIOR': 0xC9, 'DIK_LEFT': 0xCB,
    'DIK_RIGHT': 0xCD, 'DIK_END': 0xCF, 'DIK_DOWN': 0xD0, 'DIK_NEXT': 0xD1,
    'DIK_INSERT': 0xD2, 'DIK_DELETE': 0xD3, 'DIK_UPARROW': 0xC8, 'DIK_PGUP': 0xC9,
    'DIK_LEFTARROW': 0xCB, 'DIK_RIGHTARROW': 0xCD, 'DIK_DOWNARROW': 0xD0, 'DIK_PGDN': 0xD1,

    # Other Keys
    'DIK_LWIN': 0xDB, 'DIK_RWIN': 0xDC,

    # Additional keys
    'DIK_AT': 0x91, 'DIK_COLON': 0x92, 'DIK_UNDERLINE': 0x93,
    'DIK_DIVIDE': 0xB5,
}

class EDKeys:
    def __init__(self, binds_file):
        self.binds_file = binds_file
        self.bindings = self.parse_binds_file()

    def parse_binds_file(self):
        bindings = {}
        tree = ET.parse(self.binds_file)
        root = tree.getroot()

        for element in root:
            action = element.tag
            primary = element.find('Primary')
            if primary is not None and 'Key' in primary.attrib:
                key = primary.attrib['Key']
                normalized_key = self.normalize_key(key)
                scancode = self.get_scancode_for_key(normalized_key)
                bindings[action] = scancode

        return bindings

    @staticmethod
    def normalize_key(key):
        key = key.upper().replace('KEY_', '')  # Normalize each SCANCODE
        if key.startswith('NUM_KEY_'):
            return f"NUM{key[-1]}"  # This converts "NUM_KEY_8" to "NUM8"
        return key

    def get_scancode_for_key(self, key):
        normalized_key = self.normalize_key(key)  # Normalize the key
        return SCANCODE.get(f'DIK_{normalized_key.upper()}')  # Look up in SCANCODE

    def get_bound_actions(self, scancode):
        return [action for action, bound_scancode in self.bindings.items() if bound_scancode == scancode]


class KeyboardGUI(QMainWindow):
    def __init__(self, ed_keys):
        super().__init__()
        self.ed_keys = ed_keys
        self.key_buttons = {}  # Store references to key buttons
        self.key_states = {}  # Track the state of all keys
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.initUI()
        self.initialize_key_states()

    def initUI(self):
        self.setWindowTitle('ED Key Bindings')
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        keyboard_layout = QGridLayout()
        layout.addLayout(keyboard_layout)

        # Main keyboard layout
        keys = [
            ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'ENTER'],
            ['LSHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'RSHIFT'],
            ['LCTRL', 'LWIN', 'LALT', 'SPACE', 'RALT', 'RWIN', 'MENU', 'RCTRL']
        ]

        # Add the main keyboard keys
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                button = self.create_key_button(key)
                keyboard_layout.addWidget(button, row, col)
                self.key_buttons[key] = button

        # Add NUMPAD keys
        numpad_keys = [
            ['NUM 7', 'NUM 8', 'NUM 9'],
            ['NUM 4', 'NUM 5', 'NUM 6'],
            ['NUM 1', 'NUM 2', 'NUM 3'],
            ['NUM 0', 'NUM .', 'NUM ENTER']
        ]
        for row, key_row in enumerate(numpad_keys):
            for col, key in enumerate(key_row):
                button = self.create_key_button(key)
                keyboard_layout.addWidget(button, row + 1, col + 15)
                self.key_buttons[key] = button

        # Add navigation keys
        nav_keys = [
            ['INS', 'HOME', 'PGUP'],
            ['DEL', 'END', 'PGDN'],
            ['', 'UP', ''],
            ['LEFT', 'DOWN', 'RIGHT']
        ]
        for row, key_row in enumerate(nav_keys):
            for col, key in enumerate(key_row):
                if key:
                    button = self.create_key_button(key)
                    keyboard_layout.addWidget(button, row + 1, col + 12)
                    self.key_buttons[key] = button

    def initialize_key_states(self):
        for key in self.key_buttons.keys():
            self.key_states[key] = False
            
    def nativeEvent(self, eventType, message):
        msg = wintypes.MSG.from_address(message.__int__())
        if msg.message == WM_KEYDOWN or msg.message == WM_KEYUP:
            key = None
            if msg.wParam == VK_OEM_3:  # Backtick
                key = '`'
            elif msg.wParam == VK_OEM_7:  # Single quote
                key = "'"
            elif msg.wParam == 0x5B:  # Left Windows key
                key = 'LWIN'
            elif msg.wParam == 0x5C:  # Right Windows key
                key = 'RWIN'
            elif msg.wParam == 0xA5:  # Right Alt key
                key = 'RALT'
            
            if key:
                self.handle_key_event(key, msg.message == WM_KEYDOWN)
                return True, 0
        return False, 0
    
    def create_key_button(self, key):
        button = QPushButton(key)
        button.setFixedSize(QSize(50, 50))
        return button
    
    def handle_key_event(self, key, pressed):
        if key in self.key_buttons:
            self.key_states[key] = pressed
            self.update_key_visual(key)

            if pressed:
                normalized_key = self.ed_keys.normalize_key(key)
                scancode = self.ed_keys.get_scancode_for_key(normalized_key)
                bound_actions = self.ed_keys.get_bound_actions(scancode)
                if bound_actions:
                    print(f"Bindings for {key}: {', '.join(bound_actions)}")
                else:
                    print(f"No bindings found for {key}")
                
    def update_modifier_visuals(self):
        for key, state in self.modifier_states.items():
            if key in self.key_buttons:
                button = self.key_buttons[key]
                button.setStyleSheet("background-color: green;" if state else "")
          
    def update_key_visual(self, key):
        if key in self.key_buttons:
            button = self.key_buttons[key]
            button.setStyleSheet("background-color: green;" if self.key_states[key] else "")
                  
    def get_key_name(self, event):
        key = event.key()
        scan_code = event.nativeScanCode()

        # Special handling for modifier keys
        if key == Qt.Key_Shift:
            return 'LSHIFT' if scan_code == 42 else 'RSHIFT'
        elif key == Qt.Key_Control:
            return 'LCTRL' if scan_code == 29 else 'RCTRL'
        elif key == Qt.Key_Alt:
            return 'LALT' if scan_code == 56 else 'RALT'
        elif key == Qt.Key_Meta:
            return 'LWIN' if scan_code == 91 else 'RWIN'

        # Handle number keys and numpad keys
        if Qt.Key_0 <= key <= Qt.Key_9:
            return f"NUM {key - Qt.Key_0}" if event.modifiers() & Qt.KeypadModifier else str(key - Qt.Key_0)

        # Handle function keys
        if Qt.Key_F1 <= key <= Qt.Key_F12:
            return f"F{key - Qt.Key_F1 + 1}"

        # Special handling for Enter keys
        if key == Qt.Key_Return:
            return 'ENTER'
        elif key == Qt.Key_Enter:
            return 'NUM ENTER'

        # Other special keys
        key_map = {
            Qt.Key_Space: 'SPACE',
            Qt.Key_Backspace: 'BACKSPACE',
            Qt.Key_Tab: 'TAB',
            Qt.Key_CapsLock: 'CAPS',
            Qt.Key_Escape: 'ESC',
            Qt.Key_Insert: 'INS',
            Qt.Key_Delete: 'DEL',
            Qt.Key_Home: 'HOME',
            Qt.Key_End: 'END',
            Qt.Key_PageUp: 'PGUP',
            Qt.Key_PageDown: 'PGDN',
            Qt.Key_Up: 'UP',
            Qt.Key_Down: 'DOWN',
            Qt.Key_Left: 'LEFT',
            Qt.Key_Right: 'RIGHT',
            Qt.Key_NumLock: 'NUMLOCK',
            Qt.Key_ScrollLock: 'SCROLL',
            Qt.Key_Semicolon: ';',
            Qt.Key_Comma: ',',
            Qt.Key_Period: '.',
            Qt.Key_Slash: '/',
            Qt.Key_BracketLeft: '[',
            Qt.Key_BracketRight: ']',
            Qt.Key_Backslash: '\\',
            Qt.Key_Minus: '-',
            Qt.Key_Equal: '=',
            Qt.Key_QuoteLeft: '`',
            Qt.Key_Apostrophe: "'"
        }

        return key_map.get(key, event.text().upper())

    def keyPressEvent(self, event):
        key = self.get_key_name(event)
        if key not in ['`', "'", 'LWIN', 'RWIN', 'RALT']:  # These are handled by nativeEvent
            self.handle_key_event(key, True)

    def keyReleaseEvent(self, event):
        key = self.get_key_name(event)
        if key not in ['`', "'", 'LWIN', 'RWIN', 'RALT']:  # These are handled by nativeEvent
            self.handle_key_event(key, False)
            
    def event(self, event):
        if event.type() == QEvent.KeyPress or event.type() == QEvent.KeyRelease:
            # Let Qt's event system handle it, which will call our keyPressEvent or keyReleaseEvent
            return super().event(event)
        return super().event(event)

def main():
    app = QApplication([])
    ed_keys = EDKeys('Main Custom.4.1.binds')  # Replace with your .binds file path
    ex = KeyboardGUI(ed_keys)
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()