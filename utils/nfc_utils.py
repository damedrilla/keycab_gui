from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import QTimer, Qt
from py122u import nfc

def check_nfc_reader():
    """Check if the ACR122U NFC reader is connected."""
    err_msg = ""
    try:
        nfc.Reader()  # NFC reader is connected
    except Exception as e:
        err_msg = str(e)
    
    if err_msg == "No readers available":
        return False
    else:
        return True

class NFCReaderPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Checking NFC Reader")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # Remove title bar
        self.setModal(True)
        self.setFixedSize(300, 150)

        # Create a label to display the connection status
        self.status_label = QLabel("Checking for ACR122U NFC reader...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Create a progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar

        # Create a layout for the popup
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        # Set up a timer to check the NFC reader periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_nfc_reader)
        self.timer.start(2000)  # Check every 2 seconds

    def check_nfc_reader(self):
        """Check if the NFC reader is connected."""
        if check_nfc_reader():
            self.status_label.setText("NFC reader connected!")
            self.timer.stop()
            QTimer.singleShot(1000, self.accept)  # Close the popup after 1 second
        else:
            self.status_label.setText("NFC reader not connected. Retrying...")