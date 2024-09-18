import xml.etree.ElementTree as ET
import sys
import os
import configparser
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QTextEdit,
    QAction, QMenuBar, QDockWidget, QFileDialog, QTabWidget, QMessageBox,
    QInputDialog, QDialog, QTreeWidget, QTreeWidgetItem, QScrollArea, QLineEdit, QComboBox, QSplitter,
)
from PyQt5.QtCore import Qt, QEvent, QEventLoop
from PyQt5.QtGui import QFont

import importlib.util

import ctypes
from ctypes import wintypes

# Determine the architecture and define ULONG_PTR accordingly
if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Capture all levels of logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # FileHandler with UTF-8 encoding
        logging.FileHandler("EDKeyVisualizer.log", encoding='utf-8'),
        
        # StreamHandler with UTF-8 encoding and error handling
        logging.StreamHandler(sys.stdout)
    ]
)

# Remove any duplicate StreamHandlers
logger = logging.getLogger()
stream_handler_exists = any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)
if not stream_handler_exists:
    # Add StreamHandler only if it doesn't exist
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(stream_handler)


# VK_CODES dictionary
VK_CODES = {
    # Function Keys
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,

    # Numeric Keys (Main Keyboard)
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,

    # Numpad Keys
    'NUMPAD0': 0x60, 'NUMPAD1': 0x61, 'NUMPAD2': 0x62, 'NUMPAD3': 0x63,
    'NUMPAD4': 0x64, 'NUMPAD5': 0x65, 'NUMPAD6': 0x66, 'NUMPAD7': 0x67,
    'NUMPAD8': 0x68, 'NUMPAD9': 0x69,
    'ADD': 0x6B, 'SUBTRACT': 0x6D, 'MULTIPLY': 0x6A, 'DIVIDE': 0x6F,
    'DECIMAL': 0x6E, 'NUMPADENTER': 0x0D,  # ENTER is 0x0D

    # Alphabet Keys
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
    'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
    'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59,
    'Z': 0x5A,

    # Control Keys
    'ESCAPE': 0x1B, 'TAB': 0x09, 'LSHIFT': 0xA0, 'RSHIFT': 0xA1,
    'LCONTROL': 0xA2, 'RCONTROL': 0xA3, 'BACKSPACE': 0x08,
    'RETURN': 0x0D, 'LALT': 0xA4, 'RALT': 0xA5,
    'SPACE': 0x20, 'CAPSLOCK': 0x14, 'NUMLOCK': 0x90, 'SCROLLLOCK': 0x91,
    'LWIN': 0x5B, 'RWIN': 0x5C, 'MENU': 0x5D,  # Menu key

    # Symbol Keys
    'MINUS': 0xBD, 'EQUALS': 0xBB, 'LBRACKET': 0xDB, 'RBRACKET': 0xDD,
    'SEMICOLON': 0xBA, 'APOSTROPHE': 0xDE, 'GRAVE': 0xC0,
    'BACKSLASH': 0xDC, 'COMMA': 0xBC, 'PERIOD': 0xBE, 'SLASH': 0xBF,

    # Arrow Keys
    'LEFT': 0x25, 'UP': 0x26, 'RIGHT': 0x27, 'DOWN': 0x28,

    # Extended Keys
    'INSERT': 0x2D, 'DELETE': 0x2E, 'HOME': 0x24, 'END': 0x23,
    'PRIOR': 0x21, 'NEXT': 0x22,  # Page Up and Page Down
}

# Centralized Key Mapping Dictionary
KEY_MAPPING = {
    # Function Keys
    Qt.Key_F1: 'F1',
    Qt.Key_F2: 'F2',
    Qt.Key_F3: 'F3',
    Qt.Key_F4: 'F4',
    Qt.Key_F5: 'F5',
    Qt.Key_F6: 'F6',
    Qt.Key_F7: 'F7',
    Qt.Key_F8: 'F8',
    Qt.Key_F9: 'F9',
    Qt.Key_F10: 'F10',
    Qt.Key_F11: 'F11',
    Qt.Key_F12: 'F12',

    # Alphanumeric Keys
    Qt.Key_A: 'A',
    Qt.Key_B: 'B',
    Qt.Key_C: 'C',
    Qt.Key_D: 'D',
    Qt.Key_E: 'E',
    Qt.Key_F: 'F',
    Qt.Key_G: 'G',
    Qt.Key_H: 'H',
    Qt.Key_I: 'I',
    Qt.Key_J: 'J',
    Qt.Key_K: 'K',
    Qt.Key_L: 'L',
    Qt.Key_M: 'M',
    Qt.Key_N: 'N',
    Qt.Key_O: 'O',
    Qt.Key_P: 'P',
    Qt.Key_Q: 'Q',
    Qt.Key_R: 'R',
    Qt.Key_S: 'S',
    Qt.Key_T: 'T',
    Qt.Key_U: 'U',
    Qt.Key_V: 'V',
    Qt.Key_W: 'W',
    Qt.Key_X: 'X',
    Qt.Key_Y: 'Y',
    Qt.Key_Z: 'Z',

    Qt.Key_0: '0',
    Qt.Key_1: '1',
    Qt.Key_2: '2',
    Qt.Key_3: '3',
    Qt.Key_4: '4',
    Qt.Key_5: '5',
    Qt.Key_6: '6',
    Qt.Key_7: '7',
    Qt.Key_8: '8',
    Qt.Key_9: '9',

    # Modifier Keys (Handled separately based on scan codes)

    # Special Keys
    Qt.Key_Escape: 'ESCAPE',
    Qt.Key_Tab: 'TAB',
    Qt.Key_Backspace: 'BACKSPACE',
    Qt.Key_CapsLock: 'CAPSLOCK',
    Qt.Key_Shift: 'SHIFT',      # Differentiated by scan code
    Qt.Key_Control: 'CONTROL',  # Differentiated by scan code
    Qt.Key_Alt: 'ALT',          # Differentiated by scan code
    Qt.Key_Space: 'SPACE',
    Qt.Key_Return: 'RETURN',
    Qt.Key_Enter: 'RETURN',
    
    # Navigation Keys
    Qt.Key_Left: 'LEFT',
    Qt.Key_Right: 'RIGHT',
    Qt.Key_Up: 'UP',
    Qt.Key_Down: 'DOWN',
    Qt.Key_PageUp: 'PRIOR',     # PRIOR is Page Up
    Qt.Key_PageDown: 'NEXT',    # NEXT is Page Down
    Qt.Key_Home: 'HOME',
    Qt.Key_End: 'END',
    Qt.Key_Insert: 'INSERT',
    Qt.Key_Delete: 'DELETE',
    
    # Numpad Keys
    Qt.Key_NumLock: 'NUMLOCK',
    Qt.Key_ScrollLock: 'SCROLL',

    # Symbol Keys
    Qt.Key_Comma: 'COMMA',
    Qt.Key_Period: 'PERIOD',
    Qt.Key_Semicolon: 'SEMICOLON',
    Qt.Key_Apostrophe: 'APOSTROPHE',
    Qt.Key_BracketLeft: 'LBRACKET',
    Qt.Key_BracketRight: 'RBRACKET',
    Qt.Key_QuoteLeft: 'GRAVE',
    Qt.Key_Backslash: 'BACKSLASH',
    Qt.Key_Slash: 'SLASH',
    Qt.Key_Minus: 'MINUS',
    Qt.Key_Equal: 'EQUALS',

    # Meta Keys (Handled separately based on scan codes)
    Qt.Key_Meta: 'META',        # Differentiated by scan code
}
    
# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Groups for Elite:Dangerous keybinding
BINDING_CATEGORIES = {
    "General": [
        "UIFocus", "UI_Up", "UI_Down", "UI_Left", "UI_Right", "UI_Select", "UI_Back",
        "UI_Toggle", "CycleNextPanel", "CyclePreviousPanel", "CycleNextPage",
        "CyclePreviousPage", "QuickCommsPanel", "FocusCommsPanel", "FocusLeftPanel",
        "FocusRightPanel", "GalaxyMapOpen", "SystemMapOpen", "ShowPGScoreSummaryInput",
        "HeadLookToggle", "Pause", "FriendsMenu", "OpenCodexGoToDiscovery", 
        "PlayerHUDModeToggle", "PhotoCameraToggle",
        "GalaxyMapHome",
        "MouseReset", "BlockMouseDecay", "YawToRollButton",
        "ForwardKey", "BackwardKey",
        "FocusRadarPanel", "HeadLookReset", "HeadLookPitchUp", "HeadLookPitchDown",
        "HeadLookYawLeft", "HeadLookYawRight",
        "GalnetAudio_Play_Pause", "GalnetAudio_SkipForward", "GalnetAudio_SkipBackward",
        "GalnetAudio_ClearQueue",
    ],
    "Ship": [
        "YawLeftButton", "YawRightButton", "RollLeftButton", "RollRightButton",
        "PitchUpButton", "PitchDownButton", "LeftThrustButton", "RightThrustButton",
        "UpThrustButton", "DownThrustButton", "ForwardThrustButton", "BackwardThrustButton",
        "SetSpeedZero", "SetSpeed25", "SetSpeed50", "SetSpeed75", "SetSpeed100",
        "ToggleFlightAssist", "UseBoostJuice", "HyperSuperCombination", "Supercruise",
        "Hyperspace", "DisableRotationCorrectToggle", "OrbitLinesToggle", "SelectTarget",
        "CycleNextTarget", "CyclePreviousTarget", "SelectHighestThreat", "CycleNextHostileTarget",
        "CyclePreviousHostileTarget", "TargetWingman0", "TargetWingman1", "TargetWingman2",
        "SelectTargetsTarget", "WingNavLock", "CycleNextSubsystem", "CyclePreviousSubsystem",
        "TargetNextRouteSystem", "PrimaryFire", "SecondaryFire", "CycleFireGroupNext",
        "CycleFireGroupPrevious", "DeployHardpointToggle", "ToggleButtonUpInput",
        "DeployHeatSink", "ShipSpotLightToggle", "RadarIncreaseRange", "RadarDecreaseRange",
        "IncreaseEnginesPower", "IncreaseWeaponsPower", "IncreaseSystemsPower",
        "ResetPowerDistribution", "HMDReset", "ToggleCargoScoop", "EjectAllCargo",
        "LandingGearToggle", "UseShieldCell", "FireChaffLauncher", "ChargeECM",
        "WeaponColourToggle", "EngineColourToggle", "NightVisionToggle",
        "OrderRequestDock", "OrderDefensiveBehaviour", "OrderAggressiveBehaviour", 
        "OrderFocusTarget", "OrderHoldFire", "OrderHoldPosition", "OrderFollow",
        "MicrophoneMute", "UseAlternateFlightValuesToggle", "ToggleReverseThrottleInput",
        "TriggerFieldNeutraliser",
        "SetSpeedMinus100", "SetSpeedMinus75", "SetSpeedMinus50", "SetSpeedMinus25",
        "YawLeftButton_Landing", "YawRightButton_Landing", "PitchUpButton_Landing",
        "PitchDownButton_Landing", "RollLeftButton_Landing", "RollRightButton_Landing",
        "LeftThrustButton_Landing", "RightThrustButton_Landing", "UpThrustButton_Landing",
        "DownThrustButton_Landing", "ForwardThrustButton_Landing", "BackwardThrustButton_Landing",
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
        "SAAThirdPersonFovInButton"
    ],
    "FSS": [
        "ExplorationFSSCameraPitchIncreaseButton", "ExplorationFSSCameraPitchDecreaseButton",
        "ExplorationFSSCameraYawIncreaseButton", "ExplorationFSSCameraYawDecreaseButton",
        "ExplorationFSSZoomIn", "ExplorationFSSZoomOut", "ExplorationFSSMiniZoomIn",
        "ExplorationFSSMiniZoomOut", "ExplorationFSSRadioTuningX_Increase",
        "ExplorationFSSRadioTuningX_Decrease", "ExplorationFSSDiscoveryScan",
        "ExplorationFSSQuit", "ExplorationFSSTarget", "ExplorationFSSShowHelp",
    ],
    "SRV": [
        "SteerLeftButton", "SteerRightButton", "BuggyRollLeftButton", "BuggyRollRightButton",
        "BuggyPitchUpButton", "BuggyPitchDownButton", "VerticalThrustersButton",
        "BuggyPrimaryFireButton", "BuggySecondaryFireButton", "AutoBreakBuggyButton",
        "HeadlightsBuggyButton", "ToggleBuggyTurretButton", "BuggyCycleFireGroupNext",
        "BuggyCycleFireGroupPrevious", "SelectTarget_Buggy", "BuggyTurretYawLeftButton",
        "BuggyTurretYawRightButton", "BuggyTurretPitchUpButton", "BuggyTurretPitchDownButton",
        "IncreaseSpeedButtonMax", "DecreaseSpeedButtonMax", "IncreaseEnginesPower_Buggy",
        "IncreaseWeaponsPower_Buggy", "IncreaseSystemsPower_Buggy", "ResetPowerDistribution_Buggy",
        "ToggleCargoScoop_Buggy", "EjectAllCargo_Buggy", "RecallDismissShip", "ToggleDriveAssist",
        "UIFocus_Buggy", "FocusLeftPanel_Buggy", "FocusCommsPanel_Buggy",
        "QuickCommsPanel_Buggy", "FocusRadarPanel_Buggy", "FocusRightPanel_Buggy",
        "GalaxyMapOpen_Buggy", "SystemMapOpen_Buggy", "OpenCodexGoToDiscovery_Buggy",
        "PlayerHUDModeToggle_Buggy", "HeadLookToggle_Buggy",
        "PhotoCameraToggle_Buggy", "BuggyToggleReverseThrottleInput",
    ],
    "OnFoot": [
        "HumanoidForwardButton", "HumanoidBackwardButton", "HumanoidStrafeLeftButton",
        "HumanoidStrafeRightButton", "HumanoidRotateLeftButton", "HumanoidRotateRightButton",
        "HumanoidPitchUpButton", "HumanoidPitchDownButton", "HumanoidSprintButton",
        "HumanoidCrouchButton", "HumanoidJumpButton", "HumanoidPrimaryInteractButton",
        "HumanoidSecondaryInteractButton", "HumanoidItemWheelButton", "HumanoidEmoteWheelButton",
        "HumanoidUtilityWheelCycleMode", "HumanoidPrimaryFireButton", "HumanoidZoomButton",
        "HumanoidThrowGrenadeButton", "HumanoidMeleeButton", "HumanoidReloadButton",
        "HumanoidSelectPrimaryWeaponButton", "HumanoidSelectSecondaryWeaponButton",
        "HumanoidSelectNextWeaponButton", "HumanoidSelectPreviousWeaponButton",
        "HumanoidHideWeaponButton", "HumanoidToggleFlashlightButton", "HumanoidToggleNightVisionButton",
        "HumanoidToggleShieldsButton", "HumanoidClearAuthorityLevel", "HumanoidHealthPack",
        "HumanoidBattery", "HumanoidSelectFragGrenade", "HumanoidSelectEMPGrenade",
        "HumanoidSelectShieldGrenade", "HumanoidSwitchToRechargeTool", "HumanoidSwitchToCompAnalyser",
        "HumanoidSwitchToSuitTool", "HumanoidToggleToolModeButton", "HumanoidToggleMissionHelpPanelButton",
        "GalaxyMapOpen_Humanoid", "SystemMapOpen_Humanoid", "FocusCommsPanel_Humanoid",
        "QuickCommsPanel_Humanoid", "HumanoidOpenAccessPanelButton", "HumanoidConflictContextualUIButton",
        "PhotoCameraToggle_Humanoid", "HumanoidEmoteSlot1", "HumanoidEmoteSlot2", "HumanoidEmoteSlot3",
        "HumanoidEmoteSlot4", "HumanoidEmoteSlot5", "HumanoidEmoteSlot6", "HumanoidEmoteSlot7",
        "HumanoidEmoteSlot8",
        "HumanoidWalkButton", "HumanoidItemWheelButton_XLeft", "HumanoidItemWheelButton_XRight",
        "HumanoidItemWheelButton_YUp", "HumanoidItemWheelButton_YDown", "HumanoidSwitchWeapon",
        "HumanoidSelectUtilityWeaponButton", "HumanoidSelectNextGrenadeTypeButton",
        "HumanoidSelectPreviousGrenadeTypeButton", "HumanoidPing",
    ],
    "Camera": [
        "CamPitchUp", "CamPitchDown", "CamYawLeft", "CamYawRight", "CamTranslateForward",
        "CamTranslateBackward", "CamTranslateLeft", "CamTranslateRight", "CamTranslateUp",
        "CamTranslateDown", "CamZoomIn", "CamZoomOut", "CamTranslateZHold", "ToggleFreeCam",
        "FreeCamToggleHUD", "FreeCamSpeedInc", "FreeCamSpeedDec", "ToggleRotationLock",
        "FixCameraRelativeToggle", "FixCameraWorldToggle", "QuitCamera", "ToggleAdvanceMode",
        "VanityCameraScrollLeft", "VanityCameraScrollRight", "VanityCameraOne", "VanityCameraTwo",
        "VanityCameraThree", "VanityCameraFour", "VanityCameraFive", "VanityCameraSix",
        "VanityCameraSeven", "VanityCameraEight", "VanityCameraNine", "VanityCameraTen",
        "FreeCamZoomIn", "FreeCamZoomOut", "FStopDec", "FStopInc",
        "ToggleReverseThrottleInputFreeCam", "MoveFreeCamForward", "MoveFreeCamBackwards",
        "MoveFreeCamRight", "MoveFreeCamLeft", "MoveFreeCamUp", "MoveFreeCamDown",
        "PitchCameraUp", "PitchCameraDown", "YawCameraLeft", "YawCameraRight",
        "RollCameraLeft", "RollCameraRight",
    ],
    "Multi-Crew": [
        "MultiCrewToggleMode", "MultiCrewPrimaryFire", "MultiCrewSecondaryFire",
        "MultiCrewPrimaryUtilityFire", "MultiCrewSecondaryUtilityFire",
        "MultiCrewCockpitUICycleForward", "MultiCrewCockpitUICycleBackward",
        "MultiCrewThirdPersonYawLeftButton", "MultiCrewThirdPersonYawRightButton",
        "MultiCrewThirdPersonPitchUpButton", "MultiCrewThirdPersonPitchDownButton",
        "MultiCrewThirdPersonFovOutButton", "MultiCrewThirdPersonFovInButton",
        "OpenOrders",
    ],
    "Store": [
        "StoreEnableRotation", "StoreCamZoomIn", "StoreCamZoomOut", "StoreToggle",
    ],
    # "Autopilot" category is removed to be handled via plugins
}

# Define themes
THEMES = {
    'Default': {
        'background': '#2b2b2b',
        'text': '#ffffff',
        'key_normal': '#555555',
        'key_bound': '#4a6b8a',
        'key_general': '#777777',
        'key_ship': '#4a6b8a',
        'key_srv': '#4a8a6b',
        'key_onfoot': '#8a6b4a',
        'key_fss': '#6b4a8a',
        'key_camera': '#8a4a6b',
        'key_saa': '#6b8a4a',
        'key_multicrew': '#8a6b8a',
        'key_store': '#8a8a4a',
        'key_all': '#5a5a5a',
        'key_pressed': '#333333',  # Added key_pressed
    },
    'Dark Mode': {
        'background': '#1e1e1e',
        'text': '#ffffff',
        'key_normal': '#3c3c3c',
        'key_bound': '#007acc',
        'key_general': '#555555',
        'key_ship': '#66b2b2',
        'key_srv': '#00a676',
        'key_onfoot': '#ff8800',
        'key_fss': '#c678dd',
        'key_camera': '#ff5e79',
        'key_saa': '#61afef',
        'key_multicrew': '#98c379',
        'key_store': '#e5c07b',
        'key_all': '#56b6c2',
        'key_pressed': '#444444',  # Added key_pressed
    },
    'Solarized': {
        'background': '#002b36',
        'text': '#839496',
        'key_normal': '#073642',
        'key_bound': '#268bd2',
        'key_general': '#586e75',
        'key_ship': '#2aa198',
        'key_srv': '#859900',
        'key_onfoot': '#b58900',
        'key_fss': '#cb4b16',
        'key_camera': '#dc322f',
        'key_saa': '#d33682',
        'key_multicrew': '#6c71c4',
        'key_store': '#2aa198',
        'key_all': '#268bd2',
        'key_pressed': '#073642',  # Added key_pressed
    },
    # ... [Add more themes here, ensuring 'key_pressed' is included]
}

# Get current theme from config, default to 'Default' if not specified
CURRENT_THEME = config.get('Appearance', 'theme', fallback='Default')

# Define keyboard layout with key sizes
KEYBOARD_LAYOUT = [
    [('ESCAPE', 'Esc', 1.5), ('F1', 'F1', 1), ('F2', 'F2', 1), ('F3', 'F3', 1), ('F4', 'F4', 1),
     ('F5', 'F5', 1), ('F6', 'F6', 1), ('F7', 'F7', 1), ('F8', 'F8', 1), ('F9', 'F9', 1),
     ('F10', 'F10', 1), ('F11', 'F11', 1), ('F12', 'F12', 1), ('', '', 1.5)],
    [('GRAVE', '`', 1), ('1', '1', 1), ('2', '2', 1), ('3', '3', 1), ('4', '4', 1), ('5', '5', 1),
     ('6', '6', 1), ('7', '7', 1), ('8', '8', 1), ('9', '9', 1), ('0', '0', 1), ('MINUS', '-', 1),
     ('EQUALS', '=', 1), ('BACKSPACE', 'BKSP', 2)],
    [('TAB', 'Tab', 1.5), ('Q', 'Q', 1), ('W', 'W', 1), ('E', 'E', 1), ('R', 'R', 1), ('T', 'T', 1),
     ('Y', 'Y', 1), ('U', 'U', 1), ('I', 'I', 1), ('O', 'O', 1), ('P', 'P', 1), ('LBRACKET', '[', 1),
     ('RBRACKET', ']', 1), ('BACKSLASH', '\\', 1.5)],
    [('CAPSLOCK', 'Caps Lock', 2), ('A', 'A', 1), ('S', 'S', 1), ('D', 'D', 1), ('F', 'F', 1),
     ('G', 'G', 1), ('H', 'H', 1), ('J', 'J', 1), ('K', 'K', 1), ('L', 'L', 1), ('SEMICOLON', ';', 1),
     ('APOSTROPHE', "'", 1), ('RETURN', 'Enter', 2.25)],
    [('LSHIFT', 'Shift', 2.5), ('Z', 'Z', 1), ('X', 'X', 1), ('C', 'C', 1), ('V', 'V', 1), ('B', 'B', 1),
     ('N', 'N', 1), ('M', 'M', 1), ('COMMA', ',', 1), ('PERIOD', '.', 1), ('SLASH', '/', 1),
     ('RSHIFT', 'Shift', 2.5)],
    [('LCONTROL', 'Ctrl', 1.25), ('LWIN', 'Win', 1.0), ('LMENU', 'Alt', 1.0), ('SPACE', 'Space', 7.5),
     ('RMENU', 'Alt', 1.0), ('RWIN', 'Win', 1.0), ('APPS', 'Menu', 1.0), ('RCONTROL', 'Ctrl', 1.5)]
]

NUMPAD_LAYOUT = [
    [('', 4)],  # Empty row
    [('NUMLOCK', 'NM Lock', 1), ('DIVIDE', '/', 1), ('MULTIPLY', '*', 1), ('SUBTRACT', '-', 1)],
    [('NUMPAD7', '7', 1), ('NUMPAD8', '8', 1), ('NUMPAD9', '9', 1), ('ADD', '+', 1, 2)],  # ADD spans 2 rows
    [('NUMPAD4', '4', 1), ('NUMPAD5', '5', 1), ('NUMPAD6', '6', 1)],
    [('NUMPAD1', '1', 1), ('NUMPAD2', '2', 1), ('NUMPAD3', '3', 1), ('NUMPADENTER', 'Enter', 1, 2)],  # NUMPADENTER spans 2 rows
    [('NUMPAD0', '0', 2), ('DECIMAL', '.', 1)] # NUMPAD0 spans 2 columns
]

NAV_LAYOUT = [
    [('INSERT', 'Insert', 1), ('HOME', 'Home', 1), ('PRIOR', 'PG Up', 1)],  
    [('DELETE', 'Delete', 1), ('END', 'End', 1), ('NEXT', 'PG Down', 1)],  
    [('', '', 3)],  # Empty row
    [('', '', 3)],  # Empty row
    [('', '', 1), ('UP', '↑', 1), ('', '', 1)],
    [('LEFT', '←', 1), ('DOWN', '↓', 1), ('RIGHT', '→', 1)]
]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
        ]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT),
    ]

LPINPUT = ctypes.POINTER(INPUT)

class EDKeys:
    def __init__(self, binds_file): # Initializes the EDKeys instance by parsing the binds file.
        """
        Initializes the EDKeys instance by parsing the binds file.

        :param binds_file: Path to the XML binds file.
        """
        self.binds_file = binds_file
        self.normalized_key_cache = {}
        self.bindings = self.parse_binds_file()
        
    def parse_binds_file(self): # Parses the XML binds file and maps VK codes to actions.
        """
        Parses the XML binds file and maps VK codes to actions.

        :return: Dictionary mapping VK codes to a list of actions.
        """
        bindings = {}
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()

            for element in root:
                action = element.tag
                primary = element.find('Primary')
                if primary is not None and 'Key' in primary.attrib:
                    key = primary.attrib['Key'].strip()
                    if not key:
                        continue

                    # Normalize the key before further processing
                    normalized_key = self.normalize_key(key)

                    # Get the VK code for the normalized key
                    vk_code = self.get_vkcode_for_key(normalized_key)

                    if vk_code is not None:
                        if vk_code not in bindings:
                            bindings[vk_code] = []
                        bindings[vk_code].append(action)
                    else:
                        logging.warning(f"VK code not found for key '{key}' (Normalized: {normalized_key})")
        except ET.ParseError as e:
            logging.error(f"Error parsing binds file: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while parsing binds file: {e}")
        return bindings

    def normalize_key(self, key): # Normalizes the key name to match the VK_CODES dictionary.
        """
        Normalizes the key name to match the VK_CODES dictionary.

        :param key: Original key name from the binds file.
        :return: Normalized key name.
        """
        if key in self.normalized_key_cache:
            return self.normalized_key_cache[key]

        key_map = {
            'Key_Numpad_0': 'NUMPAD0',
            'Key_Numpad_1': 'NUMPAD1',
            'Key_Numpad_2': 'NUMPAD2',
            'Key_Numpad_3': 'NUMPAD3',
            'Key_Numpad_4': 'NUMPAD4',
            'Key_Numpad_5': 'NUMPAD5',
            'Key_Numpad_6': 'NUMPAD6',
            'Key_Numpad_7': 'NUMPAD7',
            'Key_Numpad_8': 'NUMPAD8',
            'Key_Numpad_9': 'NUMPAD9',
            'Key_Delete': 'DELETE',
            'Key_Insert': 'INSERT',
            'Key_PageUp': 'PRIOR',  # PRIOR is Page Up
            'Key_PageDown': 'NEXT',  # NEXT is Page Down
            'Key_UpArrow': 'UP',
            'Key_DownArrow': 'DOWN',
            'Key_LeftArrow': 'LEFT',
            'Key_RightArrow': 'RIGHT',
            'Key_LeftShift': 'LSHIFT',
            'Key_RightShift': 'RSHIFT',
            'Key_LeftControl': 'LCONTROL',
            'Key_RightControl': 'RCONTROL',
            'Key_LeftAlt': 'LALT',
            'Key_RightAlt': 'RALT',
            'Key_Return': 'RETURN',
            'Key_NumpadEnter': 'NUMPADENTER',
            'Key_LeftBracket': 'LBRACKET',
            'Key_RightBracket': 'RBRACKET',
            'Key_Enter': 'RETURN',
            # Add more mappings as needed
        }
        normalized_key = key_map.get(key, key.upper().replace('KEY_', ''))
        self.normalized_key_cache[key] = normalized_key
        logging.debug(f"Normalized key '{key}' to '{normalized_key}'")
        return normalized_key
    
    def get_vkcode_for_key(self, key): # Retrieves the VK code for a given key from the VK_CODES dictionary - TODO: Mouse and Controller
        """
        Retrieves the VK code for a given key from the VK_CODES dictionary.

        :param key: Normalized key name.
        :return: VK code integer or None if not found.
        """
        # Check for mouse-related keys and return a dummy VK code - TODO in case we ever want to do mouse keys :)
        if key.startswith(('MOUSE_', 'POS_MOUSE_', 'NEG_MOUSE_')):
            return 0  # Use 0 as a dummy VK code for mouse keys

        vk_code = VK_CODES.get(key.upper())
        if vk_code is None:
            logging.warning(f"No VK code found for key '{key.upper()}'")
        else:
            logging.debug(f"VK code for key '{key.upper()}': {vk_code}")
        return vk_code
    
    def get_bound_actions(self, vk_code): # Retrieves the list of actions bound to a specific VK code.
        """
        Retrieves the list of actions bound to a specific VK code.

        :param vk_code: VK code integer.
        :return: List of action names.
        """
        return self.bindings.get(vk_code, [])
    
    def save_bindings_to_file(self, file_path): # Saves the current bindings to an XML file.
        """
        Saves the current bindings to an XML file.

        :param file_path: Path where the bindings will be saved.
        """
        root = ET.Element('KeyBindings')
        for vk_code, actions in self.bindings.items():
            for action in actions:
                action_element = ET.SubElement(root, action)
                primary = ET.SubElement(action_element, 'Primary')
                key_name = self.get_key_name_from_vkcode(vk_code)
                primary.set('Key', key_name if key_name else '')
        tree = ET.ElementTree(root)
        try:
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            logging.info(f"Bindings successfully saved to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save bindings: {e}")
                   
    def get_key_name_from_vkcode(self, vk_code): # Retrieves the key name corresponding to a VK code.
        """
        Retrieves the key name corresponding to a VK code.

        :param vk_code: VK code integer.
        :return: Key name string or None if not found.
        """
        for key, code in VK_CODES.items():
            if code == vk_code:
                key_name = key
                logging.debug(f"Key name for VK code {vk_code}: {key_name}")
                return key_name
        logging.warning(f"No key name found for VK code {vk_code}")
        return None

    def unbind_action(self, action): # Removes the specified action from all key bindings.
        """
        Removes the specified action from all key bindings.

        :param action: Action name to unbind.
        """
        for vk_code, actions in self.bindings.items():
            if action in actions:
                actions.remove(action)
                logging.info(f"Action '{action}' unbound from VK code {vk_code}")
                

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


class PluginManager:
    """
    Manages the loading and unloading of plugins.
    """
    def __init__(self, parent):
        self.parent = parent
        self.plugins = {}       # key: plugin name, value: plugin instance
        self.plugin_paths = {}  # key: plugin name, value: plugin file path
    
    def load_plugin(self, plugin_path):
        """
        Loads a plugin from the specified file path.
        """
        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        if plugin_name in self.plugins:
            QMessageBox.warning(self.parent, "Plugin Load Error", f"Plugin '{plugin_name}' is already loaded.")
            return

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                plugin_class = getattr(module, 'Plugin', None)
                if plugin_class and issubclass(plugin_class, PluginInterface):
                    plugin_instance = plugin_class(self.parent)
                    plugin_instance.load()
                    self.plugins[plugin_name] = plugin_instance
                    self.plugin_paths[plugin_name] = plugin_path
                    QMessageBox.information(self.parent, "Plugin Loaded", f"Plugin '{plugin_name}' loaded successfully.")
                else:
                    QMessageBox.warning(self.parent, "Plugin Load Error", f"Plugin '{plugin_name}' does not have a valid 'Plugin' class.")
            except Exception as e:
                logging.error(f"Error loading plugin '{plugin_name}': {e}")
                QMessageBox.critical(self.parent, "Plugin Load Error", f"Failed to load plugin '{plugin_name}': {e}")
        else:
            QMessageBox.warning(self.parent, "Plugin Load Error", f"Could not load plugin from '{plugin_path}'.")

    def unload_plugin(self, plugin_name):
        """
        Unloads the specified plugin.
        """
        if plugin_name not in self.plugins:
            QMessageBox.warning(self.parent, "Plugin Unload Error", f"Plugin '{plugin_name}' is not loaded.")
            return

        try:
            self.plugins[plugin_name].unload()
            del self.plugins[plugin_name]
            del self.plugin_paths[plugin_name]
            QMessageBox.information(self.parent, "Plugin Unloaded", f"Plugin '{plugin_name}' unloaded successfully.")
        except Exception as e:
            logging.error(f"Error unloading plugin '{plugin_name}': {e}")
            QMessageBox.critical(self.parent, "Plugin Unload Error", f"Failed to unload plugin '{plugin_name}': {e}")

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
                plugin_path, _ = QFileDialog.getOpenFileName(self.parent, "Locate Plugin File", "", "Python Files (*.py)")
                if plugin_path:
                    self.load_plugin(plugin_path)
                else:
                    QMessageBox.warning(self.parent, "Toggle Plugin Error", f"Plugin path for '{plugin_name}' not found.")

    def list_plugins(self):
        """
        Returns a list of all available plugins with their load status.
        """
        # List all .py files in the plugins directory
        plugins_dir = os.path.join(os.getcwd(), 'plugins')
        if not os.path.isdir(plugins_dir):
            os.makedirs(plugins_dir)
        
        plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith('.py')]
        all_plugins = set(os.path.splitext(f)[0] for f in plugin_files)
        plugin_list = []
        for plugin in all_plugins:
            status = "Loaded" if plugin in self.plugins else "Not Loaded"
            plugin_list.append((plugin, status))
        return plugin_list


class KeyboardGUI(QMainWindow): # The main GUI window for the Keybind Visualizer.
    """
    The main GUI window for the Keybind Visualizer.
    Displays a visual representation of keyboard bindings and handles user interactions.
    """   
    
    def __init__(self, ed_keys): # Initializes the KeyboardGUI instance.
        """
        Initializes the KeyboardGUI instance.

        :param ed_keys: An instance of the EDKeys class containing key bindings.
        """
        super().__init__()
        self.ed_keys = ed_keys
        self.key_buttons = {}  # Nested dictionary: {category: {key_name: QPushButton}}
        self.key_states = {}   # Tracks the pressed state of keys
        self.base_key_size = 40
        self.plugin_manager = PluginManager(self)
        self.is_key_dialog_open = False
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("QWidget:focus { outline: none; }")
        
        self.initUI()
        self.initialize_key_states()
        self.update_status_bar()

    def initUI(self): # Sets up the user interface components of the GUI.
        """
        Sets up the user interface components of the GUI.
        """
        self.setWindowTitle('Elite: Dangerous Keybinds Visualizer v1.2 by glassesinsession')
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1200, 700)

        # Apply the current theme
        self.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};")

        # Create menu bar
        menubar = self.menuBar()

        # # Status bar
        # self.status_bar = self.statusBar()
        # self.status_bar.showMessage("Ready")
        # self.key_block_status_label = QLabel()
        # self.status_bar.addPermanentWidget(self.key_block_status_label)
    
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        self.key_block_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.key_block_status_label)

        # File menu
        fileMenu = menubar.addMenu('File')
        loadBindsAction = QAction('Load Keybind File', self)
        loadBindsAction.triggered.connect(self.load_bindings)
        fileMenu.addAction(loadBindsAction)

        saveBindsAction = QAction('Save Current Bindings', self)
        saveBindsAction.triggered.connect(self.save_bindings)
        fileMenu.addAction(saveBindsAction)

        # View menu
        viewMenu = menubar.addMenu('View')
        self.toggle_bindings_action = QAction('Show Bindings', self, checkable=True)
        self.toggle_bindings_action.setChecked(False)
        self.toggle_bindings_action.triggered.connect(self.toggle_bindings_text)
        viewMenu.addAction(self.toggle_bindings_action)

        self.show_unbound_actions_action = QAction('Show Unbound Actions', self)
        self.show_unbound_actions_action.triggered.connect(self.show_unbound_actions)
        viewMenu.addAction(self.show_unbound_actions_action)

        # Plugins menu
        pluginMenu = menubar.addMenu('Plugins')
        loadPluginAction = QAction('Load Plugin', self)
        loadPluginAction.triggered.connect(self.load_plugin)
        pluginMenu.addAction(loadPluginAction)

        unloadPluginAction = QAction('Unload Plugin', self)
        unloadPluginAction.triggered.connect(self.unload_plugin)
        pluginMenu.addAction(unloadPluginAction)

        # Main layout with tabs
        splitter = QSplitter(Qt.Horizontal)
        central_widget = QWidget()
        splitter.addWidget(central_widget)
        self.setCentralWidget(splitter)

        main_layout = QVBoxLayout(central_widget)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create 'All' tab first
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)
        all_keyboard_layout = QHBoxLayout()
        all_keyboard_layout.setSpacing(10)

        all_main_keyboard = self.create_keyboard_section(KEYBOARD_LAYOUT, "All")
        all_keyboard_layout.addLayout(all_main_keyboard, 70)

        all_nav_layout = self.create_keyboard_section(NAV_LAYOUT, "All", key_size=1.2)
        all_keyboard_layout.addLayout(all_nav_layout, 15)

        all_numpad_layout = self.create_keyboard_section(NUMPAD_LAYOUT, "All", key_size=1.2)
        all_keyboard_layout.addLayout(all_numpad_layout, 15)

        all_layout.addLayout(all_keyboard_layout)
        self.tab_widget.addTab(all_tab, "All")

        # Create tabs based on binding categories
        for category in BINDING_CATEGORIES:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            keyboard_layout = QHBoxLayout()
            keyboard_layout.setSpacing(10)

            main_keyboard = self.create_keyboard_section(KEYBOARD_LAYOUT, category)
            keyboard_layout.addLayout(main_keyboard, 70)

            nav_layout = self.create_keyboard_section(NAV_LAYOUT, category, key_size=1.2)
            keyboard_layout.addLayout(nav_layout, 15)

            numpad_layout = self.create_keyboard_section(NUMPAD_LAYOUT, category, key_size=1.2)
            keyboard_layout.addLayout(numpad_layout, 15)

            tab_layout.addLayout(keyboard_layout)
            self.tab_widget.addTab(tab, category)


        main_layout.addStretch()

        # Dockable output window for key bindings
        self.bindings_text = QTextEdit()
        self.bindings_text.setReadOnly(True)
        self.bindings_text.setMinimumWidth(300)
        self.bindings_text.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};")

        self.dock_output = QDockWidget("Key Bindings", self)
        self.dock_output.setWidget(self.bindings_text)
        splitter.addWidget(self.dock_output)
        self.dock_output.hide()
    
    def update_status_bar(self):
        if self.is_key_dialog_open:
            status = "Keys Unblocked (Dialog Open)"
            color = "green"
        else:
            status = "Keys Blocked (Main Interface)"
            color = "red"
        self.key_block_status_label.setText(f"<font color='{color}'>{status}</font>")
        logging.debug(f"Status bar updated: {status}")
        
    def create_keyboard_section(self, layout, tab_category, key_size=1.0):
        section_layout = QGridLayout()
        section_layout.setSpacing(4)
        section_layout.setContentsMargins(2, 2, 2, 2)

        for row, key_row in enumerate(layout):
            col = 0
            for key_data in key_row:
                if len(key_data) == 4:
                    key_name, display_label, size, row_span = key_data
                elif len(key_data) == 3:
                    key_name, display_label, size = key_data
                    row_span = 1
                else:
                    key_name, display_label, size, row_span = '', '', key_data[1], 1
                int_size = int(size * 2)

                if not key_name:
                    spacer = QLabel()
                    spacer.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']};")
                    spacer.setFixedSize(int(self.base_key_size * size * key_size), int(self.base_key_size * key_size))
                    section_layout.addWidget(spacer, row, col, row_span, int_size)
                else:
                    if tab_category == "All":
                        actual_category = self.determine_key_category(key_name)
                    else:
                        actual_category = tab_category
                    button = self.create_key_button(key_name, display_label, size * key_size, actual_category, tab_category)
                    section_layout.addWidget(button, row, col, row_span, int_size)
                    
                    # Store button in nested dictionary
                    if tab_category not in self.key_buttons:
                        self.key_buttons[tab_category] = {}
                    self.key_buttons[tab_category][key_name] = button
                
                col += int_size
            section_layout.setColumnStretch(col, 0)
        return section_layout
    
    def create_key_button(self, key_name, display_label, size, actual_category, tab_category):
        """
        Creates a QPushButton representing a key on the keyboard.

        :param key_name: Internal name of the key.
        :param display_label: Label to display on the key.
        :param size: Size multiplier for the key.
        :param actual_category: The actual binding category of the key.
        :param tab_category: The current tab's category ("All" or specific like "Ship").
        :return: Configured QPushButton object.
        """
        
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumSize(int(self.base_key_size * size), self.base_key_size)

        button.setText(display_label)

        normalized_key = self.ed_keys.normalize_key(key_name)
        vk_code = self.ed_keys.get_vkcode_for_key(normalized_key)
        bound_actions = self.ed_keys.get_bound_actions(vk_code)

        # Determine relevant actions based on the current tab
        if tab_category == "All":
            relevant_actions = bound_actions
        else:
            relevant_actions = [
                action for action in bound_actions
                if action in BINDING_CATEGORIES.get(tab_category, []) or
                action in BINDING_CATEGORIES.get("General", [])
            ]

        if relevant_actions:
            # Determine the most specific category for coloring
            categories = set()
            for action in relevant_actions:
                for cat, actions in BINDING_CATEGORIES.items():
                    if action in actions:
                        categories.add(cat)
                        break
            
            # Determine the specific category for coloring
            if categories == {"General"} or not categories:
                specific_category = "General"
            elif len(categories) == 1:
                specific_category = categories.pop()
            else:
                non_general_categories = categories - {"General"}
                if tab_category != "All" and tab_category in non_general_categories:
                    specific_category = tab_category
                else:
                    specific_category = next(iter(non_general_categories)) if non_general_categories else "General"

            key_color_key = f'key_{specific_category.lower()}'
            original_color = THEMES[CURRENT_THEME].get(key_color_key, THEMES[CURRENT_THEME]['key_bound'])
            pressed_color = self.get_lighter_color(original_color)
            tooltip_text = "\n".join(relevant_actions)
        else:
            original_color = THEMES[CURRENT_THEME]['key_normal']
            pressed_color = self.get_lighter_color(original_color)
            tooltip_text = "Unassigned"

        # Apply the stylesheet using original and pressed colors
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {original_color};
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
        """)

        button.setToolTip(tooltip_text)

        # Store original and pressed colors as properties for later use
        button.setProperty("original_color", original_color)
        button.setProperty("pressed_color", pressed_color)

        # Set other properties for later reference
        button.setProperty("all_bound_actions", bound_actions)
        button.setProperty("relevant_actions", relevant_actions)
        button.setProperty("category", actual_category)

        return button

    def initialize_key_states(self): # Initializes the state of each key (pressed or released) to False.
        """
        Initializes the state of each key (pressed or released) to False.
        """
        for category, keys in self.key_buttons.items():
            for key in keys:
                self.key_states[key] = False
        logging.debug("Initialized all key states to False.")
                          
    def display_bindings(self, key_name):
        """
        Displays the actions bound to a specific key in the bindings text area.

        :param key_name: Key name to display bindings for.
        """
        if not self.bindings_text.isVisible():
            return
        if key_name in self.key_buttons.get("All", {}):
            button = self.key_buttons["All"][key_name]
            vk_code = self.ed_keys.get_vkcode_for_key(self.ed_keys.normalize_key(key_name))
            bound_actions = self.ed_keys.get_bound_actions(vk_code)
            
            self.bindings_text.clear()
            self.bindings_text.append(f"<h2>Key: {key_name}</h2>")

            if bound_actions:
                categorized_actions = self.categorize_actions(bound_actions)

                category_order = [self.tab_widget.tabText(i) for i in range(self.tab_widget.count())]
                if "All" in category_order:
                    category_order.remove("All")
                category_order = ["General"] + category_order

                for category in category_order:
                    if category in categorized_actions:
                        self.display_category(category, categorized_actions[category])
            else:
                self.bindings_text.append("No bindings found")

    def categorize_actions(self, actions): # Categorizes actions based on predefined binding categories.
        """
        Categorizes actions based on predefined binding categories.

        :param actions: List of action names.
        :return: Dictionary mapping categories to their respective actions.
        """
        categorized = {}
        for action in actions:
            for category, category_actions in BINDING_CATEGORIES.items():
                if action in category_actions:
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(action)
                    break
            else:
                if "Uncategorized" not in categorized:
                    categorized["Uncategorized"] = []
                categorized["Uncategorized"].append(action)
        logging.debug(f"Categorized actions: {categorized}")
        return categorized      
    
    def display_category(self, category, actions): # Displays a specific category and its actions in the bindings text area.
        """
        Displays a specific category and its actions in the bindings text area.

        :param category: Category name.
        :param actions: List of actions under the category.
        """
        self.bindings_text.append(f"<h3>{category}</h3>")
        for action in actions:
            self.bindings_text.append(f"- {action}")
        self.bindings_text.append("")
        logging.debug(f"Displayed category '{category}' with actions: {actions}")
        
    def update_key_button(self, key_name, category):
        """
        Updates the visual state and tooltip of a specific key button based on its bindings.

        :param key_name: Key name to update.
        :param category: Binding category of the key.
        """
        button = self.find_key_button(key_name, category)
        if button:
            normalized_key = self.ed_keys.normalize_key(key_name)
            scancode = self.ed_keys.get_scancode_for_key(normalized_key)
            all_bound_actions = self.ed_keys.get_bound_actions(scancode)

            if category == "All":
                relevant_actions = all_bound_actions
            else:
                relevant_actions = [a for a in all_bound_actions 
                                    if a in BINDING_CATEGORIES.get(category, []) or 
                                    a in BINDING_CATEGORIES.get("General", [])]

            has_binding = bool(relevant_actions)
            specific_category = self.determine_key_category(key_name)  # Corrected Call
            is_general = specific_category == "General"

            button.setProperty("all_bound_actions", all_bound_actions)
            button.setProperty("relevant_actions", relevant_actions)
            button.setProperty("is_general", is_general)

            button.setStyleSheet(self.get_button_style(False, has_binding, specific_category or category, is_general))
            tooltip_text = "\n".join(self.order_actions_by_category(relevant_actions, specific_category or category)) if relevant_actions else "Unassigned"
            button.setToolTip(tooltip_text)
            logging.debug(f"Updated button '{key_name}': has_binding={has_binding}, category={specific_category or category}")

    def update_key_visual(self, key_name, is_pressed):
        """
        Updates the visual appearance of a key based on its pressed state.

        :param key_name: The name of the key.
        :param is_pressed: Boolean indicating if the key is pressed.
        """
        if key_name in self.key_buttons.get("All", {}):
            button = self.key_buttons["All"][key_name]
            
            if is_pressed:
                # Change to pressed color
                pressed_color = button.property("pressed_color")
                button.setStyleSheet(f"""
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
                """)
                logging.debug(f"Key '{key_name}' pressed. Changed color to pressed_color: {pressed_color}")
            else:
                # Revert to original color
                original_color = button.property("original_color")
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {original_color};
                        color: {THEMES[CURRENT_THEME]['text']};
                        border: 1px solid #555555;
                        border-radius: 3px;
                        font-weight: bold;
                        font-size: 10px;
                        text-align: center;
                        padding: 2px;
                    }}
                """)
                logging.debug(f"Key '{key_name}' released. Reverted color to original_color: {original_color}")
            
            button.setDown(is_pressed)

           
    def get_lighter_color(self, color):
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Increase each component by 20%, but not exceeding 255
        r = min(int(r * 1.2), 255)
        g = min(int(g * 1.2), 255)
        b = min(int(b * 1.2), 255)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def find_key_button(self, key_name, category): # Finds the QPushButton object corresponding to a given key name and category.
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
                background_color = THEMES[CURRENT_THEME][f'key_{category.lower()}']
            else:
                background_color = THEMES[CURRENT_THEME]['key_bound']
        else:
            background_color = THEMES[CURRENT_THEME]['key_normal']

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
  
    def get_pressed_color(self, color): # Calculates a lighter shade of the given color for the pressed state.
        """
        Calculates a lighter shade of the given color for the pressed state.

        :param color: Hex color string (e.g., '#555555').
        :return: Hex color string for the pressed state.
        """
        try:
            color = color.lstrip('#')
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            r = min(int(r * 1.3), 255)
            g = min(int(g * 1.3), 255)
            b = min(int(b * 1.3), 255)
            pressed_color = f'#{r:02x}{g:02x}{b:02x}'
            logging.debug(f"Pressed color for '{color}': {pressed_color}")
            return pressed_color
        except Exception as e:
            logging.error(f"Error in get_pressed_color with color '{color}': {e}")
            return color
        
    def order_actions_by_category(self, actions, current_category): # Orders actions by the current category followed by others.
        """
        Orders actions by the current category followed by others.

        :param actions: List of action names.
        :param current_category: Current binding category.
        :return: Ordered list of action names.
        """
        current_cat_actions = [action for action in actions if action in BINDING_CATEGORIES.get(current_category, [])]
        other_actions = [action for action in actions if action not in current_cat_actions]
        ordered_actions = current_cat_actions + other_actions
        logging.debug(f"Ordered actions: {ordered_actions}")
        return ordered_actions
    
    def determine_key_category(self, key_name): # Determines the category of a key based on predefined categories.
        """
        Determines the category of a key based on predefined categories.

        :param key_name: The name of the key.
        :return: Category as a string.
        """
        for category, keys in BINDING_CATEGORIES.items():
            if key_name in keys:
                return category
        return "General"  # Default category if not found

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
        scancode = self.ed_keys.get_scancode_for_key(normalized_key)
        current_bindings = self.ed_keys.get_bound_actions(scancode)

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
                QMessageBox.warning(dialog, "No Selection", "No actions were selected to assign.")
                return
            for item in selected_items:
                action = item.text(0)
                if action not in self.ed_keys.bindings.get(scancode, []):
                    self.ed_keys.unbind_action(action)
                    self.ed_keys.bindings.setdefault(scancode, []).append(action)
            self.refresh_all_tabs()
            self.status_bar.showMessage(f"Assigned selected actions to key '{key_name}'.")
            logging.info(f"Assigned actions to key '{key_name}': {selected_items}")
            dialog.accept()

        def on_unbind():
            selected_items = tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "No Selection", "No actions were selected to unbind.")
                return
            for item in selected_items:
                action = item.text(0)
                if action in self.ed_keys.bindings.get(scancode, []):
                    self.ed_keys.bindings[scancode].remove(action)
            self.refresh_all_tabs()
            self.status_bar.showMessage(f"Unbound selected actions from key '{key_name}'.")
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

        dialog.finished.connect(lambda: setattr(self, 'is_key_dialog_open', False))
        dialog.finished.connect(self.update_status_bar)

        dialog.exec_()
        
    def keyPressEvent(self, event):
        key = event.key()
        key_name = self.get_key_name(event)
        
        if key_name and not self.key_states.get(key_name, False):
            self.update_key_visual(key_name, True)
            self.display_bindings(key_name)
            logging.debug(f"Key pressed: {key_name}")
            self.key_states[key_name] = True

        # Always handle the event, but only prevent propagation for blocked keys
        if self.should_block_key(key):
            event.accept()
        else:
            event.ignore()  # Allow the event to propagate if not blocked

    def keyReleaseEvent(self, event):
        key = event.key()
        key_name = self.get_key_name(event)
        
        if key_name and self.key_states.get(key_name, False):
            self.update_key_visual(key_name, False)
            logging.debug(f"Key released: {key_name}")
            self.key_states[key_name] = False

        # Consistent with keyPressEvent
        if self.should_block_key(key):
            event.accept()
        else:
            event.ignore()
                 
    def handle_key_event(self, key, pressed):
        key_name = key.replace('<br>', '')
        self.key_states[key_name] = pressed
        
        # Update button state across all tabs
        for tab_buttons in self.key_buttons.values():
            if key_name in tab_buttons:
                tab_buttons[key_name].setDown(pressed)

        if pressed:
            self.display_bindings(key_name)

        logging.debug(f"Key {'pressed' if pressed else 'released'}: {key_name}")

    def should_block_key(self, key):
        blocked_keys = [
            Qt.Key_Tab, Qt.Key_Backtab,
            Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down,
            Qt.Key_PageUp, Qt.Key_PageDown,
            Qt.Key_Home, Qt.Key_End,
            Qt.Key_Return, Qt.Key_Enter,
            Qt.Key_Space
        ]
        return key in blocked_keys
            
    def focusNextPrevChild(self, next):
        return False

    def toggle_bindings_text(self, checked): # Toggles the visibility of the bindings output dock.
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
            
    def load_bindings(self): # Opens a file dialog to load a new binds file and refreshes the UI.
        """
        Opens a file dialog to load a new binds file and refreshes the UI.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Keybind File", "", "Bind Files (*.binds *.xml)")
        if file_path:
            self.ed_keys = EDKeys(file_path)
            self.refresh_all_tabs()
            QMessageBox.information(self, "Load Bindings", f"Loaded keybinds from {file_path}")
            self.status_bar.showMessage(f"Loaded keybinds from {file_path}")
            logging.info(f"Loaded keybinds from {file_path}")

    def save_bindings(self): # Opens a file dialog to save the current bindings to an XML file.
        """
        Opens a file dialog to save the current bindings to an XML file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Keybinds", "", "Bind Files (*.binds *.xml)")
        if file_path:
            self.ed_keys.save_bindings_to_file(file_path)
            QMessageBox.information(self, "Save Bindings", f"Bindings saved to {file_path}")
            self.status_bar.showMessage(f"Bindings saved to {file_path}")
            logging.info(f"Bindings saved to {file_path}")
            
    def show_unbound_actions(self): # Displays a dialog listing all unbound actions across categories. - TODO: Layout
        """
        Displays a dialog listing all unbound actions across categories.
        """
        unbound_actions = self.get_unbound_actions()
        if not any(unbound_actions.values()):
            QMessageBox.information(self, "Unbound Actions", "All actions are currently bound to keys.")
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
    
    def get_unbound_actions(self): # Retrieves all actions that are not currently bound to any key.
        """
        Retrieves all actions that are not currently bound to any key.

        :return: Dictionary mapping categories to their respective unbound actions.
        """
        unbound = {}
        all_bound_actions = set()
        for actions in self.ed_keys.bindings.values():
            all_bound_actions.update(actions)

        for category, actions in BINDING_CATEGORIES.items():
            unbound_actions = [action for action in actions if action not in all_bound_actions]
            if unbound_actions:
                unbound[category] = unbound_actions

        logging.debug(f"Unbound actions: {unbound}")
        return unbound
    
    def refresh_all_tabs(self):
        """
        Refreshes the visual representation of all tabs to reflect current bindings.
        """
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            tab_layout = tab.layout()
            while tab_layout.count():
                child = tab_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.remove_layout(child.layout())
            keyboard_layout = QHBoxLayout()
            keyboard_layout.setSpacing(10)

            category = self.tab_widget.tabText(index)

            main_keyboard = self.create_keyboard_section(KEYBOARD_LAYOUT, category)
            keyboard_layout.addLayout(main_keyboard, 70)

            nav_layout = self.create_keyboard_section(NAV_LAYOUT, category, key_size=1.2)
            keyboard_layout.addLayout(nav_layout, 15)

            numpad_layout = self.create_keyboard_section(NUMPAD_LAYOUT, category, key_size=1.2)
            keyboard_layout.addLayout(numpad_layout, 15)

            tab_layout.addLayout(keyboard_layout)
            logging.debug(f"Refreshed tab '{category}'.")
     
    def remove_layout(self, layout): # Recursively removes and deletes all widgets within a layout.
        """
        Recursively removes and deletes all widgets within a layout.

        :param layout: QLayout object to remove.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.remove_layout(child.layout())
                
    def load_plugin(self): # Opens a file dialog to load a plugin.
        """
        Opens a file dialog to load a plugin.
        """
        logging.debug("load_plugin method called in KeyboardGUI")
        plugin_path, _ = QFileDialog.getOpenFileName(self, "Load Plugin", "", "Python Files (*.py)")
        logging.debug(f"Selected plugin path: {plugin_path}")
        if plugin_path:
            self.plugin_manager.load_plugin(plugin_path)
        else:
            logging.debug("No plugin file selected")

    def unload_plugin(self): # Opens a dialog to select and unload a currently loaded plugin.
        """
        Opens a dialog to select and unload a currently loaded plugin.
        """
        if not self.plugin_manager.plugins:
            QMessageBox.information(self, "Unload Plugin", "No plugins are currently loaded.")
            logging.info("No plugins to unload.")
            return

        plugin_names = list(self.plugin_manager.plugins.keys())
        plugin_name, ok = QInputDialog.getItem(
            self, "Unload Plugin", "Select plugin to unload:", plugin_names, 0, False
        )

        if ok and plugin_name:
            self.plugin_manager.unload_plugin(plugin_name)
            logging.info(f"Unloaded plugin '{plugin_name}'")

    def keycode_to_keyname(self, key):
        """
        Maps a Qt key code to the corresponding key name using KEY_MAPPING.

        :param key: Qt.Key value.
        :return: Key name string.
        """
        # First, check in the centralized KEY_MAPPING
        key_name = KEY_MAPPING.get(key, '')

        # Handle numpad keys separately if needed
        numpad_map = {
            Qt.Key_0: 'NUMPAD0', Qt.Key_1: 'NUMPAD1', Qt.Key_2: 'NUMPAD2',
            Qt.Key_3: 'NUMPAD3', Qt.Key_4: 'NUMPAD4', Qt.Key_5: 'NUMPAD5',
            Qt.Key_6: 'NUMPAD6', Qt.Key_7: 'NUMPAD7', Qt.Key_8: 'NUMPAD8',
            Qt.Key_9: 'NUMPAD9', Qt.Key_Plus: 'ADD', Qt.Key_Minus: 'SUBTRACT',
            Qt.Key_Asterisk: 'MULTIPLY', Qt.Key_Slash: 'DIVIDE',
            Qt.Key_Period: 'DECIMAL', Qt.Key_Return: 'NUMPADENTER',
            Qt.Key_Enter: 'NUMPADENTER',
        }

        if key in numpad_map:
            return numpad_map[key]

        # Return the mapped key name or the uppercase text if not found
        if not key_name:
            logging.warning(f"Unmapped key pressed: {key}")
        return key_name

    def change_theme(self, theme_name): # Changes the current theme of the application.
        """
        Changes the current theme of the application.

        :param theme_name: Name of the theme to apply.
        """
        global CURRENT_THEME
        if theme_name not in THEMES:
            QMessageBox.critical(self, "Theme Error", f"Theme '{theme_name}' does not exist.")
            logging.error(f"Attempted to change to non-existent theme '{theme_name}'.")
            return
        CURRENT_THEME = theme_name
        self.apply_theme(theme_name)
        self.status_bar.showMessage(f"Theme changed to '{theme_name}'.")
        logging.info(f"Theme changed to '{theme_name}'.")

    def apply_theme(self, theme_name):
        """
        Applies the selected theme to the GUI components.

        :param theme_name: Name of the theme to apply.
        """
        self.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};")
        self.bindings_text.setStyleSheet(f"background-color: {THEMES[CURRENT_THEME]['background']}; color: {THEMES[CURRENT_THEME]['text']};")
        for key_name, button in self.key_buttons.items():
            bound_actions = self.ed_keys.get_bound_actions(
                self.ed_keys.get_scancode_for_key(
                    self.ed_keys.normalize_key(key_name)
                )
            )
            has_binding = bool(bound_actions)
            specific_category = self.determine_key_category(key_name)  # Corrected Call
            is_general = (specific_category == "General")

            button.setStyleSheet(self.get_button_style(
                is_pressed=False,
                has_binding=has_binding,
                category=specific_category or "General",
                is_general=is_general
            ))

            tooltip_text = "\n".join(self.order_actions_by_category(bound_actions, specific_category)) if bound_actions else "Unassigned"
            button.setToolTip(tooltip_text)
        logging.debug(f"Applied theme '{theme_name}' to all components.")
    
    def handle_toggle_plugin(self, tree): # Handles the toggling of a plugin based on user selection.
        """
        Handles the toggling of a plugin based on user selection.

        :param tree: QTreeWidget object containing plugin items.
        """
        selected_items = tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Toggle Plugin", "Please select a plugin to toggle.")
            logging.warning("No plugin selected for toggling.")
            return
        selected_item = selected_items[0]
        plugin_name = selected_item.text(0)
        self.plugin_manager.toggle_plugin(plugin_name)
        self.toggle_plugin_via_ui()
        logging.info(f"Toggled plugin '{plugin_name}'.")

    def toggle_plugin_via_ui(self): # Opens a dialog to toggle plugins via the UI.
        """
        Opens a dialog to toggle plugins via the UI.
        """
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            QMessageBox.information(self, "Toggle Plugins", "No plugins available.")
            logging.info("No plugins available to toggle.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Toggle Plugins")
        dialog.setMinimumSize(400, 300)
        layout = QVBoxLayout(dialog)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Plugin Name", "Status"])
        for plugin, status in plugins:
            item = QTreeWidgetItem([plugin, status])
            tree.addTopLevelItem(item)
        layout.addWidget(tree)

        button_layout = QHBoxLayout()
        toggle_button = QPushButton("Toggle")
        close_button = QPushButton("Close")
        button_layout.addWidget(toggle_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        toggle_button.clicked.connect(lambda: self.handle_toggle_plugin(tree))
        close_button.clicked.connect(dialog.accept)

        dialog.exec_()
        logging.debug("Opened plugin toggle dialog.")

    def closeEvent(self, event): # Handles the window close event to ensure proper cleanup.
        """
        Handles the window close event to ensure proper cleanup.

        :param event: QCloseEvent object.
        """
        logging.debug("Window closing. Clearing focus to prevent key events.")
        
        # Clear focus to prevent lingering key events
        self.clearFocus()
        
        # Ensure key events are flushed out of the event queue
        QApplication.processEvents(QEventLoop.AllEvents)
        
        event.accept()  # Proceed with the close event
        logging.info("Application closed successfully.")
  
    def flush_event_queue(self): # Flushes all pending events in the event queue.
        """
        Flushes all pending events in the event queue.
        """
        QApplication.processEvents(QEventLoop.AllEvents)
        logging.debug("Flushed the event queue.")

    def eventFilter(self, obj, event):
        """
        Filters events to block specific keys globally.

        :param obj: Object the event is sent to.
        :param event: QEvent object.
        :return: Boolean indicating if the event is handled.
        """
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if self.should_block_key(key):
                logging.debug(f"Blocked global key: {self.keycode_to_keyname(key)}")  # Single Logging
                return True  # Block the event globally

        return super().eventFilter(obj, event)
  
    def focusInEvent(self, event):
        # Ensure the widget visually indicates it has focus
        # self.setStyleSheet("border: 2px solid #007bff;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        # Clear focus indication
        # self.setStyleSheet("")
        super().focusOutEvent(event)  
        
    def get_key_name(self, event):
        """
        Translates a QKeyEvent into the internal key name using KEY_MAPPING.

        :param event: QKeyEvent object.
        :return: Internal key name string.
        """
        key = event.key()
        scan_code = event.nativeScanCode()
        
        # Debugging Output
        logging.debug(f"Key: {key}, Scan Code: {scan_code}")

        # Handle Modifier Keys with VK Codes
        if key == Qt.Key_Shift:
            if scan_code == 42:
                return 'LSHIFT'
            elif scan_code == 54:
                return 'RSHIFT'
            else:
                logging.warning(f"Unknown scan_code for Shift key: {scan_code}")
                return ''
        elif key == Qt.Key_Control:
            if scan_code == 29:
                return 'LCONTROL'
            elif scan_code in [157, 285]:  # RCONTROL can have multiple scan codes
                return 'RCONTROL'
            else:
                logging.warning(f"Unknown scan_code for Control key: {scan_code}")
                return ''
        elif key == Qt.Key_Alt:
            if scan_code == 56:
                return 'LALT'
            elif scan_code in [184, 312]:  # RMENU can have multiple scan codes
                return 'RALT'
            else:
                logging.warning(f"Unknown scan_code for Alt key: {scan_code}")
                return ''
        elif key == Qt.Key_Meta:
            if scan_code == 219:
                return 'LWIN'
            elif scan_code == 220:
                return 'RWIN'
            else:
                logging.warning(f"Unknown scan_code for Meta key: {scan_code}")
                return 'WIN'

        # Handle Numpad Keys
        if event.modifiers() & Qt.KeypadModifier:
            numpad_map = {
                Qt.Key_0: 'NUMPAD0', Qt.Key_1: 'NUMPAD1', Qt.Key_2: 'NUMPAD2',
                Qt.Key_3: 'NUMPAD3', Qt.Key_4: 'NUMPAD4', Qt.Key_5: 'NUMPAD5',
                Qt.Key_6: 'NUMPAD6', Qt.Key_7: 'NUMPAD7', Qt.Key_8: 'NUMPAD8',
                Qt.Key_9: 'NUMPAD9', Qt.Key_Plus: 'ADD', Qt.Key_Minus: 'SUBTRACT',
                Qt.Key_Asterisk: 'MULTIPLY', Qt.Key_Slash: 'DIVIDE',
                Qt.Key_Period: 'DECIMAL', Qt.Key_Return: 'NUMPADENTER',
                Qt.Key_Enter: 'NUMPADENTER',
            }
            return numpad_map.get(key, KEY_MAPPING.get(key, ''))

        # General Keys
        key_name = KEY_MAPPING.get(key, event.text().upper())

        if not key_name:
            logging.warning(f"Unmapped key pressed: {key}")
        return key_name

    def showEvent(self, event):
        # Ensure the widget has focus when shown
        self.setFocus(Qt.OtherFocusReason)
        super().showEvent(event)

    def simulate_key(self, vk_code):
        """
        Simulates a key press and release for the given VK code.

        :param vk_code: Virtual-Key code of the key to simulate.
        """
        inputs = (INPUT * 2)()

        # Key press
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].ki.wVk = vk_code
        inputs[0].ki.wScan = 0
        inputs[0].ki.dwFlags = 0
        inputs[0].ki.time = 0
        inputs[0].ki.dwExtraInfo = 0

        # Key release
        inputs[1].type = INPUT_KEYBOARD
        inputs[1].ki.wVk = vk_code
        inputs[1].ki.wScan = 0
        inputs[1].ki.dwFlags = KEYEVENTF_KEYUP
        inputs[1].ki.time = 0
        inputs[1].ki.dwExtraInfo = 0

        n_sent = SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))
        if n_sent != 2:
            logging.error(f"SendInput failed for VK code {vk_code}")
        else:
            key_name = self.ed_keys.get_key_name_from_vkcode(vk_code)
            logging.debug(f"Simulated key press and release for '{key_name}' (VK Code: {vk_code})")


# SendInput function
SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)
SendInput.restype = wintypes.UINT

# Constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
 
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set Fusion style

    # Set default text color to white
    app.setStyleSheet("""
        QWidget {
            color: white;
            background-color: #2b2b2b;
        }
        QTextEdit {
            color: white;
            background-color: #333333;
        }
        QLineEdit {
            color: white;
            background-color: #555555;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: white;
        }
        QMenuBar::item {
            color: white;
        }
        QMenuBar::item:selected {
            background-color: #555555;
        }
        QMenu {
            background-color: #2b2b2b;
            color: white;
        }
        QMenu::item:selected {
            background-color: #555555;
        }
    """)

    binds_file = 'main.binds'  # Replace with your .binds file path
    if not os.path.exists(binds_file):
        QMessageBox.critical(None, "Binds File Missing", f"The binds file '{binds_file}' does not exist.")
        sys.exit(1)
    ed_keys = EDKeys(binds_file)
    ex = KeyboardGUI(ed_keys)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
