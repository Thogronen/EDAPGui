### Features

# v1.1B-nightly is close to a full rework on how the system works, now using Virtual Keys over hardcoded values to pave the way for multi-language support.
# This version does not contain many of the UI enhancements NOR key-rebinding ability, but will show you what keys you have bound over different categories.

# - [x] An overview of your chosen (or, last used by default) keybind file
# - [ ] Ability to quickly and easily re-bind keys
# - [ ] Colour schemes/themes + tab grouping
# - [ ] Overview of what actions you have not bound
# - [ ] A search bar, allowing you to look for binds
# - [x] Key highlights on press
# - [ ] Support for multiple layouts/languages
# - [ ] Global logging! Helpful for debugging... and more.
# - [ ] Visual Cheat Sheet (Maybe this should be a plugin...)
# - [ ] Undo / Redo Stack (Undo individual key changes)
# - [ ] Keyboard Navigation in the dialog screen
# - [ ] Plugins
    # - [ ] EDAP Activation Keys
    # - [ ] Background running
    # - [ ] More?
    
#   As a sidenote, I no longer think 1500 lines is a lot LOL


import sys
import os
import configparser
import logging
import xml.etree.ElementTree as ET
import importlib.util
import ctypes

from pynput import keyboard

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QTextEdit,
    QAction,
    QMenuBar,
    QDockWidget,
    QFileDialog,
    QTabWidget,
    QMessageBox,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QScrollArea,
    QSplitter,
    QStyle,
    QGroupBox,
    QListWidget,
    QWidgetItem,
    QDialogButtonBox,
    QListWidgetItem
)

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint, QRect, QEvent
from PyQt5.QtGui import QFont, QPainter, QColor, QPen

### Recall debug code

# import traceback

# def debug_log_call(original_func):
#     def wrapper(msg, *args, **kwargs):
#         print(f"Debug: About to log: {msg}")
#         print("Debug: Stack trace:", "".join(traceback.format_stack()))
#         return original_func(msg, *args, **kwargs)
#     return wrapper

# # Apply the monkeypatch
# logging.info = debug_log_call(logging.info)
# logging.debug = debug_log_call(logging.debug)
# logging.warning = debug_log_call(logging.warning)
# logging.error = debug_log_call(logging.error)
# logging.critical = debug_log_call(logging.critical)

###

# Determine the architecture and define ULONG_PTR accordingly
if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong

# VK Code Mapping (Virtual-Key Codes) - Including mouse buttons
VK_CODE = {  # Gives a name to a hexidecimal code.
    "LBUTTON": 0x01,
    "RBUTTON": 0x02,
    "CANCEL": 0x03,
    "MBUTTON": 0x04,
    "XBUTTON1": 0x05,
    "XBUTTON2": 0x06,
    "BACK": 0x08,
    "TAB": 0x09,
    "CLEAR": 0x0C,
    "RETURN": 0x0D,
    "SHIFT": 0x10,
    "CONTROL": 0x11,
    "MENU": 0x12,
    "PAUSE": 0x13,
    "CAPITAL": 0x14,
    "KANA": 0x15,
    "HANGUL": 0x15,
    "IME_ON": 0x16,
    "JUNJA": 0x17,
    "FINAL": 0x18,
    "HANJA": 0x19,
    "KANJI": 0x19,
    "IME_OFF": 0x1A,
    "ESCAPE": 0x1B,
    "CONVERT": 0x1C,
    "NONCONVERT": 0x1D,
    "ACCEPT": 0x1E,
    "MODECHANGE": 0x1F,
    "SPACE": 0x20,
    "PRIOR": 0x21,
    "NEXT": 0x22,
    "END": 0x23,
    "HOME": 0x24,
    "LEFT": 0x25,
    "UP": 0x26,
    "RIGHT": 0x27,
    "DOWN": 0x28,
    "SELECT": 0x29,
    "PRINT": 0x2A,
    "EXECUTE": 0x2B,
    "SNAPSHOT": 0x2C,
    "INSERT": 0x2D,
    "DELETE": 0x2E,
    "HELP": 0x2F,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "A": 0x41,
    "B": 0x42,
    "C": 0x43,
    "D": 0x44,
    "E": 0x45,
    "F": 0x46,
    "G": 0x47,
    "H": 0x48,
    "I": 0x49,
    "J": 0x4A,
    "K": 0x4B,
    "L": 0x4C,
    "M": 0x4D,
    "N": 0x4E,
    "O": 0x4F,
    "P": 0x50,
    "Q": 0x51,
    "R": 0x52,
    "S": 0x53,
    "T": 0x54,
    "U": 0x55,
    "V": 0x56,
    "W": 0x57,
    "X": 0x58,
    "Y": 0x59,
    "Z": 0x5A,
    "LWIN": 0x5B,
    "RWIN": 0x5C,
    "APPS": 0x5D,
    "SLEEP": 0x5F,
    "NUMPAD0": 0x60,
    "NUMPAD1": 0x61,
    "NUMPAD2": 0x62,
    "NUMPAD3": 0x63,
    "NUMPAD4": 0x64,
    "NUMPAD5": 0x65,
    "NUMPAD6": 0x66,
    "NUMPAD7": 0x67,
    "NUMPAD8": 0x68,
    "NUMPAD9": 0x69,
    "MULTIPLY": 0x6A,
    "ADD": 0x6B,
    "SEPARATOR": 0x6C,
    "SUBTRACT": 0x6D,
    "DECIMAL": 0x6E,
    "DIVIDE": 0x6F,
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "F13": 0x7C,
    "F14": 0x7D,
    "F15": 0x7E,
    "F16": 0x7F,
    "F17": 0x80,
    "F18": 0x81,
    "F19": 0x82,
    "F20": 0x83,
    "F21": 0x84,
    "F22": 0x85,
    "F23": 0x86,
    "F24": 0x87,
    "NUMLOCK": 0x90,
    "SCROLL": 0x91,
    "LSHIFT": 0xA0,
    "RSHIFT": 0xA1,
    "LCONTROL": 0xA2,
    "RCONTROL": 0xA3,
    "LMENU": 0xA4,
    "RMENU": 0xA5,
    "BROWSER_BACK": 0xA6,
    "BROWSER_FORWARD": 0xA7,
    "BROWSER_REFRESH": 0xA8,
    "BROWSER_STOP": 0xA9,
    "BROWSER_SEARCH": 0xAA,
    "BROWSER_FAVORITES": 0xAB,
    "BROWSER_HOME": 0xAC,
    "VOLUME_MUTE": 0xAD,
    "VOLUME_DOWN": 0xAE,
    "VOLUME_UP": 0xAF,
    "MEDIA_NEXT_TRACK": 0xB0,
    "MEDIA_PREV_TRACK": 0xB1,
    "MEDIA_STOP": 0xB2,
    "MEDIA_PLAY_PAUSE": 0xB3,
    "LAUNCH_MAIL": 0xB4,
    "LAUNCH_MEDIA_SELECT": 0xB5,
    "LAUNCH_APP1": 0xB6,
    "LAUNCH_APP2": 0xB7,
    "OEM_1": 0xBA,
    "OEM_PLUS": 0xBB,
    # "EQUALS": 0xBB,
    "OEM_COMMA": 0xBC,
    "OEM_MINUS": 0xBD,
    "OEM_PERIOD": 0xBE,
    "OEM_2": 0xBF,
    "OEM_3": 0xC0,
    "OEM_4": 0xDB,
    "OEM_5": 0xDC,
    "OEM_6": 0xDD,
    "OEM_7": 0xDE,
    "OEM_8": 0xDF,
    "OEM_102": 0xE2,
    "PROCESSKEY": 0xE5,
    "PACKET": 0xE7,
    "ATTN": 0xF6,
    "CRSEL": 0xF7,
    "EXSEL": 0xF8,
    "EREOF": 0xF9,
    "PLAY": 0xFA,
    "ZOOM": 0xFB,
    "NONAME": 0xFC,
    "PA1": 0xFD,
    "OEM_CLEAR": 0xFE,
}

# Centralized Key Mapping Dictionary to map Qt keys to readable names, linking the given name from VK_Code to the keyboard layout
KEY_MAPPING = {
    Qt.Key_Escape: "Key_Escape",
    Qt.Key_Tab: "Key_Tab",
    Qt.Key_Backspace: "Key_Backspace",
    Qt.Key_Return: "Key_Enter",
    Qt.Key_Enter: "Key_Enter",
    Qt.Key_Insert: "Key_Insert",
    Qt.Key_Delete: "Key_Delete",
    Qt.Key_Pause: "Key_Pause",
    Qt.Key_Print: "Key_Print",
    Qt.Key_Home: "Key_Home",
    Qt.Key_End: "Key_End",
    Qt.Key_Left: "Key_LeftArrow",
    Qt.Key_Up: "Key_UpArrow",
    Qt.Key_Right: "Key_RightArrow",
    Qt.Key_Down: "Key_DownArrow",
    Qt.Key_PageUp: "Key_PageUp",
    Qt.Key_PageDown: "Key_PageDown",
    Qt.Key_CapsLock: "Key_CapsLock",
    Qt.Key_F1: "Key_F1",
    Qt.Key_F2: "Key_F2",
    Qt.Key_F3: "Key_F3",
    Qt.Key_F4: "Key_F4",
    Qt.Key_F5: "Key_F5",
    Qt.Key_F6: "Key_F6",
    Qt.Key_F7: "Key_F7",
    Qt.Key_F8: "Key_F8",
    Qt.Key_F9: "Key_F9",
    Qt.Key_F10: "Key_F10",
    Qt.Key_F11: "Key_F11",
    Qt.Key_F12: "Key_F12",
    Qt.Key_Space: "Key_Space",
    Qt.Key_Plus: "Key_Equals",
    Qt.Key_Comma: "Key_Comma",
    Qt.Key_Minus: "Key_Minus",
    Qt.Key_Period: "Key_Period",
    Qt.Key_Slash: "Key_Slash",
    Qt.Key_0: "Key_0",
    Qt.Key_1: "Key_1",
    Qt.Key_2: "Key_2",
    Qt.Key_3: "Key_3",
    Qt.Key_4: "Key_4",
    Qt.Key_5: "Key_5",
    Qt.Key_6: "Key_6",
    Qt.Key_7: "Key_7",
    Qt.Key_8: "Key_8",
    Qt.Key_9: "Key_9",
    Qt.Key_Colon: "Key_SemiColon",
    Qt.Key_Semicolon: "Key_SemiColon",
    Qt.Key_Less: "Key_Comma",
    Qt.Key_Equal: "Key_Equals",
    Qt.Key_Greater: "Key_Period",
    Qt.Key_Question: "Key_Slash",
    Qt.Key_At: "Key_2",
    Qt.Key_A: "Key_A",
    Qt.Key_B: "Key_B",
    Qt.Key_C: "Key_C",
    Qt.Key_D: "Key_D",
    Qt.Key_E: "Key_E",
    Qt.Key_F: "Key_F",
    Qt.Key_G: "Key_G",
    Qt.Key_H: "Key_H",
    Qt.Key_I: "Key_I",
    Qt.Key_J: "Key_J",
    Qt.Key_K: "Key_K",
    Qt.Key_L: "Key_L",
    Qt.Key_M: "Key_M",
    Qt.Key_N: "Key_N",
    Qt.Key_O: "Key_O",
    Qt.Key_P: "Key_P",
    Qt.Key_Q: "Key_Q",
    Qt.Key_R: "Key_R",
    Qt.Key_S: "Key_S",
    Qt.Key_T: "Key_T",
    Qt.Key_U: "Key_U",
    Qt.Key_V: "Key_V",
    Qt.Key_W: "Key_W",
    Qt.Key_X: "Key_X",
    Qt.Key_Y: "Key_Y",
    Qt.Key_Z: "Key_Z",
    Qt.Key_BracketLeft: "Key_LeftBracket",
    Qt.Key_Backslash: "Key_BackSlash",
    Qt.Key_BracketRight: "Key_RightBracket",
    Qt.Key_AsciiCircum: "Key_6",
    Qt.Key_Underscore: "Key_Minus",
    Qt.Key_QuoteLeft: "Key_Grave",
    Qt.Key_BraceLeft: "Key_LeftBracket",
    Qt.Key_Bar: "Key_BackSlash",
    Qt.Key_BraceRight: "Key_RightBracket",
    Qt.Key_AsciiTilde: "Key_Grave",
    Qt.Key_NumLock: "Key_NumLock",
    Qt.Key_ScrollLock: "Key_ScrollLock",
    Qt.Key_F13: "Key_F13",
    Qt.Key_F14: "Key_F14",
    Qt.Key_F15: "Key_F15",
    Qt.Key_F16: "Key_F16",
    Qt.Key_F17: "Key_F17",
    Qt.Key_F18: "Key_F18",
    Qt.Key_F19: "Key_F19",
    Qt.Key_F20: "Key_F20",
    Qt.Key_F21: "Key_F21",
    Qt.Key_F22: "Key_F22",
    Qt.Key_F23: "Key_F23",
    Qt.Key_F24: "Key_F24",
    Qt.Key_Menu: "Key_Apps",
    Qt.Key_MediaPlay: "Key_MediaPlayPause",
    Qt.Key_MediaStop: "Key_MediaStop",
    Qt.Key_VolumeDown: "Key_VolumeDown",
    Qt.Key_VolumeUp: "Key_VolumeUp",
    Qt.Key_VolumeMute: "Key_VolumeMute",
    Qt.Key_Apostrophe: "Key_Apostrophe",
    Qt.Key_QuoteLeft: "Key_Grave",
    
    # Numpad keys
    Qt.Key_0 | Qt.KeypadModifier: "Key_Numpad_0",
    Qt.Key_1 | Qt.KeypadModifier: "Key_Numpad_1",
    Qt.Key_2 | Qt.KeypadModifier: "Key_Numpad_2",
    Qt.Key_3 | Qt.KeypadModifier: "Key_Numpad_3",
    Qt.Key_4 | Qt.KeypadModifier: "Key_Numpad_4",
    Qt.Key_5 | Qt.KeypadModifier: "Key_Numpad_5",
    Qt.Key_6 | Qt.KeypadModifier: "Key_Numpad_6",
    Qt.Key_7 | Qt.KeypadModifier: "Key_Numpad_7",
    Qt.Key_8 | Qt.KeypadModifier: "Key_Numpad_8",
    Qt.Key_9 | Qt.KeypadModifier: "Key_Numpad_9",
    Qt.Key_Asterisk | Qt.KeypadModifier: "Key_Numpad_Multiply",
    Qt.Key_Plus | Qt.KeypadModifier: "Key_Numpad_Add",
    Qt.Key_Minus | Qt.KeypadModifier: "Key_Numpad_Subtract",
    Qt.Key_Period | Qt.KeypadModifier: "Key_Numpad_Decimal",
    Qt.Key_Slash | Qt.KeypadModifier: "Key_Numpad_Divide",
    Qt.Key_Enter | Qt.KeypadModifier: "Key_NumpadEnter",
    
    # Other shenenigans
    Qt.Key_Shift: "Key_LeftShift",
    Qt.Key_Control: "Key_LeftControl",
    Qt.Key_Alt: "Key_LeftAlt",
    Qt.Key_AltGr: "Key_RightAlt",
    Qt.Key_Meta: "Key_LeftWin",
    0x01000085: "Key_RightWin",  # Right Windows key
}

SCAN_CODE_MAPPING = { # You might need to update this, depending on your keyboard layout and language. In order to do this, comment the offending keys out, save, reload, and check the output on pressing that key. That will give you your scan code.
    29: "Key_LeftControl",
    56: "Key_LeftAlt",
    54: "Key_RightShift",
    285: "Key_RightControl",
    312: "Key_RightAlt",  # This is AltGr
} 

# Layout Definitions (only including QWERTY for now).
LAYOUTS = {
    "QWERTY": {
        "main": [
            [
                ("Key_Escape", "Esc", 2),
                ("Key_F1", "F1", 1),
                ("Key_F2", "F2", 1),
                ("Key_F3", "F3", 1),
                ("Key_F4", "F4", 1),
                ("Key_F5", "F5", 1),
                ("Key_F6", "F6", 1),
                ("Key_F7", "F7", 1),
                ("Key_F8", "F8", 1),
                ("Key_F9", "F9", 1),
                ("Key_F10", "F10", 1),
                ("Key_F11", "F11", 1),
                ("Key_F12", "F12", 1),
            ],
            [
                ("Key_Grave", "`", 1),
                ("Key_1", "1", 1),
                ("Key_2", "2", 1),
                ("Key_3", "3", 1),
                ("Key_4", "4", 1),
                ("Key_5", "5", 1),
                ("Key_6", "6", 1),
                ("Key_7", "7", 1),
                ("Key_8", "8", 1),
                ("Key_9", "9", 1),
                ("Key_0", "0", 1),
                ("Key_Minus", "-", 1),
                ("Key_Equals", "=", 1),
                ("Key_Backspace", "Backspace", 2),
            ],
            [
                ("Key_Tab", "Tab", 1.5),
                ("Key_Q", "Q", 1),
                ("Key_W", "W", 1),
                ("Key_E", "E", 1),
                ("Key_R", "R", 1),
                ("Key_T", "T", 1),
                ("Key_Y", "Y", 1),
                ("Key_U", "U", 1),
                ("Key_I", "I", 1),
                ("Key_O", "O", 1),
                ("Key_P", "P", 1),
                ("Key_LeftBracket", "[", 1),
                ("Key_RightBracket", "]", 1),
                ("Key_BackSlash", "\\", 1.5),
            ],
            [
                ("Key_CapsLock", "Caps Lock", 2),
                ("Key_A", "A", 1),
                ("Key_S", "S", 1),
                ("Key_D", "D", 1),
                ("Key_F", "F", 1),
                ("Key_G", "G", 1),
                ("Key_H", "H", 1),
                ("Key_J", "J", 1),
                ("Key_K", "K", 1),
                ("Key_L", "L", 1),
                ("Key_SemiColon", ";", 1),
                ("Key_Apostrophe", "'", 1),
                ("Key_Enter", "Enter", 2),
            ],
            [
                ("Key_LeftShift", "Shift", 2.5),
                ("Key_Z", "Z", 1),
                ("Key_X", "X", 1),
                ("Key_C", "C", 1),
                ("Key_V", "V", 1),
                ("Key_B", "B", 1),
                ("Key_N", "N", 1),
                ("Key_M", "M", 1),
                ("Key_Comma", ",", 1),
                ("Key_Period", ".", 1),
                ("Key_Slash", "/", 1),
                ("Key_RightShift", "Shift", 2.5),
            ],
            [
                ("Key_LeftControl", "Ctrl", 1.5),
                ("Key_LeftWin", "Win", 1.0),
                ("Key_LeftAlt", "Alt", 1.0),
                ("Key_Space", "Space", 7),
                ("Key_RightAlt", "AltGr", 1.0),
                ("Key_FN", "FN", 1.0),
                ("Key_Apps", "Menu", 1.0),
                ("Key_RightControl", "Ctrl", 1.5),
            ],
        ],
        "nav": [
            [
                ("Key_Insert", "Ins", 1),
                ("Key_Home", "Home", 1),
                ("Key_PageUp", "PG Up", 1),
            ],
            [
                ("Key_Delete", "Del", 1),
                ("Key_End", "End", 1),
                ("Key_PageDown", "PG Dwn", 1),
            ],
            [("", "", 3)],  # Empty row
            [("", "", 3)],  # Empty row
            [("", "", 1), ("Key_UpArrow", "↑", 1), ("", "", 1)],
            [
                ("Key_LeftArrow", "←", 1),
                ("Key_DownArrow", "↓", 1),
                ("Key_RightArrow", "→", 1),
            ],
        ],
        "numpad": [
            [("", 4)],  # Empty row
            [
                ("Key_NumLock", "Num LK", 1),
                ("Key_Numpad_Divide", "/", 1),
                ("Key_Numpad_Multiply", "*", 1),
                ("Key_Numpad_Subtract", "-", 1),
            ],
            [
                ("Key_Numpad_7", "7", 1),
                ("Key_Numpad_8", "8", 1),
                ("Key_Numpad_9", "9", 1),
                ("Key_Numpad_Add", "+", 1, 2),
            ],  # ADD spans 2 rows
            [
                ("Key_Numpad_4", "4", 1),
                ("Key_Numpad_5", "5", 1),
                ("Key_Numpad_6", "6", 1),
            ],
            [
                ("Key_Numpad_1", "1", 1),
                ("Key_Numpad_2", "2", 1),
                ("Key_Numpad_3", "3", 1),
                ("Key_NumpadEnter", "Enter", 1, 2),
            ],  # NUMPADENTER spans 2 rows
            [
                ("Key_Numpad_0", "0", 2),
                ("Key_Numpad_Decimal", ".", 1),
            ],  # NUMPAD0 spans 2 columns
        ],
    }
}

# Groups for Elite:Dangerous keybinding
BINDING_CATEGORIES = {
    "General": [
        "UIFocus",
        "UI_Up",
        "UI_Down",
        "UI_Left",
        "UI_Right",
        "UI_Select",
        "UI_Back",
        "UI_Toggle",
        "CycleNextPanel",
        "CyclePreviousPanel",
        "CycleNextPage",
        "CyclePreviousPage",
        "QuickCommsPanel",
        "FocusCommsPanel",
        "FocusLeftPanel",
        "FocusRightPanel",
        "GalaxyMapOpen",
        "SystemMapOpen",
        "ShowPGScoreSummaryInput",
        "HeadLookToggle",
        "Pause",
        "FriendsMenu",
        "OpenCodexGoToDiscovery",
        "PlayerHUDModeToggle",
        "PhotoCameraToggle",
        "GalaxyMapHome",
        "MouseReset",
        "BlockMouseDecay",
        "YawToRollButton",
        "ForwardKey",
        "BackwardKey",
        "FocusRadarPanel",
        "HeadLookReset",
        "HeadLookPitchUp",
        "HeadLookPitchDown",
        "HeadLookYawLeft",
        "HeadLookYawRight",
        "GalnetAudio_Play_Pause",
        "GalnetAudio_SkipForward",
        "GalnetAudio_SkipBackward",
        "GalnetAudio_ClearQueue",
    ],
    "Ship": [
        "YawLeftButton",
        "YawRightButton",
        "RollLeftButton",
        "RollRightButton",
        "PitchUpButton",
        "PitchDownButton",
        "LeftThrustButton",
        "RightThrustButton",
        "UpThrustButton",
        "DownThrustButton",
        "ForwardThrustButton",
        "BackwardThrustButton",
        "SetSpeedZero",
        "SetSpeed25",
        "SetSpeed50",
        "SetSpeed75",
        "SetSpeed100",
        "ToggleFlightAssist",
        "UseBoostJuice",
        "HyperSuperCombination",
        "Supercruise",
        "Hyperspace",
        "DisableRotationCorrectToggle",
        "OrbitLinesToggle",
        "SelectTarget",
        "CycleNextTarget",
        "CyclePreviousTarget",
        "SelectHighestThreat",
        "CycleNextHostileTarget",
        "CyclePreviousHostileTarget",
        "TargetWingman0",
        "TargetWingman1",
        "TargetWingman2",
        "SelectTargetsTarget",
        "WingNavLock",
        "CycleNextSubsystem",
        "CyclePreviousSubsystem",
        "TargetNextRouteSystem",
        "PrimaryFire",
        "SecondaryFire",
        "CycleFireGroupNext",
        "CycleFireGroupPrevious",
        "DeployHardpointToggle",
        "ToggleButtonUpInput",
        "DeployHeatSink",
        "ShipSpotLightToggle",
        "RadarIncreaseRange",
        "RadarDecreaseRange",
        "IncreaseEnginesPower",
        "IncreaseWeaponsPower",
        "IncreaseSystemsPower",
        "ResetPowerDistribution",
        "HMDReset",
        "ToggleCargoScoop",
        "EjectAllCargo",
        "LandingGearToggle",
        "UseShieldCell",
        "FireChaffLauncher",
        "ChargeECM",
        "WeaponColourToggle",
        "EngineColourToggle",
        "NightVisionToggle",
        "OrderRequestDock",
        "OrderDefensiveBehaviour",
        "OrderAggressiveBehaviour",
        "OrderFocusTarget",
        "OrderHoldFire",
        "OrderHoldPosition",
        "OrderFollow",
        "MicrophoneMute",
        "UseAlternateFlightValuesToggle",
        "ToggleReverseThrottleInput",
        "TriggerFieldNeutraliser",
        "SetSpeedMinus100",
        "SetSpeedMinus75",
        "SetSpeedMinus50",
        "SetSpeedMinus25",
        "YawLeftButton_Landing",
        "YawRightButton_Landing",
        "PitchUpButton_Landing",
        "PitchDownButton_Landing",
        "RollLeftButton_Landing",
        "RollRightButton_Landing",
        "LeftThrustButton_Landing",
        "RightThrustButton_Landing",
        "UpThrustButton_Landing",
        "DownThrustButton_Landing",
        "ForwardThrustButton_Landing",
        "BackwardThrustButton_Landing",
        "ExplorationFSSEnter",
    ],
    "SAA": [
        "ExplorationSAAChangeScannedAreaViewToggle",
        "ExplorationSAAExitThirdPerson",
        "ExplorationSAANextGenus",
        "ExplorationSAAPreviousGenus",
        "SAAThirdPersonYawLeftButton",
        "SAAThirdPersonYawRightButton",
        "SAAThirdPersonPitchUpButton",
        "SAAThirdPersonPitchDownButton",
        "SAAThirdPersonFovOutButton",
        "SAAThirdPersonFovInButton",
    ],
    "FSS": [
        "ExplorationFSSCameraPitchIncreaseButton",
        "ExplorationFSSCameraPitchDecreaseButton",
        "ExplorationFSSCameraYawIncreaseButton",
        "ExplorationFSSCameraYawDecreaseButton",
        "ExplorationFSSZoomIn",
        "ExplorationFSSZoomOut",
        "ExplorationFSSMiniZoomIn",
        "ExplorationFSSMiniZoomOut",
        "ExplorationFSSRadioTuningX_Increase",
        "ExplorationFSSRadioTuningX_Decrease",
        "ExplorationFSSDiscoveryScan",
        "ExplorationFSSQuit",
        "ExplorationFSSTarget",
        "ExplorationFSSShowHelp",
    ],
    "SRV": [
        "SteerLeftButton",
        "SteerRightButton",
        "BuggyRollLeftButton",
        "BuggyRollRightButton",
        "BuggyPitchUpButton",
        "BuggyPitchDownButton",
        "VerticalThrustersButton",
        "BuggyPrimaryFireButton",
        "BuggySecondaryFireButton",
        "AutoBreakBuggyButton",
        "HeadlightsBuggyButton",
        "ToggleBuggyTurretButton",
        "BuggyCycleFireGroupNext",
        "BuggyCycleFireGroupPrevious",
        "SelectTarget_Buggy",
        "BuggyTurretYawLeftButton",
        "BuggyTurretYawRightButton",
        "BuggyTurretPitchUpButton",
        "BuggyTurretPitchDownButton",
        "IncreaseSpeedButtonMax",
        "DecreaseSpeedButtonMax",
        "IncreaseEnginesPower_Buggy",
        "IncreaseWeaponsPower_Buggy",
        "IncreaseSystemsPower_Buggy",
        "ResetPowerDistribution_Buggy",
        "ToggleCargoScoop_Buggy",
        "EjectAllCargo_Buggy",
        "RecallDismissShip",
        "ToggleDriveAssist",
        "UIFocus_Buggy",
        "FocusLeftPanel_Buggy",
        "FocusCommsPanel_Buggy",
        "QuickCommsPanel_Buggy",
        "FocusRadarPanel_Buggy",
        "FocusRightPanel_Buggy",
        "GalaxyMapOpen_Buggy",
        "SystemMapOpen_Buggy",
        "OpenCodexGoToDiscovery_Buggy",
        "PlayerHUDModeToggle_Buggy",
        "HeadLookToggle_Buggy",
        "PhotoCameraToggle_Buggy",
        "BuggyToggleReverseThrottleInput",
    ],
    "OnFoot": [
        "HumanoidForwardButton",
        "HumanoidBackwardButton",
        "HumanoidStrafeLeftButton",
        "HumanoidStrafeRightButton",
        "HumanoidRotateLeftButton",
        "HumanoidRotateRightButton",
        "HumanoidPitchUpButton",
        "HumanoidPitchDownButton",
        "HumanoidSprintButton",
        "HumanoidCrouchButton",
        "HumanoidJumpButton",
        "HumanoidPrimaryInteractButton",
        "HumanoidSecondaryInteractButton",
        "HumanoidItemWheelButton",
        "HumanoidEmoteWheelButton",
        "HumanoidUtilityWheelCycleMode",
        "HumanoidPrimaryFireButton",
        "HumanoidZoomButton",
        "HumanoidThrowGrenadeButton",
        "HumanoidMeleeButton",
        "HumanoidReloadButton",
        "HumanoidSelectPrimaryWeaponButton",
        "HumanoidSelectSecondaryWeaponButton",
        "HumanoidSelectNextWeaponButton",
        "HumanoidSelectPreviousWeaponButton",
        "HumanoidHideWeaponButton",
        "HumanoidToggleFlashlightButton",
        "HumanoidToggleNightVisionButton",
        "HumanoidToggleShieldsButton",
        "HumanoidClearAuthorityLevel",
        "HumanoidHealthPack",
        "HumanoidBattery",
        "HumanoidSelectFragGrenade",
        "HumanoidSelectEMPGrenade",
        "HumanoidSelectShieldGrenade",
        "HumanoidSwitchToRechargeTool",
        "HumanoidSwitchToCompAnalyser",
        "HumanoidSwitchToSuitTool",
        "HumanoidToggleToolModeButton",
        "HumanoidToggleMissionHelpPanelButton",
        "GalaxyMapOpen_Humanoid",
        "SystemMapOpen_Humanoid",
        "FocusCommsPanel_Humanoid",
        "QuickCommsPanel_Humanoid",
        "HumanoidOpenAccessPanelButton",
        "HumanoidConflictContextualUIButton",
        "PhotoCameraToggle_Humanoid",
        "HumanoidEmoteSlot1",
        "HumanoidEmoteSlot2",
        "HumanoidEmoteSlot3",
        "HumanoidEmoteSlot4",
        "HumanoidEmoteSlot5",
        "HumanoidEmoteSlot6",
        "HumanoidEmoteSlot7",
        "HumanoidEmoteSlot8",
        "HumanoidWalkButton",
        "HumanoidItemWheelButton_XLeft",
        "HumanoidItemWheelButton_XRight",
        "HumanoidItemWheelButton_YUp",
        "HumanoidItemWheelButton_YDown",
        "HumanoidSwitchWeapon",
        "HumanoidSelectUtilityWeaponButton",
        "HumanoidSelectNextGrenadeTypeButton",
        "HumanoidSelectPreviousGrenadeTypeButton",
        "HumanoidPing",
    ],
    "Camera": [
        "CamPitchUp",
        "CamPitchDown",
        "CamYawLeft",
        "CamYawRight",
        "CamTranslateForward",
        "CamTranslateBackward",
        "CamTranslateLeft",
        "CamTranslateRight",
        "CamTranslateUp",
        "CamTranslateDown",
        "CamZoomIn",
        "CamZoomOut",
        "CamTranslateZHold",
        "ToggleFreeCam",
        "FreeCamToggleHUD",
        "FreeCamSpeedInc",
        "FreeCamSpeedDec",
        "ToggleRotationLock",
        "FixCameraRelativeToggle",
        "FixCameraWorldToggle",
        "QuitCamera",
        "ToggleAdvanceMode",
        "VanityCameraScrollLeft",
        "VanityCameraScrollRight",
        "VanityCameraOne",
        "VanityCameraTwo",
        "VanityCameraThree",
        "VanityCameraFour",
        "VanityCameraFive",
        "VanityCameraSix",
        "VanityCameraSeven",
        "VanityCameraEight",
        "VanityCameraNine",
        "VanityCameraTen",
        "FreeCamZoomIn",
        "FreeCamZoomOut",
        "FStopDec",
        "FStopInc",
        "ToggleReverseThrottleInputFreeCam",
        "MoveFreeCamForward",
        "MoveFreeCamBackwards",
        "MoveFreeCamRight",
        "MoveFreeCamLeft",
        "MoveFreeCamUp",
        "MoveFreeCamDown",
        "PitchCameraUp",
        "PitchCameraDown",
        "YawCameraLeft",
        "YawCameraRight",
        "RollCameraLeft",
        "RollCameraRight",
    ],
    "Multi-Crew": [
        "MultiCrewToggleMode",
        "MultiCrewPrimaryFire",
        "MultiCrewSecondaryFire",
        "MultiCrewPrimaryUtilityFire",
        "MultiCrewSecondaryUtilityFire",
        "MultiCrewCockpitUICycleForward",
        "MultiCrewCockpitUICycleBackward",
        "MultiCrewThirdPersonYawLeftButton",
        "MultiCrewThirdPersonYawRightButton",
        "MultiCrewThirdPersonPitchUpButton",
        "MultiCrewThirdPersonPitchDownButton",
        "MultiCrewThirdPersonFovOutButton",
        "MultiCrewThirdPersonFovInButton",
        "OpenOrders",
    ],
    "Store": [
        "StoreEnableRotation",
        "StoreCamZoomIn",
        "StoreCamZoomOut",
        "StoreToggle",
    ],
    # "Autopilot" category is removed to be handled via plugins
}

# Config parser to load configuration (like themes)
config = configparser.ConfigParser()
config.read("config.ini")

# Define themes for the GUI
THEMES = {
    "Default": {
        "background": "#2b2b2b",
        "text": "#ffffff",
        "key_normal": "#555555",
        "key_bound": "#4a6b8a",
        "key_general": "#777777",
        "key_ship": "#4a6b8a",
        "key_srv": "#4a8a6b",
        "key_onfoot": "#8a6b4a",
        "key_fss": "#6b4a8a",
        "key_camera": "#8a4a6b",
        "key_saa": "#6b8a4a",
        "key_multi-crew": "#8a6b8a",
        "key_store": "#8a8a4a",
        "key_all": "#5a5a5a",
        "key_pressed": "#333333",
        "key_active": "#8a4a4a",  # A distinct color for active keys - used only for debugging :)
        "key_numlock": "#8a4a4a",  # A distinct color for active keys - used only for debugging :)
    },
    "Dark Mode": {
        "background": "#1e1e1e",
        "text": "#ffffff",
        "key_normal": "#3c3c3c",
        "key_bound": "#007acc",
        "key_general": "#555555",
        "key_pressed": "#444444",
    },
    # Add more themes if necessary
}

# Get current theme from config, default to 'Default'
CURRENT_THEME = config.get("Appearance", "theme", fallback="Default")

import logging

def setup_logging(text_edit=None): # Define logging levels here !important for troubleshooting
    """
    Configures the logging system with handlers and formatters.
    Returns the configured 'EDKeysGUI' logger.
    """
    
    # Configure the root logger to avoid duplication
    logging.getLogger().handlers = []
    
    # Create a custom logger
    logger = logging.getLogger('EDKeysGUI')
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Clear any existing handlers
    logger.handlers = []

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('edkeysgui.log')

    # Set levels for handlers
    console_handler.setLevel(logging.INFO)    # INFO and above to console
    file_handler.setLevel(logging.DEBUG)      # DEBUG and above to file

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Add QTextEditLogger if text_edit is provided
    if text_edit:
        text_edit_handler = QTextEditLogger(text_edit)
        text_edit_handler.setLevel(logging.DEBUG)
        text_edit_handler.setFormatter(formatter)
        logger.addHandler(text_edit_handler)

    return logger

def is_numlock_on():
    """
    Checks if NUM LOCK is currently active.

    :return: True if NUM LOCK is on, False otherwise
    """
    VK_NUMLOCK = 0x90
    user32 = ctypes.WinDLL("User32.dll")
    return bool(user32.GetKeyState(VK_NUMLOCK) & 1)
 
# Create a console handler with UTF-8 encoding
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setStream(sys.stdout)  # Ensure it's using stdout



class QTextEditLogger(logging.Handler, QObject):
    log_signal = pyqtSignal(str)

    def __init__(self, text_edit):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.text_edit = text_edit
        self.log_signal.connect(self.append_log)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

    def append_log(self, msg):
        self.text_edit.append(msg)

    def close(self):
        self.log_signal.disconnect()
        super().close()


class EDKeys:
    """Handles parsing and managing key bindings for Elite: Dangerous."""

    binds_file = "main.binds"
    full_path = os.path.abspath(binds_file)

    def __init__(self, binds_file, logger):
        self.binds_file = binds_file
        self.logger = logger
        self.logger.info(f"Attempting to load binds file from: {os.path.abspath(binds_file)}")
        self.bindings = self.parse_binds_file()

    def parse_binds_file(self):
        bindings = {}
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()
            for binding in root.iter():
                if binding.tag != 'Root':  # Skip the root element
                    action = binding.tag
                    primary = binding.find('Primary')
                    if primary is not None and primary.get('Key'):
                        key = primary.get('Key')
                        if key not in bindings:
                            bindings[key] = []
                        bindings[key].append(action)
                        self.logger.debug(f"Bound {action} to {key}")
            total_bindings = sum(len(actions) for actions in bindings.values())
            self.logger.info(f"Total bindings loaded: {total_bindings}")
        except Exception as e:
            self.logger.error(f"Error parsing binds file: {e}", exc_info=True)
        return bindings

    def get_bound_actions(self, key):
        return self.bindings.get(key, [])

    def normalize_key(self, key):
        return key

    def get_vkcode_for_key(self, key):
        return VK_CODE.get(key)

    def unbind_action(self, action):
        """
        Removes the specified action from all key bindings.

        :param action: Action name to unbind.
        """
        for vkcode, actions in self.bindings.items():
            if action in actions:
                actions.remove(action)
                self.logger.info(f"Action '{action}' unbound from vkcode {vkcode}")

    def generate_key_binding_report(self):  # DEBUG
        report = []
        for key_name, vk_code in VK_CODE.items():
            normalized_key = self.normalize_key(key_name)
            bound_actions = self.get_bound_actions(str(vk_code))
            report.append(
                {
                    "key_name": key_name,
                    "normalized_key": normalized_key,
                    "vk_code": vk_code,
                    "bound_actions": bound_actions,
                }
            )
        return report


class KeyboardGUI(QMainWindow):
    """
    The main GUI window for the Keybind Visualizer.
    Displays a visual representation of keyboard bindings and handles user interactions.
    """
    
    ### Initial setup(s)

    def __init__(self, ed_keys, base_stylesheet, logger):
        super().__init__()
        self.ed_keys = ed_keys
        self.base_stylesheet = base_stylesheet
        self.logger = logger  # Use the configured 'EDKeysGUI' logger

        # Initialize attributes 
        self.key_buttons = {}
        self.base_key_size = 40
        self.is_key_dialog_open = False
        self.held_keys = set()

        self.highlight_active_keys = False
        self.active_keys = set()

        self.altgr_active = False
        self.show_general_keys = True

        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("QWidget:focus { outline: none; }")

        # Precompute styles
        self.precompute_styles()

        # Initialize UI components
        self.initUI()

        # Update all keys to set visibility
        self.update_all_keys()
        
        # Schedule verification after the event loop has processed the UI updates
        QTimer.singleShot(0, self.run_verifications)

        # Initialize key states
        self.initialize_key_states()

        # Update status bar
        self.update_status_bar()

        # Set focus to 'All' tab
        self.tab_widget.setCurrentIndex(0)

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Apply stylesheet to selected tab
        self.apply_selected_tab_style(self.tab_widget.currentIndex())

        # Ensure focus
        self.centralWidget().setFocusPolicy(Qt.StrongFocus)
        self.centralWidget().setFocus()

        self.logger.debug("Initialization complete. All tabs should be properly set up.")

        # Initial NUM LOCK status update
        self.update_num_lock_status()

        # Prevent Tab from changing focus
        self.setTabOrder(self, self)
    
    def precompute_styles(self):
        """
        Precomputes and stores styles for each key category based on the current theme.
        Includes styles for both normal and pressed states.
        """
        self.precomputed_styles = {}
        for category in BINDING_CATEGORIES.keys():
            color_key = f"key_{category.lower()}"
            background_color = THEMES.get(CURRENT_THEME, {}).get(color_key, THEMES[CURRENT_THEME].get("key_bound", "#000000"))
            pressed_color = self.darken_color(background_color)  # Define a function to darken the color
            
            self.precomputed_styles[category] = {
                "normal": f"""
                    QPushButton {{
                        background-color: {background_color};
                        color: {THEMES[CURRENT_THEME]['text']};
                        border: 1px solid #555555;
                        border-radius: 3px;
                        font-weight: bold;
                        font-size: 10px;
                        text-align: center;
                        padding: 2px;
                    }}
                """,
                "pressed": f"""
                    QPushButton {{
                        background-color: {pressed_color};
                        color: {THEMES[CURRENT_THEME]['text']};
                        border: 1px solid #555555;
                        border-radius: 3px;
                        font-weight: bold;
                        font-size: 10px;
                        text-align: center;
                        padding: 2px;
                    }}
                """
            }
            
            # Log the assigned colors
            self.debug_log(
                category='Style Precomputation',
                message=f"Category '{category}': Normal color = {background_color}, Pressed color = {pressed_color}.",
                level='INFO'
            )
        
        # Precompute styles for 'General' category
        general_color = THEMES.get(CURRENT_THEME, {}).get("key_general", THEMES[CURRENT_THEME].get("key_bound", "#000000"))
        general_pressed_color = self.darken_color(general_color)
        self.precomputed_styles["General"] = {
            "normal": f"""
                QPushButton {{
                    background-color: {general_color};
                    color: {THEMES[CURRENT_THEME]['text']};
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                    padding: 2px;
                }}
            """,
            "pressed": f"""
                QPushButton {{
                    background-color: {general_pressed_color};
                    color: {THEMES[CURRENT_THEME]['text']};
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                    padding: 2px;
                }}
            """
        }
        self.debug_log(
            category='Style Precomputation',
            message=f"Category 'General': Normal color = {general_color}, Pressed color = {general_pressed_color}.",
            level='INFO'
        )
        
        # Precompute styles for 'Normal' keys (no bindings)
        normal_color = THEMES.get(CURRENT_THEME, {}).get("key_normal", "#555555")
        normal_pressed_color = self.darken_color(normal_color)
        self.precomputed_styles["Normal"] = {
            "normal": f"""
                QPushButton {{
                    background-color: {normal_color};
                    color: {THEMES[CURRENT_THEME]['text']};
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                    padding: 2px;
                }}
            """,
            "pressed": f"""
                QPushButton {{
                    background-color: {normal_pressed_color};
                    color: {THEMES[CURRENT_THEME]['text']};
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                    padding: 2px;
                }}
            """
        }
        self.debug_log(
            category='Style Precomputation',
            message=f"Category 'Normal': Normal color = {normal_color}, Pressed color = {normal_pressed_color}.",
            level='INFO'
        )
        
        self.debug_log("Style Precomputation", "Precomputed styles for all categories.", level='DEBUG')
               
    def initUI(self): # Sets up the user interface components of the GUI.
        """
        Sets up the user interface components of the GUI.
        This includes creating the main window, menus, and layout.
        """
        # Set window properties
        self.setWindowTitle(
            "[Dev build] -- Elite: Dangerous Keybinds Visualizer v1.1B - by @glassesinsession"
        )
        self.setGeometry(100, 100, 1200, 400)
        self.setMinimumSize(1200, 400)
        self.setStyleSheet(
            f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};"
        )

        # Create menu bar and status bar
        self.create_menus()
        self.status_bar = self.statusBar()
        
        # Create and add key_block_status_label to the status bar
        self.key_block_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.key_block_status_label)

        # Set up main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.create_tabs()

    def create_menus(self):
        """
        Creates the application's menu bar and adds menu items.
        """
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        self.add_menu_action(file_menu, "Load Keybind File", self.load_bindings)
        self.add_menu_action(file_menu, "Save Current Bindings", self.save_bindings)

        # View menu
        view_menu = menubar.addMenu("View")
        self.toggle_general_keys_action = self.add_menu_action(
            view_menu, "Show General Keys", self.toggle_general_keys, checkable=True
        )
        self.toggle_general_keys_action.setChecked(self.show_general_keys)
        self.add_menu_action(
            view_menu, "Show Unbound Actions", self.show_unbound_actions
        )

    def add_menu_action(self, menu, name, slot, checkable=False): # Helper method to add an action to a menu.
        """
        Helper method to add an action to a menu.

        :param menu: The QMenu to add the action to
        :param name: The name of the action
        :param slot: The method to call when the action is triggered
        :param checkable: Whether the action is checkable
        :return: The created QAction
        """
        action = QAction(name, self)
        action.triggered.connect(slot)
        action.setCheckable(checkable)
        menu.addAction(action)
        return action

    def create_tabs(self): # Creates the tab widget and adds keyboard tabs for each category.
        """
        Creates the tab widget and adds keyboard tabs for each category.
        """
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create 'All' tab first
        self.add_keyboard_tab("All", "QWERTY")

        # Add additional category-based tabs
        for category in BINDING_CATEGORIES.keys():
            self.add_keyboard_tab(category, "QWERTY")

    def initialize_key_states(self):
        """
        Initializes the state of each key (pressed or released) to False.
        """
        self.key_states = {}
        for category, keys in self.key_buttons.items():
            for key_name in keys:
                self.key_states[key_name] = False
        self.logger.debug("Initialized all key states to False.")
    
    def create_log_display(self): # Creates and sets up the log display widget and clear log button.
        """
        Creates and sets up the log display widget and clear log button.
        """
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.log_text.setMinimumHeight(150)
        self.main_layout.addWidget(self.log_text)

        self.clear_log_button = QPushButton("Clear Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        self.main_layout.addWidget(self.clear_log_button)

    def clear_log(self): # Clears the log display widget
        """
        Clears the log display widget.
        """
        self.log_text.clear()
        logging.info("Log cleared by user.")

    
    
    ### Keyboard Tab and Button Management
    
    def add_keyboard_tab(self, category, layout_name): # Creates a new tab in the tab widget for the specified category using the given layout.
        """
        Creates a new tab in the tab widget for the specified category using the given layout.

        :param category: The category name (e.g., "All", "Ship", "General")
        :param layout_name: The layout identifier (e.g., "QWERTY")
        """
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        keyboard_layout = QHBoxLayout()
        keyboard_layout.setSpacing(10)

        # Fetch the specific layout sections from LAYOUTS
        main_layout = LAYOUTS.get(layout_name, {}).get("main", [])
        nav_layout = LAYOUTS.get(layout_name, {}).get("nav", [])
        numpad_layout = LAYOUTS.get(layout_name, {}).get("numpad", [])

        # Create keyboard sections
        main_keyboard = self.create_keyboard_section(main_layout, category)
        keyboard_layout.addLayout(main_keyboard, 70)

        nav_section = self.create_keyboard_section(nav_layout, category, key_size=1.2)
        keyboard_layout.addLayout(nav_section, 15)

        numpad_section = self.create_keyboard_section(numpad_layout, category, key_size=1.2)
        keyboard_layout.addLayout(numpad_section, 15)

        tab_layout.addLayout(keyboard_layout)
        self.tab_widget.addTab(tab, category)

    def create_keyboard_section(self, layout, tab_category, key_size=1.0): # Creates a section of the keyboard (main, navigation, or numpad).
        """
        Creates a section of the keyboard (main, navigation, or numpad).

        :param layout: The layout data for this section
        :param tab_category: The category of the current tab
        :param key_size: The size multiplier for keys in this section
        :return: A QGridLayout containing the keyboard section
        """

        section_layout = QGridLayout()
        section_layout.setSpacing(4)
        section_layout.setContentsMargins(2, 2, 2, 2)

        for row_idx, key_row in enumerate(layout):
            col_idx = 0
            for key_data in key_row:
                if isinstance(key_data, (tuple, list)):
                    if len(key_data) == 4:
                        key_name, display_label, size, row_span = key_data
                    elif len(key_data) == 3:
                        key_name, display_label, size = key_data
                        row_span = 1
                    else:
                        key_name, display_label, size, row_span = "", "", key_data[0], 1
                else:
                    # Handle the case where key_data is not a tuple or list
                    key_name, display_label, size, row_span = "", "", key_data, 1

                # Ensure size is a number
                size = float(size) if isinstance(size, (int, float)) else 1.0
                col_span = int(size * 2 * key_size)

                if not key_name:
                    empty_widget = QWidget()
                    empty_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    empty_widget.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']};")
                    section_layout.addWidget(empty_widget, row_idx, col_idx, row_span, col_span)
                else:
                    button = self.create_key_button(key_name, display_label, size * key_size, tab_category)
                    section_layout.addWidget(button, row_idx, col_idx, row_span, col_span)

                    if tab_category not in self.key_buttons:
                        self.key_buttons[tab_category] = {}
                    self.key_buttons[tab_category][key_name] = button

                self.logger.debug(f"Placing '{key_name}' at row {row_idx}, column {col_idx} with colspan {col_span}.") # UNDO to check all keys mapping to the keyboard
                col_idx += col_span

        for i in range(col_idx):
            section_layout.setColumnStretch(i, 1)

        return section_layout

    def create_key_button(self, key_name, display_label, size, category):
        """
        Creates a single key button for the keyboard layout.
        
        :param key_name: The internal name of the key (e.g., "Key_NumLock")
        :param display_label: The label to display on the key (e.g., "Num Lock")
        :param size: The size of the key
        :param category: The category of the current tab
        :return: A QPushButton representing the key
        """
        
        # Instantiate the button first
        button = QPushButton(display_label)
        
        # Set focus policy to NoFocus to prevent buttons from receiving focus
        button.setFocusPolicy(Qt.NoFocus)
        
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumSize(int(self.base_key_size * size), self.base_key_size)

        # **Remove or comment out the event filter installation**
        # button.installEventFilter(ButtonEventFilter(button))
        
        # Retrieve relevant actions
        bound_actions = self.ed_keys.get_bound_actions(key_name)
        
        # Determine primary category
        primary_category = self.determine_primary_category(bound_actions, category)
        
        # Get the appropriate style
        style = self.get_button_style(primary_category, bound_actions, category, is_pressed=False)
        button.setStyleSheet(style)
        
        # Set properties for later reference
        button.setProperty("primary_category", primary_category)
        button.setProperty("bound_actions", bound_actions)
        button.setProperty("is_pressed", False)
        
        # Set tooltip
        tooltip = self.create_tooltip(bound_actions, category)
        button.setToolTip(tooltip)
        
        # Connect signals
        button.pressed.connect(lambda b=button, k=key_name: self.on_button_press(b, k))
        button.released.connect(lambda b=button, k=key_name: self.on_button_release(b, k))
        
        # Add button to the category's button dictionary
        if category not in self.key_buttons:
            self.key_buttons[category] = {}
        self.key_buttons[category][key_name] = button
        
        # self.debug_log(  # DEBUG
        #     category='Button Creation',
        #     message=f"Created button '{key_name}' in category '{category}'.",
        #     level='DEBUG'
        # )
        
        return button

    def get_button_style(self, primary_category, bound_actions, tab_category, is_pressed=False):
        """
        Retrieves the precomputed stylesheet for a key button based on its category and state.
        
        :param primary_category: The primary category of the key's bindings
        :param bound_actions: List of actions bound to this key
        :param tab_category: The category of the current tab
        :param is_pressed: Boolean indicating if the key is pressed
        :return: A stylesheet string for the button
        """
        
        state = "pressed" if is_pressed else "normal"
        
        if not bound_actions:
            return self.precomputed_styles["Normal"][state]
        
        if tab_category == "All":
            return self.precomputed_styles.get(primary_category, {}).get(state, self.precomputed_styles["Normal"][state])
        
        if primary_category == "General" or tab_category == "General":
            if self.show_general_keys or tab_category == "General":
                return self.precomputed_styles["General"][state]
        
        if primary_category == tab_category:
            return self.precomputed_styles.get(primary_category, {}).get(state, self.precomputed_styles["Normal"][state])
        
        return self.precomputed_styles["Normal"][state]
  
    def create_tooltip(self, bound_actions, tab_category): # Creates a tooltip for a key button showing its bound actions.
        """
        Creates a tooltip for a key button showing its bound actions.

        :param bound_actions: List of actions bound to the key
        :param tab_category: The category of the current tab
        :return: A string to use as the button's tooltip
        """
        relevant_actions = self.get_relevant_actions(bound_actions, tab_category)
        if relevant_actions:
            return "\n".join(relevant_actions)
        return "Unassigned"

    def toggle_general_keys(self): # Toggles the visibility of general keys and updates the display.
        """
        Toggles the visibility of general keys and updates the display.
        """
        self.show_general_keys = not self.show_general_keys
        self.update_all_keys()



    # Key Event Handling and Visual Updates

    def handle_key_event(self, event, is_press):
        if event.isAutoRepeat():
            return

        key = event.key()
        key_name = self.get_key_name(event)

        if key_name:
            self.track_pressed_keys(key_name, is_press)
            self.update_key_visual(key_name, is_press)
            self.debug_log("Key Event", "Key action", key=key_name, action="pressed" if is_press else "released")
            
            if key == Qt.Key_Tab:
                self.debug_log("Tab Key", f"{'Press' if is_press else 'Release'} event handled", 
                            key_name=key_name, scan_code=event.nativeScanCode())
            
            # Handle AltGr
            if key_name == "Key_RightAlt":  
                self.handle_altgr_event(is_press)
            else:
                self.track_pressed_keys(key_name, is_press)
                self.update_key_visual(key_name, is_press)
            
            # Handle NUM LOCK directly
            if key_name == "Key_NumLock" and not is_press:
                numlock_on = is_numlock_on()
                self.update_status_bar_numlock(numlock_on)

        # Allow default behavior for all keys
        if self.should_block_key(key):
            event.accept()
        else:
            super().keyPressEvent(event) if is_press else super().keyReleaseEvent(event)

    def handle_altgr_event(self, is_press): # NEW
        self.track_pressed_keys("Key_RightAlt", is_press)
        self.update_key_visual("Key_RightAlt", is_press)
        
        # Ensure left Ctrl is not affected
        if "Key_LeftControl" in self.active_keys:
            self.active_keys.discard("Key_LeftControl")
            self.update_key_visual("Key_LeftControl", False)
        
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key_Tab:
            self.handle_key_event(event, True)
            # Prevent default focus shifting
            event.accept()
            return  # Exit to prevent further handling
        
        self.handle_key_event(event, True)
        # print(f"Main window received key press: {event.key()}")  # Debug print
        
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key = event.key()
        
        if key == Qt.Key_Tab:
            self.handle_key_event(event, False)
            # Prevent default focus shifting
            event.accept()
            return  # Exit to prevent further handling
        
        self.handle_key_event(event, False)
        
        super().keyReleaseEvent(event)
          
    def get_key_name(self, event):
        """
        Determines the name of the key from a key event.
        
        :param event: The key event from Qt
        :return: The name of the key as a string
        """
        key = event.key()
        modifiers = event.modifiers()
        scan_code = event.nativeScanCode()

        # Special handling for NUM LOCK
        if key == Qt.Key_NumLock:
            return "Key_NumLock"
        
        # Special handling for AltGr
        if scan_code == 312:  # AltGr scan code
            return "Key_RightAlt"

        # Handle modifier keys
        if key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta]:
            if scan_code in SCAN_CODE_MAPPING:
                return SCAN_CODE_MAPPING[scan_code]
            elif key == Qt.Key_Shift:
                return "Key_LeftShift" if scan_code == 42 else "Key_RightShift"
            elif key == Qt.Key_Control:
                return "Key_LeftControl" if scan_code == 29 else "Key_RightControl"
            elif key == Qt.Key_Alt:
                return "Key_LeftAlt" if scan_code == 56 else "Key_RightAlt"
            # elif key == Qt.Key_Meta:
            #     return "Key_LeftWin" if scan_code == 91 else "Key_RightWin"
    
        # Handle numpad keys
        if modifiers & Qt.KeypadModifier:
            numpad_mapping = {
                Qt.Key_0: "Key_Numpad_0",
                Qt.Key_1: "Key_Numpad_1",
                Qt.Key_2: "Key_Numpad_2",
                Qt.Key_3: "Key_Numpad_3",
                Qt.Key_4: "Key_Numpad_4",
                Qt.Key_5: "Key_Numpad_5",
                Qt.Key_6: "Key_Numpad_6",
                Qt.Key_7: "Key_Numpad_7",
                Qt.Key_8: "Key_Numpad_8",
                Qt.Key_9: "Key_Numpad_9",
                Qt.Key_Asterisk: "Key_Numpad_Multiply",
                Qt.Key_Plus: "Key_Numpad_Add",
                Qt.Key_Minus: "Key_Numpad_Subtract",
                Qt.Key_Period: "Key_Numpad_Decimal",
                Qt.Key_Slash: "Key_Numpad_Divide",
                Qt.Key_Enter: "Key_NumpadEnter",
            }
            return numpad_mapping.get(key, None)

        # Use the KEY_MAPPING for other keys
        key_name = KEY_MAPPING.get(key)
        if key_name:
            return key_name

        # If not found in KEY_MAPPING, use the text
        text = event.text().upper()
        if text:
            return f"Key_{text}"

        # If still not found, log the unmapped key
        logging.warning(f"Unmapped key: Qt Key {key}, Scan Code {scan_code}")
        return None

    def should_block_key(self, key): # Determines if a key's default behavior should be blocked.
        """
        Determines if a key's default behavior should be blocked.
        
        :param key: The key code
        :return: Boolean indicating if the key should be blocked
        """
        blocked_keys = [
            Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down,
            Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End,
            Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space
        ]
        return key in blocked_keys

    def prevent_tab_focus_change(self, old_focus_widget):
        """
        Prevents focus change when Tab is pressed and returns focus to the previous widget.
        
        :param old_focus_widget: The widget that had focus before Tab was pressed
        """
        if old_focus_widget and self.focusWidget() != old_focus_widget:
            old_focus_widget.setFocus()

    def update_key_visual(self, key_name, is_pressed):
        """
        Updates the visual state of a key button.
        
        :param key_name: The name of the key to update
        :param is_pressed: Boolean indicating if the key is pressed
        """
        # self.debug_log("Visual Update", f"Updating key visual for {key_name} - pressed: {is_pressed}") # DEBUG
        
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        categories_to_check = ["All", current_tab]

        for category in categories_to_check:
            if category in self.key_buttons and key_name in self.key_buttons[category]:
                button = self.key_buttons[category][key_name]
                if button.isVisible():
                    primary_category = button.property("primary_category")
                    bound_actions = button.property("bound_actions")
                    
                    # Special handling for AltGr
                    if key_name == "Key_RightAlt" and is_pressed:
                        # Ensure left Ctrl is not visually pressed when AltGr is pressed
                        if "Key_LeftControl" in self.key_buttons[category]:
                            left_ctrl_button = self.key_buttons[category]["Key_LeftControl"]
                            left_ctrl_style = self.get_button_style(
                                left_ctrl_button.property("primary_category"),
                                left_ctrl_button.property("bound_actions"),
                                current_tab,
                                is_pressed=False
                            )
                            left_ctrl_button.setStyleSheet(left_ctrl_style)
                            left_ctrl_button.update()

                    # Update the style for the current key
                    style = self.get_button_style(
                        primary_category,
                        bound_actions,
                        current_tab,
                        is_pressed=is_pressed
                    )
                    button.setStyleSheet(style)
                    button.update()
                    
                    # self.debug_log("Visual Update", f"Updated {key_name} in category {category}", style=style)
                    return  # Exit after updating the button
                else:
                    self.debug_log("Visual Update", f"Button for {key_name} in category {category} is not visible")
        
        self.debug_log("Visual Update", f"Key {key_name} not found or not visible in current tab or All tab")
    
    def track_pressed_keys(self, key_name, is_pressed):
        if is_pressed:
            self.active_keys.add(key_name)
            if key_name == "Key_RightAlt":
                self.active_keys.discard("Key_LeftControl")
        else:
            self.active_keys.discard(key_name)
        
        logging.debug(f"Active keys updated. Currently pressed: {self.active_keys}")
              
    # def update_button_state(self, button, is_pressed):
    #     """
    #     Updates the visual state of a key button.
        
    #     :param button: The QPushButton representing the key
    #     :param is_pressed: Boolean indicating if the key is pressed
    #     """
    #     primary_category = button.property("primary_category")
    #     relevant_actions = button.property("relevant_actions")
    #     tab_category = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
    #     # Fetch the appropriate style using get_button_style
    #     style = self.get_button_style(primary_category, relevant_actions, tab_category, is_pressed=is_pressed)
        
    #     # Ensure that 'style' is a string before applying
    #     if isinstance(style, str):
    #         button.setStyleSheet(style)
    #         button.update()
    #         self.debug_log("Button Update", f"Button state updated", background_color=style, is_pressed=is_pressed)
    #     else:
    #         logging.error(f"Expected a stylesheet string, but got {type(style)} for button '{button.text()}'.")
 
    def update_button_state(self, button, is_pressed):
        """
        Updates the visual state of a key button.
        
        :param button: The QPushButton representing the key
        :param is_pressed: Boolean indicating if the key is pressed
        :return: True if the button style was changed, False otherwise
        """
        primary_category = button.property("primary_category")
        relevant_actions = button.property("relevant_actions")
        tab_category = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        old_style = button.styleSheet()
        new_style = self.get_button_style(primary_category, relevant_actions, tab_category, is_pressed=is_pressed)
        
        if old_style != new_style:
            button.setStyleSheet(new_style)
            button.update()
            return True
        return False
    
    def create_pressed_style(self, original_style): # Creates a 'pressed' style for a button based on its original style.
        """
        Creates a 'pressed' style for a button based on its original style.
        
        :param original_style: The original stylesheet of the button
        :return: A new stylesheet for the button's pressed state
        """
        bg_color = None
        for rule in original_style.split(';'):
            if 'background-color:' in rule:
                bg_color = rule.split(':')[1].strip()
                break

        if bg_color:
            darker_color = self.darken_color(bg_color)
            pressed_style = original_style.replace(f"background-color: {bg_color}", f"background-color: {darker_color}")
        else:
            pressed_style = original_style

        return pressed_style

    def darken_color(self, color): # Darkens a given color by reducing its RGB values.
        """
        Darkens a given color by reducing its RGB values.
        
        :param color: The original color in hex format
        :return: The darkened color in hex format
        """
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(int(r * 0.8), 0)
        g = max(int(g * 0.8), 0)
        b = max(int(b * 0.8), 0)
        return f"#{r:02x}{g:02x}{b:02x}"

    def lighter_color(self, color): # Calculates a lighter shade of the given color.
        """
        Calculates a lighter shade of the given color.
        
        :param color: Hex color string (e.g., '#555555').
        :return: Hex color string for the lighter shade.
        """
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        # Increase each component by 20%, but not exceeding 255
        r = min(int(r * 1.2), 255)
        g = min(int(g * 1.2), 255)
        b = min(int(b * 1.2), 255)

        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'



    # Key Updates and Tab Handling

    def update_all_keys(self):
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        updated_keys_count = 0
        hidden_keys_count = 0
        
        for category, buttons in self.key_buttons.items():
            for key_name, button in buttons.items():
                bound_actions = self.ed_keys.get_bound_actions(key_name)
                
                if current_tab == "All":
                    relevant_actions = bound_actions
                elif current_tab == "General":
                    relevant_actions = [action for action in bound_actions if action in BINDING_CATEGORIES["General"]]
                else:
                    relevant_actions = [action for action in bound_actions if action in BINDING_CATEGORIES.get(current_tab, [])]
                    if self.show_general_keys:
                        relevant_actions += [action for action in bound_actions if action in BINDING_CATEGORIES["General"]]
        
                primary_category = self.determine_primary_category(relevant_actions, current_tab)
                
                style = self.get_button_style(primary_category, relevant_actions, current_tab, is_pressed=(key_name in self.active_keys))
                button.setStyleSheet(style)
                button.setProperty("primary_category", primary_category)
                button.setProperty("bound_actions", bound_actions)
                button.setProperty("relevant_actions", relevant_actions)
                
                tooltip = self.create_tooltip(relevant_actions, current_tab)
                button.setToolTip(tooltip)
                
                if category == current_tab or category == "All" or (self.show_general_keys and primary_category == "General"):
                    button.show()
                    updated_keys_count += 1
                else:
                    button.hide()
                    hidden_keys_count += 1
                
                button.update()

        self.logger.info(f"Updated all keys for tab '{current_tab}'. Show General Keys: {self.show_general_keys}")
        self.logger.debug(f"Tab: '{current_tab}'. {updated_keys_count} keys updated, {hidden_keys_count} keys hidden.")
     
    def on_tab_changed(self, index):
        """
        Handles the event when the user switches tabs.
        
        :param index: The index of the newly selected tab
        """
        self.update_all_keys()
        self.apply_selected_tab_style(index)
        
        current_tab = self.tab_widget.tabText(index)
        updates = []
        
        for key_name, button in self.key_buttons.get(current_tab, {}).items():
            is_pressed = key_name in self.active_keys
            if self.update_button_state(button, is_pressed):
                updates.append(f"{key_name}: {'pressed' if is_pressed else 'normal'}")
        
        # if updates:
        #     self.debug_log(
        #         category='Tab Change',
        #         message=f"Tab changed to {current_tab}. Updated keys: {', '.join(updates)}",
        #         level='DEBUG'
        #     )
        # else:
        #     self.debug_log(
        #         category='Tab Change',
        #         message=f"Tab changed to {current_tab}. No key updates needed.",
        #         level='DEBUG'
        #     )

    def apply_selected_tab_style(self, index): # Applies the appropriate style to the selected tab.
        """
        Applies the appropriate style to the selected tab.
        
        :param index: The index of the selected tab
        """
        group_color = self.get_group_color(index)
        text_color = THEMES[CURRENT_THEME]['text']

        selected_tab_stylesheet = f"""
        QTabBar::tab:selected {{
            background-color: {group_color};
            border-color: {group_color};
            border-bottom: 2px solid {text_color};
            font-weight: bold;
        }}
        """

        full_stylesheet = self.base_stylesheet + selected_tab_stylesheet
        self.tab_widget.setStyleSheet(full_stylesheet)

    def get_group_color(self, tab_index): # Retrieves the color associated with the group's tab.
        """
        Retrieves the color associated with the group's tab.
        
        :param tab_index: The index of the selected tab
        :return: Hex color string for the group
        """
        group_name = self.tab_widget.tabText(tab_index)
        color_key = f"key_{group_name.lower()}"
        return THEMES[CURRENT_THEME].get(color_key, THEMES[CURRENT_THEME]["key_bound"])

    def determine_primary_category(self, actions, tab_category):
        if not actions:
            return "Normal"  # Unbound keys
        
        categories = set()
        for action in actions:
            for category, cat_actions in BINDING_CATEGORIES.items():
                if action in cat_actions:
                    categories.add(category)
                    break
        
        if not categories:
            return "General"
        elif len(categories) == 1:
            return categories.pop()
        elif tab_category in categories:
            return tab_category
        else:
            # Prioritize non-General categories
            non_general = categories - {"General"}
            return next(iter(non_general)) if non_general else "General"
    
    def get_binding_category(self, binding): # Determines the category of a specific binding.
        """
        Determines the category of a specific binding.
        
        :param binding: The binding action to categorize
        :return: The category of the binding
        """
        for category, actions in BINDING_CATEGORIES.items():
            if binding in actions:
                return category
        return "General"

    def get_relevant_actions(self, actions, tab_category): # Filters actions to only those relevant for the current tab category.
        """
        Filters actions to only those relevant for the current tab category.
        
        :param actions: List of all actions bound to a key
        :param tab_category: The category of the current tab
        :return: List of actions relevant to the current tab
        """
        if tab_category == "All":
            return actions
        return [action for action in actions if self.get_binding_category(action) in [tab_category, "General"]]

    def on_button_press(self, button, key_name):
        """
        Handles the visual update when a key button is pressed.
        
        :param button: The QPushButton representing the key
        :param key_name: The name of the key
        """

        # For other keys, apply pressed style
        style = self.get_button_style(
            button.property("primary_category"),
            button.property("relevant_actions"),
            self.tab_widget.tabText(self.tab_widget.currentIndex()),
            is_pressed=True
        )
        button.setStyleSheet(style)
        self.active_keys.add(key_name)
        self.debug_log(
            category='Button Press',
            message=f"Key '{key_name}' pressed.",
            level='DEBUG'
        )

    def on_button_release(self, button, key_name):
        """
        Handles the visual update when a key button is released.
        
        :param button: The QPushButton representing the key
        :param key_name: The name of the key
        """
        
        # For other keys, revert to normal style
        style = self.get_button_style(
            button.property("primary_category"),
            button.property("relevant_actions"),
            self.tab_widget.tabText(self.tab_widget.currentIndex()),
            is_pressed=False
        )
        button.setStyleSheet(style)
        self.active_keys.discard(key_name)
        self.debug_log(
            category='Button Release',
            message=f"Key '{key_name}' released.",
            level='DEBUG'
        )



    # NUM LOCK handling
    
    def update_num_lock_status(self):
        """
        Checks the current state of NUM LOCK and updates the status bar accordingly.
        """
        numlock_on = is_numlock_on()
        self.update_status_bar_numlock(numlock_on)
    
    def update_num_lock_button(self, is_on):
        """
        Updates the visual state of the NUM LOCK key button based on its current state.

        :param is_on: Boolean indicating if NUM LOCK is active
        """
        key_name = "Key_NumLock"
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        categories_to_check = ["All", current_tab]

        for category in categories_to_check:
            if category in self.key_buttons and key_name in self.key_buttons[category]:
                button = self.key_buttons[category][key_name]
                # Update the style to reflect the NUM LOCK state
                style = self.get_button_style(
                    "General",
                    self.ed_keys.get_bound_actions(key_name),
                    current_tab,
                    is_pressed=is_on
                )
                button.setStyleSheet(style)
                button.update()
                break  # NUM LOCK key found and updated
            
    def update_status_bar_numlock(self, is_on):
        """
        Updates the status bar to display the current state of NUM LOCK.

        :param is_on: Boolean indicating if NUM LOCK is active
        """
        status = "ON" if is_on else "OFF"
        self.status_bar.showMessage(f"NUM LOCK: {status}", 10000)  # Message disappears after 10 seconds


    # TAB handling
    
    def focusNextPrevChild(self, next):
        # Disable focus traversal
        return False


    # Other misc.
    
    def load_bindings(self): # Loads key bindings from the binds file.
        """
        Loads key bindings from the binds file.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Keybind File", "", "Bind Files (*.binds)")
        if file_path:
            try:
                self.ed_keys.binds_file = file_path
                self.ed_keys.bindings = self.ed_keys.parse_binds_file()
                self.update_all_keys()
                self.status_bar.showMessage(f"Bindings loaded from {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load bindings: {str(e)}")

    def save_bindings(self): # Saves current key bindings to a file.
        """
        Saves current key bindings to a file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Keybind File", "", "Bind Files (*.binds)")
        if file_path:
            try:
                # Assuming ed_keys has a method to save bindings
                self.ed_keys.save_bindings_to_file(file_path)
                self.status_bar.showMessage(f"Bindings saved to {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save bindings: {str(e)}")

    def show_unbound_actions(self): # Displays a dialog showing all unbound actions.
        """
        Displays a dialog showing all unbound actions.
        """
        unbound_actions = self.get_unbound_actions()
        if not unbound_actions:
            QMessageBox.information(self, "Unbound Actions", "All actions are currently bound to keys.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Unbound Actions")
        layout = QVBoxLayout(dialog)

        for category, actions in unbound_actions.items():
            if actions:
                group_box = QGroupBox(category)
                group_layout = QVBoxLayout()
                for action in actions:
                    group_layout.addWidget(QLabel(action))
                group_box.setLayout(group_layout)
                layout.addWidget(group_box)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec_()

    def get_unbound_actions(self): # Retrieves a list of all actions that are not bound to any key.
        """
        Retrieves a list of all actions that are not bound to any key.
        """
        unbound = {}
        all_bound_actions = set()
        for actions in self.ed_keys.bindings.values():
            all_bound_actions.update(actions)

        for category, actions in BINDING_CATEGORIES.items():
            unbound_actions = [action for action in actions if action not in all_bound_actions]
            if unbound_actions:
                unbound[category] = unbound_actions

        return unbound

    def assign_key(self, key_name): # Opens a dialog to assign or unbind actions for a specific key
        """
        Opens a dialog to assign or unbind actions for a specific key.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Assign Key: {key_name}")
        layout = QVBoxLayout(dialog)

        current_bindings = self.ed_keys.get_bound_actions(key_name)
        all_actions = [action for category in BINDING_CATEGORIES.values() for action in category]

        action_list = QListWidget()
        for action in all_actions:
            item = QListWidgetItem(action)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if action in current_bindings else Qt.Unchecked)
            action_list.addItem(item)

        layout.addWidget(action_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            new_bindings = []
            for i in range(action_list.count()):
                item = action_list.item(i)
                if item.checkState() == Qt.Checked:
                    new_bindings.append(item.text())
            
            self.ed_keys.bindings[key_name] = new_bindings
            self.update_all_keys()

    def reset_active_keys(self): # Resets the state of all active keys.
        """
        Resets the state of all active keys.
        """
        self.active_keys.clear()
        self.update_all_key_visuals()
        self.status_bar.showMessage("Active keys reset", 3000)

    def toggle_global_key_logging(self, state): # Toggles global key logging on or off.
        """
        Toggles global key logging on or off. Enabling it allows the application to log *all* your keypresses. Useful for debugging, but be careful to not write anything that could be compromising. :)
        """
        if state:
            self.start_global_key_logging()
        else:
            self.stop_global_key_logging()

    def start_global_key_logging(self): # Starts global key logging.
        """
        Starts global key logging.
        """
        self.key_logger = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.key_logger.start()
        self.status_bar.showMessage("Global key logging started", 3000)

    def stop_global_key_logging(self): # Stops global key logging.
        """
        Stops global key logging.
        """
        if hasattr(self, 'key_logger'):
            self.key_logger.stop()
            self.status_bar.showMessage("Global key logging stopped", 3000)

    def on_key_press(self, key): # Handles global key press events when logging is enabled.
        """
        Handles global key press events when logging is enabled.
        """
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        logging.info(f"Key pressed: {key_char}")

    def on_key_release(self, key): # Handles global key release events when logging is enabled.
        """
        Handles global key release events when logging is enabled.
        """
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        logging.info(f"Key released: {key_char}")

    def update_status_bar(self):
        if self.is_key_dialog_open:
            status = "Keys Unblocked (Dialog Open)"
            color = "green"
        else:
            status = "Keys Blocked (Main Interface)"
            color = "red"
        self.key_block_status_label.setText(f"<font color='{color}'>{status}</font>")
        self.logger.debug(f"Status bar updated: {status}")

    def closeEvent(self, event):
        # Remove our custom handler before the application closes
        for handler in self.logger.handlers[:]:
            if isinstance(handler, QTextEditLogger):
                self.logger.removeHandler(handler)
                handler.close()
        super().closeEvent(event)


    ### Debugging
    
    def verify_key_mappings(self):
        logging.info("Verifying key mappings...")
        all_layout_keys = set()
        for layout in LAYOUTS["QWERTY"].values():
            for row in layout:
                for key_data in row:
                    if isinstance(key_data, (tuple, list)) and len(key_data) >= 1:
                        all_layout_keys.add(key_data[0])

        mapped_keys = set(KEY_MAPPING.values())
        unmapped_layout_keys = all_layout_keys - mapped_keys
        unmapped_dict_keys = mapped_keys - all_layout_keys

        if unmapped_layout_keys:
            logging.warning(f"Layout keys not in KEY_MAPPING: {unmapped_layout_keys}")
        if unmapped_dict_keys:
            logging.warning(f"KEY_MAPPING keys not in layout: {unmapped_dict_keys}")

        # Check if all keys in the layout have corresponding buttons
        for category, keys in self.key_buttons.items():
            for key_name in all_layout_keys:
                if key_name not in keys:
                    logging.warning(f"No button created for key: {key_name} in category: {category}")

        logging.info("Key mapping verification complete.")
    
    def verify_color_assignments(self):
        """
        Verifies that each category has a corresponding color assigned in the THEMES dictionary.
        Logs the result of the verification.
        """
        all_categories = set(BINDING_CATEGORIES.keys())
        all_categories.add("General")  # Include General if it's handled separately

        missing_colors = []
        duplicate_colors = {}
        color_assignments = {}

        for category in all_categories:
            color_key = f"key_{category.lower()}"
            color = THEMES.get(CURRENT_THEME, {}).get(color_key)
            if not color:
                missing_colors.append(color_key)
                self.debug_log(
                    category='Color Verification',
                    message=f"Missing color for category '{category}' with key '{color_key}'.",
                    level='WARNING'
                )
            else:
                if color in color_assignments:
                    # Duplicate color found
                    if color not in duplicate_colors:
                        duplicate_colors[color] = [color_assignments[color]]
                    duplicate_colors[color].append(category)
                else:
                    color_assignments[color] = category

        if not missing_colors and not duplicate_colors:
            self.debug_log(
                category='Color Verification',
                message="All categories have unique and assigned colors.",
                level='INFO'
            )
        else:
            if missing_colors:
                self.debug_log(
                    category='Color Verification',
                    message=f"Missing colors for categories: {', '.join(missing_colors)}.",
                    level='ERROR'
                )
            if duplicate_colors:
                duplicates = "; ".join([f"Color '{color}' assigned to categories: {', '.join(cats)}" for color, cats in duplicate_colors.items()])
                self.debug_log(
                    category='Color Verification',
                    message=f"Duplicate color assignments found: {duplicates}.",
                    level='ERROR'
                )

    def verify_buttons(self):
        expected_keys = [
            "Key_NumLock", 
            # "Key_A", "Key_S", "Key_D", "Key_W", "Key_E",
            # "Key_R", "Key_F", "Key_G", "Key_Z", "Key_X", "Key_C",
            # Add more keys as needed to test
        ]
        
        for key in expected_keys:
            found = False
            for category, buttons in self.key_buttons.items():
                if key in buttons:
                    found = True
                    button = buttons[key]
                    if not button.isVisible():
                        self.debug_log(
                            category='Button Verification',
                            message=f"Button '{key}' exists in category '{category}' but is not visible.",
                            level='WARNING'
                        )
                    else:
                        self.debug_log(
                            category='Button Verification',
                            message=f"Button '{key}' exists and is visible in category '{category}'.",
                            level='DEBUG'
                        )
                        
                        # Additional check for NUM LOCK styling
                        if key == "Key_NumLock":
                            style = button.styleSheet()
                            self.debug_log(
                                category='Button Verification',
                                message=f"NUM LOCK button style: {style}",
                                level='DEBUG'
                            )
                    break
            if not found:
                self.debug_log(
                    category='Button Verification',
                    message=f"Button '{key}' not found in any category.",
                    level='ERROR'
                )

    def track_pressed_keys(self, key_name, is_pressed):
        if is_pressed:
            self.active_keys.add(key_name)
        else:
            self.active_keys.discard(key_name)
        
        self.logger.debug(f"Active keys updated. Currently pressed: {self.active_keys}")

    def debug_log(self, category, message, level='DEBUG', **kwargs):
        """
        A custom logging wrapper.
        
        :param category: The category of the log message
        :param message: The main log message
        :param level: The severity level of the log ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        :param kwargs: Additional key-value pairs to include in the log
        """
        level = level.upper()
        log_message = f"{category}: {message}"
        if kwargs:
            log_message += " - " + ", ".join(f"{k}: {v}" for k, v in kwargs.items())

        if level == 'DEBUG':
            self.logger.debug(log_message)
        elif level == 'INFO':
            self.logger.info(log_message)
        elif level == 'WARNING':
            self.logger.warning(log_message)
        elif level == 'ERROR':
            self.logger.error(log_message)
        elif level == 'CRITICAL':
            self.logger.critical(log_message)
        else:
            self.logger.error(f"Invalid log level: {level}")

    def run_verifications(self):
        self.verify_color_assignments()
        self.verify_buttons()
            
            
class ButtonEventFilter(QObject):
    def __init__(self, button, logger):
        super().__init__()
        self.button = button
        self.logger = logger  # Use the configured 'EDKeysGUI' logger

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.logger.debug(f"Button {self.button.text()} filtered key press: {event.key()}")
            
            if event.key() == Qt.Key_Tab:
                # Do not block Tab key, let it propagate
                return False

            # Handle other keys as needed
            self.button.animateClick()
            self.logger.debug(f"Button {self.button.text()} clicked programmatically.")
            return True  # Block other key events after handling
        return super().eventFilter(obj, event)

class PluginManager:
    """
    Manages the loading and unloading of plugins.
    """

    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger  # Use the configured 'EDKeysGUI' logger
        self.plugins = {}  # key: plugin name, value: plugin instance
        self.plugin_paths = {}  # key: plugin name, value: plugin file path

    def load_plugin(self, plugin_path):
        """
        Loads a plugin from the specified file path.
        """
        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        if plugin_name in self.plugins:
            QMessageBox.warning(
                self.parent,
                "Plugin Load Error",
                f"Plugin '{plugin_name}' is already loaded.",
            )
            self.logger.warning(f"Attempted to load already loaded plugin '{plugin_name}'.")
            return

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                plugin_class = getattr(module, "Plugin", None)
                if plugin_class and issubclass(plugin_class, PluginInterface):
                    plugin_instance = plugin_class(self.parent, self.logger)
                    plugin_instance.load()
                    self.plugins[plugin_name] = plugin_instance
                    self.plugin_paths[plugin_name] = plugin_path
                    QMessageBox.information(
                        self.parent,
                        "Plugin Loaded",
                        f"Plugin '{plugin_name}' loaded successfully.",
                    )
                    self.logger.info(f"Plugin '{plugin_name}' loaded successfully.")
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Plugin Load Error",
                        f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.",
                    )
                    self.logger.error(f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.")
            except Exception as e:
                self.logger.error(f"Error loading plugin '{plugin_name}': {e}")
                QMessageBox.critical(
                    self.parent,
                    "Plugin Load Error",
                    f"Failed to load plugin '{plugin_name}': {e}",
                )
        else:
            QMessageBox.warning(
                self.parent,
                "Plugin Load Error",
                f"Could not load plugin from '{plugin_path}'.",
            )
            self.logger.error(f"Could not load plugin from '{plugin_path}'.")

    def unload_plugin(self, plugin_name):
        """
        Unloads the specified plugin.
        """
        if plugin_name not in self.plugins:
            QMessageBox.warning(
                self.parent,
                "Plugin Unload Error",
                f"Plugin '{plugin_name}' is not loaded.",
            )
            self.logger.warning(f"Attempted to unload non-loaded plugin '{plugin_name}'.")
            return

        try:
            self.plugins[plugin_name].unload()
            del self.plugins[plugin_name]
            del self.plugin_paths[plugin_name]
            QMessageBox.information(
                self.parent,
                "Plugin Unloaded",
                f"Plugin '{plugin_name}' unloaded successfully.",
            )
            self.logger.info(f"Plugin '{plugin_name}' unloaded successfully.")
        except Exception as e:
            self.logger.error(f"Error unloading plugin '{plugin_name}': {e}")
            QMessageBox.critical(
                self.parent,
                "Plugin Unload Error",
                f"Failed to unload plugin '{plugin_name}': {e}",
            )

    def toggle_plugin(self, plugin_name):
        """
        Toggles the specified plugin on or off.
        """
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)
        else:
            plugin_path = self.plugin_paths.get(plugin_name)
            if plugin_path:
                self.load_plugin(plugin_path)
            else:
                # Allow user to select the plugin file if path not stored
                plugin_path, _ = QFileDialog.getOpenFileName(
                    self.parent, "Locate Plugin File", "", "Python Files (*.py)"
                )
                if plugin_path:
                    self.load_plugin(plugin_path)
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Toggle Plugin Error",
                        f"Plugin path for '{plugin_name}' not found.",
                    )
                    self.logger.warning(f"Plugin path for '{plugin_name}' not found.")

    def list_plugins(self):
        """
        Returns a list of all available plugins with their load status.
        """
        # List all .py files in the plugins directory
        plugins_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.isdir(plugins_dir):
            os.makedirs(plugins_dir)
            self.logger.info(f"Created plugins directory at '{plugins_dir}'.")

        plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith(".py")]
        all_plugins = set(os.path.splitext(f)[0] for f in plugin_files)
        plugin_list = []
        for plugin in all_plugins:
            status = "Loaded" if plugin in self.plugins else "Not Loaded"
            plugin_list.append((plugin, status))
        self.logger.debug(f"Listed plugins: {plugin_list}")
        return plugin_list    

class PluginInterface:
    """
    A base class for all plugins. Plugins should inherit from this class and implement the load and unload methods.
    """

    def __init__(self, main_window, logger):
        self.main_window = main_window
        self.logger = logger  # Use the configured 'EDKeysGUI' logger

    def load(self):
        """
        Method to load the plugin's functionalities.
        Must be implemented by the plugin.
        """
        raise NotImplementedError("Plugin must implement the load method.")

    def unload(self):
        """
        Method to unload the plugin's functionalities.
        Must be implemented by the plugin.
        """
        raise NotImplementedError("Plugin must implement the unload method.")



def main():
    """Run the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Create the main window and QTextEdit for logging
    main_window = QMainWindow()
    log_text_edit = QTextEdit(main_window)
    log_text_edit.setReadOnly(True)

    # Setup logging and get the configured logger
    logger = setup_logging(log_text_edit)

    # Define base stylesheet without QTabBar::tab:selected
    base_stylesheet = f"""
    QWidget {{
        background-color: {THEMES[CURRENT_THEME]['background']};
        color: {THEMES[CURRENT_THEME]['text']};
    }}
    QTabWidget::pane {{
        border: 1px solid {THEMES[CURRENT_THEME]['key_normal']};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {THEMES[CURRENT_THEME]['key_normal']};
        color: {THEMES[CURRENT_THEME]['text']};
        padding: 8px 16px;
        border: 1px solid {THEMES[CURRENT_THEME]['key_normal']};
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
        min-width: 60px;
    }}
    QTabBar::tab:hover {{
        background-color: {THEMES[CURRENT_THEME]['key_pressed']};
    }}
    QTabWidget::tab-bar {{
        alignment: left;
    }}
    """

    binds_file = "main.binds"
    logger.debug(f"Loading bindings from '{binds_file}'.")
    ed_keys = EDKeys(binds_file, logger)
    logger.debug("Bindings loaded successfully.")

    # Initialize GUI and pass the logger
    ex = KeyboardGUI(ed_keys, base_stylesheet, logger)
    ex.show()
    logger.info("KeyboardGUI initialized and displayed.")

    # Example log messages (for testing purposes)
    # logger.debug("This is a DEBUG message.")
    # logger.info("This is an INFO message.")
    # logger.warning("This is a WARNING message.")
    # logger.error("This is an ERROR message.")
    # logger.critical("This is a CRITICAL message.")

    sys.exit(app.exec_())



if __name__ == "__main__":
    main()