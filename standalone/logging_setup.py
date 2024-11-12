import logging
from PyQt5.QtCore import QObject, pyqtSignal

def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobbering of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    # Return silently if already defined
    if hasattr(logging, levelName):
        return
    if hasattr(logging, methodName):
        return
    if hasattr(logging.getLoggerClass(), methodName):
        return

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

# Add TRACE level immediately when module is imported
addLoggingLevel('TRACE', logging.DEBUG - 5)

class LogBuffer(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        """Store the record without calling parent's emit"""
        self.records.append(record)

    def flush_records(self):
        """Returns and clears the current records."""
        temp = self.records.copy()
        self.records.clear()
        return temp

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
    logger.setLevel(logging.TRACE)  # TRACE level is already defined at module import

    # Clear existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler (always enabled)
    file_handler = logging.FileHandler('edkeysgui.log')
    file_handler.setLevel(logging.TRACE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Buffer handler
    log_buffer = LogBuffer()
    log_buffer.setLevel(logging.TRACE)
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