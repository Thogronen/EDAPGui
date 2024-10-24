# keyboard_layouts.py

BASE_LAYOUT = {
    "main": [
        [("Key_Escape", "Esc", 1), ("Key_F1", "F1", 1), ("Key_F2", "F2", 1), ("Key_F3", "F3", 1), ("Key_F4", "F4", 1), ("Key_F5", "F5", 1), ("Key_F6", "F6", 1), ("Key_F7", "F7", 1), ("Key_F8", "F8", 1), ("Key_F9", "F9", 1), ("Key_F10", "F10", 1), ("Key_F11", "F11", 1), ("Key_F12", "F12", 1)],
        [("Key_Grave", "`", 1), ("Key_1", "1", 1), ("Key_2", "2", 1), ("Key_3", "3", 1), ("Key_4", "4", 1), ("Key_5", "5", 1), ("Key_6", "6", 1), ("Key_7", "7", 1), ("Key_8", "8", 1), ("Key_9", "9", 1), ("Key_0", "0", 1), ("Key_Minus", "-", 1), ("Key_Equals", "=", 1), ("Key_Backspace", "Backspace", 2)],
        [("Key_Tab", "Tab", 1.5), ("Key_Q", "Q", 1), ("Key_W", "W", 1), ("Key_E", "E", 1), ("Key_R", "R", 1), ("Key_T", "T", 1), ("Key_Y", "Y", 1), ("Key_U", "U", 1), ("Key_I", "I", 1), ("Key_O", "O", 1), ("Key_P", "P", 1), ("Key_LeftBracket", "[", 1), ("Key_RightBracket", "]", 1), ("Key_Backslash", "\\", 1.5)],
        [("Key_CapsLock", "Caps", 1.75), ("Key_A", "A", 1), ("Key_S", "S", 1), ("Key_D", "D", 1), ("Key_F", "F", 1), ("Key_G", "G", 1), ("Key_H", "H", 1), ("Key_J", "J", 1), ("Key_K", "K", 1), ("Key_L", "L", 1), ("Key_Semicolon", ";", 1), ("Key_Apostrophe", "'", 1), ("Key_Enter", "Enter", 2.25)],
        [("Key_LeftShift", "Shift", 2.25), ("Key_Z", "Z", 1), ("Key_X", "X", 1), ("Key_C", "C", 1), ("Key_V", "V", 1), ("Key_B", "B", 1), ("Key_N", "N", 1), ("Key_M", "M", 1), ("Key_Comma", ",", 1), ("Key_Period", ".", 1), ("Key_Slash", "/", 1), ("Key_RightShift", "Shift", 2.75)],
        [("Key_LeftControl", "Ctrl", 1.25), ("Key_LeftWin", "Win", 1.25), ("Key_LeftAlt", "Alt", 1.25), ("Key_Space", "Space", 6.25), ("Key_RightAlt", "Alt", 1.25), ("Key_RightWin", "Win", 1.25), ("Key_Menu", "Menu", 1.25), ("Key_RightControl", "Ctrl", 1.25)]
    ],
    # ... (add nav and numpad layouts)
}

LAYOUT_VARIATIONS = {
    "ANSI_US": {},  # No changes needed for US ANSI
    "ISO_UK": {
        "Key_Backslash": ("Key_Hash", "#", 1),
        "Key_Enter": ("Key_Enter", "Enter", 1.25),
        "Key_LeftShift": ("Key_LeftShift", "Shift", 1.25),
        "new_key_102": ("Key_Backslash", "\\", 1),  # Add the extra key next to left shift
    },
    "ISO_German": {
        "Key_Y": ("Key_Z", "Z", 1),
        "Key_Z": ("Key_Y", "Y", 1),
        "Key_Backslash": ("Key_Acute", "´", 1),
        "Key_LeftBracket": ("Key_Umlaut", "Ü", 1),
        "Key_RightBracket": ("Key_Plus", "+", 1),
        "Key_Semicolon": ("Key_Umlaut", "Ö", 1),
        "Key_Apostrophe": ("Key_Umlaut", "Ä", 1),
        "Key_Enter": ("Key_Enter", "Enter", 1.25),
        "Key_LeftShift": ("Key_LeftShift", "Shift", 1.25),
        "new_key_102": ("Key_LessThan", "<", 1),
    },
    "ISO_French": {
        "Key_Q": ("Key_A", "A", 1),
        "Key_W": ("Key_Z", "Z", 1),
        "Key_A": ("Key_Q", "Q", 1),
        "Key_Z": ("Key_W", "W", 1),
        "Key_M": ("Key_Semicolon", "M", 1),
        "Key_Backslash": ("Key_Asterisk", "*", 1),
        "Key_LeftBracket": ("Key_CircumflexAccent", "^", 1),
        "Key_RightBracket": ("Key_DollarSign", "$", 1),
        "Key_Semicolon": ("Key_M", "M", 1),
        "Key_Apostrophe": ("Key_Ugrave", "ù", 1),
        "Key_Enter": ("Key_Enter", "Enter", 1.25),
        "Key_LeftShift": ("Key_LeftShift", "Shift", 1.25),
        "new_key_102": ("Key_LessThan", "<", 1),
    },
    "ISO_Spanish": {
        "Key_Backslash": ("Key_AccentGrave", "´", 1),
        "Key_LeftBracket": ("Key_AccentGrave", "`", 1),
        "Key_RightBracket": ("Key_Plus", "+", 1),
        "Key_Semicolon": ("Key_Enye", "Ñ", 1),
        "Key_Apostrophe": ("Key_AccentAcute", "´", 1),
        "Key_Enter": ("Key_Enter", "Enter", 1.25),
        "Key_LeftShift": ("Key_LeftShift", "Shift", 1.25),
        "new_key_102": ("Key_LessThan", "<", 1),
    },
    "ISO_Portuguese": {
        "Key_Backslash": ("Key_AccentTilde", "~", 1),
        "Key_LeftBracket": ("Key_Plus", "+", 1),
        "Key_RightBracket": ("Key_AccentAcute", "´", 1),
        "Key_Semicolon": ("Key_Ccedilla", "Ç", 1),
        "Key_Apostrophe": ("Key_Tilde", "~", 1),
        "Key_Enter": ("Key_Enter", "Enter", 1.25),
        "Key_LeftShift": ("Key_LeftShift", "Shift", 1.25),
        "new_key_102": ("Key_LessThan", "<", 1),
    },
}

def get_layout(layout_name):
    base = BASE_LAYOUT.copy()
    variations = LAYOUT_VARIATIONS.get(layout_name, {})
    
    for section in base:
        for row_index, row in enumerate(base[section]):
            new_row = []
            for key in row:
                if key[0] in variations:
                    new_row.append(variations[key[0]])
                else:
                    new_row.append(key)
            if 'new_key_102' in variations and section == 'main' and row_index == 4:
                new_row.insert(1, variations['new_key_102'])
            base[section][row_index] = new_row
    
    return base