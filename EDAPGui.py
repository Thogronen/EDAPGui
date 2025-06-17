import queue
import sys
import os
import threading
import kthread
from datetime import datetime
from time import sleep
import cv2
import json
from pathlib import Path
import keyboard
import webbrowser
import requests
from EDKeys import is_elite_or_edapgui_focused
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes

from PIL import Image, ImageGrab, ImageTk
import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from idlelib.tooltip import Hovertip

from Voice import *
from MousePt import MousePoint

from Image_Templates import *
from Screen import *
from Screen_Regions import *
from EDKeys import *
from EDJournal import *
from ED_AP import *

from EDlogger import logger


"""
File:EDAPGui.py

Description:
User interface for controlling the ED Autopilot

Note:
Ideas taken from:  https://github.com/skai2/EDAutopilot

 HotKeys:
    Home - Start FSD Assist
    INS  - Start SC Assist
    PG UP - Start Robigo Assist
    End - Terminate any ongoing assist (FSD, SC, AFK)

Author: sumzer0@yahoo.com
"""

# ---------------------------------------------------------------------------
# must be updated with a new release so that the update check works properly!
# contains the names of the release.

EDAP_VERSION = "V1.4.2.1 Beta "

FORM_TYPE_CHECKBOX = 0
FORM_TYPE_SPINBOX = 1
FORM_TYPE_ENTRY = 2


def hyperlink_callback(url):
    webbrowser.open_new(url)


class APGui():
    def __init__(self, root):
        self.root = root
        root.title("EDAutopilot " + EDAP_VERSION)
        # root.overrideredirect(True)
        # root.geometry("400x550")
        # root.configure(bg="blue")
        root.protocol("WM_DELETE_WINDOW", self.close_window)
        root.resizable(False, False)

        self.tooltips = {
            'FSD Route Assist': "Will execute your route. \nAt each jump the sequence will perform some fuel scooping.",
            'Supercruise Assist': "Will keep your ship pointed to target, \nyou target can only be a station for the autodocking to work.",
            'Waypoint Assist': "When selected, will prompt for the waypoint file. \nThe waypoint file contains System names that \nwill be entered into Galaxy Map and route plotted.",
            'Robigo Assist': "",
            'DSS Assist': "When selected, will perform DSS scans while you are traveling between stars.",
            'Single Waypoint Assist': "",
            'ELW Scanner': "Will perform FSS scans while FSD Assist is traveling between stars. \nIf the FSS shows a signal in the region of Earth, \nWater or Ammonia type worlds, it will announce that discovery.",
            'AFK Combat Assist': "Used with a AFK Combat ship in a Rez Zone.",
            'RollRate': "Roll rate your ship has in deg/sec. Higher the number the more maneuverable the ship.",
            'PitchRate': "Pitch (up/down) rate your ship has in deg/sec. Higher the number the more maneuverable the ship.",
            'YawRate': "Yaw rate (rudder) your ship has in deg/sec. Higher the number the more maneuverable the ship.",
            'SunPitchUp+Time': "This field are for ship that tend to overheat. \nProviding 1-2 more seconds of Pitch up when avoiding the Sun \nwill overcome this problem.",
            'Sun Bright Threshold': "The low level for brightness detection, \nrange 0-255, want to mask out darker items",
            'Nav Align Tries': "How many attempts the ap should make at alignment.",
            'Jump Tries': "How many attempts the ap should make to jump.",
            'Docking Retries': "How many attempts to make to dock.",
            'Wait For Autodock': "After docking granted, \nwait this amount of time for us to get docked with autodocking",
            'Start FSD': "Button to start FSD route assist.",
            'Start SC': "Button to start Supercruise assist.",
            'Start Robigo': "Button to start Robigo assist.",
            'Stop All': "Button to stop all assists.",
            'Refuel Threshold': "If fuel level get below this level, \nit will attempt refuel.",
            'Scoop Timeout': "Number of second to wait for full tank, \nmight mean we are not scooping well or got a small scooper",
            'Fuel Threshold Abort': "Level at which AP will terminate, \nbecause we are not scooping well.",
            'X Offset': "Offset left the screen to start place overlay text.",
            'Y Offset': "Offset down the screen to start place overlay text.",
            'Font Size': "Font size of the overlay.",
            'Ship Config Button': "Read in a file with roll, pitch, yaw values for a ship.",
            'Calibrate': "Will iterate through a set of scaling values \ngetting the best match for your system. \nSee HOWTO-Calibrate.md",
            'Waypoint List Button': "Read in a file with with your Waypoints.",
            'Cap Mouse XY': "This will provide the StationCoord value of the Station in the SystemMap. \nSelecting this button and then clicking on the Station in the SystemMap \nwill return the x,y value that can be pasted in the waypoints file",
            'Reset Waypoint List': "Reset your waypoint list, \nthe waypoint assist will start again at the first point in the list."
        }

        self.gui_loaded = False
        self.log_buffer = queue.Queue()

        self.ed_ap = EDAutopilot(cb=self.callback)
        self.ed_ap.robigo.set_single_loop(self.ed_ap.config['Robigo_Single_Loop'])

        self.mouse = MousePoint()

        self.checkboxvar = {}
        self.radiobuttonvar = {}
        self.entries = {}
        self.lab_ck = {}
        self.single_waypoint_system = StringVar()
        self.single_waypoint_station = StringVar()
        self.TCE_Destination_Filepath = StringVar()

        self.FSD_A_running = False
        self.SC_A_running = False
        self.WP_A_running = False
        self.RO_A_running = False
        self.DSS_A_running = False
        self.SWP_A_running = False

        self.cv_view = False

        self.TCE_Destination_Filepath.set(self.ed_ap.config['TCEDestinationFilepath'])

        self.msgList = self.gui_gen(root)

        self.checkboxvar['Enable Randomness'].set(self.ed_ap.config['EnableRandomness'])
        self.checkboxvar['Activate Elite for each key'].set(self.ed_ap.config['ActivateEliteEachKey'])
        self.checkboxvar['Automatic logout'].set(self.ed_ap.config['AutomaticLogout'])
        self.checkboxvar['Enable Overlay'].set(self.ed_ap.config['OverlayTextEnable'])
        self.checkboxvar['Enable Voice'].set(self.ed_ap.config['VoiceEnable'])

        self.radiobuttonvar['dss_button'].set(self.ed_ap.config['DSSButton'])

        self.entries['ship']['PitchRate'].delete(0, END)
        self.entries['ship']['RollRate'].delete(0, END)
        self.entries['ship']['YawRate'].delete(0, END)
        self.entries['ship']['SunPitchUp+Time'].delete(0, END)

        self.entries['autopilot']['Sun Bright Threshold'].delete(0, END)
        self.entries['autopilot']['Nav Align Tries'].delete(0, END)
        self.entries['autopilot']['Jump Tries'].delete(0, END)
        self.entries['autopilot']['Docking Retries'].delete(0, END)
        self.entries['autopilot']['Wait For Autodock'].delete(0, END)

        self.entries['refuel']['Refuel Threshold'].delete(0, END)
        self.entries['refuel']['Scoop Timeout'].delete(0, END)
        self.entries['refuel']['Fuel Threshold Abort'].delete(0, END)

        self.entries['overlay']['X Offset'].delete(0, END)
        self.entries['overlay']['Y Offset'].delete(0, END)
        self.entries['overlay']['Font Size'].delete(0, END)

        self.entries['buttons']['Start FSD'].delete(0, END)
        self.entries['buttons']['Start SC'].delete(0, END)
        self.entries['buttons']['Start Robigo'].delete(0, END)
        self.entries['buttons']['Stop All'].delete(0, END)

        self.entries['ship']['PitchRate'].insert(0, float(self.ed_ap.pitchrate))
        self.entries['ship']['RollRate'].insert(0, float(self.ed_ap.rollrate))
        self.entries['ship']['YawRate'].insert(0, float(self.ed_ap.yawrate))
        self.entries['ship']['SunPitchUp+Time'].insert(0, float(self.ed_ap.sunpitchuptime))

        self.entries['autopilot']['Sun Bright Threshold'].insert(0, int(self.ed_ap.config['SunBrightThreshold']))
        self.entries['autopilot']['Nav Align Tries'].insert(0, int(self.ed_ap.config['NavAlignTries']))
        self.entries['autopilot']['Jump Tries'].insert(0, int(self.ed_ap.config['JumpTries']))
        self.entries['autopilot']['Docking Retries'].insert(0, int(self.ed_ap.config['DockingRetries']))
        self.entries['autopilot']['Wait For Autodock'].insert(0, int(self.ed_ap.config['WaitForAutoDockTimer']))
        self.entries['refuel']['Refuel Threshold'].insert(0, int(self.ed_ap.config['RefuelThreshold']))
        self.entries['refuel']['Scoop Timeout'].insert(0, int(self.ed_ap.config['FuelScoopTimeOut']))
        self.entries['refuel']['Fuel Threshold Abort'].insert(0, int(self.ed_ap.config['FuelThreasholdAbortAP']))
        self.entries['overlay']['X Offset'].insert(0, int(self.ed_ap.config['OverlayTextXOffset']))
        self.entries['overlay']['Y Offset'].insert(0, int(self.ed_ap.config['OverlayTextYOffset']))
        self.entries['overlay']['Font Size'].insert(0, int(self.ed_ap.config['OverlayTextFontSize']))

        self.entries['buttons']['Start FSD'].insert(0, str(self.ed_ap.config['HotKey_StartFSD']))
        self.entries['buttons']['Start SC'].insert(0, str(self.ed_ap.config['HotKey_StartSC']))
        self.entries['buttons']['Start Robigo'].insert(0, str(self.ed_ap.config['HotKey_StartRobigo']))
        self.entries['buttons']['Stop All'].insert(0, str(self.ed_ap.config['HotKey_StopAllAssists']))

        if self.ed_ap.config['LogDEBUG']:
            self.radiobuttonvar['debug_mode'].set("Debug")
        elif self.ed_ap.config['LogINFO']:
            self.radiobuttonvar['debug_mode'].set("Info")
        else:
            self.radiobuttonvar['debug_mode'].set("Error")

        # global trap for these keys, the 'end' key will stop any current AP action
        # the 'home' key will start the FSD Assist.  May want another to start SC Assist

        keyboard.add_hotkey(self.ed_ap.config['HotKey_StopAllAssists'], self.stop_all_assists)
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartFSD'], self.callback, args=('fsd_start', None))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartSC'],  self.callback, args=('sc_start',  None))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartRobigo'],  self.callback, args=('robigo_start',  None))

        # check for updates
        self.check_updates()

        self.ed_ap.gui_loaded = True
        self.gui_loaded = True
        # Send a log entry which will flush out the buffer.
        self.callback('log', 'ED Autopilot loaded successfully.')

<<<<<<< Updated upstream
    # callback from the EDAP, to configure GUI items
=======
    def programmatic_update(self):
        """Context manager to prevent change detection during programmatic GUI updates"""
        class ProgrammaticUpdateContext:
            def __init__(self, gui):
                self.gui = gui
                
            def __enter__(self):
                self.gui._programmatic_update = True
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.gui._programmatic_update = False
                
        return ProgrammaticUpdateContext(self)

    def _create_gui(self, root):
        """Create the main GUI structure with modular components"""
        # Create menus
        self._create_menus(root)

        # Create notebook pages
        nb = ttk.Notebook(root)
        nb.grid()
        
        page_control = Frame(nb)
        page_settings = Frame(nb)
        page_waypoints = Frame(nb)
        
        nb.add(page_control, text="Control")
        nb.add(page_settings, text="Settings")
        nb.add(page_waypoints, text="Waypoints")
        
        # Store notebook reference and add tab change detection
        self.notebook = nb
        self.current_tab_index = 0
        self.switching_tabs = False
        nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Create modular panels
        self.assist_panel = AssistPanel(page_control, self.ed_ap, self.tooltips, self._check_cb)
        self.settings_panel = SettingsPanel(page_settings, self.ed_ap, self.tooltips, 
                                           self._entry_update, self._check_cb)
        self.waypoint_panel = WaypointPanel(page_waypoints, self.ed_ap, 
                                           self._entry_update, self._check_cb)

        # Connect assist panel callbacks
        self.assist_panel.set_stop_all_callback(self.stop_all_assists)

        # Create status bar
        self._create_status_bar(root)

        return self.assist_panel.msgList

    def _create_menus(self, root):
        """Create application menus"""
        menubar = Menu(root, background='#ff8000', foreground='black', 
                      activebackground='white', activeforeground='black')
        
        file = Menu(menubar, tearoff=0)
        file.add_command(label="Calibrate Target", command=self.calibrate_callback)
        file.add_command(label="Calibrate Compass", command=self.calibrate_compass_callback)
        
        # CV View checkbox
        self.cv_view_var = IntVar()
        self.cv_view_var.set(int(self.ed_ap.config['Enable_CV_View']))
        file.add_checkbutton(label='Enable CV View', onvalue=1, offvalue=0, 
                            variable=self.cv_view_var, 
                            command=lambda: self._check_cb('Enable CV View'))
        
        file.add_separator()
        file.add_command(label="Restart", command=self.restart_program)
        file.add_command(label="Exit", command=self.close_window)
        menubar.add_cascade(label="File", menu=file)

        help = Menu(menubar, tearoff=0)
        help.add_command(label="Check for Updates", command=self.check_updates)
        help.add_command(label="View Changelog", command=self.open_changelog)
        help.add_separator()
        help.add_command(label="Join Discord", command=self.open_discord)
        help.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=help)
        
        # Add dev menu if in development mode
        if self._is_dev_mode():
            self._create_dev_menu(menubar)

        root.config(menu=menubar)

    def _create_status_bar(self, root):
        """Create status bar"""
        self.statusbar = Frame(root)
        self.statusbar.grid(row=4, column=0)
        self.status = tk.Label(root, text="Status: ", bd=1, relief=tk.SUNKEN, 
                              anchor=tk.W, justify=LEFT, width=29)
        self.jumpcount = tk.Label(self.statusbar, text="<info> ", bd=1, relief=tk.SUNKEN, 
                                 anchor=tk.W, justify=LEFT, width=40)
        self.status.pack(in_=self.statusbar, side=LEFT, fill=BOTH, expand=True)
        self.jumpcount.pack(in_=self.statusbar, side=RIGHT, fill=Y, expand=False)

    def _initialize_all_components(self):
        """Initialize values in all components"""
        from EDlogger import logger
        
        # Set initialization flag to prevent change detection during initialization
        logger.debug("Setting _initializing = True")
        self._initializing = True
        
        try:
            # Initialize settings panel (ship config, autopilot settings, checkboxes, radio buttons, etc.)
            if self.settings_panel:
                logger.debug("Initializing settings panel...")
                self.settings_panel.initialize_all_values()
            
            # Initialize waypoint panel
            if self.waypoint_panel:
                logger.debug("Initializing waypoint panel...")
                self.waypoint_panel.initialize_values()
                
            # Initialize assist panel checkboxes and state
            if self.assist_panel:
                logger.debug("Initializing assist panel...")
                self._initialize_assist_panel_values()
                
        except Exception as e:
            logger.error(f"Error during component initialization: {e}")
            raise
        finally:
            # Always clear initialization flag
            logger.debug("Setting _initializing = False")
            self._initializing = False

    def _initialize_settings_panel_values(self):
        """Initialize settings panel values from configuration"""
        if not self.settings_panel:
            return
            
        # Initialize autopilot settings
        if 'autopilot' in self.settings_panel.entries:
            autopilot_entries = self.settings_panel.entries['autopilot']
            if 'Sun Bright Threshold' in autopilot_entries:
                autopilot_entries['Sun Bright Threshold'].delete(0, END)
                autopilot_entries['Sun Bright Threshold'].insert(0, str(self.ed_ap.config.get('SunBrightThreshold', 125)))
            if 'Nav Align Tries' in autopilot_entries:
                autopilot_entries['Nav Align Tries'].delete(0, END)
                autopilot_entries['Nav Align Tries'].insert(0, str(self.ed_ap.config.get('NavAlignTries', 3)))
            if 'Jump Tries' in autopilot_entries:
                autopilot_entries['Jump Tries'].delete(0, END)
                autopilot_entries['Jump Tries'].insert(0, str(self.ed_ap.config.get('JumpTries', 3)))
            if 'Docking Retries' in autopilot_entries:
                autopilot_entries['Docking Retries'].delete(0, END)
                autopilot_entries['Docking Retries'].insert(0, str(self.ed_ap.config.get('DockingRetries', 6)))
            if 'Wait For Autodock' in autopilot_entries:
                autopilot_entries['Wait For Autodock'].delete(0, END)
                autopilot_entries['Wait For Autodock'].insert(0, str(self.ed_ap.config.get('WaitForAutoDockTimer', 120)))
        
        # Initialize fuel settings
        if 'refuel' in self.settings_panel.entries:
            refuel_entries = self.settings_panel.entries['refuel']
            if 'Refuel Threshold' in refuel_entries:
                refuel_entries['Refuel Threshold'].delete(0, END)
                refuel_entries['Refuel Threshold'].insert(0, str(self.ed_ap.config.get('RefuelThreshold', 65)))
            if 'Scoop Timeout' in refuel_entries:
                refuel_entries['Scoop Timeout'].delete(0, END)
                refuel_entries['Scoop Timeout'].insert(0, str(self.ed_ap.config.get('FuelScoopTimeOut', 180)))
            if 'Fuel Threshold Abort' in refuel_entries:
                refuel_entries['Fuel Threshold Abort'].delete(0, END)
                refuel_entries['Fuel Threshold Abort'].insert(0, str(self.ed_ap.config.get('FuelThresholdAbort', 10)))
        
        # Initialize overlay settings
        if 'overlay' in self.settings_panel.entries:
            overlay_entries = self.settings_panel.entries['overlay']
            if 'X Offset' in overlay_entries:
                overlay_entries['X Offset'].delete(0, END)
                overlay_entries['X Offset'].insert(0, str(self.ed_ap.config.get('OverlayTextXoffset', 100)))
            if 'Y Offset' in overlay_entries:
                overlay_entries['Y Offset'].delete(0, END)
                overlay_entries['Y Offset'].insert(0, str(self.ed_ap.config.get('OverlayTextYoffset', 100)))
            if 'Font Size' in overlay_entries:
                overlay_entries['Font Size'].delete(0, END)
                overlay_entries['Font Size'].insert(0, str(self.ed_ap.config.get('OverlayTextFontSize', 14)))
        
        # Initialize checkboxes
        if hasattr(self.settings_panel, 'checkboxvar'):
            checkboxes = {
                'Enable Randomness': self.ed_ap.config.get('EnableRandomness', False),
                'Activate Elite for each key': self.ed_ap.config.get('EliteKeySequenceRepeat', False),
                'Automatic logout': self.ed_ap.config.get('Auto_Logout', False),
                'Enable Overlay': self.ed_ap.config.get('Enable_Overlay', False),
                'Enable Voice': self.ed_ap.config.get('Enable_Voice', True),
                'ELW Scanner': self.ed_ap.config.get('EnableElwScannerSearch', False),
            }
            
            for field, value in checkboxes.items():
                if field in self.settings_panel.checkboxvar:
                    self.settings_panel.checkboxvar[field].set(bool(value))
        
        # Initialize radio buttons
        if hasattr(self.settings_panel, 'radiobuttonvar'):
            if 'dss_button' in self.settings_panel.radiobuttonvar:
                dss_button_value = self.ed_ap.config.get('DSSButton', 'Primary')
                self.settings_panel.radiobuttonvar['dss_button'].set(dss_button_value)
            
            if 'debug_mode' in self.settings_panel.radiobuttonvar:
                # Determine debug level from current log level
                debug_level = "Info"  # default
                if hasattr(self.ed_ap, 'logger_level'):
                    level = self.ed_ap.logger_level
                    if level == 'ERROR':
                        debug_level = "Error"
                    elif level == 'DEBUG':
                        debug_level = "Debug"
                    elif level == 'INFO':
                        debug_level = "Info"
                self.settings_panel.radiobuttonvar['debug_mode'].set(debug_level)
        
        # Initialize hotkey buttons
        if 'buttons' in self.settings_panel.entries:
            button_entries = self.settings_panel.entries['buttons']
            hotkey_mappings = {
                'Start FSD': self.ed_ap.config.get('HotKey_StartFSD', 'home'),
                'Start SC': self.ed_ap.config.get('HotKey_StartSC', 'insert'),
                'Start Robigo': self.ed_ap.config.get('HotKey_StartRobigo', 'page up'),
                'Start Waypoint': self.ed_ap.config.get('HotKey_StartWaypoint', 'f12'),
                'Stop All': self.ed_ap.config.get('HotKey_StopAllAssists', 'end'),
                'Pause/Resume': self.ed_ap.config.get('HotKey_PauseResume', '')
            }
            
            for field, hotkey in hotkey_mappings.items():
                if field in button_entries and hotkey:
                    button_entries[field].config(text=hotkey)
                elif field in button_entries:
                    button_entries[field].config(text="Click to set...")

    def _initialize_assist_panel_values(self):
        """Initialize assist panel values and state"""
        if not self.assist_panel:
            return
            
        # Initialize all assist checkboxes to unchecked state
        assist_modes = ['FSD Route Assist (INS)', 'Supercruise Assist (HOME)', 'Waypoint Assist (DEL)', 
                      'Robigo Assist (PG UP)', 'AFK Combat Assist', 'DSS Assist']
        
        for mode in assist_modes:
            if mode in self.assist_panel.checkboxvar:
                self.assist_panel.checkboxvar[mode].set(0)
        
        # Reset all assist running states
        self.assist_panel.FSD_A_running = False
        self.assist_panel.SC_A_running = False
        self.assist_panel.WP_A_running = False
        self.assist_panel.RO_A_running = False
        self.assist_panel.DSS_A_running = False
        self.assist_panel.SWP_A_running = False
        
        # Reset pause system
        self.assist_panel.all_paused = False
        self.assist_panel.paused_assists = []
        self.assist_panel.btn_pause.config(state='normal', bg='orange')
        self.assist_panel.btn_resume.config(state='disabled', bg='gray')

    def _setup_config_management(self):
        """Set up configuration management with GUI elements"""
        gui_elements = {
            'settings_panel': self.settings_panel,
            'assist_panel': self.assist_panel,
            'waypoint_panel': self.waypoint_panel,
            'save_button': self.settings_panel.save_button if self.settings_panel else None,
            'revert_button': self.settings_panel.revert_button if self.settings_panel else None
        }
        self.config_manager.set_gui_elements(gui_elements)
        self.config_manager.set_programmatic_update_context(self.programmatic_update)
        
        # Inject dependencies into settings panel
        if self.settings_panel:
            self.settings_panel.set_config_manager(self.config_manager)
            self.settings_panel.set_hotkey_capture_callback(self._capture_hotkey)
            self.settings_panel.set_button_commands(
                self.config_manager.save_settings,
                self.config_manager.revert_all_changes
            )

    def _setup_hotkeys(self):
        from EDlogger import logger
        # Set up global hotkeys with focus checking
        logger.info(f"Registering hotkeys: Stop={self.ed_ap.config['HotKey_StopAllAssists']}, FSD={self.ed_ap.config['HotKey_StartFSD']}, SC={self.ed_ap.config['HotKey_StartSC']}")
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StopAllAssists'], self._focused_hotkey_wrapper, args=(self.stop_all_assists,))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartFSD'], self._focused_hotkey_wrapper, args=(self.callback, 'fsd_start', None))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartSC'], self._focused_hotkey_wrapper, args=(self.callback, 'sc_start', None))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartRobigo'], self._focused_hotkey_wrapper, args=(self.callback, 'robigo_start', None))
        keyboard.add_hotkey(self.ed_ap.config['HotKey_StartWaypoint'], self._focused_hotkey_wrapper, args=(self.callback, 'waypoint_start', None))
        
        # Only register pause hotkey if it's not empty
        pause_hotkey = self.ed_ap.config.get('HotKey_PauseResume', '').strip()
        if pause_hotkey:
            try:
                keyboard.add_hotkey(pause_hotkey, self._focused_hotkey_wrapper, args=(self._toggle_pause_all,))
            except ValueError as e:
                logger.warning(f"Invalid pause hotkey '{pause_hotkey}': {e}. Pause hotkey disabled.")
        else:
            logger.info("No pause hotkey configured. Pause function available only via GUI buttons.")
    
    def _focused_hotkey_wrapper(self, callback_func, *args):
        """Wrapper that only executes hotkey callbacks when Elite or EDAPGui has focus"""
        from EDlogger import logger
        
        if is_elite_or_edapgui_focused():
            logger.debug(f"Hotkey triggered: {callback_func.__name__} (focus check passed)")
            callback_func(*args)
        else:
            logger.debug(f"Hotkey blocked: {callback_func.__name__} (focus check failed)")
            # Silently ignore hotkeys when other applications have focus

    # Callback from the EDAP, to configure GUI items
>>>>>>> Stashed changes
    def callback(self, msg, body=None):
        if msg == 'log':
            self.log_msg(body)
        elif msg == 'log+vce':
            self.log_msg(body)
            self.ed_ap.vce.say(body)
        elif msg == 'statusline':
            self.update_statusline(body)
        elif msg == 'fsd_stop':
            logger.debug("Detected 'fsd_stop' callback msg")
<<<<<<< Updated upstream
            self.checkboxvar['FSD Route Assist'].set(0)
            self.check_cb('FSD Route Assist')
        elif msg == 'fsd_start':
            self.checkboxvar['FSD Route Assist'].set(1)
            self.check_cb('FSD Route Assist')
        elif msg == 'sc_stop':
            logger.debug("Detected 'sc_stop' callback msg")
            self.checkboxvar['Supercruise Assist'].set(0)
            self.check_cb('Supercruise Assist')
        elif msg == 'sc_start':
            self.checkboxvar['Supercruise Assist'].set(1)
            self.check_cb('Supercruise Assist')
        elif msg == 'waypoint_stop':
            logger.debug("Detected 'waypoint_stop' callback msg")
            self.checkboxvar['Waypoint Assist'].set(0)
            self.check_cb('Waypoint Assist')
        elif msg == 'waypoint_start':
            self.checkboxvar['Waypoint Assist'].set(1)
            self.check_cb('Waypoint Assist')
        elif msg == 'robigo_stop':
            logger.debug("Detected 'robigo_stop' callback msg")
            self.checkboxvar['Robigo Assist'].set(0)
            self.check_cb('Robigo Assist')
        elif msg == 'robigo_start':
            self.checkboxvar['Robigo Assist'].set(1)
            self.check_cb('Robigo Assist')
=======
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('FSD Route Assist (INS)', 0)
                self._check_cb('FSD Route Assist (INS)')
        elif msg == 'fsd_start':
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('FSD Route Assist (INS)', 1)
                self._check_cb('FSD Route Assist (INS)')
        elif msg == 'sc_stop':
            logger.debug("Detected 'sc_stop' callback msg")
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Supercruise Assist (HOME)', 0)
                self._check_cb('Supercruise Assist (HOME)')
        elif msg == 'sc_start':
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Supercruise Assist (HOME)', 1)
                self._check_cb('Supercruise Assist (HOME)')
        elif msg == 'waypoint_stop':
            logger.debug("Detected 'waypoint_stop' callback msg")
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Waypoint Assist (DEL)', 0)
                self._check_cb('Waypoint Assist (DEL)')
        elif msg == 'waypoint_start':
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Waypoint Assist (DEL)', 1)
                self._check_cb('Waypoint Assist (DEL)')
        elif msg == 'robigo_stop':
            logger.debug("Detected 'robigo_stop' callback msg")
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Robigo Assist (PG UP)', 0)
                self._check_cb('Robigo Assist (PG UP)')
        elif msg == 'robigo_start':
            if self.assist_panel:
                self.assist_panel.set_checkbox_state('Robigo Assist (PG UP)', 1)
                self._check_cb('Robigo Assist (PG UP)')
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        elif msg == 'afk_stop':
            logger.debug("Detected 'afk_stop' callback msg")
            self.checkboxvar['AFK Combat Assist'].set(0)
            self.check_cb('AFK Combat Assist')
        elif msg == 'dss_start':
            logger.debug("Detected 'dss_start' callback msg")
            self.checkboxvar['DSS Assist'].set(1)
            self.check_cb('DSS Assist')
        elif msg == 'dss_stop':
            logger.debug("Detected 'dss_stop' callback msg")
            self.checkboxvar['DSS Assist'].set(0)
            self.check_cb('DSS Assist')
        elif msg == 'single_waypoint_stop':
            logger.debug("Detected 'single_waypoint_stop' callback msg")
            self.checkboxvar['Single Waypoint Assist'].set(0)
            self.check_cb('Single Waypoint Assist')

        elif msg == 'stop_all_assists':
            logger.debug("Detected 'stop_all_assists' callback msg")
<<<<<<< Updated upstream

            self.checkboxvar['FSD Route Assist'].set(0)
            self.check_cb('FSD Route Assist')

            self.checkboxvar['Supercruise Assist'].set(0)
            self.check_cb('Supercruise Assist')

            self.checkboxvar['Waypoint Assist'].set(0)
            self.check_cb('Waypoint Assist')

            self.checkboxvar['Robigo Assist'].set(0)
            self.check_cb('Robigo Assist')

            self.checkboxvar['AFK Combat Assist'].set(0)
            self.check_cb('AFK Combat Assist')

            self.checkboxvar['DSS Assist'].set(0)
            self.check_cb('DSS Assist')

            self.checkboxvar['Single Waypoint Assist'].set(0)
            self.check_cb('Single Waypoint Assist')

=======
            # Stop all assists in assist panel
            if self.assist_panel:
                for assist in ['FSD Route Assist (INS)', 'Supercruise Assist (HOME)', 'Waypoint Assist (DEL)', 
                              'Robigo Assist (PG UP)', 'AFK Combat Assist', 'DSS Assist']:
                    self.assist_panel.set_checkbox_state(assist, 0)
                    self._check_cb(assist)
            # Stop single waypoint assist
            if self.waypoint_panel:
                self.waypoint_panel.set_checkbox_state('Single Waypoint Assist', 0)
                self._check_cb('Single Waypoint Assist')
>>>>>>> Stashed changes
        elif msg == 'jumpcount':
            self.update_jumpcount(body)
        elif msg == 'update_ship_cfg':
            self.update_ship_cfg()

    def update_ship_cfg(self):
        # load up the display with what we read from ED_AP for the current ship
        self.entries['ship']['PitchRate'].delete(0, END)
        self.entries['ship']['RollRate'].delete(0, END)
        self.entries['ship']['YawRate'].delete(0, END)
        self.entries['ship']['SunPitchUp+Time'].delete(0, END)

        self.entries['ship']['PitchRate'].insert(0, self.ed_ap.pitchrate)
        self.entries['ship']['RollRate'].insert(0, self.ed_ap.rollrate)
        self.entries['ship']['YawRate'].insert(0, self.ed_ap.yawrate)
        self.entries['ship']['SunPitchUp+Time'].insert(0, self.ed_ap.sunpitchuptime)

    def calibrate_callback(self):
        self.ed_ap.calibrate()

    def calibrate_compass_callback(self):
        self.ed_ap.calibrate_compass()

    def quit(self):
        logger.debug("Entered: quit")
        self.close_window()

    def close_window(self):
        logger.debug("Entered: close_window")
        self.stop_fsd()
        self.stop_sc()
        self.ed_ap.quit()
        sleep(0.1)
        self.root.destroy()

<<<<<<< Updated upstream
    # this routine is to stop any current autopilot activity
=======
    def _capture_hotkey(self, field_name):
        """Capture a hotkey by listening for the next key press"""
        if not self.settings_panel or 'buttons' not in self.settings_panel.entries:
            return
            
        button = self.settings_panel.entries['buttons'][field_name]
        
        # Change button appearance to show it's waiting for input
        original_text = button.cget('text')
        original_bg = button.cget('bg')
        button.config(text="Press any key...", bg='yellow')
        self.root.update()
        
        # Variables to store the captured key
        captured_key: dict[str, str | None] = {'key': None}
        
        def on_key_press(event):
            """Handle key press during capture"""
            from EDlogger import logger
            
            # Build list of modifiers and main key
            modifiers = []
            
            # Check for modifier keys (skip Alt since it's unreliable on some systems)
            if event.state & 0x4:  # Control key
                modifiers.append('ctrl')
            # Skip Alt key detection - it's often falsely detected on Windows
            # if event.state & 0x8:  # Alt key  
            #     modifiers.append('alt')
            if event.state & 0x1:  # Shift key
                modifiers.append('shift')
            if event.state & 0x40:  # Windows/Super key
                modifiers.append('win')
            
            # Convert tkinter key names to keyboard library format
            key_name = event.keysym.lower()
            
            # Handle special keys
            key_mapping = {
                'return': 'enter', 'prior': 'page up', 'next': 'page down',
                'delete': 'del', 'insert': 'ins', 'escape': 'esc',
                'control_l': 'ctrl', 'control_r': 'ctrl',
                'alt_l': 'alt', 'alt_r': 'alt',
                'shift_l': 'shift', 'shift_r': 'shift',
                'super_l': 'win', 'super_r': 'win',
                'space': 'space', 'tab': 'tab', 'backspace': 'backspace',
                'pause': 'pause', 'scroll_lock': 'scroll lock',
                'num_lock': 'num lock', 'caps_lock': 'caps lock',
                'print': 'print screen', 'menu': 'menu'
            }
            
            # Handle function keys
            if key_name.startswith('f') and key_name[1:].isdigit():
                key_name = key_name  # f1, f2, etc. are already correct
            elif key_name in key_mapping:
                key_name = key_mapping[key_name]
            
            # Skip if the pressed key is only a modifier key
            if key_name in ['ctrl', 'alt', 'shift', 'win']:
                return  # Don't capture, wait for a real key
            
            # Build final hotkey string
            if modifiers and len(modifiers) > 0:
                modifiers = sorted(list(set(modifiers)))
                hotkey_string = '+'.join(modifiers) + '+' + key_name
            else:
                hotkey_string = key_name
            
            captured_key['key'] = hotkey_string
            
            # Stop capturing
            self.root.unbind('<KeyPress>')
            self.root.focus_set()
            
            # Update button with captured key
            button.config(text=hotkey_string, bg=original_bg)
            
            # Mark that changes need to be saved
            self.config_manager.mark_unsaved_changes()
            
            logger.info(f"Captured hotkey '{hotkey_string}' for {field_name}")
            
        # Start capturing
        self.root.bind('<KeyPress>', on_key_press)
        self.root.focus_set()
        
        # Add a cancel option with right-click
        def on_right_click(event):
            self.root.unbind('<KeyPress>')
            self.root.unbind('<Button-3>')
            button.config(text=original_text, bg=original_bg)
            logger.info(f"Hotkey capture cancelled for {field_name}")
            
        self.root.bind('<Button-3>', on_right_click)

    def _on_tab_changed(self, event):
        """Handle tab change - check for unsaved changes when leaving Settings tab"""
        if self.switching_tabs:
            return
            
        notebook = event.widget
        new_tab_index = notebook.index(notebook.select())
        new_tab_name = notebook.tab(new_tab_index, "text")
        old_tab_name = notebook.tab(self.current_tab_index, "text") if self.current_tab_index < len(notebook.tabs()) else ""
        
        # Only check for unsaved changes when leaving the Settings tab
        if (self.config_manager.has_unsaved_changes and 
            old_tab_name == "Settings" and 
            new_tab_name != "Settings" and 
            new_tab_index != self.current_tab_index):
            
            self.switching_tabs = True
            
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                f"You have unsaved settings changes.\n\nDo you want to save them before switching to the {new_tab_name} tab?",
                icon="question"
            )
            
            if result is True:  # Yes - save and continue
                self.config_manager.save_settings()
            elif result is False:  # No - discard changes and continue
                self.config_manager.clear_unsaved_changes()
            else:  # Cancel - go back to Settings tab
                self.notebook.select(self.current_tab_index)
                self.switching_tabs = False
                return
                
            self.switching_tabs = False
        
        # Update current tab tracking
        self.current_tab_index = new_tab_index

>>>>>>> Stashed changes
    def stop_all_assists(self):
        logger.debug("Entered: stop_all_assists")
        self.callback('stop_all_assists')

<<<<<<< Updated upstream
=======
    def _toggle_pause_all(self):
        """Toggle pause/resume all running assists"""
        from EDlogger import logger
        logger.info("Pause/Resume hotkey pressed")
        if self.assist_panel:
            self.assist_panel._toggle_pause_all()
        else:
            logger.warning("Assist panel not available for pause/resume")

    def _entry_update(self, event=None, mark_changes=True):
        """Handle entry field updates - only trigger on meaningful changes"""
        from EDlogger import logger
        
        logger.debug(f"_entry_update called: event={event}, mark_changes={mark_changes}")
        logger.debug(f"  Guard checks: _saving_settings={getattr(self, '_saving_settings', False)}, "
                    f"_initializing={getattr(self, '_initializing', False)}, "
                    f"_reverting_changes={getattr(self, '_reverting_changes', False)}, "
                    f"_programmatic_update={self._programmatic_update}")
        
        if (mark_changes and event is not None and 
            not getattr(self, '_saving_settings', False) and 
            not getattr(self, '_initializing', False) and
            not getattr(self, '_reverting_changes', False) and
            not self._programmatic_update):
            
            logger.debug("  Guards passed, checking for changes...")
            has_changes = self.config_manager.has_actual_changes()
            logger.debug(f"  has_actual_changes() returned: {has_changes}")
            
            if has_changes:
                if not self.config_manager.has_unsaved_changes:
                    logger.debug("  Marking unsaved changes")
                    self.config_manager.mark_unsaved_changes()
                else:
                    logger.debug("  Already marked as unsaved")
            else:
                # Only clear if we previously had unsaved changes
                if self.config_manager.has_unsaved_changes:
                    logger.debug("  Clearing unsaved changes")
                    self.config_manager.clear_unsaved_changes()
                else:
                    logger.debug("  No changes detected, no action needed")
        else:
            logger.debug("  Guards failed, skipping change detection")

    def _check_cb(self, field):
        """Handle checkbox and radio button changes"""
        # Handle assist mode checkboxes
        if field in ['FSD Route Assist (INS)', 'Supercruise Assist (HOME)', 'Waypoint Assist (DEL)', 
                    'Robigo Assist (PG UP)', 'AFK Combat Assist', 'DSS Assist']:
            self._handle_assist_checkbox(field)
        
        # Handle Single Waypoint Assist
        elif field == 'Single Waypoint Assist':
            self._handle_single_waypoint_assist()
        
        # Handle CV View
        elif field == 'Enable CV View':
            self._handle_cv_view()
        
        # Handle settings checkboxes and radio buttons
        else:
            self._handle_settings_controls(field)
        
        # Mark unsaved changes for setting controls
        setting_fields = ['Enable Randomness', 'Activate Elite for each key', 'Automatic logout', 
                         'Enable Overlay', 'Enable Voice', 'ELW Scanner', 'debug_mode', 'dss_button']
        if (field in setting_fields and 
            not hasattr(self, '_initializing') and 
            not hasattr(self, '_saving_settings') and
            not hasattr(self, '_reverting_changes')):
            
            if self.config_manager.has_actual_changes():
                if not self.config_manager.has_unsaved_changes:
                    self.config_manager.mark_unsaved_changes()
            else:
                if self.config_manager.has_unsaved_changes:
                    self.config_manager.clear_unsaved_changes()

    def _handle_assist_checkbox(self, field):
        """Handle assist mode checkbox changes"""
        if not self.assist_panel:
            return
            
        checkbox_state = self.assist_panel.get_checkbox_state(field)
        
        if field == 'FSD Route Assist (INS)':
            if checkbox_state == 1 and not self.assist_panel.FSD_A_running:
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
                self.start_fsd()
            elif checkbox_state == 0 and self.assist_panel.FSD_A_running:
                self.stop_fsd()
                self.assist_panel.enable_disable_checkboxes(field, 'active')
        
        elif field == 'Supercruise Assist (HOME)':
            if checkbox_state == 1 and not self.assist_panel.SC_A_running:
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
                self.start_sc()
            elif checkbox_state == 0 and self.assist_panel.SC_A_running:
                self.stop_sc()
                self.assist_panel.enable_disable_checkboxes(field, 'active')
        
        elif field == 'Waypoint Assist (DEL)':
            if checkbox_state == 1 and not self.assist_panel.WP_A_running:
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
                self.start_waypoint()
            elif checkbox_state == 0 and self.assist_panel.WP_A_running:
                self.stop_waypoint()
                self.assist_panel.enable_disable_checkboxes(field, 'active')
        
        elif field == 'Robigo Assist (PG UP)':
            if checkbox_state == 1 and not self.assist_panel.RO_A_running:
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
                self.start_robigo()
            elif checkbox_state == 0 and self.assist_panel.RO_A_running:
                self.stop_robigo()
                self.assist_panel.enable_disable_checkboxes(field, 'active')
        
        elif field == 'AFK Combat Assist':
            if checkbox_state == 1:
                self.ed_ap.set_afk_combat_assist(True)
                self.log_msg("AFK Combat Assist start")
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
            elif checkbox_state == 0:
                self.ed_ap.set_afk_combat_assist(False)
                self.log_msg("AFK Combat Assist stop")
                self.assist_panel.enable_disable_checkboxes(field, 'active')
        
        elif field == 'DSS Assist':
            if checkbox_state == 1:
                self.assist_panel.enable_disable_checkboxes(field, 'disabled')
                self.start_dss()
            elif checkbox_state == 0:
                self.stop_dss()
                self.assist_panel.enable_disable_checkboxes(field, 'active')

    def _handle_single_waypoint_assist(self):
        """Handle single waypoint assist checkbox"""
        if not self.waypoint_panel:
            return
            
        checkbox_state = self.waypoint_panel.get_checkbox_state('Single Waypoint Assist')
        if checkbox_state == 1 and self.assist_panel and not self.assist_panel.SWP_A_running:
            self.start_single_waypoint_assist()
        elif checkbox_state == 0 and self.assist_panel and self.assist_panel.SWP_A_running:
            self.stop_single_waypoint_assist()

    def _handle_cv_view(self):
        """Handle CV View checkbox"""
        if self.cv_view_var.get() == 1:
            self.cv_view = True
            x = self.root.winfo_x() + self.root.winfo_width() + 4
            y = self.root.winfo_y()
            self.ed_ap.set_cv_view(True, x, y)
        else:
            self.cv_view = False
            self.ed_ap.set_cv_view(False)

    def _handle_settings_controls(self, field):
        """Handle settings checkboxes and radio buttons"""
        if not self.settings_panel:
            return
            
        # Handle checkboxes
        if field in self.settings_panel.checkboxvar:
            checkbox_value = self.settings_panel.checkboxvar[field].get()
            
            if field == 'Enable Randomness':
                self.ed_ap.set_randomness(checkbox_value)
            elif field == 'Activate Elite for each key':
                self.ed_ap.set_activate_elite_eachkey(checkbox_value)
                self.ed_ap.keys.activate_window = checkbox_value
            elif field == 'Automatic logout':
                self.ed_ap.set_automatic_logout(checkbox_value)
            elif field == 'Enable Overlay':
                self.ed_ap.set_overlay(checkbox_value)
            elif field == 'Enable Voice':
                self.ed_ap.set_voice(checkbox_value)
            elif field == 'ELW Scanner':
                self.ed_ap.set_fss_scan(checkbox_value)
        
        # Handle radio buttons
        if field in self.settings_panel.radiobuttonvar:
            radio_value = self.settings_panel.radiobuttonvar[field].get()
            
            if field == 'dss_button':
                self.ed_ap.config['DSSButton'] = radio_value
            elif field == 'debug_mode':
                if radio_value == "Error":
                    self.ed_ap.set_log_error(True)
                elif radio_value == "Debug":
                    self.ed_ap.set_log_debug(True)
                elif radio_value == "Info":
                    self.ed_ap.set_log_info(True)

    # Assist control methods
>>>>>>> Stashed changes
    def start_fsd(self):
        logger.debug("Entered: start_fsd")
        self.ed_ap.set_fsd_assist(True)
        self.FSD_A_running = True
        self.log_msg("FSD Route Assist start")
        self.ed_ap.vce.say("FSD Route Assist On")

    def stop_fsd(self):
        logger.debug("Entered: stop_fsd")
        self.ed_ap.set_fsd_assist(False)
        self.FSD_A_running = False
        self.log_msg("FSD Route Assist stop")
        self.ed_ap.vce.say("FSD Route Assist Off")
        self.update_statusline("Idle")

    def start_sc(self):
        logger.debug("Entered: start_sc")
        self.ed_ap.set_sc_assist(True)
        self.SC_A_running = True
        self.log_msg("SC Assist start")
        self.ed_ap.vce.say("Supercruise Assist On")

    def stop_sc(self):
        logger.debug("Entered: stop_sc")
        self.ed_ap.set_sc_assist(False)
        self.SC_A_running = False
        self.log_msg("SC Assist stop")
        self.ed_ap.vce.say("Supercruise Assist Off")
        self.update_statusline("Idle")

    def start_waypoint(self):
        logger.debug("Entered: start_waypoint")
        self.ed_ap.set_waypoint_assist(True)
        self.WP_A_running = True
        self.log_msg("Waypoint Assist start")
        self.ed_ap.vce.say("Waypoint Assist On")

    def stop_waypoint(self):
        logger.debug("Entered: stop_waypoint")
        self.ed_ap.set_waypoint_assist(False)
        self.WP_A_running = False
        self.log_msg("Waypoint Assist stop")
        self.ed_ap.vce.say("Waypoint Assist Off")
        self.update_statusline("Idle")

    def start_robigo(self):
        logger.debug("Entered: start_robigo")
        self.ed_ap.set_robigo_assist(True)
        self.RO_A_running = True
        self.log_msg("Robigo Assist start")
        self.ed_ap.vce.say("Robigo Assist On")

    def stop_robigo(self):
        logger.debug("Entered: stop_robigo")
        self.ed_ap.set_robigo_assist(False)
        self.RO_A_running = False
        self.log_msg("Robigo Assist stop")
        self.ed_ap.vce.say("Robigo Assist Off")
        self.update_statusline("Idle")

    def start_dss(self):
        logger.debug("Entered: start_dss")
        self.ed_ap.set_dss_assist(True)
        self.DSS_A_running = True
        self.log_msg("DSS Assist start")
        self.ed_ap.vce.say("DSS Assist On")

    def stop_dss(self):
        logger.debug("Entered: stop_dss")
        self.ed_ap.set_dss_assist(False)
        self.DSS_A_running = False
        self.log_msg("DSS Assist stop")
        self.ed_ap.vce.say("DSS Assist Off")
        self.update_statusline("Idle")

    def start_single_waypoint_assist(self):
        """ The debug command to go to a system or station or both."""
        logger.debug("Entered: start_single_waypoint_assist")
        system = self.single_waypoint_system.get()
        station = self.single_waypoint_station.get()

        if system != "" or station != "":
            self.ed_ap.set_single_waypoint_assist(system, station, True)
            self.SWP_A_running = True
            self.log_msg("Single Waypoint Assist start")
            self.ed_ap.vce.say("Single Waypoint Assist On")

    def stop_single_waypoint_assist(self):
        """ The debug command to go to a system or station or both."""
        logger.debug("Entered: stop_single_waypoint_assist")
        self.ed_ap.set_single_waypoint_assist("", "", False)
        self.SWP_A_running = False
        self.log_msg("Single Waypoint Assist stop")
        self.ed_ap.vce.say("Single Waypoint Assist Off")
        self.update_statusline("Idle")

    def about(self):
        webbrowser.open_new("https://github.com/SumZer0-git/EDAPGui")

    def check_updates(self):
        # response = requests.get("https://api.github.com/repos/SumZer0-git/EDAPGui/releases/latest")
        # if EDAP_VERSION != response.json()["name"]:
        #     mb = messagebox.askokcancel("Update Check", "A new release version is available. Download now?")
        #     if mb == True:
        #         webbrowser.open_new("https://github.com/SumZer0-git/EDAPGui/releases/latest")
        pass

    def open_changelog(self):
        webbrowser.open_new("https://github.com/SumZer0-git/EDAPGui/blob/main/ChangeLog.md")

    def open_discord(self):
        webbrowser.open_new("https://discord.gg/HCgkfSc")

    def open_logfile(self):
        os.startfile('autopilot.log')

    def log_msg(self, msg):
        message = datetime.now().strftime("%H:%M:%S: ") + msg

        if not self.gui_loaded:
            # Store message in queue
            self.log_buffer.put(message)
            logger.info(msg)
        else:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            # Add queued messages to the list
            while not self.log_buffer.empty():
                self.msgList.insert(END, self.log_buffer.get())
=======
            try:
                while not self.log_buffer.empty():
                    self.msgList.insert(END, self.log_buffer.get())
>>>>>>> Stashed changes
=======
            try:
                while not self.log_buffer.empty():
                    self.msgList.insert(END, self.log_buffer.get())
>>>>>>> Stashed changes

                self.msgList.insert(END, message)
                self.msgList.yview(END)
            except tk.TclError:
                # msgList widget was destroyed, skip GUI update
                pass
            logger.info(msg)

    def set_statusbar(self, txt):
        self.statusbar.configure(text=txt)

    def update_jumpcount(self, txt):
        self.jumpcount.configure(text=txt)

    def update_statusline(self, txt):
        self.status.configure(text="Status: " + txt)
        self.log_msg(f"Status update: {txt}")

    def ship_tst_pitch(self):
        self.ed_ap.ship_tst_pitch()

    def ship_tst_roll(self):
        self.ed_ap.ship_tst_roll()

    def ship_tst_yaw(self):
        self.ed_ap.ship_tst_yaw()

    def open_ship_file(self, filename=None):
        # if a filename was not provided, then prompt user for one
        if not filename:
            filetypes = (
                ('json files', '*.json'),
                ('All files', '*.*')
            )

            filename = fd.askopenfilename(
                title='Open a file',
                initialdir='./ships/',
                filetypes=filetypes)

        if not filename:
            return

        with open(filename, 'r') as json_file:
            f_details = json.load(json_file)

        # load up the display with what we read, the pass it along to AP
        self.entries['ship']['PitchRate'].delete(0, END)
        self.entries['ship']['RollRate'].delete(0, END)
        self.entries['ship']['YawRate'].delete(0, END)
        self.entries['ship']['SunPitchUp+Time'].delete(0, END)

        self.entries['ship']['PitchRate'].insert(0, f_details['pitchrate'])
        self.entries['ship']['RollRate'].insert(0, f_details['rollrate'])
        self.entries['ship']['YawRate'].insert(0, f_details['yawrate'])
        self.entries['ship']['SunPitchUp+Time'].insert(0, f_details['SunPitchUp+Time'])

        self.ed_ap.rollrate = float(f_details['rollrate'])
        self.ed_ap.pitchrate = float(f_details['pitchrate'])
        self.ed_ap.yawrate = float(f_details['yawrate'])
        self.ed_ap.sunpitchuptime = float(f_details['SunPitchUp+Time'])

        self.ship_filelabel.set("loaded: " + Path(filename).name)
        self.ed_ap.update_config()

    def open_wp_file(self):
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title="Waypoint File", initialdir='./waypoints/', filetypes=filetypes)
        if filename != "":
            res = self.ed_ap.waypoint.load_waypoint_file(filename)
            if res:
                self.wp_filelabel.set("loaded: " + Path(filename).name)
            else:
                self.wp_filelabel.set("<no list loaded>")

    def reset_wp_file(self):
        if self.WP_A_running != True:
            mb = messagebox.askokcancel("Waypoint List Reset", "After resetting the Waypoint List, the Waypoint Assist will start again from the first point in the list at the next start.")
            if mb == True:
                self.ed_ap.waypoint.mark_all_waypoints_not_complete()
        else:
            mb = messagebox.showerror("Waypoint List Error", "Waypoint Assist must be disabled before you can reset the list.")

    def save_settings(self):
        self.entry_update()
        self.ed_ap.update_config()
        self.ed_ap.update_ship_configs()

    def load_tce_dest(self):
        filename = self.ed_ap.config['TCEDestinationFilepath']
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                f_details = json.load(json_file)

            self.single_waypoint_system.set(f_details['StarSystem'])
            self.single_waypoint_station.set(f_details['Station'])

    # new data was added to a field, re-read them all for simple logic
    def entry_update(self, event=''):
        try:
            self.ed_ap.pitchrate = float(self.entries['ship']['PitchRate'].get())
            self.ed_ap.rollrate = float(self.entries['ship']['RollRate'].get())
            self.ed_ap.yawrate = float(self.entries['ship']['YawRate'].get())
            self.ed_ap.sunpitchuptime = float(self.entries['ship']['SunPitchUp+Time'].get())

            self.ed_ap.config['SunBrightThreshold'] = int(self.entries['autopilot']['Sun Bright Threshold'].get())
            self.ed_ap.config['NavAlignTries'] = int(self.entries['autopilot']['Nav Align Tries'].get())
            self.ed_ap.config['JumpTries'] = int(self.entries['autopilot']['Jump Tries'].get())
            self.ed_ap.config['DockingRetries'] = int(self.entries['autopilot']['Docking Retries'].get())
            self.ed_ap.config['WaitForAutoDockTimer'] = int(self.entries['autopilot']['Wait For Autodock'].get())
            self.ed_ap.config['RefuelThreshold'] = int(self.entries['refuel']['Refuel Threshold'].get())
            self.ed_ap.config['FuelScoopTimeOut'] = int(self.entries['refuel']['Scoop Timeout'].get())
            self.ed_ap.config['FuelThreasholdAbortAP'] = int(self.entries['refuel']['Fuel Threshold Abort'].get())
            self.ed_ap.config['OverlayTextXOffset'] = int(self.entries['overlay']['X Offset'].get())
            self.ed_ap.config['OverlayTextYOffset'] = int(self.entries['overlay']['Y Offset'].get())
            self.ed_ap.config['OverlayTextFontSize'] = int(self.entries['overlay']['Font Size'].get())
            self.ed_ap.config['HotKey_StartFSD'] = str(self.entries['buttons']['Start FSD'].get())
            self.ed_ap.config['HotKey_StartSC'] = str(self.entries['buttons']['Start SC'].get())
            self.ed_ap.config['HotKey_StartRobigo'] = str(self.entries['buttons']['Start Robigo'].get())
            self.ed_ap.config['HotKey_StopAllAssists'] = str(self.entries['buttons']['Stop All'].get())
            self.ed_ap.config['VoiceEnable'] = self.checkboxvar['Enable Voice'].get()
            self.ed_ap.config['TCEDestinationFilepath'] = str(self.TCE_Destination_Filepath.get())
        except:
            messagebox.showinfo("Exception", "Invalid float entered")

    # ckbox.state:(ACTIVE | DISABLED)

    # ('FSD Route Assist', 'Supercruise Assist', 'Enable Voice', 'Enable CV View')
    def check_cb(self, field):
        # print("got event:",  checkboxvar['FSD Route Assist'].get(), " ", str(FSD_A_running))
        if field == 'FSD Route Assist':
            if self.checkboxvar['FSD Route Assist'].get() == 1 and self.FSD_A_running == False:
                self.lab_ck['AFK Combat Assist'].config(state='disabled')
                self.lab_ck['Supercruise Assist'].config(state='disabled')
                self.lab_ck['Waypoint Assist'].config(state='disabled')
                self.lab_ck['Robigo Assist'].config(state='disabled')
                self.lab_ck['DSS Assist'].config(state='disabled')
                self.start_fsd()

            elif self.checkboxvar['FSD Route Assist'].get() == 0 and self.FSD_A_running == True:
                self.stop_fsd()
                self.lab_ck['Supercruise Assist'].config(state='active')
                self.lab_ck['AFK Combat Assist'].config(state='active')
                self.lab_ck['Waypoint Assist'].config(state='active')
                self.lab_ck['Robigo Assist'].config(state='active')
                self.lab_ck['DSS Assist'].config(state='active')

        if field == 'Supercruise Assist':
            if self.checkboxvar['Supercruise Assist'].get() == 1 and self.SC_A_running == False:
                self.lab_ck['FSD Route Assist'].config(state='disabled')
                self.lab_ck['AFK Combat Assist'].config(state='disabled')
                self.lab_ck['Waypoint Assist'].config(state='disabled')
                self.lab_ck['Robigo Assist'].config(state='disabled')
                self.lab_ck['DSS Assist'].config(state='disabled')
                self.start_sc()

            elif self.checkboxvar['Supercruise Assist'].get() == 0 and self.SC_A_running == True:
                self.stop_sc()
                self.lab_ck['FSD Route Assist'].config(state='active')
                self.lab_ck['AFK Combat Assist'].config(state='active')
                self.lab_ck['Waypoint Assist'].config(state='active')
                self.lab_ck['Robigo Assist'].config(state='active')
                self.lab_ck['DSS Assist'].config(state='active')

        if field == 'Waypoint Assist':
            if self.checkboxvar['Waypoint Assist'].get() == 1 and self.WP_A_running == False:
                self.lab_ck['FSD Route Assist'].config(state='disabled')
                self.lab_ck['Supercruise Assist'].config(state='disabled')
                self.lab_ck['AFK Combat Assist'].config(state='disabled')
                self.lab_ck['Robigo Assist'].config(state='disabled')
                self.lab_ck['DSS Assist'].config(state='disabled')
                self.start_waypoint()

            elif self.checkboxvar['Waypoint Assist'].get() == 0 and self.WP_A_running == True:
                self.stop_waypoint()
                self.lab_ck['FSD Route Assist'].config(state='active')
                self.lab_ck['Supercruise Assist'].config(state='active')
                self.lab_ck['AFK Combat Assist'].config(state='active')
                self.lab_ck['Robigo Assist'].config(state='active')
                self.lab_ck['DSS Assist'].config(state='active')

        if field == 'Robigo Assist':
            if self.checkboxvar['Robigo Assist'].get() == 1 and self.RO_A_running == False:
                self.lab_ck['FSD Route Assist'].config(state='disabled')
                self.lab_ck['Supercruise Assist'].config(state='disabled')
                self.lab_ck['AFK Combat Assist'].config(state='disabled')
                self.lab_ck['Waypoint Assist'].config(state='disabled')
                self.lab_ck['DSS Assist'].config(state='disabled')
                self.start_robigo()

            elif self.checkboxvar['Robigo Assist'].get() == 0 and self.RO_A_running == True:
                self.stop_robigo()
                self.lab_ck['FSD Route Assist'].config(state='active')
                self.lab_ck['Supercruise Assist'].config(state='active')
                self.lab_ck['AFK Combat Assist'].config(state='active')
                self.lab_ck['Waypoint Assist'].config(state='active')
                self.lab_ck['DSS Assist'].config(state='active')

        if field == 'AFK Combat Assist':
            if self.checkboxvar['AFK Combat Assist'].get() == 1:
                self.ed_ap.set_afk_combat_assist(True)
                self.log_msg("AFK Combat Assist start")
                self.lab_ck['FSD Route Assist'].config(state='disabled')
                self.lab_ck['Supercruise Assist'].config(state='disabled')
                self.lab_ck['Waypoint Assist'].config(state='disabled')
                self.lab_ck['Robigo Assist'].config(state='disabled')
                self.lab_ck['DSS Assist'].config(state='disabled')

            elif self.checkboxvar['AFK Combat Assist'].get() == 0:
                self.ed_ap.set_afk_combat_assist(False)
                self.log_msg("AFK Combat Assist stop")
                self.lab_ck['FSD Route Assist'].config(state='active')
                self.lab_ck['Supercruise Assist'].config(state='active')
                self.lab_ck['Waypoint Assist'].config(state='active')
                self.lab_ck['Robigo Assist'].config(state='active')
                self.lab_ck['DSS Assist'].config(state='active')

        if field == 'DSS Assist':
            if self.checkboxvar['DSS Assist'].get() == 1:
                self.lab_ck['FSD Route Assist'].config(state='disabled')
                self.lab_ck['AFK Combat Assist'].config(state='disabled')
                self.lab_ck['Supercruise Assist'].config(state='disabled')
                self.lab_ck['Waypoint Assist'].config(state='disabled')
                self.lab_ck['Robigo Assist'].config(state='disabled')
                self.start_dss()

            elif self.checkboxvar['DSS Assist'].get() == 0:
                self.stop_dss()
                self.lab_ck['FSD Route Assist'].config(state='active')
                self.lab_ck['Supercruise Assist'].config(state='active')
                self.lab_ck['AFK Combat Assist'].config(state='active')
                self.lab_ck['Waypoint Assist'].config(state='active')
                self.lab_ck['Robigo Assist'].config(state='active')

        if self.checkboxvar['Enable Randomness'].get():
            self.ed_ap.set_randomness(True)
        else:
            self.ed_ap.set_randomness(False)

        if self.checkboxvar['Activate Elite for each key'].get():
            self.ed_ap.set_activate_elite_eachkey(True)
            self.ed_ap.keys.activate_window=True
        else:
            self.ed_ap.set_activate_elite_eachkey(False)
            self.ed_ap.keys.activate_window = False

        if self.checkboxvar['Automatic logout'].get():
            self.ed_ap.set_automatic_logout(True)
        else:
            self.ed_ap.set_automatic_logout(False)

        if self.checkboxvar['Enable Overlay'].get():
            self.ed_ap.set_overlay(True)
        else:
            self.ed_ap.set_overlay(False)

        if self.checkboxvar['Enable Voice'].get():
            self.ed_ap.set_voice(True)
        else:
            self.ed_ap.set_voice(False)

        if self.checkboxvar['ELW Scanner'].get():
            self.ed_ap.set_fss_scan(True)
        else:
            self.ed_ap.set_fss_scan(False)

        if self.checkboxvar['Enable CV View'].get() == 1:
            self.cv_view = True
            x = self.root.winfo_x() + self.root.winfo_width() + 4
            y = self.root.winfo_y()
            self.ed_ap.set_cv_view(True, x, y)
        else:
            self.cv_view = False
            self.ed_ap.set_cv_view(False)

        self.ed_ap.config['DSSButton'] = self.radiobuttonvar['dss_button'].get()

        if self.radiobuttonvar['debug_mode'].get() == "Error":
            self.ed_ap.set_log_error(True)
        elif self.radiobuttonvar['debug_mode'].get() == "Debug":
            self.ed_ap.set_log_debug(True)
        elif self.radiobuttonvar['debug_mode'].get() == "Info":
            self.ed_ap.set_log_info(True)

        if field == 'Single Waypoint Assist':
            if self.checkboxvar['Single Waypoint Assist'].get() == 1 and self.SWP_A_running == False:
                self.start_single_waypoint_assist()
            elif self.checkboxvar['Single Waypoint Assist'].get() == 0 and self.SWP_A_running == True:
                self.stop_single_waypoint_assist()

    def makeform(self, win, ftype, fields, r=0, inc=1, rfrom=0, rto=1000):
        entries = {}

        for field in fields:
            row = tk.Frame(win)
            row.grid(row=r, column=0, padx=2, pady=2, sticky=(N, S, E, W))
            r += 1

            if ftype == FORM_TYPE_CHECKBOX:
                self.checkboxvar[field] = IntVar()
                lab = Checkbutton(row, text=field, anchor='w', width=27, justify=LEFT, variable=self.checkboxvar[field], command=(lambda field=field: self.check_cb(field)))
                self.lab_ck[field] = lab
            else:
                lab = tk.Label(row, anchor='w', width=20, pady=3, text=field + ": ")
                if ftype == FORM_TYPE_SPINBOX:
                    ent = tk.Spinbox(row, width=10, from_=rfrom, to=rto, increment=inc)
                else:
                    ent = tk.Entry(row, width=10)
                ent.bind('<FocusOut>', self.entry_update)
                ent.insert(0, "0")

            lab.grid(row=0, column=0)
            lab = Hovertip(row, self.tooltips[field], hover_delay=1000)

            if ftype != FORM_TYPE_CHECKBOX:
                ent.grid(row=0, column=1)
                entries[field] = ent

        return entries

    def gui_gen(self, win):

        modes_check_fields = ('FSD Route Assist', 'Supercruise Assist', 'Waypoint Assist', 'Robigo Assist', 'AFK Combat Assist', 'DSS Assist')
        ship_entry_fields = ('RollRate', 'PitchRate', 'YawRate')
        autopilot_entry_fields = ('Sun Bright Threshold', 'Nav Align Tries', 'Jump Tries', 'Docking Retries', 'Wait For Autodock')
        buttons_entry_fields = ('Start FSD', 'Start SC', 'Start Robigo', 'Stop All')
        refuel_entry_fields = ('Refuel Threshold', 'Scoop Timeout', 'Fuel Threshold Abort')
        overlay_entry_fields = ('X Offset', 'Y Offset', 'Font Size')

        #
        # Define all the menus
        #
        menubar = Menu(win, background='#ff8000', foreground='black', activebackground='white', activeforeground='black')
        file = Menu(menubar, tearoff=0)
        file.add_command(label="Calibrate Target", command=self.calibrate_callback)
        file.add_command(label="Calibrate Compass", command=self.calibrate_compass_callback)
        self.checkboxvar['Enable CV View'] = IntVar()
        self.checkboxvar['Enable CV View'].set(int(self.ed_ap.config['Enable_CV_View']))  # set IntVar value to the one from config
        file.add_checkbutton(label='Enable CV View', onvalue=1, offvalue=0, variable=self.checkboxvar['Enable CV View'], command=(lambda field='Enable CV View': self.check_cb(field)))
        file.add_separator()
        file.add_command(label="Restart", command=self.restart_program)
        file.add_command(label="Exit", command=self.close_window)  # win.quit)
        menubar.add_cascade(label="File", menu=file)

        help = Menu(menubar, tearoff=0)
        help.add_command(label="Check for Updates", command=self.check_updates)
        help.add_command(label="View Changelog", command=self.open_changelog)
        help.add_separator()
        help.add_command(label="Join Discord", command=self.open_discord)
        help.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=help)

        win.config(menu=menubar)

        # notebook pages
        nb = ttk.Notebook(win)
        nb.grid()
        page0 = Frame(nb)
        page1 = Frame(nb)
        page2 = Frame(nb)
        nb.add(page0, text="Main")  # main page
        nb.add(page1, text="Settings")  # options page
        nb.add(page2, text="Debug/Test")  # debug/test page

        # main options block
        blk_main = tk.Frame(page0)
        blk_main.grid(row=0, column=0, padx=10, pady=5, sticky=(E, W))
        blk_main.columnconfigure([0, 1], weight=1, minsize=100, uniform="group1")

        # ap mode checkboxes block
        blk_modes = LabelFrame(blk_main, text="MODE")
        blk_modes.grid(row=0, column=0, padx=2, pady=2, sticky=(N, S, E, W))
        self.makeform(blk_modes, FORM_TYPE_CHECKBOX, modes_check_fields)

        # ship values block
        blk_ship = LabelFrame(blk_main, text="SHIP")
        blk_ship.grid(row=0, column=1, padx=2, pady=2, sticky=(N, S, E, W))
        self.entries['ship'] = self.makeform(blk_ship, FORM_TYPE_SPINBOX, ship_entry_fields, 0, 0.5)

        lbl_sun_pitch_up = tk.Label(blk_ship, text='SunPitchUp +/- Time:', anchor='w', width=20)
        lbl_sun_pitch_up.grid(row=3, column=0, pady=3, sticky=(N, S, E, W))
        spn_sun_pitch_up = tk.Spinbox(blk_ship, width=10, from_=-100, to=100, increment=0.5)
        spn_sun_pitch_up.grid(row=3, column=1, padx=2, pady=2, sticky=(N, S, E, W))
        spn_sun_pitch_up.bind('<FocusOut>', self.entry_update)
        self.entries['ship']['SunPitchUp+Time'] = spn_sun_pitch_up

        btn_tst_roll = Button(blk_ship, text='Test Roll', command=self.ship_tst_roll)
        btn_tst_roll.grid(row=4, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))
        btn_tst_pitch = Button(blk_ship, text='Test Pitch', command=self.ship_tst_pitch)
        btn_tst_pitch.grid(row=5, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))
        btn_tst_yaw = Button(blk_ship, text='Test Yaw', command=self.ship_tst_yaw)
        btn_tst_yaw.grid(row=6, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        # profile load / info button in ship values block
        self.ship_filelabel = StringVar()
        self.ship_filelabel.set("<no config loaded>")
        btn_ship_file = Button(blk_ship, textvariable=self.ship_filelabel, command=self.open_ship_file)
        btn_ship_file.grid(row=8, column=0, padx=2, pady=2, sticky=(N, E, W))
        tip_ship_file = Hovertip(btn_ship_file, self.tooltips['Ship Config Button'], hover_delay=1000)

        # waypoints button block
        blk_wp_buttons = tk.LabelFrame(page0, text="Waypoints")
        blk_wp_buttons.grid(row=1, column=0, padx=10, pady=5, columnspan=2, sticky=(N, S, E, W))
        blk_wp_buttons.columnconfigure([0, 1], weight=1, minsize=100, uniform="group1")

        self.wp_filelabel = StringVar()
        self.wp_filelabel.set("<no list loaded>")
        btn_wp_file = Button(blk_wp_buttons, textvariable=self.wp_filelabel, command=self.open_wp_file)
        btn_wp_file.grid(row=0, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))
        tip_wp_file = Hovertip(btn_wp_file, self.tooltips['Waypoint List Button'], hover_delay=1000)

        btn_reset = Button(blk_wp_buttons, text='Reset List', command=self.reset_wp_file)
        btn_reset.grid(row=1, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))
        tip_reset = Hovertip(btn_reset, self.tooltips['Reset Waypoint List'], hover_delay=1000)

        # log window
        log = LabelFrame(page0, text="LOG")
        log.grid(row=3, column=0, padx=12, pady=5, sticky=(N, S, E, W))
        scrollbar = Scrollbar(log)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        mylist = Listbox(log, width=72, height=10, yscrollcommand=scrollbar.set)
        mylist.grid(row=0, column=0)
        scrollbar.config(command=mylist.yview)

        # settings block
        blk_settings = tk.Frame(page1)
        blk_settings.grid(row=0, column=0, padx=10, pady=5, sticky=(E, W))
        blk_main.columnconfigure([0, 1], weight=1, minsize=100, uniform="group1")

        # autopilot settings block
        blk_ap = LabelFrame(blk_settings, text="AUTOPILOT")
        blk_ap.grid(row=0, column=0, padx=2, pady=2, sticky=(N, S, E, W))
        self.entries['autopilot'] = self.makeform(blk_ap, FORM_TYPE_SPINBOX, autopilot_entry_fields)
        self.checkboxvar['Enable Randomness'] = BooleanVar()
        cb_random = Checkbutton(blk_ap, text='Enable Randomness', anchor='w', pady=3, justify=LEFT, onvalue=1, offvalue=0, variable=self.checkboxvar['Enable Randomness'], command=(lambda field='Enable Randomness': self.check_cb(field)))
        cb_random.grid(row=5, column=0, columnspan=2, sticky=(W))
        self.checkboxvar['Activate Elite for each key'] = BooleanVar()
        cb_activate_elite = Checkbutton(blk_ap, text='Activate Elite for each key', anchor='w', pady=3, justify=LEFT, onvalue=1, offvalue=0, variable=self.checkboxvar['Activate Elite for each key'], command=(lambda field='Activate Elite for each key': self.check_cb(field)))
        cb_activate_elite.grid(row=6, column=0, columnspan=2, sticky=(W))
        self.checkboxvar['Automatic logout'] = BooleanVar()
        cb_logout = Checkbutton(blk_ap, text='Automatic logout', anchor='w', pady=3, justify=LEFT, onvalue=1, offvalue=0, variable=self.checkboxvar['Automatic logout'], command=(lambda field='Automatic logout': self.check_cb(field)))
        cb_logout.grid(row=7, column=0, columnspan=2, sticky=(W))

        # buttons settings block
        blk_buttons = LabelFrame(blk_settings, text="BUTTONS")
        blk_buttons.grid(row=0, column=1, padx=2, pady=2, sticky=(N, S, E, W))
        blk_dss = Frame(blk_buttons)
        blk_dss.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky=(N, S, E, W))
        lb_dss = Label(blk_dss, width=18, anchor='w', pady=3, text="DSS Button: ")
        lb_dss.grid(row=0, column=0, sticky=(W))
        self.radiobuttonvar['dss_button'] = StringVar()
        rb_dss_primary = Radiobutton(blk_dss, pady=3, text="Primary", variable=self.radiobuttonvar['dss_button'], value="Primary", command=(lambda field='dss_button': self.check_cb(field)))
        rb_dss_primary.grid(row=0, column=1, sticky=(W))
        rb_dss_secandary = Radiobutton(blk_dss, pady=3, text="Secondary", variable=self.radiobuttonvar['dss_button'], value="Secondary", command=(lambda field='dss_button': self.check_cb(field)))
        rb_dss_secandary.grid(row=1, column=1, sticky=(W))
        self.entries['buttons'] = self.makeform(blk_buttons, FORM_TYPE_ENTRY, buttons_entry_fields, 2)

        # refuel settings block
        blk_fuel = LabelFrame(blk_settings, text="FUEL")
        blk_fuel.grid(row=1, column=0, padx=2, pady=2, sticky=(N, S, E, W))
        self.entries['refuel'] = self.makeform(blk_fuel, FORM_TYPE_SPINBOX, refuel_entry_fields)

        # overlay settings block
        blk_overlay = LabelFrame(blk_settings, text="OVERLAY")
        blk_overlay.grid(row=1, column=1, padx=2, pady=2, sticky=(N, S, E, W))
        self.checkboxvar['Enable Overlay'] = BooleanVar()
        cb_enable = Checkbutton(blk_overlay, text='Enable (requires restart)', onvalue=1, offvalue=0, anchor='w', pady=3, justify=LEFT, variable=self.checkboxvar['Enable Overlay'], command=(lambda field='Enable Overlay': self.check_cb(field)))
        cb_enable.grid(row=0, column=0, columnspan=2, sticky=(W))
        self.entries['overlay'] = self.makeform(blk_overlay, FORM_TYPE_SPINBOX, overlay_entry_fields, 1, 1.0, 0.0, 3000.0)

        # tts / voice settings block
        blk_voice = LabelFrame(blk_settings, text="VOICE")
        blk_voice.grid(row=2, column=0, padx=2, pady=2, sticky=(N, S, E, W))
        self.checkboxvar['Enable Voice'] = BooleanVar()
        cb_enable = Checkbutton(blk_voice, text='Enable', onvalue=1, offvalue=0, anchor='w', pady=3, justify=LEFT, variable=self.checkboxvar['Enable Voice'], command=(lambda field='Enable Voice': self.check_cb(field)))
        cb_enable.grid(row=0, column=0, columnspan=2, sticky=(W))

        # Scanner settings block
        blk_voice = LabelFrame(blk_settings, text="ELW SCANNER")
        blk_voice.grid(row=2, column=1, padx=2, pady=2, sticky=(N, S, E, W))
        self.checkboxvar['ELW Scanner'] = BooleanVar()
        cb_enable = Checkbutton(blk_voice, text='Enable', onvalue=1, offvalue=0, anchor='w', pady=3, justify=LEFT, variable=self.checkboxvar['ELW Scanner'], command=(lambda field='ELW Scanner': self.check_cb(field)))
        cb_enable.grid(row=0, column=0, columnspan=2, sticky=(W))

        # settings button block
        blk_settings_buttons = tk.Frame(page1)
        blk_settings_buttons.grid(row=3, column=0, padx=10, pady=5, sticky=(N, S, E, W))
        blk_settings_buttons.columnconfigure([0, 1], weight=1, minsize=100)
        btn_save = Button(blk_settings_buttons, text='Save All Settings', command=self.save_settings)
        btn_save.grid(row=0, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        # debug block
        blk_debug = tk.Frame(page2)
        blk_debug.grid(row=0, column=0, padx=10, pady=5, sticky=(E, W))
        blk_debug.columnconfigure([0, 1], weight=1, minsize=100, uniform="group2")

        # debug settings block
        blk_debug_settings = LabelFrame(blk_debug, text="DEBUG")
        blk_debug_settings.grid(row=0, column=0, padx=2, pady=2, sticky=(N, S, E, W))
        self.radiobuttonvar['debug_mode'] = StringVar()
        rb_debug_debug = Radiobutton(blk_debug_settings, pady=3, text="Debug + Info + Errors", variable=self.radiobuttonvar['debug_mode'], value="Debug", command=(lambda field='debug_mode': self.check_cb(field)))
        rb_debug_debug.grid(row=0, column=1, columnspan=2, sticky=(W))
        rb_debug_info = Radiobutton(blk_debug_settings, pady=3, text="Info + Errors", variable=self.radiobuttonvar['debug_mode'], value="Info", command=(lambda field='debug_mode': self.check_cb(field)))
        rb_debug_info.grid(row=1, column=1, columnspan=2, sticky=(W))
        rb_debug_error = Radiobutton(blk_debug_settings, pady=3, text="Errors only (default)", variable=self.radiobuttonvar['debug_mode'], value="Error", command=(lambda field='debug_mode': self.check_cb(field)))
        rb_debug_error.grid(row=2, column=1, columnspan=2, sticky=(W))
        btn_open_logfile = Button(blk_debug_settings, text='Open Log File', command=self.open_logfile)
        btn_open_logfile.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        # debug settings block
        blk_single_waypoint_asst = LabelFrame(page2, text="Single Waypoint Assist")
        blk_single_waypoint_asst.grid(row=1, column=0, padx=10, pady=5, columnspan=2, sticky=(N, S, E, W))
        blk_single_waypoint_asst.columnconfigure(0, weight=1, minsize=10, uniform="group1")
        blk_single_waypoint_asst.columnconfigure(1, weight=3, minsize=10, uniform="group1")

        lbl_system = tk.Label(blk_single_waypoint_asst, text='System:')
        lbl_system.grid(row=0, column=0, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))
        txt_system = Entry(blk_single_waypoint_asst, textvariable=self.single_waypoint_system)
        txt_system.grid(row=0, column=1, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))
        lbl_station = tk.Label(blk_single_waypoint_asst, text='Station:')
        lbl_station.grid(row=1, column=0, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))
        txt_station = Entry(blk_single_waypoint_asst, textvariable=self.single_waypoint_station)
        txt_station.grid(row=1, column=1, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))
        self.checkboxvar['Single Waypoint Assist'] = BooleanVar()
        cb_single_waypoint = Checkbutton(blk_single_waypoint_asst, text='Single Waypoint Assist', onvalue=1, offvalue=0, anchor='w', pady=3, justify=LEFT, variable=self.checkboxvar['Single Waypoint Assist'], command=(lambda field='Single Waypoint Assist': self.check_cb(field)))
        cb_single_waypoint.grid(row=2, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        lbl_tce = tk.Label(blk_single_waypoint_asst, text='Trade Computer Extension (TCE)', fg="blue", cursor="hand2")
        lbl_tce.bind("<Button-1>", lambda e: hyperlink_callback("https://forums.frontier.co.uk/threads/trade-computer-extension-mk-ii.223056/"))
        lbl_tce.grid(row=3, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))
        lbl_tce_dest = tk.Label(blk_single_waypoint_asst, text='TCE Dest json:')
        lbl_tce_dest.grid(row=4, column=0, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))
        txt_tce_dest = Entry(blk_single_waypoint_asst, textvariable=self.TCE_Destination_Filepath)
        txt_tce_dest.bind('<FocusOut>', self.entry_update)
        txt_tce_dest.grid(row=4, column=1, padx=2, pady=2, columnspan=1, sticky=(N, E, W, S))

        btn_load_tce = Button(blk_single_waypoint_asst, text='Load TCE Destination', command=self.load_tce_dest)
        btn_load_tce.grid(row=5, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        blk_debug_buttons = tk.Frame(page2)
        blk_debug_buttons.grid(row=3, column=0, padx=10, pady=5, columnspan=2, sticky=(N, S, E, W))
        blk_debug_buttons.columnconfigure([0, 1], weight=1, minsize=100)

        btn_save = Button(blk_debug_buttons, text='Save All Settings', command=self.save_settings)
        btn_save.grid(row=6, column=0, padx=2, pady=2, columnspan=2, sticky=(N, E, W, S))

        # Statusbar
        statusbar = Frame(win)
        statusbar.grid(row=4, column=0)
        self.status = tk.Label(win, text="Status: ", bd=1, relief=tk.SUNKEN, anchor=tk.W, justify=LEFT, width=29)
        self.jumpcount = tk.Label(statusbar, text="<info> ", bd=1, relief=tk.SUNKEN, anchor=tk.W, justify=LEFT, width=40)
        self.status.pack(in_=statusbar, side=LEFT, fill=BOTH, expand=True)
        self.jumpcount.pack(in_=statusbar, side=RIGHT, fill=Y, expand=False)

        return mylist

    def restart_program(self):
        logger.debug("Entered: restart_program")
        print("restart now")

        self.stop_fsd()
        self.stop_sc()
        self.ed_ap.quit()
        sleep(0.1)

        import sys
        print("argv was", sys.argv)
        print("sys.executable was", sys.executable)
        print("restart now")

        import os
        os.execv(sys.executable, ['python'] + sys.argv)

<<<<<<< Updated upstream
=======
    # ===== DEVELOPMENT MODE METHODS =====
    
    def _is_dev_mode(self):
        """Check if we're in development mode"""
        return (
            os.path.exists('.git') or                    # Git repository
            '--dev' in sys.argv or                       # Command line flag
            os.getenv('EDAP_DEV_MODE') == '1' or        # Environment variable
            os.path.exists('dev_mode.txt')              # Dev mode file
        )
    
    def _create_dev_menu(self, menubar):
        """Create development menu"""
        dev_menu = Menu(menubar, tearoff=0)
        
        # Panel reloading
        dev_menu.add_command(label="🔄 Reload Waypoint Panel", command=self._reload_waypoint_panel)
        dev_menu.add_command(label="🔄 Reload Settings Panel", command=self._reload_settings_panel)
        dev_menu.add_command(label="🔄 Reload Assist Panel", command=self._reload_assist_panel)
        dev_menu.add_separator()
        
        # Debug tools
        dev_menu.add_command(label="🐛 Toggle Debug Logging", command=self._toggle_debug_logging)
        dev_menu.add_command(label="📊 Show Panel State", command=self._show_panel_state)
        dev_menu.add_command(label="🧪 Open Dev Console", command=self._open_dev_console)
        dev_menu.add_separator()
        
        # File operations
        dev_menu.add_command(label="💾 Force Save All", command=self._force_save_all)
        dev_menu.add_command(label="🔍 Validate Config Files", command=self._validate_config_files)
        
        menubar.add_cascade(label="🔧 Dev", menu=dev_menu)
        
        # Log that dev mode is active
        logger.info("🔧 Development mode enabled - Dev menu available")
    
    def _reload_waypoint_panel(self):
        """Hot reload the waypoint panel"""
        try:
            logger.info("🔄 Reloading waypoint panel...")
            
            # Save current state
            state = self._save_waypoint_panel_state()
            
            # Reload the module
            import gui.waypoint_panel
            importlib.reload(gui.waypoint_panel)
            
            # Recreate the panel
            if self.waypoint_panel:
                parent = self.waypoint_panel.parent
                
                # Destroy old panel
                for widget in parent.winfo_children():
                    widget.destroy()
                
                # Create new panel
                self.waypoint_panel = gui.waypoint_panel.WaypointPanel(
                    parent, self.ed_ap, self._entry_update, self._check_cb
                )
                
                # Restore state
                self._restore_waypoint_panel_state(state)
                
            logger.info("✅ Waypoint panel reloaded successfully")
            self.log_msg("Dev: Waypoint panel reloaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to reload waypoint panel: {e}")
            messagebox.showerror("Reload Error", f"Failed to reload waypoint panel:\n{e}")
    
    def _reload_settings_panel(self):
        """Hot reload the settings panel"""
        try:
            logger.info("🔄 Reloading settings panel...")
            
            # Save current state
            state = self._save_settings_panel_state()
            
            # Reload the module
            import gui.settings_panel
            importlib.reload(gui.settings_panel)
            
            # Recreate the panel
            if self.settings_panel:
                parent = self.settings_panel.parent
                
                # Destroy old panel
                for widget in parent.winfo_children():
                    widget.destroy()
                
                # Create new panel
                self.settings_panel = gui.settings_panel.SettingsPanel(
                    parent, self.ed_ap, self.tooltips, self._entry_update, self._check_cb
                )
                
                # Re-inject dependencies
                self.settings_panel.set_config_manager(self.config_manager)
                self.settings_panel.set_hotkey_capture_callback(self._capture_hotkey)
                self.settings_panel.set_button_commands(
                    self.config_manager.save_settings,
                    self.config_manager.revert_all_changes
                )
                
                # Update config manager references
                gui_elements = self.config_manager.gui_elements
                gui_elements['settings_panel'] = self.settings_panel
                gui_elements['save_button'] = self.settings_panel.save_button
                gui_elements['revert_button'] = self.settings_panel.revert_button
                self.config_manager.set_gui_elements(gui_elements)
                
                # Restore state
                self._restore_settings_panel_state(state)
                
            logger.info("✅ Settings panel reloaded successfully")
            self.log_msg("Dev: Settings panel reloaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to reload settings panel: {e}")
            messagebox.showerror("Reload Error", f"Failed to reload settings panel:\n{e}")
    
    def _reload_assist_panel(self):
        """Hot reload the assist panel"""
        try:
            logger.info("🔄 Reloading assist panel...")
            
            # Save current state
            state = self._save_assist_panel_state()
            
            # Reload the module
            import gui.assist_panel
            importlib.reload(gui.assist_panel)
            
            # Recreate the panel
            if self.assist_panel:
                parent = self.assist_panel.parent
                
                # Destroy old panel
                for widget in parent.winfo_children():
                    widget.destroy()
                
                # Create new panel
                self.assist_panel = gui.assist_panel.AssistPanel(
                    parent, self.ed_ap, self.tooltips, self._check_cb
                )
                
                # Restore state
                self._restore_assist_panel_state(state)
                
                # Restore callback
                self.assist_panel.set_stop_all_callback(self.stop_all_assists)
                
            logger.info("✅ Assist panel reloaded successfully")
            self.log_msg("Dev: Assist panel reloaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to reload assist panel: {e}")
            messagebox.showerror("Reload Error", f"Failed to reload assist panel:\n{e}")
    
    def _save_waypoint_panel_state(self):
        """Save current waypoint panel state"""
        if not self.waypoint_panel:
            return {}
        
        return {
            'wp_filelabel': getattr(self.waypoint_panel, 'wp_filelabel', StringVar()).get(),
            'changed_waypoints': getattr(self.waypoint_panel, 'changed_waypoints', set()).copy(),
            'global_shopping_enabled': getattr(self.waypoint_panel, 'global_shopping_enabled', BooleanVar()).get(),
            'TCE_Destination_Filepath': getattr(self.waypoint_panel, 'TCE_Destination_Filepath', StringVar()).get(),
            'single_waypoint_system': getattr(self.waypoint_panel, 'single_waypoint_system', StringVar()).get(),
            'single_waypoint_station': getattr(self.waypoint_panel, 'single_waypoint_station', StringVar()).get(),
        }
    
    def _restore_waypoint_panel_state(self, state):
        """Restore waypoint panel state after reload"""
        if not self.waypoint_panel or not state:
            return
        
        try:
            # Restore file label
            if 'wp_filelabel' in state and hasattr(self.waypoint_panel, 'wp_filelabel'):
                self.waypoint_panel.wp_filelabel.set(state['wp_filelabel'])
            
            # Restore changed waypoints
            if 'changed_waypoints' in state and hasattr(self.waypoint_panel, 'changed_waypoints'):
                self.waypoint_panel.changed_waypoints = state['changed_waypoints']
            
            # Restore global shopping state
            if 'global_shopping_enabled' in state and hasattr(self.waypoint_panel, 'global_shopping_enabled'):
                self.waypoint_panel.global_shopping_enabled.set(state['global_shopping_enabled'])
            
            # Restore TCE and single waypoint fields
            for field in ['TCE_Destination_Filepath', 'single_waypoint_system', 'single_waypoint_station']:
                if field in state and hasattr(self.waypoint_panel, field):
                    getattr(self.waypoint_panel, field).set(state[field])
            
            # Refresh the panel - add small delay to ensure widgets are fully initialized
            self.waypoint_panel.parent.after(100, self._delayed_waypoint_refresh)
                
        except Exception as e:
            logger.warning(f"Some state could not be restored: {e}")
    
    def _delayed_waypoint_refresh(self):
        """Delayed refresh for waypoint panel after reload"""
        try:
            if hasattr(self.waypoint_panel, '_wp_editor_refresh'):
                self.waypoint_panel._wp_editor_refresh()
            if hasattr(self.waypoint_panel, '_refresh_global_shopping_summary'):
                self.waypoint_panel._refresh_global_shopping_summary()
        except Exception as e:
            logger.warning(f"Delayed waypoint refresh failed: {e}")
    
    def _save_settings_panel_state(self):
        """Save current settings panel state"""
        # Settings panel state is managed by config_manager, so we just need to capture current values
        return {
            'has_unsaved_changes': getattr(self.config_manager, 'has_unsaved_changes', False)
        }
    
    def _restore_settings_panel_state(self, state):
        """Restore settings panel state after reload"""
        # Re-initialize values from configuration
        if self.settings_panel and hasattr(self.settings_panel, 'initialize_all_values'):
            self.settings_panel.initialize_all_values()
        
        # Restore unsaved changes state if needed
        if state.get('has_unsaved_changes', False):
            self.config_manager.mark_unsaved_changes()
    
    def _save_assist_panel_state(self):
        """Save current assist panel state"""
        if not self.assist_panel:
            return {}
        
        # Get current assist states
        return {
            'assist_states': {
                'FSD': getattr(self.ed_ap, 'fsd_assist_enabled', False),
                'SC': getattr(self.ed_ap, 'sc_assist_enabled', False),
                'WP': getattr(self.ed_ap, 'waypoint_assist_enabled', False),
                'Robigo': getattr(self.ed_ap, 'robigo_assist_enabled', False),
                'AFK': getattr(self.ed_ap, 'afk_combat_assist_enabled', False),
                'DSS': getattr(self.ed_ap, 'dss_assist_enabled', False),
            }
        }
    
    def _restore_assist_panel_state(self, state):
        """Restore assist panel state after reload"""
        if not self.assist_panel or not state:
            return
        
        # Restore assist states
        assist_states = state.get('assist_states', {})
        for assist_type, enabled in assist_states.items():
            if hasattr(self.assist_panel, 'update_assist_state'):
                self.assist_panel.update_assist_state(assist_type, enabled)
    
    def _toggle_debug_logging(self):
        """Toggle debug logging level"""
        from EDlogger import logger
        current_level = logger.getEffectiveLevel()
        
        if current_level == 10:  # DEBUG
            logger.setLevel(20)  # INFO
            self.log_msg("Dev: Debug logging OFF")
        else:
            logger.setLevel(10)  # DEBUG
            self.log_msg("Dev: Debug logging ON")
    
    def _show_panel_state(self):
        """Show current panel states for debugging"""
        state_info = []
        
        # Waypoint panel state
        if self.waypoint_panel:
            wp_state = self._save_waypoint_panel_state()
            state_info.append("=== Waypoint Panel ===")
            for key, value in wp_state.items():
                state_info.append(f"{key}: {value}")
        
        # Settings panel state
        if self.settings_panel:
            state_info.append("\n=== Settings Panel ===")
            state_info.append(f"has_unsaved_changes: {getattr(self.config_manager, 'has_unsaved_changes', False)}")
        
        # Assist panel state
        if self.assist_panel:
            assist_state = self._save_assist_panel_state()
            state_info.append("\n=== Assist Panel ===")
            for assist_type, enabled in assist_state.get('assist_states', {}).items():
                state_info.append(f"{assist_type}: {enabled}")
        
        # Show in a dialog
        state_text = "\n".join(state_info)
        messagebox.showinfo("Panel State Debug", state_text)
    
    def _open_dev_console(self):
        """Open a development console window"""
        console = Toplevel(self.root)
        console.title("🧪 Dev Console")
        console.geometry("600x400")
        
        # Create text area for commands
        console_frame = Frame(console)
        console_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        Label(console_frame, text="Development Console - Python REPL", 
              font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        
        # Text widget for output
        output_text = tk.Text(console_frame, height=15, font=('Courier', 9))
        output_scrollbar = Scrollbar(console_frame, command=output_text.yview)
        output_text.configure(yscrollcommand=output_scrollbar.set)
        
        output_text.pack(side=LEFT, fill=BOTH, expand=True)
        output_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Input frame
        input_frame = Frame(console)
        input_frame.pack(fill=X, padx=10, pady=5)
        
        Label(input_frame, text=">>> ").pack(side=LEFT)
        input_entry = Entry(input_frame)
        input_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        def execute_command(event=None):
            command = input_entry.get()
            if not command:
                return
            
            output_text.insert(END, f">>> {command}\n")
            
            try:
                # Create a safe namespace with access to main objects
                namespace = {
                    'app': self,
                    'ed_ap': self.ed_ap,
                    'waypoint_panel': self.waypoint_panel,
                    'settings_panel': self.settings_panel,
                    'assist_panel': self.assist_panel,
                    'config_manager': self.config_manager,
                    'logger': logger,
                }
                
                result = eval(command, namespace)
                if result is not None:
                    output_text.insert(END, f"{result}\n")
            except Exception as e:
                output_text.insert(END, f"Error: {e}\n")
            
            output_text.see(END)
            input_entry.delete(0, END)
        
        input_entry.bind('<Return>', execute_command)
        
        Button(input_frame, text="Execute", command=execute_command).pack(side=RIGHT)
        
        # Add some helpful info
        output_text.insert(END, "Available objects: app, ed_ap, waypoint_panel, settings_panel, assist_panel, config_manager, logger\n")
        output_text.insert(END, "Example commands:\n")
        output_text.insert(END, "  app.waypoint_panel.changed_waypoints\n")
        output_text.insert(END, "  ed_ap.config['SunBrightThreshold']\n")
        output_text.insert(END, "  logger.info('Hello from console')\n\n")
        
        input_entry.focus()
    
    def _force_save_all(self):
        """Force save all panels and configurations"""
        try:
            if self.config_manager:
                self.config_manager.save_all_settings()
            
            if self.waypoint_panel and hasattr(self.waypoint_panel, '_wp_editor_save'):
                self.waypoint_panel._wp_editor_save()
            
            logger.info("✅ Force save completed")
            self.log_msg("Dev: Force save completed")
            
        except Exception as e:
            logger.error(f"❌ Force save failed: {e}")
            messagebox.showerror("Save Error", f"Force save failed:\n{e}")
    
    def _validate_config_files(self):
        """Validate all configuration files"""
        issues = []
        
        try:
            # Check waypoint files
            waypoint_files = ['./waypoints/waypoints.json', './waypoints/completed.json', './waypoints/repeat.json']
            for file_path in waypoint_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            json.load(f)
                    except json.JSONDecodeError as e:
                        issues.append(f"Invalid JSON in {file_path}: {e}")
                else:
                    issues.append(f"Missing file: {file_path}")
            
            # Check ship configs
            ship_config_file = './configs/ship_configs.json'
            if os.path.exists(ship_config_file):
                try:
                    with open(ship_config_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {ship_config_file}: {e}")
            
            # Show results
            if issues:
                messagebox.showwarning("Config Validation", f"Found {len(issues)} issues:\n\n" + "\n".join(issues))
            else:
                messagebox.showinfo("Config Validation", "✅ All configuration files are valid!")
                
        except Exception as e:
            messagebox.showerror("Validation Error", f"Failed to validate configs:\n{e}")


>>>>>>> Stashed changes
def main():
    #   handle = win32gui.FindWindow(0, "Elite - Dangerous (CLIENT)")
    #   if handle != None:
    #       win32gui.SetForegroundWindow(handle)  # put the window in foreground

    root = tk.Tk()
    app = APGui(root)

    root.mainloop()


if __name__ == "__main__":
    main()
