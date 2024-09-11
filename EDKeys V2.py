import os
import xml.etree.ElementTree as ET
from os.path import getmtime, isfile, join
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QGridLayout, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize

# SCANCODE dictionary (abbreviated for brevity)
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
    'DIK_SEMICOLON': 0x27, 'DIK_APOSTROPHE': 0x28, 'DIK_GRAVE': 0x29, 'DIK_BACKSLASH': 0x2B,
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
    
    'DIK_TAB': 0x0F,
    'DIK_CAPITAL': 0x3A,
    'DIK_LSHIFT': 0x2A,
    'DIK_RSHIFT': 0x36,
    'DIK_LCONTROL': 0x1D,
    'DIK_RCONTROL': 0x9D,
    'DIK_LMENU': 0x38,
    'DIK_RMENU': 0xB8,
    'DIK_LWIN': 0xDB,
    'DIK_RWIN': 0xDC,
    'DIK_APPS': 0xDD,
    'DIK_SPACE': 0x39,
    'DIK_BACK': 0x0E,
    'DIK_RETURN': 0x1C,
    'DIK_ESCAPE': 0x01,
    
    # V1.1
    'DIK_ESCAPE': 0x01,
    'DIK_1': 0x02, 'DIK_2': 0x03, 'DIK_3': 0x04, 'DIK_4': 0x05, 'DIK_5': 0x06, 'DIK_6': 0x07,
    'DIK_7': 0x08, 'DIK_8': 0x09, 'DIK_9': 0x0A, 'DIK_0': 0x0B, 'DIK_MINUS': 0x0C, 'DIK_EQUALS': 0x0D,
    'DIK_BACK': 0x0E, 'DIK_TAB': 0x0F, 'DIK_Q': 0x10, 'DIK_W': 0x11, 'DIK_E': 0x12, 'DIK_R': 0x13,
    'DIK_T': 0x14, 'DIK_Y': 0x15, 'DIK_U': 0x16, 'DIK_I': 0x17, 'DIK_O': 0x18, 'DIK_P': 0x19,
    'DIK_LBRACKET': 0x1A, 'DIK_RBRACKET': 0x1B, 'DIK_RETURN': 0x1C, 'DIK_LCONTROL': 0x1D,
    'DIK_A': 0x1E, 'DIK_S': 0x1F, 'DIK_D': 0x20, 'DIK_F': 0x21, 'DIK_G': 0x22, 'DIK_H': 0x23,
    'DIK_J': 0x24, 'DIK_K': 0x25, 'DIK_L': 0x26, 'DIK_SEMICOLON': 0x27, 'DIK_APOSTROPHE': 0x28,
    'DIK_GRAVE': 0x29,  # Backtick
    'DIK_LSHIFT': 0x2A, 'DIK_BACKSLASH': 0x2B, 'DIK_Z': 0x2C, 'DIK_X': 0x2D, 'DIK_C': 0x2E,
    'DIK_V': 0x2F, 'DIK_B': 0x30, 'DIK_N': 0x31, 'DIK_M': 0x32, 'DIK_COMMA': 0x33, 'DIK_PERIOD': 0x34,
    'DIK_SLASH': 0x35, 'DIK_RSHIFT': 0x36, 'DIK_MULTIPLY': 0x37, 'DIK_LALT': 0x38, 'DIK_SPACE': 0x39,
    'DIK_CAPITAL': 0x3A, 'DIK_F1': 0x3B, 'DIK_F2': 0x3C, 'DIK_F3': 0x3D, 'DIK_F4': 0x3E, 'DIK_F5': 0x3F,
    'DIK_F6': 0x40, 'DIK_F7': 0x41, 'DIK_F8': 0x42, 'DIK_F9': 0x43, 'DIK_F10': 0x44, 'DIK_NUMLOCK': 0x45,
    'DIK_SCROLL': 0x46, 'DIK_NUMPAD7': 0x47, 'DIK_NUMPAD8': 0x48, 'DIK_NUMPAD9': 0x49, 'DIK_SUBTRACT': 0x4A,
    'DIK_NUMPAD4': 0x4B, 'DIK_NUMPAD5': 0x4C, 'DIK_NUMPAD6': 0x4D, 'DIK_ADD': 0x4E, 'DIK_NUMPAD1': 0x4F,
    'DIK_NUMPAD2': 0x50, 'DIK_NUMPAD3': 0x51, 'DIK_NUMPAD0': 0x52, 'DIK_DECIMAL': 0x53, 'DIK_F11': 0x57,
    'DIK_F12': 0x58
}

class EDKeys:
    def __init__(self, binds_file=None):
        self.binds_file = binds_file or self.get_latest_keybinds()
        self.bindings = self.parse_binds_file()

    def get_latest_keybinds(self):
        try:
            path_bindings = os.path.join(os.environ['LOCALAPPDATA'], "Frontier Developments", "Elite Dangerous", "Options", "Bindings")
            bindings_files = [join(path_bindings, f) for f in os.listdir(path_bindings) if isfile(join(path_bindings, f)) and f.endswith('.binds')]
            return max(bindings_files, key=getmtime) if bindings_files else None
        except Exception as e:
            print(f"Failed to get latest keybinds: {e}")
            return None

    def parse_binds_file(self):
        bindings = {}
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()

            for element in root:
                action = element.tag
                primary = element.find('Primary')
                secondary = element.find('Secondary')

                bindings[action] = {'Primary': None, 'Secondary': None}

                if primary is not None and 'Key' in primary.attrib:
                    key = primary.attrib['Key']
                    normalized_key = self.normalize_key(key.replace('Key_', ''))
                    bindings[action]['Primary'] = self.key_to_scancode(normalized_key)

                if secondary is not None and 'Key' in secondary.attrib:
                    key = secondary.attrib['Key']
                    normalized_key = self.normalize_key(key.replace('Key_', ''))
                    bindings[action]['Secondary'] = self.key_to_scancode(normalized_key)

        except Exception as e:
            print(f"An error occurred while parsing the binds file: {e}")

        return bindings

    def normalize_and_convert_to_scancode(self, key):
        normalized = self.normalize_key(key)
        return self.key_to_scancode(normalized)

    def normalize_key(self, key):
        key = key.upper().replace('KEY_', '')

        # Normalize specific dead keys
        if key == 'GRAVE':
            return '`'
        elif key == 'APOSTROPHE':
            return '\''
        
        # Handle numpad keys
        if key.startswith('NUMPAD'):
            return f'NUM {key[-1]}'

        return key


    @staticmethod
    def key_to_scancode(key):
        if key.startswith('NUMPAD'):
            key = 'DIK_' + key
        elif len(key) == 1 and key.isalpha():
            key = f'DIK_{key}'
        else:
            key = f'DIK_{key}'
        return SCANCODE.get(key, None)

    def print_all_keybinds(self):
        for action, bindings in self.bindings.items():
            primary = self.scancode_to_key(bindings['Primary'])
            secondary = self.scancode_to_key(bindings['Secondary'])
            print(f"{action}: Primary - {primary} ({hex(bindings['Primary']) if bindings['Primary'] else 'None'}), "
                  f"Secondary - {secondary} ({hex(bindings['Secondary']) if bindings['Secondary'] else 'None'})")

    @staticmethod
    def scancode_to_key(scancode):
        for key, code in SCANCODE.items():
            if code == scancode:
                return key.replace('DIK_', '')
        return 'Unknown'
    
    def load_binds_file(self, file_path):
        self.binds_file = file_path
        self.bindings = self.parse_binds_file()
        return self.bindings
    
    def get_bindings(self):
        return self.bindings

class KeyboardGUI(QMainWindow):
    def __init__(self, ed_keys):
        super().__init__()
        self.ed_keys = ed_keys
        self.keybindings = self.ed_keys.get_bindings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Elite Dangerous Keybindings')
        self.setGeometry(100, 100, 800, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        load_button = QPushButton('Load .binds File')
        load_button.clicked.connect(self.load_new_binds_file)
        self.main_layout.addWidget(load_button)

        print_keybinds_button = QPushButton('Print All Keybinds')
        print_keybinds_button.clicked.connect(self.print_all_keybinds)
        self.main_layout.addWidget(print_keybinds_button)

        self.keyboard_layout = QHBoxLayout()
        self.main_layout.addLayout(self.keyboard_layout)

        self.create_keyboard()
        
    def create_keyboard(self):
        main_keyboard = QGridLayout()
        self.create_main_keyboard(main_keyboard)
        self.keyboard_layout.addLayout(main_keyboard, 5)

        right_layout = QVBoxLayout()
        self.create_function_keys(right_layout)
        self.create_arrow_keys(right_layout)
        self.create_numpad_area(right_layout)
        self.keyboard_layout.addLayout(right_layout, 1)
        
    def create_main_keyboard(self, layout):
        keys = [
            ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],  # Added `]` key here
            ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'ENTER'],
            ['LSHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'RSHIFT'],
            ['LCTRL', 'LWIN', 'LALT', 'SPACE', 'RALT', 'RWIN', 'MENU', 'RCTRL']
        ]


        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                button = self.create_key_button(key)
                layout.addWidget(button, row, col, 1, 2 if key in ['BACK', 'RETURN', 'LSHIFT', 'RSHIFT', 'SPACE'] else 1)
                
    def create_function_keys(self, layout):
        f_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        f_layout = QGridLayout()
        for i, key in enumerate(f_keys):
            button = self.create_key_button(key)
            f_layout.addWidget(button, i // 4, i % 4)
        layout.addLayout(f_layout)

    def create_arrow_keys(self, layout):
        arrow_layout = QGridLayout()
        arrows = [('UP', 0, 1), ('LEFT', 1, 0), ('DOWN', 1, 1), ('RIGHT', 1, 2)]
        for key, row, col in arrows:
            button = self.create_key_button(key)
            arrow_layout.addWidget(button, row, col)
        layout.addLayout(arrow_layout)

    def create_numpad_area(self, layout):
        numpad_layout = QGridLayout()
        numpad = [
            ['NUM7', 'NUM8', 'NUM9', 'NUM+'],
            ['NUM4', 'NUM5', 'NUM6', 'NUM-'],
            ['NUM1', 'NUM2', 'NUM3', 'NUM*'],
            ['NUM0', 'NUM.', 'NUM/', 'NUMENTER']
        ]
        for row, key_row in enumerate(numpad):
            for col, key in enumerate(key_row):
                button = self.create_key_button(key)
                numpad_layout.addWidget(button, row, col)
        layout.addLayout(numpad_layout)
    
    def create_key_button(self, key):
        button = QPushButton(key)
        button.setFixedSize(QSize(50, 50))
        
        # Special handling for numpad keys
        if key.startswith('NUM'):
            if key == 'NUMENTER':
                normalized_key = 'NUMPADENTER'
            elif key == 'NUM.':
                normalized_key = 'DECIMAL'
            elif key in ['NUM+', 'NUM-', 'NUM*', 'NUM/']:
                normalized_key = {'NUM+': 'ADD', 'NUM-': 'SUBTRACT', 'NUM*': 'MULTIPLY', 'NUM/': 'DIVIDE'}[key]
            else:
                normalized_key = 'NUMPAD' + key[3:]
        else:
            normalized_key = self.ed_keys.normalize_key(key)
        
        scancode = self.ed_keys.key_to_scancode(normalized_key)
        if scancode:
            bound_actions = self.get_bound_actions(scancode)
            if bound_actions:
                button.setStyleSheet("background-color: yellow;")
                tooltip = "\n".join(f"{action}: {binding}" for action, binding in bound_actions)
                button.setToolTip(tooltip)
        return button
    
    def load_new_binds_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .binds file", "", "Binds Files (*.binds)")
        if file_path:
            try:
                self.keybindings = self.ed_keys.load_binds_file(file_path)
                self.update_keyboard()
                QMessageBox.information(self, "Success", f"Loaded bindings from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load bindings: {str(e)}")

    def update_keyboard(self):
        # Clear existing keyboard layout
        while self.keyboard_layout.count():
            item = self.keyboard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

        # Recreate keyboard layout
        self.create_keyboard()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def get_bound_actions(self, scancode):
        bound_actions = []
        for action, bindings in self.keybindings.items():
            if bindings['Primary'] == scancode:
                bound_actions.append((action, 'Primary'))
            if bindings['Secondary'] == scancode:
                bound_actions.append((action, 'Secondary'))
        return bound_actions

    # def keyPressEvent(self, event):
    #     key = event.key()
    #     text = event.text().upper()
    #     scancode = self.ed_keys.key_to_scancode(self.ed_keys.normalize_key(text))
    #     if scancode:
    #         actions = self.get_bound_actions(scancode)
    #         if actions:
    #             print(f"Key pressed: {text} (Scancode: {hex(scancode)})")
    #             for action, binding_type in actions:
    #                 print(f"  {action} ({binding_type})")
    #         else:
    #             print(f"Key pressed: {text} (Scancode: {hex(scancode)}) (No bound actions)")
    #     else:
    #         print(f"Unmapped key pressed: {text}")
    
    def keyPressEvent(self, event):
        # Ignore auto-repeat events
        if event.isAutoRepeat():
            return

        key_code = event.key()
        key_name = event.text()

        # If event.text() is empty, it's likely a dead key
        if not key_name:
            if key_code == Qt.Key_QuoteLeft:
                key_name = '`'
            elif key_code == Qt.Key_Apostrophe:
                key_name = '\''
            else:
                key_name = chr(key_code) if key_code < 128 else ''  # Fallback for other dead keys

        # Print the detected key for debugging
        print(f"Detected key: {key_name}")

        # Highlight the button and show bindings if it exists in the layout
        if key_name in self.key_buttons:
            button = self.key_buttons[key_name]
            button.setStyleSheet("background-color: green;")
            normalized_key = self.ed_keys.normalize_key(key_name)
            scancode = self.ed_keys.get_scancode_for_key(normalized_key)
            bound_actions = self.ed_keys.get_bound_actions(scancode)
            if bound_actions:
                print(f"Bindings for {key_name}: {', '.join(bound_actions)}")
            else:
                print(f"No bindings found for {key_name}")



    def print_all_keybinds(self):
        self.ed_keys.print_all_keybinds()

def main():
    app = QApplication(sys.argv)
    ed_keys = EDKeys()
    ex = KeyboardGUI(ed_keys)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()