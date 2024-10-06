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
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont


# Determine the architecture and define ULONG_PTR accordingly
if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong


# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a file handler with UTF-8 encoding
file_handler = logging.FileHandler("key_log.txt", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Create a console handler with UTF-8 encoding
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setStream(sys.stdout)  # Ensure it's using stdout

# Define a logging format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


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
    Qt.Key_Escape: "ESCAPE",
    Qt.Key_Tab: "TAB",
    Qt.Key_Backspace: "BACK",
    Qt.Key_Return: "RETURN",
    Qt.Key_Enter: "RETURN",
    Qt.Key_Insert: "INSERT",
    Qt.Key_Delete: "DELETE",
    Qt.Key_Pause: "PAUSE",
    Qt.Key_Print: "PRINT",
    Qt.Key_SysReq: "SYSREQ",
    Qt.Key_Clear: "CLEAR",
    Qt.Key_Home: "HOME",
    Qt.Key_End: "END",
    Qt.Key_Left: "LEFT",
    Qt.Key_Up: "UP",
    Qt.Key_Right: "RIGHT",
    Qt.Key_Down: "DOWN",
    Qt.Key_PageUp: "PRIOR",
    Qt.Key_PageDown: "NEXT",
    Qt.Key_Shift: "SHIFT",
    Qt.Key_Control: "CONTROL",
    Qt.Key_Meta: "LWIN",
    Qt.Key_Alt: "MENU",
    Qt.Key_CapsLock: "CAPITAL",
    Qt.Key_NumLock: "NUMLOCK",
    Qt.Key_ScrollLock: "SCROLL",
    Qt.Key_F1: "F1",
    Qt.Key_F2: "F2",
    Qt.Key_F3: "F3",
    Qt.Key_F4: "F4",
    Qt.Key_F5: "F5",
    Qt.Key_F6: "F6",
    Qt.Key_F7: "F7",
    Qt.Key_F8: "F8",
    Qt.Key_F9: "F9",
    Qt.Key_F10: "F10",
    Qt.Key_F11: "F11",
    Qt.Key_F12: "F12",
    Qt.Key_Space: "SPACE",
    Qt.Key_Exclam: "1",
    Qt.Key_At: "2",
    Qt.Key_NumberSign: "3",
    Qt.Key_Dollar: "4",
    Qt.Key_Percent: "5",
    Qt.Key_AsciiCircum: "6",
    Qt.Key_Ampersand: "7",
    Qt.Key_Asterisk: "8",
    Qt.Key_ParenLeft: "9",
    Qt.Key_ParenRight: "0",
    Qt.Key_Minus: "MINUS",
    Qt.Key_Plus: "PLUS",
    Qt.Key_Equal: "EQUALS",
    Qt.Key_BracketLeft: "OEM_4",
    Qt.Key_BracketRight: "OEM_6",
    Qt.Key_Backslash: "OEM_5",
    Qt.Key_Semicolon: "OEM_1",
    Qt.Key_Apostrophe: "OEM_7",
    Qt.Key_Comma: "OEM_COMMA",
    Qt.Key_Period: "OEM_PERIOD",
    Qt.Key_Slash: "OEM_2",
    Qt.Key_QuoteLeft: "OEM_3",
    # Arrow Keys
    Qt.Key_Up: "UP",
    Qt.Key_Down: "DOWN",
    Qt.Key_Left: "LEFT",
    Qt.Key_Right: "RIGHT",
    # Numpad Keys
    Qt.Key_NumLock: "Key_NumLock",
    Qt.Key_Plus | Qt.KeypadModifier: "Key_Numpad_Add",
    Qt.Key_Minus | Qt.KeypadModifier: "Key_Numpad_Subtract",
    Qt.Key_Asterisk | Qt.KeypadModifier: "Key_Numpad_Multiply",
    Qt.Key_Slash | Qt.KeypadModifier: "Key_Numpad_Divide",
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
    Qt.Key_Enter | Qt.KeypadModifier: "Key_NumpadEnter",
    Qt.Key_Period | Qt.KeypadModifier: "Key_Numpad_Decimal",
}

# Layout Definitions (only including QWERTY for now).
LAYOUTS = {
    "QWERTY": {
        "main": [
            [
                ("ESCAPE", "Esc", 2),
                ("F1", "F1", 1),
                ("F2", "F2", 1),
                ("F3", "F3", 1),
                ("F4", "F4", 1),
                ("F5", "F5", 1),
                ("F6", "F6", 1),
                ("F7", "F7", 1),
                ("F8", "F8", 1),
                ("F9", "F9", 1),
                ("F10", "F10", 1),
                ("F11", "F11", 1),
                ("F12", "F12", 1),
            ],
            [
                ("OEM_3", "`", 1),  # Previously TILDE
                ("1", "1", 1),
                ("2", "2", 1),
                ("3", "3", 1),
                ("4", "4", 1),
                ("5", "5", 1),
                ("6", "6", 1),
                ("7", "7", 1),
                ("8", "8", 1),
                ("9", "9", 1),
                ("0", "0", 1),
                ("MINUS", "-", 1),
                ("EQUALS", "=", 1),
                ("BACK", "Backspace", 2),  # Previously BACKSPACE
            ],
            [
                ("TAB", "Tab", 1.5),
                ("Q", "Q", 1),
                ("W", "W", 1),
                ("E", "E", 1),
                ("R", "R", 1),
                ("T", "T", 1),
                ("Y", "Y", 1),
                ("U", "U", 1),
                ("I", "I", 1),
                ("O", "O", 1),
                ("P", "P", 1),
                ("OEM_4", "[", 1),
                ("OEM_6", "]", 1),
                ("OEM_5", "\\", 1.5),  # BACKSLASH
            ],
            [
                ("CAPITAL", "Caps Lock", 2),  # CAPSLOCK
                ("A", "A", 1),
                ("S", "S", 1),
                ("D", "D", 1),
                ("F", "F", 1),
                ("G", "G", 1),
                ("H", "H", 1),
                ("J", "J", 1),
                ("K", "K", 1),
                ("L", "L", 1),
                ("OEM_1", ";", 1),  # SEMICOLON
                ("OEM_7", "'", 1),  # APOSTROPHE
                ("RETURN", "Enter", 2),  # ENTER
            ],
            [
                ("LSHIFT", "Shift", 2.5),
                ("Z", "Z", 1),
                ("X", "X", 1),
                ("C", "C", 1),
                ("V", "V", 1),
                ("B", "B", 1),
                ("N", "N", 1),
                ("M", "M", 1),
                ("OEM_COMMA", ",", 1),  # COMMA
                ("OEM_PERIOD", ".", 1),  # PERIOD
                ("OEM_2", "/", 1),  # SLASH
                ("RSHIFT", "Shift", 2.5),
            ],
            [
                ("LCONTROL", "Ctrl", 1.5),
                ("LWIN", "Win", 1.0),
                ("LMENU", "Alt", 1.0),  # LALT
                ("SPACE", "Space", 7),
                ("ALTGR", "AltGr", 1.0),  # RALT / RMENU
                ("RWIN", "Win", 1.0),
                ("APPS", "Menu", 1.0),
                ("RCONTROL", "Ctrl", 1.5),
            ],
        ],
        "nav": [
            [("INSERT", "Insert", 1), ("HOME", "Home", 1), ("PRIOR", "PG Up", 1)],
            [("DELETE", "Delete", 1), ("END", "End", 1), ("NEXT", "PG Down", 1)],
            [("", "", 3)],  # Empty row
            [("", "", 3)],  # Empty row
            [
                ("", "", 1),
                ("UP", "↑", 1),
                ("", "", 1),
            ],  # Empty row
            [
                ("LEFT", "←", 1),
                ("DOWN", "↓", 1),
                ("RIGHT", "→", 1),
            ],
        ],
        "numpad": [
            [("", 4)],  # Empty row
            [
                ("NUMLOCK", "Num Lock", 1),
                ("DIVIDE", "/", 1),
                ("MULTIPLY", "*", 1),
                ("SUBTRACT", "-", 1),
            ],
            [
                ("NUMPAD7", "7", 1),
                ("NUMPAD8", "8", 1),
                ("NUMPAD9", "9", 1),
                ("ADD", "+", 1, 2),
            ],  # ADD spans 2 rows
            [("NUMPAD4", "4", 1), ("NUMPAD5", "5", 1), ("NUMPAD6", "6", 1)],
            [
                ("NUMPAD1", "1", 1),
                ("NUMPAD2", "2", 1),
                ("NUMPAD3", "3", 1),
                ("NUMPADENTER", "Enter", 1, 2),
            ],  # NUMPADENTER spans 2 rows
            [("NUMPAD0", "0", 2), ("DECIMAL", ".", 1)],  # NUMPAD0 spans 2 columns
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
        "key_multicrew": "#8a6b8a",
        "key_store": "#8a8a4a",
        "key_all": "#5a5a5a",
        "key_pressed": "#333333",
        "key_active": "#8a4a4a",  # A distinct color for active keys - used only for debugging :)
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


class QTextEditLogger(logging.Handler, QObject):
    """A logging handler that emits log messages to a QTextEdit widget."""

    log_signal = pyqtSignal(str)

    def __init__(self, text_edit: QTextEdit):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.text_edit = text_edit
        self.log_signal.connect(self.append_log)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

    def append_log(self, msg):
        """Appends a log message to the QTextEdit widget."""
        self.text_edit.append(msg)


class EDKeys:
    """Handles parsing and managing key bindings for Elite: Dangerous."""

    binds_file = "main.binds"
    full_path = os.path.abspath(binds_file)
    print(f"Attempting to load binds file from: {full_path}")

    # def __init__(self, binds_file):
    #     """Initialize by parsing the provided binds file."""
    # logging.debug(f"Initializing EDKeys with binds file: '{binds_file}'")
    # self.binds_file = binds_file
    # self.bindings = self.parse_binds(binds_file)  # Changed from parse_binds_file to parse_binds
    # logging.debug(f"EDKeys initialized with bindings: {self.bindings}")

    def __init__(self, binds_file):
        self.binds_file = binds_file
        self.bindings = self.parse_binds_file()

    def parse_binds_file(self):
        bindings = {}
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()

            for element in root:
                action = element.tag
                primary = element.find("Primary")
                if primary is not None and "Key" in primary.attrib:
                    key = primary.attrib["Key"].strip()
                    if not key:
                        continue

                    normalized_key = self.normalize_key(key)
                    vkcode = self.get_vkcode_for_key(normalized_key)

                    if vkcode is not None:
                        if vkcode not in bindings:
                            bindings[vkcode] = []
                        bindings[vkcode].append(action)
        except ET.ParseError as e:
            logging.error(f"Error parsing binds file: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while parsing binds file: {e}")
        return bindings

    def normalize_key(self, key):
        key_map = {
            "Key_Numpad_0": "NUMPAD0",
            "Key_Numpad_1": "NUMPAD1",
            "Key_Numpad_2": "NUMPAD2",
            "Key_Numpad_3": "NUMPAD3",
            "Key_Numpad_4": "NUMPAD4",
            "Key_Numpad_5": "NUMPAD5",
            "Key_Numpad_6": "NUMPAD6",
            "Key_Numpad_7": "NUMPAD7",
            "Key_Numpad_8": "NUMPAD8",
            "Key_Numpad_9": "NUMPAD9",
            "Key_Up": "UP",
            "Key_Down": "DOWN",
            "Key_Left": "LEFT",
            "Key_Right": "RIGHT",
            "Key_PageUp": "PRIOR",
            "Key_PageDown": "NEXT",
            "Key_Home": "HOME",
            "Key_End": "END",
            "Key_Insert": "INSERT",
            "Key_Delete": "DELETE",
        }
        return key_map.get(key, key.upper().replace("KEY_", ""))

    def get_vkcode_for_key(self, key):
        return VK_CODE.get(key)

    def get_bound_actions(self, vkcode):
        return self.bindings.get(vkcode, [])

    def unbind_action(
        self, action
    ):  # Removes the specified action from all key bindings.
        """
        Removes the specified action from all key bindings.

        :param action: Action name to unbind.
        """
        for vkcode, actions in self.bindings.items():
            if action in actions:
                actions.remove(action)
                logging.info(f"Action '{action}' unbound from vkcode {vkcode}")


class KeyboardGUI(QMainWindow):
    """
    The main GUI window for the Keybind Visualizer.
    Displays a visual representation of keyboard bindings and handles user interactions.
    """

    def __init__(self, ed_keys, base_stylesheet):
        """
        Initializes the KeyboardGUI instance.

        :param ed_keys: An instance of the EDKeys class containing key bindings.
        :param base_stylesheet: The base stylesheet string without QTabBar::tab:selected.
        """
        super().__init__()
        self.ed_keys = ed_keys
        self.base_stylesheet = base_stylesheet  # Assign the base_stylesheet

        self.key_buttons = {}  # Nested dictionary: {category: {key_name: QPushButton}}
        self.key_states = {}  # Tracks the pressed state of keys
        self.base_key_size = 40
        self.is_key_dialog_open = False
        self.held_keys = set()

        self.highlight_active_keys = False  # Flag to toggle active key highlighting
        self.active_keys = set()  # Set to store keys that respond to keypresses

        self.altgr_active = False  # Flag to track ALTGR state

        # Initialize the refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_active_keys)
        self.refresh_timer.setInterval(1000)  # Refresh every 1 second

        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("QWidget:focus { outline: none; }")

        # Initialize UI components
        self.initUI()
        self.initialize_key_states()
        self.update_status_bar()

        # Ensure the central widget can receive focus
        central_widget = self.centralWidget()
        central_widget.setFocusPolicy(Qt.StrongFocus)
        central_widget.setFocus()

        # Alternatively, set focus to the main window
        self.setFocus()
        self.centralWidget().setFocus()

        # # Set up logging
        # logger = logging.getLogger()
        # logger.setLevel(logging.DEBUG)

        # # File handler
        # file_handler = logging.FileHandler("key_log.txt")
        # file_handler.setLevel(logging.DEBUG)
        # file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # file_handler.setFormatter(file_formatter)
        # logger.addHandler(file_handler)

        # # GUI handler
        # self.gui_handler = QTextEditLogger(self.log_text)
        # self.gui_handler.setLevel(logging.DEBUG)
        # gui_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # self.gui_handler.setFormatter(gui_formatter)
        # logger.addHandler(self.gui_handler)

        # Connect the tab changed signal to update the stylesheet
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Apply the stylesheet for the initially selected tab
        self.apply_selected_tab_style(self.tab_widget.currentIndex())

    def initUI(self):
        """
        Sets up the user interface components of the GUI.
        """
        self.setWindowTitle(
            "Elite: Dangerous Keybinds Visualizer v1.2 by glassesinsession"
        )
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1200, 700)

        # Apply the current theme
        self.setStyleSheet(
            f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};"
        )

        # Create menu bar
        menubar = self.menuBar()

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        self.key_block_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.key_block_status_label)

        # File menu
        fileMenu = menubar.addMenu("File")
        loadBindsAction = QAction("Load Keybind File", self)
        loadBindsAction.triggered.connect(self.load_bindings)
        fileMenu.addAction(loadBindsAction)

        saveBindsAction = QAction("Save Current Bindings", self)
        saveBindsAction.triggered.connect(self.save_bindings)
        fileMenu.addAction(saveBindsAction)

        # View menu
        viewMenu = menubar.addMenu("View")
        self.toggle_bindings_action = QAction("Show Bindings", self, checkable=True)
        self.toggle_bindings_action.setChecked(False)
        self.toggle_bindings_action.triggered.connect(self.toggle_bindings_text)
        viewMenu.addAction(self.toggle_bindings_action)

        self.show_unbound_actions_action = QAction("Show Unbound Actions", self)
        self.show_unbound_actions_action.triggered.connect(self.show_unbound_actions)
        viewMenu.addAction(self.show_unbound_actions_action)

        # Plugins menu
        pluginMenu = menubar.addMenu("Plugins")
        loadPluginAction = QAction("Load Plugin", self)
        loadPluginAction.triggered.connect(PluginManager.load_plugin)
        pluginMenu.addAction(loadPluginAction)

        unloadPluginAction = QAction("Unload Plugin", self)
        unloadPluginAction.triggered.connect(PluginManager.unload_plugin)
        pluginMenu.addAction(unloadPluginAction)

        # Main layout with tabs using a splitter
        splitter = QSplitter(Qt.Horizontal)
        central_widget = QWidget()
        splitter.addWidget(central_widget)
        self.setCentralWidget(splitter)

        # Initialize self.main_layout as an instance attribute
        self.main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(self.main_layout)  # Explicitly set the layout

        # Tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create 'All' tab first
        self.add_keyboard_tab("All", "QWERTY")

        # Add additional category-based tabs
        for category in BINDING_CATEGORIES.keys():
            self.add_keyboard_tab(
                category, "QWERTY"
            )  # Assuming all categories use 'QWERTY' layout

        # Dockable output window for key bindings
        self.bindings_text = QTextEdit()
        self.bindings_text.setReadOnly(True)
        self.bindings_text.setMinimumWidth(300)
        self.bindings_text.setStyleSheet(
            f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};"
        )

        self.dock_output = QDockWidget("Key Bindings", self)
        self.dock_output.setWidget(self.bindings_text)
        splitter.addWidget(self.dock_output)
        self.dock_output.hide()

        # DEBUG - Showing all recognized keys
        highlightActiveKeysAction = QAction(
            "Highlight Active Keys", self, checkable=True
        )
        highlightActiveKeysAction.setChecked(False)
        highlightActiveKeysAction.triggered.connect(self.toggle_active_key_highlight)
        viewMenu.addAction(highlightActiveKeysAction)

        # Log display widget
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.log_text.setMinimumHeight(150)  # Adjust as needed
        self.main_layout.addWidget(
            self.log_text
        )  # Now correctly using self.main_layout

        # Optionally, add a Clear Log button
        self.clear_log_button = QPushButton("Clear Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        self.main_layout.addWidget(self.clear_log_button)

        # Add a new toggle action for global key logging
        self.globalKeyLoggingAction = QAction(
            "Enable Global Key Logging", self, checkable=True
        )
        self.globalKeyLoggingAction.setChecked(False)
        self.globalKeyLoggingAction.triggered.connect(self.toggle_global_key_logging)
        viewMenu.addAction(self.globalKeyLoggingAction)

        reset_button = QPushButton("Reset Active Keys")
        reset_button.clicked.connect(self.reset_active_keys)
        self.main_layout.addWidget(reset_button)

    def clear_log(self):
        """Clears the log display widget."""
        self.log_text.clear()
        logging.info("Log cleared by user.")

    def apply_theme(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {THEMES[CURRENT_THEME]['background']};
                color: {THEMES[CURRENT_THEME]['text']};
            }}
            QTextEdit, QLineEdit {{
                background-color: {self.get_lighter_color(THEMES[CURRENT_THEME]['background'])};
                color: {THEMES[CURRENT_THEME]['text']};
                border: 1px solid {THEMES[CURRENT_THEME]['key_normal']};
            }}
        """
        )
        self.update()

    def create_menu(self):
        """Create the application menu."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        load_binds_action = QAction("Load Keybind File", self)
        load_binds_action.triggered.connect(self.load_bindings)
        file_menu.addAction(load_binds_action)

        save_binds_action = QAction("Save Current Bindings", self)
        save_binds_action.triggered.connect(self.save_bindings)
        file_menu.addAction(save_binds_action)

    def add_keyboard_tab(self, category, layout_name):
        """
        Creates a new tab in the tab widget for the specified category using the given layout.

        :param category: The category name (e.g., "All", "Ship", "General").
        :param layout_name: The layout identifier (e.g., "QWERTY").
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

        numpad_section = self.create_keyboard_section(
            numpad_layout, category, key_size=1.2
        )
        keyboard_layout.addLayout(numpad_section, 15)

        tab_layout.addLayout(keyboard_layout)
        self.tab_widget.addTab(tab, category)

    def create_keyboard_section(self, layout, tab_category, key_size=1.0):
        section_layout = QGridLayout()
        section_layout.setSpacing(4)
        section_layout.setContentsMargins(2, 2, 2, 2)

        for row_idx, key_row in enumerate(layout):
            col_idx = 0
            for key_data in key_row:
                if len(key_data) == 4:
                    key_name, display_label, size, row_span = key_data
                elif len(key_data) == 3:
                    key_name, display_label, size = key_data
                    row_span = 1
                else:
                    key_name, display_label, size, row_span = "", "", key_data[1], 1

                col_span = int(size * 2 * key_size)

                if not key_name:
                    empty_widget = QWidget()
                    empty_widget.setSizePolicy(
                        QSizePolicy.Expanding, QSizePolicy.Expanding
                    )
                    empty_widget.setStyleSheet(
                        f"background-color: {THEMES[CURRENT_THEME]['background']};"
                    )
                    section_layout.addWidget(
                        empty_widget, row_idx, col_idx, row_span, col_span
                    )
                else:
                    button = self.create_key_button(
                        key_name, display_label, size * key_size, tab_category
                    )
                    section_layout.addWidget(
                        button, row_idx, col_idx, row_span, col_span
                    )

                    if tab_category not in self.key_buttons:
                        self.key_buttons[tab_category] = {}
                    self.key_buttons[tab_category][key_name] = button

                col_idx += col_span

        for i in range(col_idx):
            section_layout.setColumnStretch(i, 1)

        return section_layout

    def create_key_button(self, key_name, display_label, size, tab_category):
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumSize(int(self.base_key_size * size), self.base_key_size)
        button.setText(display_label)

        normalized_key = self.ed_keys.normalize_key(key_name)
        vkcode = self.ed_keys.get_vkcode_for_key(normalized_key)
        bound_actions = self.ed_keys.get_bound_actions(vkcode)

        if tab_category == "All":
            relevant_actions = bound_actions
        else:
            relevant_actions = [
                action
                for action in bound_actions
                if action in BINDING_CATEGORIES.get(tab_category, [])
            ]
            # Include General actions only in the General tab
            if tab_category == "General":
                relevant_actions += [
                    action
                    for action in bound_actions
                    if action in BINDING_CATEGORIES["General"]
                ]

        if relevant_actions:
            if tab_category != "All":
                primary_category = tab_category
            else:
                categories = self.determine_key_categories(key_name)
                non_general_categories = categories - {"General"}
                primary_category = (
                    next(iter(non_general_categories))
                    if non_general_categories
                    else "General"
                )

            key_color_key = f"key_{primary_category.lower()}"
            background_color = THEMES[CURRENT_THEME].get(
                key_color_key, THEMES[CURRENT_THEME]["key_bound"]
            )
        else:
            background_color = THEMES[CURRENT_THEME]["key_normal"]

        pressed_color = self.get_lighter_color(background_color)

        button.setStyleSheet(
            f"""
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
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
        )

        tooltip_text = "\n".join(relevant_actions) if relevant_actions else "Unassigned"
        button.setToolTip(tooltip_text)

        button.setProperty("all_bound_actions", bound_actions)
        button.setProperty("relevant_actions", relevant_actions)
        button.setProperty(
            "primary_category", primary_category if relevant_actions else None
        )

        return button

    def toggle_active_key_highlight(self):
        self.highlight_active_keys = not self.highlight_active_keys
        if self.highlight_active_keys:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
            self.active_keys.clear()  # Clear active keys when turning off the feature
        self.update_all_key_visuals()

    def toggle_active_key_highlight(
        self,
    ):  # Debug function - shows all recognized keys.
        self.highlight_active_keys = not self.highlight_active_keys
        if self.highlight_active_keys:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
            self.active_keys.clear()
        self.refresh_all_tabs()

    def refresh_active_keys(self):  # Debug function - shows all recognized keys.
        if self.highlight_active_keys:
            self.update_all_key_visuals()

    def apply_text_widget_theme(self, text_widget):
        """Apply theme to text widgets such as the key bindings output."""
        text_widget.setStyleSheet(
            f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};"
        )

    def load_bindings(self):
        logging.debug(f"EDKeys: Attempting to load binds from '{self.binds_file}'.")
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()
            logging.debug("EDKeys: XML parsed successfully.")

            for binding in root:
                action_name = binding.tag  # e.g., StoreCamZoomIn
                primary = binding.find("Primary")
                secondary = binding.find("Secondary")

                # Extract primary binding
                if primary is not None:
                    device = primary.get("Device")
                    key = primary.get("Key")
                    if device == "Keyboard" and key:
                        self.bindings[key] = action_name
                        logging.debug(
                            f"EDKeys: Bound key '{key}' to action '{action_name}'."
                        )

                # Extract secondary binding (if needed)
                # Currently, secondary bindings are ignored if Device is {NoDevice}
                # Implement as per your application's requirements

            logging.info(f"Total bindings loaded: {len(self.bindings)}")
        except FileNotFoundError:
            logging.error(f"EDKeys: Binds file '{self.binds_file}' not found.")
            raise
        except ET.ParseError as e:
            logging.error(f"EDKeys: XML parse error in binds file: {e}")
            raise
        except Exception as e:
            logging.error(f"EDKeys: Unexpected error while loading binds: {e}")
            raise

    def get_bindings(self):
        return self.bindings

    def save_bindings(self):
        """Save the current bindings to an XML file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Keybinds", "", "Bind Files (*.binds *.xml)"
        )
        if file_path:
            self.ed_keys.save_bindings_to_file(file_path)

    def refresh_all_tabs(self):
        logging.debug("Starting to refresh all tabs")

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            category = self.tab_widget.tabText(index)

            # Clear existing layout
            layout = tab.layout()
            if layout:
                self.clear_layout(layout)
            else:
                layout = QVBoxLayout(tab)

            keyboard_layout = QHBoxLayout()
            keyboard_layout.setSpacing(10)

            # Fetch the specific layout sections from LAYOUTS
            main_layout = LAYOUTS["QWERTY"]["main"]
            nav_layout = LAYOUTS["QWERTY"]["nav"]
            numpad_layout = LAYOUTS["QWERTY"]["numpad"]

            # Create keyboard sections
            main_keyboard = self.create_keyboard_section(main_layout, category)
            keyboard_layout.addLayout(main_keyboard, 70)

            nav_section = self.create_keyboard_section(
                nav_layout, category, key_size=1.2
            )
            keyboard_layout.addLayout(nav_section, 15)

            numpad_section = self.create_keyboard_section(
                numpad_layout, category, key_size=1.2
            )
            keyboard_layout.addLayout(numpad_section, 15)

            layout.addLayout(keyboard_layout)
            logging.debug(f"Refreshed tab '{category}'")

        logging.debug("Finished refreshing all tabs")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def get_lighter_color(self, color):
        # Convert hex to RGB
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))

        # Increase each component by 20%, but not exceeding 255
        r = min(int(r * 1.2), 255)
        g = min(int(g * 1.2), 255)
        b = min(int(b * 1.2), 255)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def initialize_key_states(self):
        """
        Initializes the state of each key (pressed or released) to False.
        """
        for category, keys in self.key_buttons.items():
            for key in keys:
                self.key_states[key] = False
        logging.debug("Initialized all key states to False.")

    def update_status_bar(self):
        if self.is_key_dialog_open:
            status = "Keys Unblocked (Dialog Open)"
            color = "green"
        else:
            status = "Keys Blocked (Main Interface)"
            color = "red"
        self.key_block_status_label.setText(f"<font color='{color}'>{status}</font>")
        logging.debug(f"Status bar updated: {status}")

    def toggle_bindings_text(
        self, checked
    ):  # Toggles the visibility of the bindings output dock.
        """
        Toggles the visibility of the bindings output dock.

        :param checked: Boolean indicating if the action is checked.
        """
        if checked:
            self.dock_output.show()
            logging.debug("Bindings dock shown.")
        else:
            self.dock_output.hide()
            logging.debug("Bindings dock hidden.")

    def show_unbound_actions(
        self,
    ):  # Displays a dialog listing all unbound actions across categories. - TODO: Layout
        """
        Displays a dialog listing all unbound actions across categories.
        """
        unbound_actions = self.get_unbound_actions()
        if not any(unbound_actions.values()):
            QMessageBox.information(
                self, "Unbound Actions", "All actions are currently bound to keys."
            )
            logging.info("All actions are bound.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Unbound Actions")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)

        for category, actions in unbound_actions.items():
            if actions:
                group_layout = QVBoxLayout()
                category_label = QLabel(f"<h3>{category}</h3>")
                group_layout.addWidget(category_label)
                for action in actions:
                    action_label = QLabel(f"- {action}")
                    group_layout.addWidget(action_label)
                scroll_layout.addLayout(group_layout)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec_()
        logging.debug("Displayed unbound actions dialog.")

    def get_unbound_actions(
        self,
    ):  # Retrieves all actions that are not currently bound to any key.
        """
        Retrieves all actions that are not currently bound to any key.

        :return: Dictionary mapping categories to their respective unbound actions.
        """
        unbound = {}
        all_bound_actions = set()
        for actions in self.ed_keys.bindings.values():
            all_bound_actions.update(actions)

        for category, actions in BINDING_CATEGORIES.items():
            unbound_actions = [
                action for action in actions if action not in all_bound_actions
            ]
            if unbound_actions:
                unbound[category] = unbound_actions

        logging.debug(f"Unbound actions: {unbound}")
        return unbound

    def assign_key(self, key_name):
        """
        Opens a dialog to assign or unbind actions to a specific key.

        :param key_name: Key name to assign actions to.
        """
        self.is_key_dialog_open = True
        self.update_status_bar()

        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())

        category_order = ["General"] + [
            self.tab_widget.tabText(i)
            for i in range(self.tab_widget.count())
            if self.tab_widget.tabText(i) not in ["All", "General"]
        ]

        if current_tab == "All":
            relevant_categories = category_order
        else:
            relevant_categories = [current_tab, "General"]

        actions = []
        subcategories = {}
        for category in relevant_categories:
            for action in BINDING_CATEGORIES.get(category, []):
                actions.append(action)
                subcategories[action] = category

        normalized_key = self.ed_keys.normalize_key(key_name)
        vkcode = self.ed_keys.get_vkcode_for_key(normalized_key)
        current_bindings = self.ed_keys.get_bound_actions(vkcode)

        available_actions = actions

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Assign Key '{key_name}'")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setSelectionMode(QTreeWidget.MultiSelection)
        category_items = {}
        for category in relevant_categories:
            if category in set(subcategories.values()):
                category_item = QTreeWidgetItem([category])
                tree.addTopLevelItem(category_item)
                category_items[category] = category_item

        for action in sorted(available_actions):
            sub_item = QTreeWidgetItem([action])
            category = subcategories.get(action, "Unknown")
            category_items[category].addChild(sub_item)
            if action in current_bindings:
                sub_item.setCheckState(0, Qt.Checked)
                font = QFont()
                font.setBold(True)
                sub_item.setFont(0, font)
            else:
                sub_item.setCheckState(0, Qt.Unchecked)

        tree.expandAll()
        layout.addWidget(tree)

        button_layout = QHBoxLayout()

        # Define buttons before connecting signals
        assign_button = QPushButton("Assign Selected")
        unbind_button = QPushButton("Unbind Selected")
        close_button = QPushButton("Close")

        button_layout.addWidget(assign_button)
        button_layout.addWidget(unbind_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Define slot functions within the method
        def on_assign():
            selected_items = tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(
                    dialog, "No Selection", "No actions were selected to assign."
                )
                return
            for item in selected_items:
                action = item.text(0)
                if action not in self.ed_keys.bindings.get(vkcode, []):
                    self.ed_keys.unbind_action(action)
                    self.ed_keys.bindings.setdefault(vkcode, []).append(action)
            self.refresh_all_tabs()
            self.status_bar.showMessage(
                f"Assigned selected actions to key '{key_name}'."
            )
            logging.info(f"Assigned actions to key '{key_name}': {selected_items}")
            dialog.accept()

        def on_unbind():
            selected_items = tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(
                    dialog, "No Selection", "No actions were selected to unbind."
                )
                return
            for item in selected_items:
                action = item.text(0)
                if action in self.ed_keys.bindings.get(vkcode, []):
                    self.ed_keys.bindings[vkcode].remove(action)
            self.refresh_all_tabs()
            self.status_bar.showMessage(
                f"Unbound selected actions from key '{key_name}'."
            )
            logging.info(f"Unbound actions from key '{key_name}': {selected_items}")
            dialog.accept()

        def on_dialog_close():
            self.is_key_dialog_open = False
            self.update_status_bar()
            logging.debug("Key assignment dialog closed.")
            dialog.reject()

        # Connect signals after defining buttons and slots
        assign_button.clicked.connect(on_assign)
        unbind_button.clicked.connect(on_unbind)
        close_button.clicked.connect(on_dialog_close)

        dialog.finished.connect(lambda: setattr(self, "is_key_dialog_open", False))
        dialog.finished.connect(self.update_status_bar)

        dialog.exec_()

    def update_key_button(self, key_name, category):
        """
        Updates the visual state and tooltip of a specific key button based on its bindings.
        """
        button = self.key_buttons[category].get(key_name)
        if button:
            normalized_key = self.ed_keys.normalize_key(key_name)
            vkcode = self.ed_keys.get_vkcode_for_key(normalized_key)
            all_bound_actions = self.ed_keys.get_bound_actions(vkcode)

            if category == "All":
                relevant_actions = all_bound_actions
            else:
                relevant_actions = [
                    a
                    for a in all_bound_actions
                    if a in BINDING_CATEGORIES.get(category, [])
                    or a in BINDING_CATEGORIES.get("General", [])
                ]

            categories = self.determine_key_categories(key_name)

            if all_bound_actions:
                primary_category = next(iter(categories))
                key_color_key = f"key_{primary_category.lower()}"
                background_color = THEMES[CURRENT_THEME].get(
                    key_color_key, THEMES[CURRENT_THEME]["key_bound"]
                )
            else:
                background_color = THEMES[CURRENT_THEME]["key_normal"]
                primary_category = None

            pressed_color = self.get_lighter_color(background_color)

            button.setStyleSheet(
                f"""
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
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """
            )

            tooltip_text = (
                "\n".join(relevant_actions) if relevant_actions else "Unassigned"
            )
            button.setToolTip(tooltip_text)

            button.setProperty("all_bound_actions", all_bound_actions)
            button.setProperty("primary_category", primary_category)

            logging.debug(f"Updated button '{key_name}' in category '{category}'")

    def update_key_visual(self, key_name, is_pressed):
        current_category = self.tab_widget.tabText(self.tab_widget.currentIndex())
        categories = ["All", current_category] if current_category != "All" else ["All"]

        for category in categories:
            if category in self.key_buttons and key_name in self.key_buttons[category]:
                button = self.key_buttons[category][key_name]
                if button.isVisible():
                    button.setDown(is_pressed)

                    if self.highlight_active_keys:
                        if is_pressed:
                            self.active_keys.add(key_name)
                        self.update_key_style(button, key_name in self.active_keys)
                    else:
                        self.update_key_style(button, is_pressed)

                    logging.debug(
                        f"Updated visual for key: {key_name}, pressed: {is_pressed}, category: {category}"
                    )
                    break  # Exit after updating the first visible button

    def reset_active_keys(self):
        self.active_keys.clear()
        self.update_all_key_visuals()

    # def update_all_key_visuals(self):
    #     for category in self.key_buttons:
    #         for key_name, button in self.key_buttons[category].items():
    #             self.update_key_button(key_name, category)

    def update_all_key_visuals(self):
        """
        Updates the visual state of all key buttons across all tabs.
        """
        for category in self.key_buttons:
            for key_name, button in self.key_buttons[category].items():
                self.update_key_button(key_name, category)

    def update_key_style(self, button, is_active_or_pressed):
        has_binding = bool(button.property("relevant_actions"))
        primary_category = button.property("primary_category")

        if self.highlight_active_keys:
            if is_active_or_pressed:
                background_color = THEMES[CURRENT_THEME]["key_active"]
            elif has_binding:
                key_color_key = f"key_{primary_category.lower()}"
                background_color = THEMES[CURRENT_THEME].get(
                    key_color_key, THEMES[CURRENT_THEME]["key_bound"]
                )
            else:
                background_color = THEMES[CURRENT_THEME]["key_normal"]
        else:
            if is_active_or_pressed:
                background_color = THEMES[CURRENT_THEME]["key_pressed"]
            elif has_binding:
                key_color_key = f"key_{primary_category.lower()}"
                background_color = THEMES[CURRENT_THEME].get(
                    key_color_key, THEMES[CURRENT_THEME]["key_bound"]
                )
            else:
                background_color = THEMES[CURRENT_THEME]["key_normal"]

        button.setStyleSheet(
            f"""
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
        """
        )

        # Update tooltip
        tooltip_text = button.toolTip().split("\n")[0]  # Keep only the first line
        if self.highlight_active_keys:
            tooltip_text += "\n(Active)" if is_active_or_pressed else ""
        else:
            tooltip_text += "\n(Pressed)" if is_active_or_pressed else ""
        button.setToolTip(tooltip_text)

    def find_key_button(
        self, key_name, category
    ):  # Finds the QPushButton object corresponding to a given key name and category.
        """
        Finds the QPushButton object corresponding to a given key name and category.

        :param key_name: Key name to search for.
        :param category: Binding category.
        :return: QPushButton object or None if not found.
        """
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            tab_category = self.tab_widget.tabText(index)
            if tab_category != category and category != "All":
                continue
            for btn_key, button in self.key_buttons.items():
                if btn_key == key_name and button.property("category") == category:
                    return button
        return None

    def get_button_style(self, is_pressed, has_binding, category, is_general=False):
        """
        Generates the stylesheet for a key button based on its state and category.

        :param is_pressed: Boolean indicating if the key is pressed.
        :param has_binding: Boolean indicating if the key has bindings.
        :param category: Binding category of the key.
        :param is_general: Boolean indicating if the key is in the 'General' category.
        :return: Stylesheet string.
        """
        if has_binding:
            if category.lower() in THEMES[CURRENT_THEME]:
                background_color = THEMES[CURRENT_THEME][f"key_{category.lower()}"]
            else:
                background_color = THEMES[CURRENT_THEME]["key_bound"]
        else:
            background_color = THEMES[CURRENT_THEME]["key_normal"]

        if is_pressed:
            background_color = self.get_pressed_color(background_color)

        style = f"""
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
        """
        if is_pressed:
            style += f"""
                QPushButton:pressed {{
                    background-color: {THEMES[CURRENT_THEME]['key_pressed']};
                }}
            """
        return style

    def get_pressed_color(
        self, color
    ):  # Calculates a lighter shade of the given color for the pressed state.
        """
        Calculates a lighter shade of the given color for the pressed state.

        :param color: Hex color string (e.g., '#555555').
        :return: Hex color string for the pressed state.
        """
        try:
            color = color.lstrip("#")
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            r = min(int(r * 1.3), 255)
            g = min(int(g * 1.3), 255)
            b = min(int(b * 1.3), 255)
            pressed_color = f"#{r:02x}{g:02x}{b:02x}"
            logging.debug(f"Pressed color for '{color}': {pressed_color}")
            return pressed_color
        except Exception as e:
            logging.error(f"Error in get_pressed_color with color '{color}': {e}")
            return color

    def order_actions_by_category(
        self, actions, current_category
    ):  # Orders actions by the current category followed by others.
        """
        Orders actions by the current category followed by others.

        :param actions: List of action names.
        :param current_category: Current binding category.
        :return: Ordered list of action names.
        """
        current_cat_actions = [
            action
            for action in actions
            if action in BINDING_CATEGORIES.get(current_category, [])
        ]
        other_actions = [
            action for action in actions if action not in current_cat_actions
        ]
        ordered_actions = current_cat_actions + other_actions
        logging.debug(f"Ordered actions: {ordered_actions}")
        return ordered_actions

    def determine_key_categories(self, key_name):
        categories = set()
        normalized_key = self.ed_keys.normalize_key(key_name)
        vkcode = self.ed_keys.get_vkcode_for_key(normalized_key)
        bound_actions = self.ed_keys.get_bound_actions(vkcode)

        for action in bound_actions:
            for category, actions in BINDING_CATEGORIES.items():
                if action in actions:
                    categories.add(category)

        if not categories:
            categories.add("General")  # Default category if no bindings found

        return categories

    def determine_specific_category(self, actions, tab_category):
        categories = set()
        for action in actions:
            for cat, cat_actions in BINDING_CATEGORIES.items():
                if action in cat_actions:
                    categories.add(cat)
                    break

        if categories == {"General"} or not categories:
            return "General"
        elif len(categories) == 1:
            return categories.pop()
        else:
            non_general_categories = categories - {"General"}
            if tab_category != "All" and tab_category in non_general_categories:
                return tab_category
            else:
                return (
                    next(iter(non_general_categories))
                    if non_general_categories
                    else "General"
                )

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        key = event.key()
        key_name = self.get_key_name(event)

        if key_name:
            self.key_states[key_name] = True
            logging.info(f"Key pressed - Key Name: {key_name}")
            self.update_key_visual(key_name, True)

        if self.should_block_key(key):
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        key = event.key()
        key_name = self.get_key_name(event)

        if key_name:
            self.key_states[key_name] = False
            logging.info(f"Key released - Key Name: {key_name}")
            self.update_key_visual(key_name, False)

        if self.should_block_key(key):
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def get_key_name(self, event):
        key = event.key()
        scan_code = event.nativeScanCode()
        text = event.text()
        logging.debug(
            f"Key pressed - Qt Key: {key}, Scan Code: {scan_code}, Text: '{text}'"
        )

        # Handle modifier keys based on scan codes
        if key == Qt.Key_Shift:
            key_name = "LSHIFT" if scan_code == 42 else "RSHIFT"
        elif key == Qt.Key_Control:
            key_name = "LCONTROL" if scan_code == 29 else "RCONTROL"
        elif key == Qt.Key_Alt:
            if scan_code == 56:  # Left Alt
                key_name = "LMENU"
            elif scan_code == 100:  # Right Alt (AltGr)
                key_name = "RMENU"  # or "ALTGR"
            else:
                key_name = "ALT"  # Generic fallback
        elif key == Qt.Key_Meta:
            key_name = "RWIN" if scan_code == 91 else "LWIN"
        elif key == Qt.Key_NumLock:
            key_name = "NUMLOCK"
        elif key == Qt.Key_Tab:
            key_name = "TAB"
            logging.debug(f"Tab key detected. Key: {key}, Scan Code: {scan_code}")
        else:
            # Handle numpad keys
            if event.modifiers() & Qt.KeypadModifier:
                numpad_map = {
                    Qt.Key_0: "NUMPAD0",
                    Qt.Key_1: "NUMPAD1",
                    Qt.Key_2: "NUMPAD2",
                    Qt.Key_3: "NUMPAD3",
                    Qt.Key_4: "NUMPAD4",
                    Qt.Key_5: "NUMPAD5",
                    Qt.Key_6: "NUMPAD6",
                    Qt.Key_7: "NUMPAD7",
                    Qt.Key_8: "NUMPAD8",
                    Qt.Key_9: "NUMPAD9",
                    Qt.Key_Plus: "ADD",
                    Qt.Key_Minus: "SUBTRACT",
                    Qt.Key_Asterisk: "MULTIPLY",
                    Qt.Key_Slash: "DIVIDE",
                    Qt.Key_Period: "DECIMAL",
                    Qt.Key_Return: "NUMPADENTER",
                    Qt.Key_Enter: "NUMPADENTER",
                }
                key_name = numpad_map.get(key, "")
                if key_name:
                    logging.debug(f"Mapped to numpad key: {key_name}")
                else:
                    logging.debug("Numpad key not found in mapping.")
            else:
                # For other keys, use the KEY_MAPPING
                key_name = KEY_MAPPING.get(key, "")
                if not key_name:
                    # If not found in KEY_MAPPING, try to get it from the event's text
                    key_name = text.upper()
                    if key_name:
                        logging.debug(f"Mapped using text: {key_name}")
                    else:
                        logging.debug("Key name could not be determined.")

        logging.debug(f"Final Mapped Key Name: {key_name}")  # Detailed log
        return key_name

    def display_bindings(
        self, key_name
    ):  # Displays the actions bound to a specific key in the bindings text area.
        """
        Displays the actions bound to a specific key in the bindings text area.

        :param key_name: Key name to display bindings for.
        """
        if not self.bindings_text.isVisible():
            return
        if key_name in self.key_buttons:
            button = self.key_buttons[key_name]
            all_bound_actions = button.property("all_bound_actions")
            current_category = self.tab_widget.tabText(self.tab_widget.currentIndex())

            self.bindings_text.clear()
            self.bindings_text.append(f"<h2>Key: {key_name}</h2>")

            if all_bound_actions:
                categorized_actions = self.categorize_actions(all_bound_actions)

                category_order = [current_category, "General"] + [
                    cat
                    for cat in BINDING_CATEGORIES.keys()
                    if cat not in [current_category, "General"]
                ]

                for category in category_order:
                    if category in categorized_actions:
                        self.display_category(category, categorized_actions[category])
            else:
                self.bindings_text.append("No bindings found")

    def should_block_key(self, key):
        blocked_keys = [
            Qt.Key_Tab,
            Qt.Key_Backtab,
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_PageUp,
            Qt.Key_PageDown,
            Qt.Key_Home,
            Qt.Key_End,
            Qt.Key_Return,
            Qt.Key_Enter,
            Qt.Key_Space,
        ]
        return key in blocked_keys

    ###  Using keyboard to log keypresses to show on keyboard, even while in game - technically DEBUG, allows you to see the keypresses in the GUI no matter where you are.

    def on_key_press(self, key):
        if not self.globalKeyLoggingAction.isChecked():
            return

        try:
            key_char = key.char.upper()
        except AttributeError:
            key_char = str(key).split(".")[-1].upper()

        if key_char in VK_CODE and key_char not in self.held_keys:
            self.held_keys.add(key_char)
            logging.debug(f"Global key pressed: {key_char}")
            self.update_key_visual(key_char, True)

    def on_key_release(self, key):
        if not self.globalKeyLoggingAction.isChecked():
            return

        try:
            key_char = key.char.upper()
        except AttributeError:
            key_char = str(key).split(".")[-1].upper()

        if key_char in VK_CODE and key_char in self.held_keys:
            self.held_keys.remove(key_char)
            logging.debug(f"Global key released: {key_char}")
            self.update_key_visual(key_char, False)

    def toggle_global_key_logging(self, state):
        if state:
            # Enable global key logging
            self.listener = keyboard.Listener(
                on_press=self.on_key_press, on_release=self.on_key_release
            )
            self.listener.start()
            logging.info("Global key logging enabled")
        else:
            # Disable global key logging
            if hasattr(self, "listener"):
                self.listener.stop()
                del self.listener
            logging.info("Global key logging disabled")

    ### GUI tab colours

    def get_group_color(self, tab_index):
        """
        Retrieves the color associated with the group's tab.

        :param tab_index: The index of the selected tab.
        :return: Hex color string.
        """
        group_name = self.tab_widget.tabText(tab_index)
        # Assuming group_name corresponds to a color key, e.g., "Ship" -> "key_ship"
        color_key = f"key_{group_name.lower()}"
        return THEMES[CURRENT_THEME].get(color_key, THEMES[CURRENT_THEME]["key_bound"])

    def on_tab_changed(self, index):
        """
        Slot triggered when the current tab changes.

        :param index: The new tab index.
        """
        self.apply_selected_tab_style(index)

    def apply_selected_tab_style(self, index):
        """
        Updates the stylesheet to reflect the selected tab's group color.

        :param index: The index of the selected tab.
        """
        group_color = self.get_group_color(index)
        text_color = THEMES[CURRENT_THEME]["text"]

        # Define the QTabBar::tab:selected stylesheet with the group color
        selected_tab_stylesheet = f"""
        QTabBar::tab:selected {{
            background-color: {group_color};
            border-color: {group_color};
            border-bottom: 2px solid {text_color};
            font-weight: bold;
        }}
        """

        # Combine the base stylesheet with the selected_tab_stylesheet
        full_stylesheet = self.base_stylesheet + selected_tab_stylesheet

        # Apply the combined stylesheet to the QTabWidget
        self.tab_widget.setStyleSheet(full_stylesheet)

    ### New


class PluginManager:
    """
    Manages the loading and unloading of plugins.
    """

    def __init__(self, parent):
        self.parent = parent
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
            return

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                plugin_class = getattr(module, "Plugin", None)
                if plugin_class and issubclass(plugin_class, PluginInterface):
                    plugin_instance = plugin_class(self.parent)
                    plugin_instance.load()
                    self.plugins[plugin_name] = plugin_instance
                    self.plugin_paths[plugin_name] = plugin_path
                    QMessageBox.information(
                        self.parent,
                        "Plugin Loaded",
                        f"Plugin '{plugin_name}' loaded successfully.",
                    )
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Plugin Load Error",
                        f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.",
                    )
            except Exception as e:
                logging.error(f"Error loading plugin '{plugin_name}': {e}")
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
        except Exception as e:
            logging.error(f"Error unloading plugin '{plugin_name}': {e}")
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

    def list_plugins(self):
        """
        Returns a list of all available plugins with their load status.
        """
        # List all .py files in the plugins directory
        plugins_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.isdir(plugins_dir):
            os.makedirs(plugins_dir)

        plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith(".py")]
        all_plugins = set(os.path.splitext(f)[0] for f in plugin_files)
        plugin_list = []
        for plugin in all_plugins:
            status = "Loaded" if plugin in self.plugins else "Not Loaded"
            plugin_list.append((plugin, status))
        return plugin_list


class PluginInterface:
    """
    A base class for all plugins. Plugins should inherit from this class and implement the load and unload methods.
    """

    def __init__(self, main_window):
        self.main_window = main_window

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
    logging.debug("Application started.")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

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
    logging.debug(f"Loading bindings from '{binds_file}'.")
    ed_keys = EDKeys(binds_file)
    logging.debug("Bindings loaded successfully.")

    # Pass the base_stylesheet to KeyboardGUI
    ex = KeyboardGUI(ed_keys, base_stylesheet)
    ex.show()
    logging.debug("KeyboardGUI initialized and displayed.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
