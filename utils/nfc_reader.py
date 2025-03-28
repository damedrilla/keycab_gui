from PySide6.QtCore import QThread, Signal
from threading import Event
from . import api_utils

class NFCReaderThread(QThread):
    uid_signal = Signal(str)  # Signal to send the UID to the main thread
    error_signal = Signal(str)  # Signal to send error messages

    def __init__(self):
        super().__init__()
        self.stop_flag = Event()  # Create a stop flag

    def run(self):
        try:
            uid = api_utils.getUID(self.stop_flag)  # Pass the stop flag to getUID
            if uid:
                self.uid_signal.emit(uid)  # Emit the UID if found
            else:
                self.error_signal.emit("Scanning canceled.")
        except Exception as e:
            self.error_signal.emit(str(e))

    def stop(self):
        """Stop the thread gracefully."""
        self.stop_flag.set()  # Set the stop flag to interrupt getUI
        
