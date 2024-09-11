# TODO for 1.2: 


# - Fix AP key conflicts not showing up
# - Change key colours (and maybe try and find out how to make stiped buttons)


# - Make print output more readable / easy to debug
# - Add a Help / How to
# - Remove double 'File' entry
# - Fix different behaviour for left, middle and right keyboard areas on increasing the window size
# - Make search function work on every tab without having to re-type
# - Fix Selector window size + colours

# - Clean up old code
# - Check requirements.txt

# FIXED

# - In somewhat the same vein, can't press to see anything but the QWERTY keys + numbers. Numpad numbers are seen as the other numbers.
# - Why do I need to put normalize_keys in twice? It breaks if I remove it from EDKeys, but GUI needs it too.
# - Fix different behaviour for left, middle and right keyboard areas on increasing the window size
# - LeftShift and RightShift are still not working. Do we also need to differentiate between slashes?
# - Key Highlight on pressing keys
# - Fix resolution thing / stretching keys where needed (space)


import sys
import os
import logging
from os.path import getmtime, isfile, join
import xml.etree.ElementTree as ET
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy, 
                             QSpacerItem, QFileDialog, QMenuBar, QAction, QToolTip, 
                             QMessageBox, QInputDialog, QLineEdit, QTabWidget, QComboBox,
                             QStatusBar, QLabel, QListWidget, QDialog, QTextEdit, QScrollArea)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
import configparser
import gettext

# Configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Internationalization
_ = gettext.gettext

# Constants

# SCANCODE: Dictionary mapping key names to their respective scan codes
SCANCODE = {
    'DIK_ESCAPE': 0x01, 'DIK_1': 0x02, 'DIK_2': 0x03, 'DIK_3': 0x04, 'DIK_4': 0x05,
    'DIK_5': 0x06, 'DIK_6': 0x07, 'DIK_7': 0x08, 'DIK_8': 0x09, 'DIK_9': 0x0A,
    'DIK_0': 0x0B, 'DIK_MINUS': 0x0C, 'DIK_EQUALS': 0x0D, 'DIK_BACK': 0x0E, 'DIK_TAB': 0x0F,
    'DIK_Q': 0x10, 'DIK_W': 0x11, 'DIK_E': 0x12, 'DIK_R': 0x13, 'DIK_T': 0x14,
    'DIK_Y': 0x15, 'DIK_U': 0x16, 'DIK_I': 0x17, 'DIK_O': 0x18, 'DIK_P': 0x19,
    'DIK_LBRACKET': 0x1A, 'DIK_RBRACKET': 0x1B, 'DIK_RETURN': 0x1C, 'DIK_LCONTROL': 0x1D,
    'DIK_A': 0x1E, 'DIK_S': 0x1F, 'DIK_D': 0x20, 'DIK_F': 0x21, 'DIK_G': 0x22,
    'DIK_H': 0x23, 'DIK_J': 0x24, 'DIK_K': 0x25, 'DIK_L': 0x26, 'DIK_SEMICOLON': 0x27,
    'DIK_APOSTROPHE': 0x28, 'DIK_GRAVE': 0x29, 'DIK_LSHIFT': 0x2A, 'DIK_BACKSLASH': 0x2B,
    'DIK_Z': 0x2C, 'DIK_X': 0x2D, 'DIK_C': 0x2E, 'DIK_V': 0x2F, 'DIK_B': 0x30,
    'DIK_N': 0x31, 'DIK_M': 0x32, 'DIK_COMMA': 0x33, 'DIK_PERIOD': 0x34, 'DIK_SLASH': 0x35,
    'DIK_RSHIFT': 0x36, 'DIK_MULTIPLY': 0x37, 'DIK_LALT': 0x38, 'DIK_SPACE': 0x39,
    'DIK_CAPITAL': 0x3A, 'DIK_F1': 0x3B, 'DIK_F2': 0x3C, 'DIK_F3': 0x3D, 'DIK_F4': 0x3E,
    'DIK_F5': 0x3F, 'DIK_F6': 0x40, 'DIK_F7': 0x41, 'DIK_F8': 0x42, 'DIK_F9': 0x43,
    'DIK_F10': 0x44, 'DIK_NUMLOCK': 0x45, 'DIK_SCROLL': 0x46, 'DIK_NUMPAD7': 0x47,
    'DIK_NUMPAD8': 0x48, 'DIK_NUMPAD9': 0x49, 'DIK_SUBTRACT': 0x4A, 'DIK_NUMPAD4': 0x4B,
    'DIK_NUMPAD5': 0x4C, 'DIK_NUMPAD6': 0x4D, 'DIK_ADD': 0x4E, 'DIK_NUMPAD1': 0x4F,
    'DIK_NUMPAD2': 0x50, 'DIK_NUMPAD3': 0x51, 'DIK_NUMPAD0': 0x52, 'DIK_DECIMAL': 0x53,
    'DIK_F11': 0x57, 'DIK_F12': 0x58,
    'DIK_NUMPADENTER': 0x9C, 'DIK_RCONTROL': 0x9D, 'DIK_DIVIDE': 0xB5, 'DIK_RALT': 0xB8,
    'DIK_HOME': 0xC7, 'DIK_UP': 0xC8, 'DIK_PRIOR': 0xC9, 'DIK_LEFT': 0xCB, 'DIK_RIGHT': 0xCD,
    'DIK_END': 0xCF, 'DIK_DOWN': 0xD0, 'DIK_NEXT': 0xD1, 'DIK_INSERT': 0xD2, 'DIK_DELETE': 0xD3,
    'DIK_LWIN': 0xDB, 'DIK_RWIN': 0xDC, 'DIK_APPS': 0xDD,
    'DIK_PAUSE': 0x45, 'DIK_PRINTSCREEN': 0xB7,
    'DIK_PAGEUP': 0xC9, 'DIK_PAGEDOWN': 0xD1, 'DIK_TILDE': 0x29,
    'DIK_LEFTMETA': 0xDB, 'DIK_RIGHTMETA': 0xDC, 'DIK_MEDIASELECT': 0xED, 'DIK_MUTE': 0xA0,
    'DIK_VOLUMEDOWN': 0xAE, 'DIK_VOLUMEUP': 0xB0, 'DIK_WEBHOME': 0xB2, 'DIK_POWER': 0xDE,
    'DIK_SLEEP': 0xDF, 'DIK_WAKE': 0xE3, 'DIK_MEDIASTOP': 0xA4, 'DIK_CALCULATOR': 0xA1,
    'DIK_ACPI_POWER': 0xDE, 'DIK_ACPI_SLEEP': 0xDF, 'DIK_ACPI_WAKE': 0xE3, 'DIK_WEBSEARCH': 0xEA,
    'DIK_WEBFAVORITES': 0xEB, 'DIK_WEBREFRESH': 0xE9, 'DIK_WEBSTOP': 0xE8, 'DIK_WEBFORWARD': 0xE7,
    'DIK_WEBBACK': 0xE6, 'DIK_MYCOMPUTER': 0xEB, 'DIK_MAIL': 0xEC,
    
    # Aliases for consistency
    'DIK_BACKSPACE': 0x0E,
    'DIK_ENTER': 0x1C,
    'DIK_NUMPADSLASH': 0xB5,
    'DIK_NUMPADSTAR': 0x37,
    'DIK_NUMPADMINUS': 0x4A,
    'DIK_NUMPADPLUS': 0x4E,
    'DIK_NUMPADPERIOD': 0x53,
}

# KEYBOARD_LAYOUTS: Dictionary containing different keyboard layout configurations
KEYBOARD_LAYOUTS = {
    'QWERTY': [
        ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BKSP'],
        ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
        ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'ENTER'],
        ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'SHIFT'],
        ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
    ],
    'AZERTY': [
        ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
        ['²', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '°', '+', 'BKSP'],
        ['TAB', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '^', '$'],
        ['CAPS', 'Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'Ù', '*', 'ENTER'],
        ['SHIFT', 'W', 'X', 'C', 'V', 'B', 'N', ',', ';', ':', '!', 'SHIFT'],
        ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
    ],
    'QWERTZ': [
        ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
        ['^', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'ß', '´', 'BKSP'],
        ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü', '+'],
        ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä', '#', 'ENTER'],
        ['SHIFT', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-', 'SHIFT'],
        ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'WIN', 'MENU', 'CTRL']
    ]
}

# BINDING_CATEGORIES: Dictionary containing all KeyActions (ACTIONS you can bind KEY to) sorted by category
BINDING_CATEGORIES = {
    "General": [
        "UIFocus", "UI_Up", "UI_Down", "UI_Left", "UI_Right", "UI_Select", "UI_Back",
        "UI_Toggle", "CycleNextPanel", "CyclePreviousPanel", "CycleNextPage",
        "CyclePreviousPage", "QuickCommsPanel", "FocusCommsPanel", "FocusLeftPanel",
        "FocusRightPanel", "GalaxyMapOpen", "SystemMapOpen", "ShowPGScoreSummaryInput",
        "HeadLookToggle", "Pause", "FriendsMenu", "OpenCodexGoToDiscovery", 
        "PlayerHUDModeToggle", "ExplorationFSSEnter", "PhotoCameraToggle",
        "GalaxyMapHome",  # Moved from "Galaxy Map" category
        #NEW
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

        # NEW
        "SetSpeedMinus100", "SetSpeedMinus75", "SetSpeedMinus50", "SetSpeedMinus25",
        "YawLeftButton_Landing", "YawRightButton_Landing", "PitchUpButton_Landing",
        "PitchDownButton_Landing", "RollLeftButton_Landing", "RollRightButton_Landing",
        "LeftThrustButton_Landing", "RightThrustButton_Landing", "UpThrustButton_Landing",
        "DownThrustButton_Landing", "ForwardThrustButton_Landing", "BackwardThrustButton_Landing",

        # # SAA  (Surface Scanner) controls
        # "ExplorationSAAChangeScannedAreaViewToggle", "ExplorationSAAExitThirdPerson",
        # "ExplorationSAANextGenus", "ExplorationSAAPreviousGenus",
        # "SAAThirdPersonYawLeftButton", "SAAThirdPersonYawRightButton",
        # "SAAThirdPersonPitchUpButton", "SAAThirdPersonPitchDownButton",
        # "SAAThirdPersonFovOutButton", "SAAThirdPersonFovInButton",
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
        "UIFocus_Buggy", "FocusLeftPanel_Buggy", "FocusCommsPanel_Buggy", "QuickCommsPanel_Buggy",
        "FocusRadarPanel_Buggy", "FocusRightPanel_Buggy", "GalaxyMapOpen_Buggy", "SystemMapOpen_Buggy",
        "OpenCodexGoToDiscovery_Buggy", "PlayerHUDModeToggle_Buggy", "HeadLookToggle_Buggy",
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

        # NEW
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

        # NEW
        "ToggleReverseThrottleInputFreeCam", "MoveFreeCamForward", "MoveFreeCamBackwards",
        "MoveFreeCamRight", "MoveFreeCamLeft", "MoveFreeCamUp", "MoveFreeCamDown",
        "PitchCameraUp", "PitchCameraDown", "YawCameraLeft", "YawCameraRight",
        "RollCameraLeft", "RollCameraRight",
    ],
    "Multi-Crew": [
        "MultiCrewToggleMode", "MultiCrewPrimaryFire", "MultiCrewSecondaryFire",
        "MultiCrewPrimaryUtilityFire", "MultiCrewSecondaryUtilityFire",
        "MultiCrewCockpitUICycleForward", "MultiCrewCockpitUICycleBackward",

        # NEW
        "MultiCrewThirdPersonYawLeftButton", "MultiCrewThirdPersonYawRightButton",
        "MultiCrewThirdPersonPitchUpButton", "MultiCrewThirdPersonPitchDownButton",
        "MultiCrewThirdPersonFovOutButton", "MultiCrewThirdPersonFovInButton",
        "OpenOrders",
    ],
    "Store": [
        "StoreEnableRotation", "StoreCamZoomIn", "StoreCamZoomOut", "StoreToggle",
    ],
    "Autopilot": [
        "AutoDockButton", "SetSpeedZero", "SetSpeed50", "SetSpeed100",
        "ToggleFlightAssist", "ToggleButtonUpInput", "HyperSuperCombination",
        "Supercruise", "Hyperspace", "GalaxyMapOpen", "SystemMapOpen",
        "TargetNextRouteSystem", "EngageAutopilot", "DisengageAutopilot",
        "AutopilotSpeedIncrease", "AutopilotSpeedDecrease"
    ],
    
}

# Add a dictionary for category exceptions. These functions and their keybindings won't show up in their respective groups!
CATEGORY_EXCEPTIONS = {
    "General":["CommanderCreator_Undo", "CommanderCreator_Redo", "CommanderCreator_Rotation_MouseToggle"], # Really don't know where to put those lol
    "SpaceShip": [],
    "SRV": [],
    "On-Foot": [],
    # Add other categories as needed
}
# Utility Functions

def setup_logging():
    """Set up logging configuration for the application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh = logging.FileHandler('ed_keybinds.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

class EDKeys:
    """
    Handles the loading, parsing, and normalization of Elite Dangerous key bindings.
    """
    def __init__(self, binds_file=None):
        self.binds_file = binds_file or self.get_latest_keybinds()
        self.bindings = self.parse_binds_file()

    def parse_binds_file(self):
        bindings = {category: {} for category in BINDING_CATEGORIES.keys()}
        try:
            tree = ET.parse(self.binds_file)
            root = tree.getroot()

            for element in root:
                key = element.find('Primary')
                if key is not None and 'Key' in key.attrib:
                    normalized_key = self.normalize_key(key.attrib['Key'])
                    action = element.tag

                    # Check action against the predefined BINDING_CATEGORIES
                    assigned = False
                    for category, actions in BINDING_CATEGORIES.items():
                        if action in actions:
                            bindings[category][action] = normalized_key
                            assigned = True
                            break
                    
                    if not assigned:
                        bindings["General"][action] = normalized_key

            # Load Autopilot bindings
            self.load_autopilot_bindings()
            bindings["Autopilot"] = self.autopilot_bindings

        except Exception as e:
            print(f"An error occurred while parsing the binds file: {e}")

        print(f"Loaded bindings: {bindings}")
        return bindings

    def get_latest_keybinds(self):
        try:
            path_bindings = config.get('Paths', 'BindingsPath', fallback=os.path.join(os.environ['LOCALAPPDATA'], "Frontier Developments", "Elite Dangerous", "Options", "Bindings"))
            bindings_files = [join(path_bindings, f) for f in os.listdir(path_bindings) if isfile(join(path_bindings, f)) and f.endswith('.binds')]
            return max(bindings_files, key=getmtime) if bindings_files else None
        except Exception as e:
            logging.error(f"Failed to get latest keybinds: {e}")
            return None

    @staticmethod
    def save_bindings(bindings, file_name):
        root = ET.Element("Root")
        for category, category_bindings in bindings.items():
            for action, key in category_bindings.items():
                binding = ET.SubElement(root, action)
                primary = ET.SubElement(binding, "Primary")
                primary.set("Device", "Keyboard")
                primary.set("Key", key)
        tree = ET.ElementTree(root)
        tree.write(file_name, encoding="utf-8", xml_declaration=True)
    

    # @staticmethod
    # def normalize_key(key):
    #     key = key.lower().replace('key_', '').replace('dik_', '')
    #     key_map = {
    #         'leftcontrol': 'lctrl', 'rightcontrol': 'rctrl',
    #         'leftshift': 'lshift', 'rightshift': 'rshift',
    #         'leftalt': 'lalt', 'rightalt': 'ralt',
    #         'return': 'enter', 'escape': 'esc',
    #         'prior': 'pg up', 'next': 'pg dn',
    #         'numpad_0': 'num0', 'numpad_1': 'num1', 'numpad_2': 'num2', 'numpad_3': 'num3',
    #         'numpad_4': 'num4', 'numpad_5': 'num5', 'numpad_6': 'num6', 'numpad_7': 'num7',
    #         'numpad_8': 'num8', 'numpad_9': 'num9',
    #         'numpad_slash': 'num/', 'numpad_star': 'num*', 'numpad_minus': 'num-', 'numpad_plus': 'num+',
    #         'numpad_period': 'num.',
    #         'numpad_enter': 'numenter',
    #         'uparrow': '↑', 'downarrow': '↓', 'leftarrow': '←', 'rightarrow': '→',
    #     }
    #     return key_map.get(key, key)

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


class KeyboardGUI(QMainWindow):
    """
    Main GUI class for the Elite Dangerous Keybindings Visualizer.
    Handles the creation and management of the keyboard interface.
    """

    def __init__(self, keybindings, normalize_key_func):
        super().__init__()
        self.keybindings = keybindings
        self.current_layout = 'QWERTY'
        self.key_buttons = {category: {} for category in BINDING_CATEGORIES.keys()}
        self.pressed_keys = set()
        self.key_highlight_timer = QTimer()
        self.key_highlight_timer.timeout.connect(self.reset_key_highlights)
        self.key_highlight_timer.setSingleShot(True)
        self.keybindings = keybindings
        self.normalize_key = normalize_key_func
        
        self.autopilot_functions = [ # More to add
            "EngageAutopilot",
            "DisengageAutopilot",
            "SetDestination",
            "ToggleObstacleAvoidance",
            "IncreaseAutopilotSpeed",
            "DecreaseAutopilotSpeed",
            "ToggleAutodocking",
            "EmergencyStop"
        ]
        self.autopilot_default_bindings = {
            "EngageAutopilot": "home",
            "DisengageAutopilot": "end",
            "SetDestination": "insert"
        }
        self.load_autopilot_bindings()
        # print(f"Received keybindings: {self.keybindings}") # DEBUG
        self.initUI()

    def initUI(self): # Fix sizing
        self.setWindowTitle('Elite: Dangerous Keybind Checker by #glassesinsession')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #333333;
            }
            QTabBar::tab {
                background-color: #444444;
                color: #ffffff;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #666666;
            }
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QLineEdit, QTextEdit {
                background-color: #444444;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #666666;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #ffffff;
                selection-background-color: #555555;
            }
            QMenuBar {
                background-color: #333333;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #555555;
            }
            QMenu {
                background-color: #333333;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
        """)
        
        self.setGeometry(100, 100, 1800, 600)
        self.setMaximumSize(2000, 800)  # Set maximum width and height
        self.setMinimumSize(800, 400)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Layout switcher
        self.layout_switcher = QComboBox()
        self.layout_switcher.addItems(KEYBOARD_LAYOUTS.keys())
        self.layout_switcher.setCurrentText(self.current_layout)
        self.layout_switcher.currentTextChanged.connect(self.change_layout)
        main_layout.addWidget(self.layout_switcher)
        
        # Create menu bar
        self.create_menus()

        # Add search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search by key name or bound action...")
        self.search_bar.textChanged.connect(self.search_keybindings)
        main_layout.addWidget(self.search_bar)

        # Create a scroll area for the tab widget to avoid squashing widgets on small screens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Tab widget inside the scroll area
        self.tab_widget = QTabWidget()
        scroll_area.setWidget(self.tab_widget)



        # Add text area for displaying bound keys
        self.bound_keys_display = QTextEdit()
        self.bound_keys_display.setReadOnly(True)
        self.bound_keys_display.setMaximumHeight(150)
        
        for category in BINDING_CATEGORIES.keys(): # Create the TABS based on BINDING_CATEGORIES
            if category != "Autopilot":  # Skip creating a tab for Autopilot
                self.create_keyboard_tab(category, self.get_category_color(category))

        # Add a status bar for messages
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Adjust widget size policies
        self.set_resizing_policies()

        self.show()



    def set_resizing_policies(self):
        """Set resizing policies for buttons and other widgets to adapt to different resolutions."""
        for tab_name, buttons in self.key_buttons.items():
            for key, button in buttons.items():
                if button is not None and isinstance(button, QPushButton):
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                elif button is None:
                    print(f"Warning: Button for '{key}' in '{tab_name}' is None")
    
    def resizeEvent(self, event):
        """Adjust fonts and other settings dynamically on window resize."""
        super().resizeEvent(event)
        self.adjust_fonts()

    def adjust_fonts(self):
        """Adjust fonts dynamically based on window size."""
        window_width = self.size().width()
        font_size = max(10, window_width // 6000)  # Example: scale font size based on width
        
        for tab_name, buttons in self.key_buttons.items():
            for key, button in buttons.items():
                font = button.font()
                font.setPointSize(font_size)
                button.setFont(font)
                
    def keyPressEvent(self, event): # NEW - Keyboard Press Highlights
        key = event.text().upper()
        if key:
            self.pressed_keys.add(key)
            self.highlight_pressed_keys()
            self.key_highlight_timer.start(300)  # Reset after 300ms

    def keyReleaseEvent(self, event): # NEW - Keyboard Press Highlights
        key = event.text().upper()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def highlight_pressed_keys(self): # NEW - TODO: Change color scheme
        current_category = self.tab_widget.tabText(self.tab_widget.currentIndex())
        for key, button in self.key_buttons[current_category].items():
            if key.upper() in self.pressed_keys:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffff00;
                        color: #000000;
                        border: 2px solid #ff0000;
                        font-weight: bold;
                    }
                """)
            else:
                normalized_key = self.normalize_key(key)
                is_active = self.is_key_active_for_category(normalized_key, current_category)
                self.update_key_color(button, normalized_key, current_category, self.get_category_color(current_category), is_active)

    def reset_key_highlights(self):
        QTimer.singleShot(0, self.update_all_key_colors)

    def show_status_message(self, message, timeout=0):
        self.statusBar().setStyleSheet("color: white; background-color: #333333;")
        self.statusBar().showMessage(message, timeout)
        self.statusBar().repaint()

    def create_key_button(self, text, category, color, size=(60, 40), max_size=(90, 60)):
        button = QPushButton(text)
        button.setMinimumSize(QSize(*size))
        button.setMaximumSize(QSize(*max_size))
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setContentsMargins(0, 0, 0, 0)
        button.clicked.connect(lambda _, b=button, c=category: self.key_button_clicked(b, c))
        
        normalized_key = self.normalize_key(text)
        is_active = self.is_key_active_for_category(normalized_key, category)
        self.update_key_color(button, normalized_key, category, color, is_active)
        return button
    
    def is_key_active_for_category(self, key, category):
        if category in BINDING_CATEGORIES:
            for action in BINDING_CATEGORIES[category]:
                if self.keybindings[category].get(action) == key:
                    return True
        return False

    def create_menus(self): # TODO - add other categories, too
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        load_action = QAction('Load Binds', self)
        load_action.triggered.connect(self.load_custom_binds)
        file_menu.addAction(load_action)
        save_action = QAction('Save Binds', self)
        save_action.triggered.connect(self.save_binds)
        file_menu.addAction(save_action)

        # Print menu
        print_menu = menubar.addMenu('Print')
        categories = ["Ship", "SRV", "OnFoot", "General"]
        for category in categories:
            category_menu = print_menu.addMenu(category)
            all_action = QAction(f'All {category} Activities', self)
            all_action.triggered.connect(lambda checked, c=category: self.print_all_activities(c))
            category_menu.addAction(all_action)
            bound_action = QAction(f'Bound {category} Activities', self)
            bound_action.triggered.connect(lambda checked, c=category: self.print_bound_activities(c))
            category_menu.addAction(bound_action)
        autopilot_action = QAction('Autopilot Keys', self)
        autopilot_action.triggered.connect(self.print_autopilot_keys)
        print_menu.addAction(autopilot_action)

        # Debug menu
        debug_menu = menubar.addMenu('Debug')
        print_all_action = QAction('Print All Bindings', self)
        print_all_action.triggered.connect(self.print_all_bindings)
        debug_menu.addAction(print_all_action)

        # Help menu item
        help_menu = menubar.addMenu('Help')
        help_action = QAction('Show Help', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def show_help(self):
        help_text = """
        Elite Dangerous Key Binding Checker

        This tool allows you to view and modify key bindings for Elite Dangerous.

        - Use the tabs to switch between different control categories.
        - Click on a key to view or change its binding.
        - Use the search bar to find specific bindings.
        - Colors indicate different categories of bindings.

        For more information, visit: [Your Website or GitHub Repository]
        """
        QMessageBox.information(self, "Help", help_text)
    
    def change_layout(self, new_layout):
        self.current_layout = new_layout
        self.recreate_keyboards()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clear_layout(item.layout())

    def recreate_keyboards(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            category = self.tab_widget.tabText(i)
            
            if tab.layout():
                self.clear_layout(tab.layout())
            else:
                tab.setLayout(QVBoxLayout())
            
            self.create_keyboard(tab.layout(), category)

    def create_keyboard_tab(self, category, color):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.create_keyboard(layout, category)
        self.tab_widget.addTab(tab, category)
        
    def create_keyboard(self, layout, category):
        color = self.get_category_color(category)
        main_keyboard = self.create_main_keyboard(category, color)
        home_arrow = self.create_home_arrow_area(category, color)
        numpad = self.create_numpad_area(category, color)

        keyboard_layout = QHBoxLayout()
        keyboard_layout.addLayout(main_keyboard, 7)
        keyboard_layout.addLayout(home_arrow, 1)
        keyboard_layout.addLayout(numpad, 2)
        keyboard_layout.setSpacing(10)
        keyboard_layout.setContentsMargins(10, 10, 10, 10)

        layout.addLayout(keyboard_layout)
    
    def create_main_keyboard(self, category, color):
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Vertical spacing between rows
        for row in KEYBOARD_LAYOUTS[self.current_layout]:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)  # Horizontal spacing between keys
            for key in row:
                if key == '':
                    row_layout.addSpacerItem(QSpacerItem(20, 40))
                else:
                    if key == 'SPACE':
                        button = self.create_key_button(key, category, color, size=(300, 40), max_size=(800, 60))
                    elif key in ['SHIFT', 'ENTER', 'BKSP']:
                        button = self.create_key_button(key, category, color, size=(100, 40), max_size=(150, 60))
                    else:
                        button = self.create_key_button(key, category, color)
                    row_layout.addWidget(button)
                    self.key_buttons[category][key.lower()] = button
            layout.addLayout(row_layout)
        return layout

    def create_home_arrow_area(self, category, color): # TODO - Fix extending keys
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Set fixed spacing

        home_layout = QGridLayout()
        home_keys = ['INS', 'HOME', 'PGUP', 'DEL', 'END', 'PGDN']
        for i, key in enumerate(home_keys):
            button = self.create_key_button(key, category, color)
            home_layout.addWidget(button, i // 3, i % 3)
            self.key_buttons[category][key.lower()] = button
        layout.addLayout(home_layout)

        layout.addStretch()

        arrow_layout = QGridLayout()
        arrow_keys = [('↑', 0, 1), ('←', 1, 0), ('↓', 1, 1), ('→', 1, 2)]
        for key, row, col in arrow_keys:
            button = self.create_key_button(key, category, color)
            arrow_layout.addWidget(button, row, col)
            self.key_buttons[category][key.lower()] = button
        layout.addLayout(arrow_layout)

        return layout
    
    def create_numpad_area(self, category, color):
        layout = QGridLayout()
        layout.setSpacing(5)  # Set fixed spacing
        numpad_keys = [
            ['NUM', '/', '*', '-'],
            ['7', '8', '9', '+'],
            ['4', '5', '6', ''],
            ['1', '2', '3', 'ENTER'],
            ['0', '', '.', '']
        ]

        for row, keys in enumerate(numpad_keys):
            for col, key in enumerate(keys):
                if key:
                    if key == '0':
                        button = self.create_key_button(f'NUM{key}', category, color, size=(120, 40), max_size=(180, 60))
                        layout.addWidget(button, 4, 0, 1, 2)
                    elif key == '+':
                        button = self.create_key_button(f'NUM{key}', category, color, size=(60, 80), max_size=(90, 120))
                        layout.addWidget(button, 1, 3, 2, 1)
                    elif key == 'ENTER':
                        button = self.create_key_button(f'NUM{key}', category, color, size=(60, 80), max_size=(90, 120))
                        layout.addWidget(button, 3, 3, 2, 1)
                    else:
                        button = self.create_key_button(f'NUM{key}', category, color)
                        layout.addWidget(button, row, col)
                    self.key_buttons[category][f'num{key.lower()}'] = button
        return layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # We can add any necessary resize logic here if needed in the future
    
    def check_key_conflicts(self, key, category):
        conflicts = []
        general_action = None
        
        # Check the specific category
        if key in self.keybindings[category]:
            conflicts.append((category, self.keybindings[category][key]))
        
        # Check General category
        if key in self.keybindings['General']:
            general_action = self.keybindings['General'][key]
            if category != 'General':
                conflicts.append(('General', general_action))
        
        # Check Autopilot bindings
        for ap_function, ap_key in self.autopilot_bindings.items():
            if ap_key == key:
                conflicts.append(("Autopilot", ap_function))
        
        return conflicts, general_action

    def update_key_color(self, button, key, category, base_color, is_active):
        bound_action = self.get_bound_action(key, category) if is_active else None
        
        if bound_action:
            if bound_action.startswith("General:"):
                color = self.get_category_color("General")
            else:
                color = base_color
            text_color = "#ffffff"
            tooltip = bound_action
        else:
            color = "#555555"  # Standard color for all unbound keys
            text_color = "#ffffff"
            tooltip = "Unassigned" if is_active else "Inactive for this category"

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-weight: {'bold' if is_active else 'normal'};
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
        """)
        button.setToolTip(tooltip)
    
    def is_general_binding(self, key):
        return any(bound_key == key for bound_key in self.keybindings['General'].values())

    def get_general_action(self, key):
        for action, bound_key in self.keybindings['General'].items():
            if bound_key == key:
                return action
        return None
    
    def get_category_color(self, category, action=None):
        colors = {
            "Ship": "#3498db",
            "SRV": "#2ecc71",
            "OnFoot": "#e67e22",
            "General": "#95a5a6",
            "Camera": "#f39c12",
            "FSS": "#d35400",  # Changed from "Full Spectrum System Scanner"
            "Multi-Crew": "#8e44ad",
            "Store": "#c0392b",
        }
        
        return colors.get(category, "#95a5a6")
            
    def blend_colors(self, color1, color2):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        return f"#{((r1 + r2) // 2):02x}{((g1 + g2) // 2):02x}{((b1 + b2) // 2):02x}"

    @staticmethod
    def lighten_color(color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        factor = 1.3
        r, g, b = [min(int(c * factor), 255) for c in (r, g, b)]
        return f"#{r:02x}{g:02x}{b:02x}"

    def darken_color(self, color, factor=0.7):
        """Darken the given color by the specified factor."""
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_all_key_colors(self):
        for category, buttons in self.key_buttons.items():
            for key, button in buttons.items():
                normalized_key = self.normalize_key(key)
                is_active = self.is_key_active_for_category(normalized_key, category)
                self.update_key_color(button, normalized_key, category, self.get_category_color(category), is_active)
        print("All key colors updated")
    
    def search_keybindings(self, search_text):
        search_text = search_text.lower()
        found = False
        for tab_index in range(self.tab_widget.count()):
            category = self.tab_widget.tabText(tab_index)
            for key, button in self.key_buttons[category].items():
                normalized_key = self.normalize_key(key)
                bound_action = self.get_bound_action(normalized_key, category)
                is_active = self.is_key_active_for_category(normalized_key, category)
                if search_text and (search_text in key.lower() or (bound_action and search_text in bound_action.lower())):
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #ffff00;
                            color: #000000;
                            border: none;
                            padding: 5px;
                            border-radius: 3px;
                            font-weight: bold;
                        }
                    """)
                    if not found:
                        self.tab_widget.setCurrentIndex(tab_index)
                        found = True
                else:
                    self.update_key_color(button, normalized_key, category, self.get_category_color(category), is_active)

        if not found:
            self.statusBar().showMessage("No matches found", 3000)

    def get_bound_action(self, key, category):
        # Check category-specific bindings first
        for action, bound_key in self.keybindings.get(category, {}).items():
            if self.normalize_key(bound_key) == key:
                return f"{category}: {action}"
        
        # Check general bindings
        for action, bound_key in self.keybindings.get('General', {}).items():
            if self.normalize_key(bound_key) == key:
                return f"General: {action}"
        
        # Check autopilot bindings
        for action, bound_key in self.autopilot_bindings.items():
            if self.normalize_key(bound_key) == key:
                return f"Autopilot: {action}"
        
        return None
    
    def key_button_clicked(self, button, category):
        key = button.text().lower()
        normalized_key = self.normalize_key(key)
        is_active = self.is_key_active_for_category(normalized_key, category)

        conflicts, general_action = self.check_key_conflicts(normalized_key, category)
        conflict_text = f"Current bindings:\n{', '.join([f'{cat}: {act}' for cat, act in conflicts])}\n" if conflicts else ""
        if general_action:
            conflict_text += f"General: {general_action}\n"

        available_actions = ["Unassign"]
        for cat in [category, 'General', 'Autopilot']:  # Add 'Autopilot' here
            category_actions = [action for action in BINDING_CATEGORIES.get(cat, []) if action in self.keybindings.get(cat, {})]
            if category_actions:
                available_actions.append(f"<b style='color: #4a90e2;'>{cat}</b>")
                available_actions.extend(category_actions)

        dialog = CustomActionDialog(self, f"Select action for {button.text()} in {category}", available_actions, conflict_text)
        if dialog.exec_():
            selected_action = dialog.list_widget.currentItem().text()
            if selected_action == "Unassign":
                self.unassign_key(normalized_key, category)
            elif selected_action.startswith("Autopilot:"):
                autopilot_function = selected_action.split(": ")[1]
                self.assign_autopilot_key(normalized_key, autopilot_function)
            elif not selected_action.startswith("<b"):
                self.assign_game_key(normalized_key, selected_action, category)

            self.update_key_color(button, normalized_key, category, self.get_category_color(category), is_active)
            print(f"Updated binding: {normalized_key} -> {selected_action}")

    def load_custom_binds(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Binds File", "", "Binds Files (*.binds)")
        if file_name:
            ed_keys = EDKeys(file_name)
            self.keybindings = ed_keys.bindings
            self.update_all_key_colors()

    def assign_game_key(self, key, action, category):
        old_action = self.get_bound_action(key, category)
        target_category = 'General' if action in self.keybindings['General'] else category

        for cat in [category, 'General']:
            self.keybindings[cat] = {k: v for k, v in self.keybindings[cat].items() if v != key and k != action}

        self.keybindings[target_category][action] = key

        self.autopilot_bindings = {k: v for k, v in self.autopilot_bindings.items() if v != key}

        if old_action:
            self.show_status_message(f"Reassigned '{key}' from '{old_action}' to '{action}' in {category}")
        else:
            self.show_status_message(f"Assigned '{key}' to '{action}' in {category}")
        
        try:
            self.update_all_key_colors()
        except Exception as e:
            print(f"Error updating key colors: {e}")
            # Optionally, add more robust error handling here

    def assign_autopilot_key(self, key, function):
        old_function = next((func for func, k in self.autopilot_bindings.items() if k == key), None)
        self.autopilot_bindings = {k: v for k, v in self.autopilot_bindings.items() if v != key and k != function}
        
        self.autopilot_bindings[function] = key

        for category in self.keybindings:
            self.keybindings[category] = {k: v for k, v in self.keybindings[category].items() if v != key}

        self.update_all_key_colors()
        
        if old_function:
            self.show_status_message(f"Reassigned '{key}' from '{old_function}' to Autopilot function '{function}' and saved")
        else:
            self.show_status_message(f"Assigned '{key}' to Autopilot function '{function}' and saved")
        self.save_autopilot_bindings()

    def unassign_key(self, key, category):
        for cat in [category, 'General']:
            self.keybindings[cat] = {k: v for k, v in self.keybindings[cat].items() if v != key}
        
        self.autopilot_bindings = {k: v for k, v in self.autopilot_bindings.items() if v != key}

        self.show_status_message(f"Unassigned '{key}' in {category}")
        self.update_all_key_colors()
        
        self.save_autopilot_bindings()

    def save_binds(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Binds File", "", "Binds Files (*.binds)")
        if file_name:
            EDKeys.save_bindings(self.keybindings, file_name)

    def save_autopilot_bindings(self, filename='./configs/autopilot_bindings.json'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.autopilot_bindings, f, indent=4)

    def load_autopilot_bindings(self, filename='./configs/autopilot_bindings.json', default_filename='./configs/default_autopilot_bindings.json'):
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                if content:
                    self.autopilot_bindings = json.loads(content)
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            logging.warning(f"Autopilot bindings file not found: {filename}")
            self.load_default_autopilot_bindings(default_filename)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in {filename}. Loading default autopilot bindings.")
            self.load_default_autopilot_bindings(default_filename)
        except Exception as e:
            logging.error(f"Unexpected error loading autopilot bindings: {e}")
            self.autopilot_bindings = self.autopilot_default_bindings.copy()

    def load_default_autopilot_bindings(self, default_filename):
        try:
            with open(default_filename, 'r') as f:
                self.autopilot_bindings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.autopilot_bindings = self.autopilot_default_bindings.copy()
            print("Warning: Could not load default autopilot bindings. Using hardcoded defaults.")
    
    def print_all_activities(self, category):
        output = f"\nAll activities for {category}:\n"
        for action, key in self.keybindings[category].items():
            line = f"{action}: {key}\n"
            output += line
            print(line, end='')
        self.bound_keys_display.append(output)

    def print_bound_activities(self, category):
        output = f"\nBound activities for {category}:\n"
        for action, key in self.keybindings[category].items():
            if key:
                line = f"{action}: {key}\n"
                output += line
                print(line, end='')
        self.bound_keys_display.append(output)

    def print_autopilot_keys(self):
        output = "\nAutopilot related keys:\n"
        for function, key in self.autopilot_bindings.items():
            line = f"{function}: {key}\n"
            output += line
            print(line, end='')
        self.bound_keys_display.append(output)

    def print_all_bindings(self):
        output = "\nAll Bindings:\n"
        for category, bindings in self.keybindings.items():
            output += f"\n{category}:\n"
            print(f"\n{category}:")
            for action, key in bindings.items():
                line = f"  {action}: {key}\n"
                output += line
                print(line, end='')
        self.bound_keys_display.append(output)
        print("\nAll Bindings:")
        for category, bindings in self.keybindings.items():
            print(f"\n{category}:")
            for action, key in bindings.items():
                print(f"  {action}: {key}")

    def add_category_exception(self, category, action):
        if category in CATEGORY_EXCEPTIONS:
            CATEGORY_EXCEPTIONS[category].append(action)

    def remove_category_exception(self, category, action):
        if category in CATEGORY_EXCEPTIONS and action in CATEGORY_EXCEPTIONS[category]:
            CATEGORY_EXCEPTIONS[category].remove(action)

    def show_error(self, message):
        QMessageBox.critical(self, _("Error"), message)

    def closeEvent(self, event): # Temporarily commented AP functions out
        all_conflicts = []
        for category in ['Ship', 'SRV', 'OnFoot', 'General']:
            for key in set(self.keybindings[category].values()):
                conflicts, general_action = self.check_key_conflicts(key, category)
                if len(conflicts) > 1 or (conflicts and general_action):
                    conflict_str = ', '.join([f'{cat}: {act}' for cat, act in conflicts])
                    if general_action and category != 'General':
                        conflict_str += f', General: {general_action}'
                    all_conflicts.append(f"'{key}' in {category}: {conflict_str}")
        
            # for function, key in self.autopilot_bindings.items():
            #     conflicts, _ = self.check_key_conflicts(key, 'Autopilot')
            #     if conflicts:
            #         conflict_str = ', '.join([f'{cat}: {act}' for cat, act in conflicts])
            #         all_conflicts.append(f"'{key}' in Autopilot: {conflict_str}")
        
        if all_conflicts:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("There are key binding conflicts:")
            msg.setInformativeText("\n".join(all_conflicts))
            msg.setDetailedText("These conflicts may cause unexpected behavior in the game. It's recommended to resolve them before closing.")
            msg.setWindowTitle("Key Binding Conflicts")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.No)
            msg.button(QMessageBox.Yes).setText("Close anyway")
            msg.button(QMessageBox.No).setText("Go back and fix")
            
            retval = msg.exec_()
            if retval == QMessageBox.No:
                event.ignore()
                return
            elif retval == QMessageBox.Cancel:
                event.ignore()
                return

        event.accept()

    def initialize_key_colors(self):
        self.update_all_key_colors()



class CustomActionDialog(QDialog):
    def __init__(self, parent, title, actions, conflict_text=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        
        if conflict_text:
            conflict_label = QLabel(conflict_text)
            layout.addWidget(conflict_label)
        
        self.list_widget = QListWidget()
        for action in actions:
            if action.startswith('<b style'):
                self.list_widget.addItem('-------------------')
            self.list_widget.addItem(action)
        layout.addWidget(self.list_widget)
        button = QPushButton("Select")
        button.clicked.connect(self.accept)
        layout.addWidget(button)

    def get_selected_action(self):
        selected_item = self.list_widget.currentItem()
        if selected_item and selected_item.text() != '-------------------':
            return selected_item.text()
        return None

def main():
    app = QApplication(sys.argv)  # Must be created before any QWidget
    ed_keys = EDKeys()
    ex = KeyboardGUI(ed_keys.bindings, ed_keys.normalize_key)  # Pass the normalize_key method
    
    setup_logging()
    app.setStyle('Fusion')
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()