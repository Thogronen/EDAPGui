### Features

# v1.1B-nightly is close to a full rework on how the system works, now using Virtual Keys over hardcoded values to pave the way for multi-language support.
# This version does not contain many of the UI enhancements NOR key-rebinding ability, but will show you what keys you have bound over different categories.

# - [x] An overview of your chosen (or, last used by default) keybind file
# - [x] Ability to quickly and easily re-bind keys
# - [ ] Colour schemes/themes + tab grouping
# - [x] Overview of what actions you have not bound
# - [ ] A search bar, allowing you to look for binds
# - [x] Key highlights on press
# - [?] Drag n'Drop Interface (Drag actions from list to key)
# - [x] Quick Bind mode - Select an action, then press a key to bind it
# - [-] Conflict detection - If a key is already bound, highlight it. This should not happen unless you're using the same key for multiple actions.
# - [ ] Essential Key Setup - A quick way to check / set up the most important keys
# - [ ] Support for multiple layouts/languages
# - [x] Global logging! Helpful for debugging... and more.
# - [ ] Visual Cheat Sheet (Maybe this should be a plugin...)
# - [ ] Undo / Redo Stack (Undo individual key changes)
# - [ ] Keyboard Navigation in the dialog screen
# - [ ] Gamepad / Joystick support
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
import argparse
from typing import List, Dict

import unittest
from unittest.mock import Mock, patch
import tempfile

from pynput import keyboard
from datetime import datetime

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
    QFileDialog,
    QTabWidget,
    QMessageBox,
    QDialog,
    QScrollArea,
    QGroupBox,
    QListWidget,
    QDialogButtonBox,
    QListWidgetItem,
    QRadioButton,
    QCheckBox,
    QLineEdit,
    QComboBox,
)

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QEvent, QMetaObject, pyqtSlot, Q_ARG
from PyQt5.QtGui import QKeyEvent


    
TRACE = 5
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kwargs): # Adds another logging level, TRACE, which is below DEBUG.
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

logging.Logger.trace = trace


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
    
    0x01000085: "Key_RightWin",  # You might need to verify this key code. I don't recommend using this key. Why'd you use an action key?
    0x01000088: "Key_FN", # You might need to verify this key code. You should not need this, though - FN is only for layered keyboards. I do doubt you'll be using this, as it's not very practical.
    # Qt.Key_LeftShift: "Key_LeftShift", # Honestly not sure if this is doing anything, but it's here to be safe.
    # Qt.Key_RightShift: "Key_RightShift", # Honestly not sure if this is doing anything, but it's here to be safe.
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


BINDING_CATEGORIES = { # This is a list of all the categories in the bindings, used to generate the tabs. They will show up in the order they are defined here.
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
        # yay
        "ForwardKey",
        "BackwardKey",
        "MouseReset",
        "BlockMouseDecay",
        "YawToRollButton",
        "FocusRadarPanel",
        "HeadLookReset",
        "HeadLookPitchUp",
        "HeadLookPitchDown",
        "HeadLookYawLeft",
        "HeadLookYawRight",
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
    # "Autopilot" category is removed to be handled via plugins # TODO
}

# Config parser to load configuration (like themes)
config = configparser.ConfigParser()
config.read("config.ini")

# Define themes for the GUI
THEMES = {
    "Default": {
        "background": "#2b2b2b", # Dark grey
        "text": "#ffffff", # White
        "key_normal": "#555555", # Dark grey	
        "key_bound": "#4a6b8a", # Blue
        "key_general": "#777777", # Grey
        "key_ship": "#1289A7", # Cyan
        "key_srv": "#4a8a6b", # Green
        "key_onfoot": "#aa7b4a", # Orange-Brown
        "key_fss": "#6b4a8a", # Purple
        "key_camera": "#833471", # Pink
        "key_saa": "#8a4a6b", # Red
        "key_multi-crew": "#8a6b8a", # Purple
        "key_store": "#aa4a7b", # Pink
        "key_all": "#5a5a5a", # Dark grey
        "key_pressed": "#333333",  # Darker grey
        # "key_active": "#8a4a4a",  # A distinct color for active keys - used only for debugging :)
        # "key_numlock": "#8a4a4a",  # A distinct color for active keys - used only for debugging :)
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


class LogBuffer(logging.Handler):
    def __init__(self):
        super().__init__()
        self.buffer = []

    def emit(self, record):
        self.buffer.append(record)

    def flush_records(self):
        records = self.buffer.copy()
        self.buffer.clear()
        return records


log_buffer = LogBuffer()

class QTextEditLogger(QObject, logging.Handler):
    log_signal = pyqtSignal(str, str)  # Emits (message, level)

    def __init__(self, text_edit):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.text_edit = text_edit
        self._is_valid = True

    def emit(self, record):
        if self._is_valid:
            msg = self.format(record)
            level = record.levelname
            self.log_signal.emit(msg, level)

    def close(self):
        self._is_valid = False
        super().close()
        
def setup_logging(text_edit=None, enable_console=False):
    """
    Sets up logging for the application.

    Args:
        text_edit (QTextEdit, optional): The QTextEdit widget for GUI logging.
        enable_console (bool): Whether to enable logging to the console.

    Returns:
        tuple: (logger, log_buffer, console_handler, gui_handler)
    """
    logger = logging.getLogger('EDKeysGUI')
    logger.setLevel(TRACE) # Set to work with TRACE over DEBUG. You can filter in the GUI.

    # Clear existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler (always enabled)
    file_handler = logging.FileHandler('edkeysgui.log')
    file_handler.setLevel(TRACE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Buffer handler
    log_buffer = LogBuffer()
    log_buffer.setLevel(TRACE)
    log_buffer.setFormatter(formatter)
    logger.addHandler(log_buffer)

    # Console handler (conditionally added)
    console_handler = None
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # GUI handler (conditionally added if text_edit is provided)
    gui_handler = None
    if text_edit:
        gui_handler = QTextEditLogger(text_edit)
        gui_handler.setLevel(logging.DEBUG)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)

    return logger, log_buffer, console_handler, gui_handler

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


class EDKeys: # EDKeys uses the built-in logger, not the custom one. Everything is still logged to the GUI, regardless. 
    """Handles parsing and managing key bindings for Elite: Dangerous."""

    # binds_file = "main.binds"
    # full_path = os.path.abspath(binds_file)

    def __init__(self, binds_file, logger):
        self.binds_file = binds_file
        self.logger = logger
        self.logger.info(f"Attempting to load binds file from: {os.path.abspath(binds_file)}")
        self.category_bindings = {}
        self.parse_binds_file()

    def get_vkcode_for_key(self, key):
        return VK_CODE.get(key)
            
    def parse_binds_file(self):
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()
            for binding in root.iter():
                if binding.tag != 'Root':
                    action = binding.tag
                    primary = binding.find('Primary')
                    if primary is not None and primary.get('Key'):
                        key = primary.get('Key')
                        category = self.get_action_category(action)
                        self.bind_action(key, action, category)
            self.logger.info("Bindings loaded successfully")
        except FileNotFoundError:
            self.logger.error(f"Bindings file not found: {self.binds_file}")
            raise
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise

    def get_action_category(self, action):
        for category, actions in BINDING_CATEGORIES.items():
            if action in actions:
                return category
        return "General"

    def get_bound_actions(self, key, category):
        if category == "All":
            actions = []
            for cat_bindings in self.category_bindings.values():
                actions.extend(cat_bindings.get(key, []))
            return actions
        return self.category_bindings.get(category, {}).get(key, [])

    def bind_action(self, key_name, action, category):
        if category not in self.category_bindings:
            self.category_bindings[category] = {}
        if key_name not in self.category_bindings[category]:
            self.category_bindings[category][key_name] = []
        if action not in self.category_bindings[category][key_name]:
            self.category_bindings[category][key_name].append(action)
            self.logger.info(f"Bound action '{action}' to key '{key_name}' in category '{category}'")

    def unbind_action(self, action, category):
        if category in self.category_bindings:
            for key, actions in self.category_bindings[category].items():
                if action in actions:
                    actions.remove(action)
                    self.logger.info(f"Unbound action '{action}' from key '{key}' in category '{category}'")
                    return
        self.logger.warning(f"Action '{action}' not found in category '{category}'")
                         
    def save_bindings_to_file(self, file_path):
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()

            # Clear existing bindings
            for binding in root.iter():
                if binding.tag != 'Root':
                    primary = binding.find('Primary')
                    if primary is not None:
                        primary.attrib.clear()

            # Set new bindings
            for key, actions in self.bindings.items():
                for action in actions:
                    binding = root.find(action)
                    if binding is not None:
                        primary = binding.find('Primary')
                        if primary is None:
                            primary = ET.SubElement(binding, 'Primary')
                        primary.set('Key', key)

            # Write the updated XML to file
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            self.logger.info(f"Bindings saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save bindings: {str(e)}")
            raise
    
    def generate_key_binding_report(self):  # DEBUG function to generate a report of all key bindings
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

class KeyboardGUI(QMainWindow): # Main GUI window
    """
    The main GUI window for the Keybind Visualizer.
    Displays a visual representation of keyboard bindings and handles user interactions.
    """
    
    ### Initial setup(s)

    log_signal = pyqtSignal(str, str)  # Signal for logging (message, level)
    
    def __init__(self, ed_keys, base_stylesheet, logger, log_handler, log_buffer):
        super().__init__()
        self.ed_keys = ed_keys
        self.base_stylesheet = base_stylesheet
        self.logger = logger
        self.log_handler = log_handler
        self.log_buffer = log_buffer
        self.log_signal.connect(self.debug_log)  # Connect the signal to debug_log method
        self.installEventFilter(self)  # Make sure we catch all events

        # Initialize non-UI attributes
        self.key_buttons = {}
        self.base_key_size = 40
        self.is_key_dialog_open = False
        self.held_keys = set()
        self.highlight_active_keys = False
        self.active_keys = set()
        self.altgr_active = False
        self.show_general_keys = True
        self.binding_mode = False

        # Initialize the console log window
        self.console_log_window = None # Will be initialized later
        self.init_console_log_window() # Initialize the console log window
        
        test_log_levels(logger) # debug test logs

        # Precompute styles
        self.precompute_styles()

        # Initialize the User Interface
        self.initUI()

        # Initialize unbound_actions_dialog
        self.unbound_actions_dialog = None

        # Initialize key states
        self.initialize_key_states()

        # Initialize key logger
        self.global_logging_enabled = False
        self.key_logger = None

        self.currently_pressed_keys = set()  # To keep track of held keys
        self.installEventFilter(self)  # Install event filter on the main window

        self.debug_log("KeyboardGUI initialized successfully.", level='INFO')

    def init_console_log_window(self):
        self.console_log_window = ConsoleLogWindow(self)
        self.console_log_window.flush_buffer(self.log_buffer)
        # self.console_log_window.show()  # Uncomment this line if you want to show the console log window immediately
                    
    def precompute_styles(self):
        self.precomputed_styles = {}
        
        def create_style(background_color: str) -> str:
            pressed_color = self.darken_color(background_color)
            text_color = THEMES[CURRENT_THEME]['text']
            return f"""
                QPushButton {{
                    background-color: {background_color};
                    color: {text_color};
                    border: 1px solid #555555;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 10px;
                    text-align: center;
                    padding: 2px;
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """
        
        for category in BINDING_CATEGORIES.keys():
            color_key = f"key_{category.lower()}"
            background_color = THEMES.get(CURRENT_THEME, {}).get(color_key, THEMES[CURRENT_THEME].get("key_bound", "#000000"))
            self.precomputed_styles[category] = create_style(background_color)
            self.debug_log(
                message=f"Category '{category}': Normal color = {background_color}, Pressed color = {self.darken_color(background_color)}.",
                level='DEBUG'
            )
        
        # 'All' category
        all_color = THEMES.get(CURRENT_THEME, {}).get("key_all", "#5a5a5a")
        self.precomputed_styles["All"] = create_style(all_color)
        
        # 'Normal' keys
        normal_color = THEMES.get(CURRENT_THEME, {}).get("key_normal", "#555555")
        self.precomputed_styles["Normal"] = create_style(normal_color)
        self.debug_log(
            message=f"Category 'Normal': Normal color = {normal_color}, Pressed color = {self.darken_color(normal_color)}.",
            level='DEBUG'
        )
        
        self.debug_log("Precomputed styles for all categories.", level='DEBUG')

               
    def initUI(self): # Set up the user interface components.
        """Set up the user interface components."""
        # Set window properties
        self.setWindowTitle("[Dev build] -- Elite: Dangerous Keybinds Visualizer v1.1B - by @glassesinsession")
        self.setGeometry(100, 100, 1200, 420)
        self.setMinimumSize(1200, 420)
        self.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};")

        # Create menu bar, status bar, and console window
        self.console_log_window = None
        self.create_menus()
        self.status_bar = self.statusBar()

        # Create and add key_block_status_label to the status bar
        self.key_block_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.key_block_status_label)

        # Set up main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create a widget to hold tabs and toggle button
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for a cleaner look

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        tab_layout.addWidget(self.tab_widget)

        # Add a stretch to push the toggle button to the right
        tab_layout.addStretch()

        # Create binding mode toggle button
        self.binding_toggle = QPushButton("Binding Mode: Off")
        self.binding_toggle.setCheckable(True)
        self.binding_toggle.clicked.connect(self.toggle_binding_mode)
        self.binding_toggle.setFixedWidth(120)  # Set a fixed width for consistency
        tab_layout.addWidget(self.binding_toggle, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Add the tab container to the main layout
        self.main_layout.addWidget(tab_container)

        # Create tabs for different key categories
        self.create_tabs()

        # Initialize NUM LOCK status label
        self.num_lock_label = QLabel()
        self.num_lock_label.setFixedWidth(100)
        self.num_lock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_bar.addPermanentWidget(self.num_lock_label)
        self.update_num_lock_status()

        # Apply stylesheet to selected tab
        self.apply_selected_tab_style(self.tab_widget.currentIndex())

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Ensure focus
        self.centralWidget().setFocusPolicy(Qt.StrongFocus)
        self.centralWidget().setFocus()

        # Initial update of all keys
        self.update_all_keys()

        # Schedule verification after the event loop has processed the UI updates
        QTimer.singleShot(0, self.run_verifications)

        self.debug_log("UI components initialized successfully.", level='INFO')

    def create_action_groups(self): # Groups actions into categories for display in the GUI.
        groups = {
            "Flight Rotation": [],
            "Flight Thrust": [],
            "Alternate Flight Controls": [],
            "Flight Throttle": [],
            "Flight Landing Overrides": [],
            "Flight Miscellaneous": [],
            "Targeting": [],
            "Weapons": [],
            "Cooling": [],
            "Miscellaneous": [],
            "Mode Switches": [],
            "Headlook Mode": [],
        }

        if self.category == "All":
            categories_to_show = BINDING_CATEGORIES.keys()
        else:
            categories_to_show = [self.category]
            if self.show_general_keys:
                categories_to_show.append("General")

        for category in categories_to_show:
            for action in BINDING_CATEGORIES.get(category, []):
                # Assign action to appropriate group (you may need to adjust this logic)
                if "Rotation" in action:
                    groups["Flight Rotation"].append(action)
                elif "Thrust" in action:
                    groups["Flight Thrust"].append(action)
                # ... (add more conditions for other groups)
                else:
                    groups["Miscellaneous"].append(action)

        return {k: v for k, v in groups.items() if v}  # Remove empty groups

    def on_action_selected(self, checked): # Updates the selected action when an action button is clicked.
        if checked:
            self.selected_action = self.sender().text()        
          
    def create_menus(self): # Creates the application's menu bar and adds menu items.
        
        """
        Creates the application's menu bar and adds menu items for 'File' and 'View' menus.
        The 'File' menu includes:
        - Load Keybind File: Triggers the load_bindings method.
        - Save Current Bindings: Triggers the save_bindings method.
        
        The 'View' menu includes:
        - Show General Keys: Toggles the visibility of general keys, linked to the toggle_general_keys method.
        - Show Unbound Actions: Triggers the show_unbound_actions method.
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
        

        
        # Tools menu
        tools_menu = self.menuBar().addMenu("Tools")
        
        self.global_logging_action = self.add_menu_action(
            tools_menu, "Enable Global Key Logging", self.toggle_global_key_logging, checkable=True
        )
        self.global_logging_action.setChecked(False)
        
        self.toggle_general_keys_action.setChecked(self.show_general_keys)
        self.add_menu_action(
            tools_menu, "Bind Unbound Actions", self.show_unbound_actions
        )
        
        
        # Add Console Log to the View menu
        self.add_menu_action(view_menu, "Show Console Log", self.show_console_log)

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

    def create_tabs(self):
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create 'All' tab
        self.add_keyboard_tab("All", "QWERTY")

        # Add additional category-based tabs
        for category in BINDING_CATEGORIES.keys():
            self.add_keyboard_tab(category, "QWERTY")

        # Initially hide all tabs except the first one
        for index in range(self.tab_widget.count()):
            if index != 0:
                self.tab_widget.widget(index).setVisible(False)

    def initialize_key_states(self): # Initializes the state of each key (pressed or released) to False.
        """
        Initializes the state of each key (pressed or released) to False.
        """
        self.key_states = {}
        for category, keys in self.key_buttons.items():
            for key_name in keys:
                self.key_states[key_name] = False
        self.debug_log("Initialized all key states to False.", level='DEBUG')


    ### Keyboard Tab and Button Management
    
    def add_keyboard_tab(self, category, layout_name):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        keyboard_layout = QHBoxLayout()
        keyboard_layout.setSpacing(10)

        main_layout = LAYOUTS.get(layout_name, {}).get("main", [])
        nav_layout = LAYOUTS.get(layout_name, {}).get("nav", [])
        numpad_layout = LAYOUTS.get(layout_name, {}).get("numpad", [])

        main_keyboard, main_placements = self.create_keyboard_section(main_layout, category)
        keyboard_layout.addLayout(main_keyboard, 70)

        nav_section, nav_placements = self.create_keyboard_section(nav_layout, category, key_size=1.2)
        keyboard_layout.addLayout(nav_section, 15)

        numpad_section, numpad_placements = self.create_keyboard_section(numpad_layout, category, key_size=1.2)
        keyboard_layout.addLayout(numpad_section, 15)

        # Store the placements for verification
        if not hasattr(self, 'key_placements'):
            self.key_placements = []
        self.key_placements.extend(main_placements + nav_placements + numpad_placements)

        tab_layout.addLayout(keyboard_layout)
        self.tab_widget.addTab(tab, category)
    
    def create_keyboard_section(self, layout, tab_category, key_size=1.0):
        section_layout = QGridLayout()
        section_layout.setSpacing(4)
        section_layout.setContentsMargins(2, 2, 2, 2)

        key_placements = []  # List to collect key placement info

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
                    key_name, display_label, size, row_span = "", "", key_data, 1

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

                key_placements.append({
                    'key_name': key_name,
                    'row': row_idx,
                    'column': col_idx,
                    'colspan': col_span
                })

                col_idx += col_span

        for i in range(col_idx):
            section_layout.setColumnStretch(i, 1)

        return section_layout, key_placements

    def create_key_button(self, key_name, display_label, size, category): # Creates a button for a keyboard key.
        """
        Create a button for a keyboard key.

        Args:
            key_name (str): Internal name of the key
            display_label (str): Label to display on the key
            size (float): Size multiplier for the key
            category (str): Category (tab) the key belongs to

        Returns:
            QPushButton: The created key button
        """
        button = QPushButton(display_label)
        button.setFocusPolicy(Qt.NoFocus)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumSize(int(self.base_key_size * size), self.base_key_size)
        
        # Get bound actions and determine the primary category for styling
        bound_actions = self.ed_keys.get_bound_actions(key_name, category)
        primary_category = self.determine_primary_category(bound_actions, category)
        
        # Set button style based on its bindings and category
        style = self.get_button_style(primary_category, bound_actions, category, is_pressed=False)
        button.setStyleSheet(style)
        
        # Store properties for later use
        button.setProperty("primary_category", primary_category)
        button.setProperty("bound_actions", bound_actions)
        button.setProperty("is_pressed", False)
        
        # Set tooltip showing bound actions
        tooltip = self.create_tooltip(bound_actions, category)
        button.setToolTip(tooltip)
        
        # Connect the clicked signal to handle key clicks
        button.clicked.connect(lambda: self.on_key_button_clicked(key_name))
        
        # Store the button in the key_buttons dictionary
        if category not in self.key_buttons:
            self.key_buttons[category] = {}
        self.key_buttons[category][key_name] = button
        
        
        # self.debug_log(  # UNDO to check all keys mapping to the keyboard
        #     category='Button Creation',
        #     message=f"Created button '{key_name}' in category '{category}'.",
        #     level='DEBUG'
        # )
        
        return button

    def on_key_button_clicked(self, key_name):
        self.debug_log(f"Key '{key_name}' clicked", level='DEBUG')
        
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if current_tab == "All":
            self.debug_log(f"Cannot bind key '{key_name}' in 'All' tab", level='WARNING')
            QMessageBox.warning(self, "Binding Not Allowed", "Cannot bind keys in the 'All' tab. Please select a specific category.") # TODO
            return

        if self.binding_mode:
            self.debug_log(f"Opening binding dialog for key '{key_name}' in category '{current_tab}'", level='INFO')
            self.open_binding_dialog(key_name)
        else:
            self.debug_log(f"Key '{key_name}' clicked (not in binding mode)", level='INFO')

    def get_button_style(self, primary_category, bound_actions, tab_category, is_pressed):
        """
        Get the appropriate button style with consistent pressed appearance.
        
        Args:
            primary_category: Primary category for the button
            bound_actions: List of bound actions
            tab_category: Current tab category
            is_pressed: Whether the button is pressed
            
        Returns:
            str: Complete CSS style string
        """
        if not bound_actions:
            base_style = self.precomputed_styles["Normal"]
        else:
            base_style = self.precomputed_styles.get(primary_category, self.precomputed_styles["Normal"])

        if is_pressed:
            # Extract the current background color
            bg_color = None
            for line in base_style.split('\n'):
                if 'background-color:' in line and 'pressed' not in line:
                    bg_color = line.split(':')[1].strip().rstrip(';')
                    break
            
            if bg_color:
                # Use our existing darken_color function
                darker_color = self.darken_color(bg_color)
                return base_style.replace(f"background-color: {bg_color}", f"background-color: {darker_color}")
        
        return base_style
    
    def determine_applicable_categories(self, primary_category: str, tab_category: str) -> List[str]:
        if tab_category == "All":
            return [primary_category]
        
        categories = []
        if primary_category == "General" or tab_category == "General":
            if self.show_general_keys or tab_category == "General":
                categories.append("General" if primary_category == "General" else "Normal")
        if primary_category == tab_category:
            categories.append(primary_category)
        
        return categories

    def create_tooltip(self, bound_actions, tab_category):
        """
        Creates a tooltip for a key button showing its bound actions.
        Ensures each action appears only once.

        Args:
            bound_actions: List of actions bound to the key
            tab_category: The category of the current tab
            
        Returns:
            str: Formatted tooltip text
        """
        # Use a set to eliminate duplicates
        relevant_actions = set(self.get_relevant_actions(bound_actions, tab_category))
        
        if relevant_actions:
            return "\n".join(sorted(relevant_actions))  # Sort for consistent display
        return "Unassigned"

    def toggle_general_keys(self): # Toggles the visibility of general keys and updates the display.
        """
        Toggles the visibility of general keys and updates the display.
        """
        self.show_general_keys = not self.show_general_keys
        self.update_all_keys()



    # Key Event Handling and Visual Updates

    def handle_key_event(self, event, is_press):
        """Centralized key event handling."""
        if event.isAutoRepeat():
            return False

        # Special handling for AltGr (scan code 312)
        if event.nativeScanCode() == 312:
            self.handle_altgr_event(is_press)
            return True

        key_name = self.get_key_name(event)
        if not key_name:
            return False

        self.debug_log(f"Key {'pressed' if is_press else 'released'}: {key_name}", level='DEBUG')

        # Add NUM LOCK check
        if key_name == "Key_NumLock" and not is_press:
            self.update_num_lock_status()

        if is_press:
            self.active_keys.add(key_name)
        else:
            self.active_keys.discard(key_name)

        # Update visuals for all tabs that show this key
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        # Only update the button in the current tab
        if key_name in self.key_buttons.get(current_tab, {}):
            button = self.key_buttons[current_tab][key_name]
            if button.isVisible():
                primary_category = button.property("primary_category") or "Normal"
                bound_actions = button.property("bound_actions") or []
                
                style = self.get_button_style(
                    primary_category,
                    bound_actions,
                    current_tab,
                    is_press
                )
                
                button.setStyleSheet(style)
                button.update()
                
                self.debug_log(
                    f"Updated button style for {key_name} in {current_tab}",
                    level='DEBUG'
                )

        return True

    def handle_altgr_event(self, is_press):
        """Handles the AltGr key event."""
        self.track_pressed_keys("Key_RightAlt", is_press)
        self.update_key_visual("Key_RightAlt", is_press)
        
        # Ensure left Ctrl is not affected
        if "Key_LeftControl" in self.active_keys:
            self.active_keys.discard("Key_LeftControl")
            self.update_key_visual("Key_LeftControl", False)
          
    def keyPressEvent(self, event):
        """
        Handle key press events and update visual feedback.
        
        Args:
            event: QKeyEvent containing key press information
        """
        if event.isAutoRepeat():
            return

        key_name = self.get_key_name(event)
        if key_name:
            self.debug_log(f"Key pressed: {key_name}", level='DEBUG')
            
            # Update active keys set
            self.active_keys.add(key_name)
            
            # Update visual state for all tabs that show this key
            self.update_key_visual(key_name, True)
            
            # Handle binding mode if active
            if self.binding_mode:
                self.open_binding_dialog(key_name)
                event.accept()
                return
                
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Handle key release events and update visual feedback.
        
        Args:
            event: QKeyEvent containing key release information
        """
        if event.isAutoRepeat():
            return

        key_name = self.get_key_name(event)
        if key_name:
            self.debug_log(f"Key released: {key_name}", level='DEBUG')
            
            # Remove from active keys
            self.active_keys.discard(key_name)
            
            # Update visual state
            self.update_key_visual(key_name, False)
            
        super().keyReleaseEvent(event)
                                     
    def get_key_name(self, event): # Determines the name of the key from a key event.
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
        self.debug_log(f"Unmapped key: Qt Key {key}, Scan Code {scan_code}", level='WARNING')
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

    def prevent_tab_focus_change(self, old_focus_widget): # Prevents focus change when Tab is pressed and returns focus to the previous widget.
        """
        Prevents focus change when Tab is pressed and returns focus to the previous widget.
        
        :param old_focus_widget: The widget that had focus before Tab was pressed
        """
        if old_focus_widget and self.focusWidget() != old_focus_widget:
            old_focus_widget.setFocus()

    @pyqtSlot(str, bool)
    def update_key_visual(self, key_name, is_pressed):
        """
        Update the visual state of a key across all tabs.
        
        Args:
            key_name: Name of the key to update
            is_pressed: Boolean indicating if key is pressed
        """
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        # Update key in current tab and 'All' tab
        for category in [current_tab, "All"]:
            if category in self.key_buttons and key_name in self.key_buttons[category]:
                button = self.key_buttons[category][key_name]
                if button.isVisible():
                    primary_category = button.property("primary_category")
                    bound_actions = button.property("bound_actions")
                    
                    style = self.get_button_style(
                        primary_category,
                        bound_actions,
                        category,
                        is_pressed=is_pressed
                    )
                    button.setStyleSheet(style)
                    button.update()
        
        self.debug_log(
            f"Updated visual state for key '{key_name}' - pressed: {is_pressed}",
            level='DEBUG'
        )

    def update_button_state(self, button, is_pressed): # Updates the press state of a key button.
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
        self.debug_log(f"Updating all keys for tab '{current_tab}'. Show General Keys: {self.show_general_keys}", level='INFO')

        # Determine categories to include based on current tab
        if current_tab == "All":
            categories_to_include = list(BINDING_CATEGORIES.keys())
        else:
            categories_to_include = [current_tab]
            if self.show_general_keys:
                categories_to_include.append("General")

        for category, buttons in self.key_buttons.items():
            # Skip categories not included in the current tab
            if category not in categories_to_include and category != "All":
                # Hide buttons not in the current category
                for button in buttons.values():
                    if button.isVisible():
                        button.hide()
                continue

            for key_name, button in buttons.items():
                # Fetch bound actions based on the current category
                if current_tab == "All":
                    bound_actions = self.ed_keys.get_bound_actions(key_name, "All")
                else:
                    bound_actions = self.ed_keys.get_bound_actions(key_name, current_tab)
                    if self.show_general_keys:
                        bound_actions += self.ed_keys.get_bound_actions(key_name, "General")

                # Get relevant actions
                relevant_actions = self.get_relevant_actions(bound_actions, current_tab)
                primary_category = self.determine_primary_category(relevant_actions, current_tab)

                # Determine if the button should be shown
                should_show = category == current_tab or category == "All" or (self.show_general_keys and primary_category == "General")
                if button.isVisible() != should_show:
                    button.setVisible(should_show)
                    button.update()

                # Update style only if it has changed
                new_style = self.get_button_style(primary_category, relevant_actions, current_tab, is_pressed=(key_name in self.active_keys))
                if button.styleSheet() != new_style:
                    button.setStyleSheet(new_style)
                    button.setProperty("primary_category", primary_category)
                    button.setProperty("bound_actions", bound_actions)
                    button.setProperty("relevant_actions", relevant_actions)
                    button.setToolTip(self.create_tooltip(relevant_actions, current_tab))
                    button.update()

        self.debug_log(f"Finished updating all keys for tab '{current_tab}'", level='INFO')
        
    def on_tab_changed(self, index):
        current_tab = self.tab_widget.tabText(index)
        self.debug_log(f"Switched to tab: {current_tab}", level='INFO')
        self.update_all_keys()
        self.apply_selected_tab_style(index)

        if current_tab == "All":
            self.binding_toggle.setEnabled(False)
            self.debug_log("Binding mode is unavilable on this tab.", level='INFO')
        else:
            self.binding_toggle.setEnabled(True)

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

    def determine_primary_category(self, bound_actions, tab_category):
        """
        Determines the primary category for binding display.
        Ensures proper category assignment without duplication.
        
        Args:
            bound_actions: List of bound actions
            tab_category: Current tab category
            
        Returns:
            str: Primary category name
        """
        if not bound_actions:
            return "Normal"
        
        # Use a set to track categories
        categories = set()
        for action in bound_actions:
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
        
        # Priority order for multiple categories
        category_priority = ["Ship", "SRV", "OnFoot", "FSS", "SAA", "Camera", 
                           "Multi-Crew", "Store", "General"]
        for cat in category_priority:
            if cat in categories:
                return cat
        return "General"
           
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

    def get_relevant_actions(self, actions, tab_category):
        """
        Filters actions to only those relevant for the current tab category.
        Ensures no duplicate actions are returned.
        
        Args:
            actions: List of all actions bound to a key
            tab_category: The category of the current tab
            
        Returns:
            list: Filtered list of unique actions
        """
        if tab_category == "All":
            return list(set(actions))  # Remove duplicates
        
        relevant = set()  # Use set to prevent duplicates
        for action in actions:
            action_category = self.get_binding_category(action)
            if action_category in [tab_category, "General"]:
                relevant.add(action)
                
        return list(relevant)
    
    def on_button_press(self, button, key_name): # Handles the visual update when a key button is pressed.
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
            message=f"Key '{key_name}' pressed.",
            level='DEBUG'
        )

    def on_button_release(self, button, key_name): # Handles the visual update when a key button is released.
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
            message=f"Key '{key_name}' released.",
            level='DEBUG'
        )

    def on_key_press(self, key): # Handles global key press events when logging is enabled.
        """
        Handles global key press events when logging is enabled.
        """
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        self.debug_log(f"[GL] Key pressed: {key_char}", level='WARNING')

    def on_key_release(self, key): # Handles global key release events when logging is enabled.
        """
        Handles global key release events when logging is enabled.
        """
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        self.debug_log(f"[GL] Key released: {key_char}", level='WARNING')


    # NUM LOCK handling
    
    def update_num_lock_status(self): # Updates the status of the Num Lock key and displays it on the num_lock_label.
        """
        Updates the status of the Num Lock key and displays it on the num_lock_label.

        This method checks the current state of the Num Lock key using the keyboard
        modifiers from the QApplication. It then updates the text and color of the
        num_lock_label to indicate whether Num Lock is on or off.

        The label text will be "NUM LOCK ON" in green if Num Lock is enabled, and
        "NUM LOCK OFF" in red if it is disabled.
        """
        
        num_lock_on = is_numlock_on()
        status_text = "NUM LOCK ON" if num_lock_on else "NUM LOCK OFF"
        color = "green" if num_lock_on else "red"
        self.num_lock_label.setText(f'<font color="{color}" style="font-weight: bold;">{status_text}</font>')
        

        # Update the visual state of the NUM LOCK key
        self.update_key_visual("Key_NumLock", num_lock_on)
        
        
    # TAB handling
    
    def focusNextPrevChild(self, next): # Prevents focus traversal when Tab is pressed.
        # Disable focus traversal
        return False


    # Binding Functions
    
    def toggle_binding_mode(self):
        self.binding_mode = self.binding_toggle.isChecked()
        if self.binding_mode:
            self.binding_toggle.setText("Binding Mode: On")
            self.status_bar.showMessage("Binding Mode: Active. Click a key to bind an action.")
            self.debug_log("Binding Mode activated", level='INFO')
        else:
            self.binding_toggle.setText("Binding Mode: Off")
            self.status_bar.showMessage("Binding Mode: Inactive", 5000)
            self.debug_log("Binding Mode deactivated", level='INFO')
            
    def open_binding_dialog(self, key_name): # Opens the binding dialog for a specific key.
        """
        Open the binding dialog for a specific key.

        Args:
            key_name (str): Name of the key to bind
        """
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if current_tab == "All":
            self.status_bar.showMessage("Binding not allowed in 'All' tab. Please select a specific category.", 5000)
            return

        if key_name in self.key_buttons.get(current_tab, {}):
            dialog = BindingDialog(self, key_name, self.ed_keys, self.logger, current_tab, self.show_general_keys)
            if dialog.exec_() == QDialog.Accepted:
                self.update_key_binding(key_name, dialog.selected_action)
        else:
            self.debug_log(f"Attempted to open binding dialog for non-existent key: {key_name}", level='WARNING')
            
    def update_key_binding(self, key_name, new_action):
        self.debug_log(f"Attempting to bind action '{new_action}' to key '{key_name}'", level='DEBUG')
        
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        if new_action:
            conflicting_key = self.check_action_conflict(new_action, category=current_tab)
            
            if conflicting_key and conflicting_key != key_name:
                self.debug_log(f"Conflict detected: '{new_action}' is already bound to key '{conflicting_key}' in category '{current_tab}'", level='DEBUG')
                reply = QMessageBox.question(
                    self, "Binding Conflict",
                    f"The action '{new_action}' is already bound to key '{conflicting_key}' in the '{current_tab}' category.\n"
                    f"Do you want to move it to '{key_name}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    self.debug_log("User chose not to rebind due to conflict", level='DEBUG')
                    return
                else:
                    self.ed_keys.unbind_action(new_action, category=current_tab)

        # Remove old bindings from the target key for the current category
        old_actions = self.ed_keys.get_bound_actions(key_name, category=current_tab)
        self.debug_log(f"Removing old bindings from key '{key_name}' in category '{current_tab}': {old_actions}", level='INFO')
        for action in old_actions:
            self.ed_keys.unbind_action(action, category=current_tab)

        # Add new binding if provided
        if new_action:
            self.debug_log(f"Binding new action '{new_action}' to key '{key_name}' in category '{current_tab}'", level='INFO')
            self.ed_keys.bind_action(key_name, new_action, category=current_tab)

        # Update UI to reflect changes
        self.update_all_keys()
        if new_action:
            self.status_bar.showMessage(f"Bound '{new_action}' to key '{key_name}' in category '{current_tab}'", 5000)
        else:
            self.status_bar.showMessage(f"Unbound action(s) {old_actions} from key '{key_name}' in category '{current_tab}'", 5000)
                                                     
    def get_action_group(self, action): # Get the group an action belongs to.
        """
        Get the group an action belongs to.

        Args:
            action (str): The action to find the group for

        Returns:
            str: The group name, or None if not found
        """
        for group, actions in BINDING_CATEGORIES.items():
            if action in actions:
                return group
        return None
    
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
    
    def assign_key(self, key_name): # Opens a dialog to assign or unbind actions for a specific key.
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
   
   
    # (Global) Key Logging 
    
    def toggle_global_key_logging(self):
        self.global_logging_enabled = self.global_logging_action.isChecked()
        if self.global_logging_enabled:
            self.start_global_key_logging()
            self.show_console_log()  # Make sure console log is visible
        else:
            self.stop_global_key_logging()

    def show_console_log(self):
        if not self.console_log_window:
            self.init_console_log_window()
        self.console_log_window.show()

    def start_global_key_logging(self):
        if not self.key_logger:
            self.key_logger = keyboard.Listener(
                on_press=self.on_global_key_press,
                on_release=self.on_global_key_release
            )
            self.key_logger.start()
        self.currently_pressed_keys.clear()
        self.debug_log("Global key logging started", level='INFO')
        self.status_bar.showMessage("Global key logging started", 3000)
        
    def stop_global_key_logging(self):
        if self.key_logger:
            self.key_logger.stop()
            self.key_logger = None
        self.currently_pressed_keys.clear()
        self.debug_log("Global key logging stopped", level='INFO')
        self.status_bar.showMessage("Global key logging stopped", 3000)

    def on_global_key_press(self, key):
        key_name = self.pynput_to_custom_key(key)
        if key_name not in self.currently_pressed_keys:
            self.currently_pressed_keys.add(key_name)
            self.log_signal.emit(f"[GL] Key pressed: {key_name}", 'DEBUG')
            QMetaObject.invokeMethod(self, "update_key_visual",
                                    Qt.QueuedConnection,
                                    Q_ARG(str, key_name),
                                    Q_ARG(bool, True))

    def on_global_key_release(self, key):
        key_name = self.pynput_to_custom_key(key)
        if key_name in self.currently_pressed_keys:
            self.currently_pressed_keys.remove(key_name)
            self.log_signal.emit(f"[GL] Key released: {key_name}", 'DEBUG')
            QMetaObject.invokeMethod(self, "update_key_visual",
                                    Qt.QueuedConnection,
                                    Q_ARG(str, key_name),
                                    Q_ARG(bool, False))
                        
    def pynput_to_custom_key(self, key):
        try:
            if hasattr(key, 'char'):
                return f"Key_{key.char.upper()}"
            elif hasattr(key, 'name'):
                pynput_to_custom = {
                    'space': 'Key_Space',
                    'enter': 'Key_Enter',
                    'esc': 'Key_Escape',
                    'shift': 'Key_LeftShift',
                    'ctrl': 'Key_LeftControl',
                    'alt': 'Key_LeftAlt',
                    'tab': 'Key_Tab',
                    # Add more mappings as needed
                }
                return pynput_to_custom.get(key.name, f"Key_{key.name.capitalize()}")
            else:
                return str(key)
        except AttributeError:
            return str(key)

    def eventFilter(self, obj, event):
        """Filter all events to ensure we catch key events."""
        if event.type() == QEvent.KeyPress:
            self.handle_key_event(event, True)
            return True
        elif event.type() == QEvent.KeyRelease:
            self.handle_key_event(event, False)
            return True
        return super().eventFilter(obj, event)
    
    def reset_all_keys(self):
        for key in self.currently_pressed_keys.copy():
            self.on_global_key_release(key)
        self.currently_pressed_keys.clear()
            
    def check_action_conflict(self, action, category):
        for key, actions in self.ed_keys.category_bindings.get(category, {}).items():
            if action in actions:
                return key
        return None
     
    # Other misc.
    
    def show_unbound_actions(self):
        """
        Displays a dialog showing all unbound actions and allows binding them.
        """
        unbound_actions = self.get_unbound_actions()
        if not unbound_actions:
            QMessageBox.information(self, "Unbound Actions", "All actions are currently bound to keys.")
            return

        if self.unbound_actions_dialog is None or not self.unbound_actions_dialog.isVisible():
            self.unbound_actions_dialog = UnboundActionsDialog(self, unbound_actions, self.ed_keys, self.logger)
            self.unbound_actions_dialog.show()  # Use show() instead of exec_()
        else:
            self.unbound_actions_dialog.activateWindow()  # Bring existing dialog to front

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

    def closeEvent(self, event):
        # Stop global key logging if active
        self.stop_global_key_logging()

        # Remove and close log handlers
        if self.log_handler:
            self.logger.removeHandler(self.log_handler)
            self.log_handler.close()
            self.log_handler = None

        # Close the console log window if it exists
        if hasattr(self, 'console_log_window') and self.console_log_window:
            self.console_log_window.close()

        super().closeEvent(event)
        
    ### Debugging

    def log_key_placements(self): # DEBUG: Logs the placement of keys in the layout.
        self.debug_log("Logging key placements:", level='INFO')
        # for placement in self.key_placements:
        #     if placement['key_name']:  # Only log actual keys, not empty spaces
        #         self.debug_log(
        #             f"Key '{placement['key_name']}' placed at row {placement['row']}, "
        #             f"column {placement['column']} with colspan {placement['colspan']}",
        #             level='DEBUG'
        #         )
        self.debug_log("Key placement logging complete.", level='INFO')
           
    def verify_key_mappings(self): # DEBUG: Verifies that all keys in the layout have corresponding buttons and vice versa.
        self.debug_log("Verifying key mappings...", level='INFO')
        all_layout_keys = set()
        for layout in LAYOUTS["QWERTY"].values():
            for row in layout:
                for key_data in row:
                    if isinstance(key_data, (tuple, list)) and len(key_data) >= 1 and key_data[0]:
                        all_layout_keys.add(key_data[0])

        mapped_keys = set(KEY_MAPPING.values())
        ignore_keys = self.get_ignored_keys()
        
        # Handle generic Shift and Control keys
        if "Key_LeftShift" in all_layout_keys or "Key_RightShift" in all_layout_keys:
            all_layout_keys.add("Key_Shift")
        if "Key_LeftControl" in all_layout_keys or "Key_RightControl" in all_layout_keys:
            all_layout_keys.add("Key_Control")
        
        unmapped_layout_keys = all_layout_keys - mapped_keys - ignore_keys
        unmapped_dict_keys = mapped_keys - all_layout_keys - ignore_keys

        if unmapped_layout_keys:

            self.debug_log(f"Layout keys not in KEY_MAPPING: {unmapped_layout_keys}", level='WARNING')
        if unmapped_dict_keys:

            self.debug_log(f"KEY_MAPPING keys not in layout: {unmapped_dict_keys}", level='WARNING')

        # Check if all keys in the layout have corresponding buttons
        for category, keys in self.key_buttons.items():
            for key_name in all_layout_keys:
                if key_name not in keys and key_name not in ignore_keys:

                    self.debug_log(f"No button created for key: {key_name} in category: {category}", level='WARNING')


        self.debug_log("Key mapping verification complete.", level='INFO')
     
    def verify_color_assignments(self): # DEBUG: Verifies that each category has a corresponding color assigned in the THEMES dictionary.
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
                message="All categories have unique and assigned colors.",
                level='INFO'
            )
        else:
            if missing_colors:
                self.debug_log(
                    message=f"Missing colors for categories: {', '.join(missing_colors)}.",
                    level='ERROR'
                )
            if duplicate_colors:
                duplicates = "; ".join([f"Color '{color}' assigned to categories: {', '.join(cats)}" for color, cats in duplicate_colors.items()])
                self.debug_log(
                    message=f"Duplicate color assignments found: {duplicates}.",
                    level='ERROR'
                )

    def verify_buttons(self): # DEBUG: Verifies the existence and visibility of key buttons. Do add your expected keys to the list for testing.
        expected_keys = [
            # "Key_NumLock", 
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

                            message=f"Button '{key}' exists in category '{category}' but is not visible.",
                            level='WARNING'
                        )
                    else:
                        self.debug_log(

                            message=f"Button '{key}' exists and is visible in category '{category}'.",
                            level='DEBUG'
                        )
                        
                        # Additional check for NUM LOCK styling
                        # if key == "Key_NumLock":
                        #     style = button.styleSheet()
                        #     self.debug_log(
                        #         message=f"NUM LOCK button style: {style}",
                        #         level='DEBUG'
                        #     )
                    break
            if not found:
                self.debug_log(
                    message=f"Button '{key}' not found in any category.",
                    level='ERROR'
                )

    def track_pressed_keys(self, key_name, is_pressed): # DEBUG: Tracks the currently pressed keys.
        if is_pressed:
            self.active_keys.add(key_name)
        else:
            self.active_keys.discard(key_name)
        
        self.debug_log(f"Active keys updated. Currently pressed: {self.active_keys}", level='DEBUG')

    def debug_log(self, message, level='DEBUG', **kwargs): # DEBUG: Logs a message to the console log window.
        log_message = message
        if kwargs:
            log_message += " - " + ", ".join(f"{k}: {v}" for k, v in kwargs.items())

        if level == 'TRACE':
            self.logger.trace(log_message)
        elif level == 'DEBUG':
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

        # Send to console log window
        if hasattr(self, 'console_log_window') and self.console_log_window:
            self.console_log_window.log_signal.emit(log_message, level)
      
    def get_ignored_keys(self): # DEBUG: Returns a set of keys to ignore in the key mapping verification. USER: Add any keys you want to ignore here.
        return {
            'Key_F13', 'Key_F14', 'Key_F15', 'Key_F16', 'Key_F17', 'Key_F18', 'Key_F19', 'Key_F20', 
            'Key_F21', 'Key_F22', 'Key_F23', 'Key_F24', 'Key_MediaPlayPause', 'Key_MediaStop', 
            'Key_VolumeUp', 'Key_VolumeDown', 'Key_VolumeMute', 'Key_RightWin', 'Key_ScrollLock', 'Key_Pause', 'Key_Print', 'Key_FN',
            # Add any other keys you don't have on your keyboard here to surpress warnings.
            
            # The keys below are being handled separately. Don't make changes here unless you know what you're doing.
            'Key_Shift', 'Key_Control', 'Key_LeftShift', 'Key_RightShift', 'Key_LeftControl', 'Key_RightControl'
        }
                           
    def run_verifications(self): # DEBUG: Runs all verification checks. USER: Enable as needed. 
        self.log_key_placements()
        self.verify_key_mappings()
        self.verify_color_assignments()
        self.verify_buttons()
                               
class ButtonEventFilter(QObject):
    def __init__(self, button, main_window):
        super().__init__()
        self.button = button
        self.main_window = main_window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.main_window.debug_log("Key Filter", f"Button {self.button.text()} filtered key press: {event.key()}", level='DEBUG')
            
            if event.key() == Qt.Key_Tab:
                # Do not block Tab key, let it propagate
                return False

            # Handle other keys as needed
            self.button.animateClick()
            self.main_window.debug_log("Key Filter", f"Button {self.button.text()} clicked programmatically.", level='DEBUG')
            return True  # Block other key events after handling
        return super().eventFilter(obj, event)

class BindingDialog(QDialog):
    def __init__(self, parent, key_name, ed_keys, logger, category, show_general_keys):
        super().__init__(parent)
        self.key_name = key_name
        self.ed_keys = ed_keys
        self.logger = logger
        self.category = category
        self.show_general_keys = show_general_keys
        self.selected_action = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Bind Action to {self.key_name}")
        layout = QVBoxLayout(self)

        # Current binding display
        current_binding_label = QLabel("Current Binding:")
        current_binding_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(current_binding_label)

        current_bindings = self.get_current_bindings()
        if current_bindings:
            for category, action in current_bindings:
                binding_label = QLabel(f"{category}: {action}")
                binding_label.setStyleSheet("font-size: 12px; margin-left: 10px;")
                layout.addWidget(binding_label)
        else:
            no_binding_label = QLabel("No current binding")
            no_binding_label.setStyleSheet("font-style: italic; margin-left: 10px; font-size: 12px;")
            layout.addWidget(no_binding_label)

        layout.addSpacing(20)

        # Action groups
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.action_groups = self.create_action_groups()
        self.radio_buttons = []

        for group_name, actions in self.action_groups.items():
            group_box = QGroupBox(group_name)
            group_layout = QVBoxLayout()

            for action in actions:
                radio_button = QRadioButton(action)
                radio_button.toggled.connect(self.on_action_selected)
                group_layout.addWidget(radio_button)
                self.radio_buttons.append(radio_button)

                # Pre-select the current binding
                if any(binding[1] == action for binding in current_bindings):
                    radio_button.setChecked(True)

            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Unbind option
        self.unbind_checkbox = QCheckBox("Unbind current action")
        self.unbind_checkbox.setStyleSheet("font-size: 12px;")
        self.unbind_checkbox.stateChanged.connect(self.toggle_action_groups)
        layout.addWidget(self.unbind_checkbox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setMinimumSize(400, 500)

    def get_current_bindings(self):
        if self.category == "All":
            return [(category, action) for category, actions in BINDING_CATEGORIES.items() 
                    for action in self.ed_keys.get_bound_actions(self.key_name, category) 
                    if action in actions]
        else:
            return [(self.category, action) for action in self.ed_keys.get_bound_actions(self.key_name, self.category) 
                    if action in BINDING_CATEGORIES.get(self.category, [])]


    def create_action_groups(self):
        groups = {}
        if self.category == "All":
            categories_to_show = BINDING_CATEGORIES.keys()
        else:
            categories_to_show = [self.category]
            if self.show_general_keys:
                categories_to_show.append("General")

        for category in categories_to_show:
            groups[category] = BINDING_CATEGORIES.get(category, [])
        
        return groups

    def on_action_selected(self, checked):
        if checked:
            self.selected_action = self.sender().text()

    def toggle_action_groups(self, state):
        for radio_button in self.radio_buttons:
            radio_button.setEnabled(not state)

    def accept(self):
        if self.unbind_checkbox.isChecked():
            self.selected_action = None
        elif not self.selected_action:
            QMessageBox.warning(self, "No Selection", "Please select an action to bind or choose to unbind.")
            return
        super().accept()           

class UnboundActionsDialog(QDialog):
    def __init__(self, parent, unbound_actions, ed_keys, logger, show_general_keys=True):
        super().__init__(parent, Qt.Window)
        self.setWindowModality(Qt.NonModal)
        self.unbound_actions = unbound_actions
        self.ed_keys = ed_keys
        self.logger = logger
        self.show_general_keys = show_general_keys
        self.selected_action = None
        self.key_to_bind = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Bind Unbound Actions")
        self.setGeometry(200, 200, 500, 600)
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)

        instruction_label = QLabel("Select an unbound action to bind to a key:")
        instruction_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(instruction_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        if not self.unbound_actions:
            no_unbound_label = QLabel("All actions are currently bound.")
            no_unbound_label.setStyleSheet("font-style: italic; font-size: 12px;")
            self.scroll_layout.addWidget(no_unbound_label)
        else:
            self.create_action_groups(self.scroll_layout)

        self.scroll_area.setWidget(scroll_content)
        layout.addWidget(self.scroll_area)

        # Key input area
        key_input_layout = QHBoxLayout()
        key_input_label = QLabel("Press a key to bind:")
        self.key_input = QLineEdit()
        self.key_input.setReadOnly(True)
        self.key_input.setPlaceholderText("Click here and press a key")
        self.key_input.installEventFilter(self)
        key_input_layout.addWidget(key_input_label)
        key_input_layout.addWidget(self.key_input)
        layout.addLayout(key_input_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bind_button = button_box.button(QDialogButtonBox.Ok)
        bind_button.setText("Bind Selected Action")
        bind_button.setEnabled(False)
        button_box.accepted.connect(self.bind_selected_action)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        if obj == self.key_input and event.type() == QEvent.KeyPress:
            key_name = self.parent().get_key_name(event)
            if key_name:
                self.key_input.setText(key_name)
                self.key_to_bind = key_name
            return True
        return super().eventFilter(obj, event)

    def create_action_groups(self, layout):
        self.radio_buttons = []

        for category, actions in self.unbound_actions.items():
            group_box = QGroupBox(category)
            group_layout = QVBoxLayout()

            for action in actions:
                radio_button = QRadioButton(action)
                radio_button.toggled.connect(self.on_action_selected)
                group_layout.addWidget(radio_button)
                self.radio_buttons.append(radio_button)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

    def on_action_selected(self):
        selected = any(rb.isChecked() for rb in self.radio_buttons)
        self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).setEnabled(selected)
        if selected:
            for rb in self.radio_buttons:
                if rb.isChecked():
                    self.selected_action = rb.text()
                    break
        else:
            self.selected_action = None

    def bind_selected_action(self):
        if not self.selected_action:
            QMessageBox.warning(self, "No Selection", "Please select an action to bind.")
            return

        if not self.key_to_bind:
            QMessageBox.warning(self, "No Key Pressed", "Please press a key to bind the action.")
            return

        # Get the group of the selected action
        action_group = self.parent().get_action_group(self.selected_action)
        
        # Check for conflicts within the same group
        conflicting_action = self.check_group_conflict(action_group, self.key_to_bind)
        
        if conflicting_action:
            reply = QMessageBox.question(
                self, "Confirm Rebind",
                f"The key '{self.key_to_bind}' is already bound to '{conflicting_action}' in the '{action_group}' group.\n"
                f"Do you want to replace it with '{self.selected_action}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            else:
                self.ed_keys.unbind_action(conflicting_action)
                self.debug_log(f"Unbound action '{conflicting_action}' from key '{self.key_to_bind}'.", level='INFO')

        # Unbind the selected action from any previous key
        for key, actions in self.ed_keys.bindings.items():
            if self.selected_action in actions:
                self.ed_keys.unbind_action(self.selected_action)
                self.debug_log(f"Unbound action '{self.selected_action}' from key '{key}'.", level='INFO')
                break

        self.ed_keys.bind_action(self.key_to_bind, self.selected_action)
        self.debug_log(f"Bound action '{self.selected_action}' to key '{self.key_to_bind}'.", level='INFO')

        QMessageBox.information(
            self, "Binding Successful",
            f"Action '{self.selected_action}' has been bound to key '{self.key_to_bind}'."
        )

        self.parent().update_all_keys()
        self.parent().status_bar.showMessage(
            f"Bound '{self.selected_action}' to key '{self.key_to_bind}'.", 5000
        )

        self.remove_bound_action(self.selected_action)
        self.selected_action = None
        self.key_input.clear()
        self.key_to_bind = None
        self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).setEnabled(False)
    
    def remove_bound_action(self, action):
        for category, actions in self.unbound_actions.items():
            if action in actions:
                actions.remove(action)
                if not actions:
                    del self.unbound_actions[category]
                break
        self.refresh_action_list()

    def refresh_action_list(self):
        self.unbound_actions = self.parent().get_unbound_actions()

        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if not self.unbound_actions:
            no_unbound_label = QLabel("All actions are currently bound.")
            no_unbound_label.setStyleSheet("font-style: italic; font-size: 12px;")
            self.scroll_layout.addWidget(no_unbound_label)
        else:
            self.create_action_groups(self.scroll_layout)

        self.scroll_area.widget().updateGeometry()

    def check_group_conflict(self, group, key):
        """
        Check if there's a conflict within the same group for a given key.

        Args:
            group (str): The group to check
            key (str): The key to check for conflicts

        Returns:
            str: The conflicting action, or None if no conflict
        """
        bound_actions = self.ed_keys.get_bound_actions(key)
        for action in bound_actions:
            if self.parent().get_action_group(action) == group:
                return action
        return None
    
    def closeEvent(self, event):
        self.parent().unbound_actions_dialog = None
        super().closeEvent(event)

class ConsoleLogWindow(QDialog):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Console Log")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout()

        controls_layout = QHBoxLayout()
        self.level_selector = QComboBox()
        self.level_selector.addItems(["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_selector.setCurrentText("INFO")
        self.level_selector.currentTextChanged.connect(self.refresh_display)

        self.show_timestamp_checkbox = QCheckBox("Show Timestamp")
        self.show_timestamp_checkbox.setChecked(True)
        self.show_timestamp_checkbox.stateChanged.connect(self.refresh_display)

        controls_layout.addWidget(self.level_selector)
        controls_layout.addWidget(self.show_timestamp_checkbox)
        controls_layout.addStretch()

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Consolas, Monospace;
                font-size: 12pt;
            }
        """)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Log")
        self.save_button.clicked.connect(self.save_log)
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(controls_layout)
        layout.addWidget(self.log_display)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.full_log = []
        self.log_signal.connect(self.append_log)

    def get_level_num(self, level_name):
        return logging.getLevelName(level_name)
    
    def flush_buffer(self, log_buffer):
        records = log_buffer.flush_records()
        for record in records:
            self.append_log(record.getMessage(), record.levelname)

    def append_log(self, message, level):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        self.full_log.append((timestamp, level, message))
        self.update_display_for_new_log(timestamp, level, message)

    def update_display_for_new_log(self, timestamp, level, message):
        if self.is_visible_level(level):
            self.add_formatted_text(timestamp, level, message)
            self.log_display.ensureCursorVisible()

    def refresh_display(self):
        self.log_display.clear()
        for timestamp, level, message in self.full_log:
            if self.is_visible_level(level):
                self.add_formatted_text(timestamp, level, message)

    def add_formatted_text(self, timestamp, level, message):
        if self.show_timestamp_checkbox.isChecked():
            timestamp_html = f'<span style="color: #bbbbbb;">{timestamp}</span> - '
        else:
            timestamp_html = ''

        level_html = self.colorize_level(level)
        full_html = f'{timestamp_html}{level_html} {message}'
        self.log_display.append(full_html)

    def colorize_level(self, level):
        color = self.get_color_for_level(level)
        return f'<span style="color: {color}; font-weight: bold;">{level:<8}</span>-'

    def is_visible_level(self, message_level):
        return self.get_level_num(message_level) >= self.get_level_num(self.level_selector.currentText())

    def get_level_num(self, level_name):
        if level_name == "TRACE":
            return TRACE
        return getattr(logging, level_name, 0)
    
    def get_color_for_level(self, level):
        colors = {
            "TRACE": "#AAAAAA",    # Light Gray for TRACE
            "DEBUG": "#787878",    # Gray
            "INFO": "#00ff00",     # Green
            "WARNING": "#FFA500",  # Orange
            "ERROR": "#FF4136",    # Red
            "CRITICAL": "#9D00FF", # Purple
        }
        return colors.get(level, "#FFFFFF")

    def clear_log(self):
        self.log_display.clear()
        self.full_log.clear()

    def save_log(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Log File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                for timestamp, level, message in self.full_log:
                    file.write(f"{timestamp} - {level:<8}- {message}\n")

## Plugins

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
            self.debug_log(f"Attempted to load already loaded plugin '{plugin_name}'.", level='WARNING')
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
                    self.debug_log(f"Plugin '{plugin_name}' loaded successfully.", level='INFO')
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Plugin Load Error",
                        f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.",
                    )
                    self.debug_log(f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.", level='error'.upper())
            except Exception as e:
                self.debug_log(f"Error loading plugin '{plugin_name}': {e}", level='error'.upper())
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
            self.debug_log(f"Could not load plugin from '{plugin_path}'.", level='error'.upper())

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
            self.debug_log(f"Attempted to unload non-loaded plugin '{plugin_name}'.", level='WARNING')
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
            self.debug_log(f"Plugin '{plugin_name}' unloaded successfully.", level='INFO')
        except Exception as e:
            self.debug_log(f"Error unloading plugin '{plugin_name}': {e}", level='error'.upper())
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
                    self.debug_log(f"Plugin path for '{plugin_name}' not found.", level='WARNING')

    def list_plugins(self):
        """
        Returns a list of all available plugins with their load status.
        """
        # List all .py files in the plugins directory
        plugins_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.isdir(plugins_dir):
            os.makedirs(plugins_dir)
            self.debug_log(f"Created plugins directory at '{plugins_dir}'.", level='INFO')

        plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith(".py")]
        all_plugins = set(os.path.splitext(f)[0] for f in plugin_files)
        plugin_list = []
        for plugin in all_plugins:
            status = "Loaded" if plugin in self.plugins else "Not Loaded"
            plugin_list.append((plugin, status))
        self.debug_log(f"Listed plugins: {plugin_list}", level='INFO')
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

## Testing classes

class MinimalKeyboardGUI(KeyboardGUI):
    """Minimal version of KeyboardGUI for testing"""
    
    def __init__(self, ed_keys, base_stylesheet, logger, log_handler, log_buffer):
        QMainWindow.__init__(self)
        
        # Initialize necessary attributes from parent class
        self.ed_keys = ed_keys
        self.base_stylesheet = base_stylesheet
        self.logger = logger
        self.log_handler = log_handler
        self.log_buffer = log_buffer
        
        # Initialize required attributes
        self.key_buttons = {}
        self.active_keys = set()
        self.binding_mode = False
        self.currently_pressed_keys = set()
        self.held_keys = set()
        self.highlight_active_keys = False
        self.show_general_keys = True
        
        # Initialize attributes needed for cleanup
        self.key_logger = None
        self.console_log_window = None
        self.global_logging_enabled = False
        
        # Create minimal UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add binding toggle button
        self.binding_toggle = QPushButton("Binding Mode: Off")
        self.binding_toggle.setCheckable(True)
        self.binding_toggle.clicked.connect(self.toggle_binding_mode)
        layout.addWidget(self.binding_toggle)
        
        # Initialize styles
        self.precompute_styles()
        
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
        
    def toggle_binding_mode(self):
        """Toggle binding mode and update UI accordingly"""
        self.binding_mode = not self.binding_mode
        self.binding_toggle.setChecked(self.binding_mode)
        self.binding_toggle.setText("Binding Mode: On" if self.binding_mode else "Binding Mode: Off")
        status_message = "Binding Mode: Active. Click a key to bind an action." if self.binding_mode else "Binding Mode: Inactive"
        self.status_bar.showMessage(status_message, 5000 if not self.binding_mode else 0)

class TestEDKeys(unittest.TestCase):
    """Test core binding functionality"""
    
    def setUp(self):
        """Create test environment with temporary binds file"""
        self.logger = Mock()
        self.test_file = tempfile.mktemp(suffix='.binds')
        with open(self.test_file, 'w') as f:
            f.write('''<?xml version="1.0"?>
                <Root>
                    <UIFocus>
                        <Primary Key="Key_LeftAlt" />
                    </UIFocus>
                    <PitchUpButton>
                        <Primary Key="Key_S" />
                    </PitchUpButton>
                </Root>
            ''')
        self.ed_keys = EDKeys(self.test_file, self.logger)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_parse_binds_file(self):
        """Test that bindings are correctly parsed"""
        self.ed_keys.parse_binds_file()
        self.assertIn("Key_LeftAlt", self.ed_keys.category_bindings.get("General", {}))
        self.assertIn("Key_S", self.ed_keys.category_bindings.get("Ship", {}))

    def test_get_action_category(self):
        """Test action categorization"""
        self.assertEqual(self.ed_keys.get_action_category("UIFocus"), "General")
        self.assertEqual(self.ed_keys.get_action_category("PitchUpButton"), "Ship")

    def test_bind_action(self):
        """Test binding new actions"""
        self.ed_keys.bind_action("Key_F", "ForwardThrustButton", "Ship")
        self.assertIn("ForwardThrustButton", 
                     self.ed_keys.category_bindings["Ship"]["Key_F"])

    def test_unbind_action(self):
        """Test removing bindings"""
        self.ed_keys.bind_action("Key_R", "SelectTarget", "Ship")
        self.ed_keys.unbind_action("SelectTarget", "Ship")
        self.assertNotIn("SelectTarget", 
                        self.ed_keys.category_bindings.get("Ship", {}).get("Key_R", []))

class TestKeyboardGUI(unittest.TestCase):
    """Test GUI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
            
        self.logger = Mock()
        self.ed_keys = Mock()
        self.ed_keys.get_bound_actions.return_value = []
        
        self.log_buffer = Mock()
        self.log_buffer.flush_records = Mock(return_value=[])
        
        self.gui = MinimalKeyboardGUI(
            self.ed_keys,
            "",
            self.logger,
            Mock(),
            self.log_buffer
        )

    def tearDown(self):
        """Clean up test environment"""
        try:
            if self.gui:
                self.gui.close()
        except:
            pass

    def test_key_press_handling(self):
        """Test key press event handling"""
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier)
        # Use direct method call instead of event system
        key_name = self.gui.get_key_name(event)
        if key_name:
            self.gui.active_keys.add(key_name)
        self.assertIn("Key_A", self.gui.active_keys)

    def test_key_release_handling(self):
        """Test key release event handling"""
        # Setup: add key to active keys
        self.gui.active_keys.add("Key_A")
        # Create release event
        event = QKeyEvent(QEvent.KeyRelease, Qt.Key_A, Qt.NoModifier)
        # Use direct method call
        key_name = self.gui.get_key_name(event)
        if key_name:
            self.gui.active_keys.discard(key_name)
        self.assertNotIn("Key_A", self.gui.active_keys)

    def test_binding_mode(self):
        """Test binding mode toggle"""
        # Verify initial state
        self.assertFalse(self.gui.binding_mode)
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: Off")
        self.assertFalse(self.gui.binding_toggle.isChecked())
        
        # Toggle on
        self.gui.toggle_binding_mode()
        self.assertTrue(self.gui.binding_mode, "Binding mode should be on")
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: On", "Button text should indicate On")
        self.assertTrue(self.gui.binding_toggle.isChecked(), "Button should be checked")
        
        # Toggle off
        self.gui.toggle_binding_mode()
        self.assertFalse(self.gui.binding_mode, "Binding mode should be off")
        self.assertEqual(self.gui.binding_toggle.text(), "Binding Mode: Off", "Button text should indicate Off")
        self.assertFalse(self.gui.binding_toggle.isChecked(), "Button should be unchecked")
        
class TestTooltipAndStyle(unittest.TestCase):
    """Test tooltip generation and button styling"""
    
    def setUp(self):
        self.app = QApplication([])
        self.logger = Mock()
        self.ed_keys = Mock()
        self.ed_keys.get_bound_actions.return_value = []
        
        self.log_buffer = Mock()
        self.log_buffer.flush_records = Mock(return_value=[])
        
        self.gui = MinimalKeyboardGUI(
            self.ed_keys,
            "",
            self.logger,
            Mock(),
            self.log_buffer
        )

    def tearDown(self):
        self.gui.close()
        self.app.quit()

    def test_tooltip_no_duplicates(self):
        """Test that tooltips don't contain duplicate actions"""
        bound_actions = [
            "StoreCamZoomIn",
            "StoreCamZoomIn",  # Duplicate
            "CommanderCreator_Redo"
        ]
        tooltip = self.gui.create_tooltip(bound_actions, "Store")
        tooltip_actions = tooltip.split('\n')
        self.assertEqual(
            len(tooltip_actions),
            len(set(tooltip_actions)),
            "Tooltip contains duplicate actions"
        )
        self.assertEqual(len(tooltip_actions), 2)

    def test_button_style_pressed_state(self):
        """Test that pressed button style uses darken_color"""
        normal_style = self.gui.get_button_style("Store", ["StoreCamZoomIn"], "Store", False)
        pressed_style = self.gui.get_button_style("Store", ["StoreCamZoomIn"], "Store", True)
        
        def get_bg_color(style):
            for line in style.split('\n'):
                if 'background-color:' in line and 'pressed' not in line:
                    return line.split(':')[1].strip().rstrip(';')
            return None
            
        normal_color = get_bg_color(normal_style)
        pressed_color = get_bg_color(pressed_style)
        
        self.assertNotEqual(normal_color, pressed_color)
        self.assertEqual(
            pressed_color,
            self.gui.darken_color(normal_color)
        )

    def test_category_handling(self):
        """Test category handling for multiple bindings"""
        actions = ["StoreCamZoomIn", "UIFocus"]
        
        # Test primary category determination
        category = self.gui.determine_primary_category(actions, "Store")
        self.assertEqual(category, "Store")
        
        # Test relevant actions filtering
        store_actions = self.gui.get_relevant_actions(actions, "Store")
        self.assertIn("StoreCamZoomIn", store_actions)
        self.assertIn("UIFocus", store_actions)  # General category should be included

def run_tests():
    """Run all tests and ensure results are printed"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEDKeys)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestKeyboardGUI))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTooltipAndStyle))
    
    # Run tests with result collection
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for failure in result.failures:
            print(f"\n{failure[0]}")
            print(f"{failure[1]}")
            
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"\n{error[0]}")
            print(f"{error[1]}")
    
    return result.wasSuccessful()
  
def test_log_levels(logger): # DEBUG: Test logging levels. Will always show in the console log window. - USER: Enable as needed.
    logger.trace("This is a TRACE message, used for detailed debugging.")
    logger.debug("This is a DEBUG message, used for general debugging.")
    logger.info("This is an INFO message, used for general information.")
    logger.warning("This is a WARNING message, used for potential issues.")
    logger.error("This is an ERROR message, used for errors that aren't an immediate problem, but you still should fix to ensure proper operation.")
    logger.critical("This is a CRITICAL message, used for critical errors that require immediate attention and might crash the application.")

def main():
    """Main function with requirement checking"""
    parser = argparse.ArgumentParser(description="EDKeysGUI Application")
    parser.add_argument(
        '--enable-console', 
        action='store_true', 
        help='Enable logging to the console.'
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Create the main window and QTextEdit for logging
    main_window = QMainWindow()
    central_widget = QWidget(main_window)
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout()
    central_widget.setLayout(layout)

    log_text_edit = QTextEdit()
    log_text_edit.setReadOnly(True)
    layout.addWidget(log_text_edit)

    # Setup logging with GUI
    logger, log_buffer, console_handler, gui_handler = setup_logging(
        text_edit=log_text_edit, 
        enable_console=args.enable_console
    )
    logger.info("Application starting...")

    # Define base stylesheet
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

    ex = KeyboardGUI(ed_keys, base_stylesheet, logger, gui_handler, log_buffer)
    ex.init_console_log_window()  # Initialize but don't show
    ex.show()

    logger.info("GUI initialized. Application running.")

    # Run the application
    exit_code = app.exec_()

    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    sys.exit(exit_code)
    
if __name__ == "__main__": # Run the test suite if necessary!
    # run_tests()
    main()