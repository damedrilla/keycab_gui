from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
import requests
from PySide6.QtWidgets import QDialog, QProgressBar
from PySide6.QtCore import QTimer
from PySide6.QtCore import QThread, Signal

class ConnectionPopup(QDialog):
    def __init__(self, server_url, parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.retry_count = 0  # Counter for retries
        self.max_retries = 5  # Maximum number of retries

        # Set up the dialog
        self.setWindowTitle("Connecting to Server")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # Remove title bar
        self.setModal(True)
        self.setFixedSize(300, 150)

        # Create a label to display the connection status
        self.status_label = QLabel("Checking connection to CCS KeyCabinet server...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Create a progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar

        # Create a layout for the popup
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        # Set up a timer to check the connection periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(2000)  # Check every 2 seconds

    def check_connection(self):
        try:
            # Send a GET request to the server
            response = requests.get(self.server_url, timeout=5)
            if response.status_code == 200:
                # Connection successful
                self.status_label.setText("Connection established!")
                self.timer.stop()
                self.accept()  # Close the popup
            else:
                # Connection failed
                self.retry_count += 1
                self.status_label.setText(f"Retrying connection... ({self.retry_count}/{self.max_retries})")
                self.check_retry_limit()
        except requests.RequestException:
            # Handle connection errors
            self.retry_count += 1
            self.status_label.setText(f"Retrying connection... ({self.retry_count}/{self.max_retries})")
            self.check_retry_limit()

    def check_retry_limit(self):
        if self.retry_count >= self.max_retries:
            self.timer.stop()
            self.show_failure_popup()

    def show_failure_popup(self):
        # Show a popup indicating connection failure
        failure_popup = QDialog(self)
        failure_popup.setWindowTitle("Connection Failed")
        failure_popup.setModal(True)
        failure_popup.setFixedSize(400, 200)  # Increased size to fit the text

        # Create a label for the error message
        error_label = QLabel("Connection failed. Please check connection and restart the device.")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)  # Enable text wrapping for long messages

        # Create a button to close the application
        close_button = QPushButton("Close Application")
        close_button.setFixedHeight(40)  # Make the button slightly thicker
        close_button.clicked.connect(QApplication.instance().quit)  # Close the app when clicked

        # Create a layout for the failure popup
        layout = QVBoxLayout()
        layout.addWidget(error_label)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)  # Center-align the button
        failure_popup.setLayout(layout)

        # Show the failure popup
        failure_popup.exec()

        # Close the main connection popup
        self.reject()  # Close the popup and indicate failure


class ConnectionMonitor(QThread):
    """Monitors the server connection during the app's runtime."""
    connection_lost_signal = Signal()  # Signal to notify when the connection is lost
    connection_restored_signal = Signal()  # Signal to notify when the connection is restored

    def __init__(self, server_url, parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.running = True  # Flag to control the thread
        self.connection_lost = False  # Track if the connection was previously lost

    def run(self):
        while self.running:
            try:
                # Send a GET request to check the server connection
                response = requests.get(self.server_url, timeout=5)
                if response.status_code == 200:
                    if self.connection_lost:  # If the connection was previously lost
                        self.connection_restored_signal.emit()  # Emit signal for connection restored
                        self.connection_lost = False
                else:
                    if not self.connection_lost:  # If the connection is lost for the first time
                        self.connection_lost_signal.emit()  # Emit signal for connection lost
                        self.connection_lost = True
            except requests.RequestException:
                if not self.connection_lost:  # If the connection is lost for the first time
                    self.connection_lost_signal.emit()  # Emit signal for connection lost
                    self.connection_lost = True
            self.msleep(5000)  # Check every 5 seconds

    def stop(self):
        """Stop the connection monitor."""
        self.running = False

def show_connection_error_popup(app, connection_restored_signal):
    """Display a blocking popup when the connection is lost."""
    error_popup = QDialog()
    error_popup.setWindowTitle("Connection Error")
    error_popup.setModal(True)
    error_popup.setFixedSize(400, 200)

    # Create a label for the error message
    error_label = QLabel("Connection to the server has been lost. Please check your network connection.")
    error_label.setAlignment(Qt.AlignCenter)
    error_label.setWordWrap(True)
    error_label.setStyleSheet("font-size: 30px; font-weight: bold;")  # Set font size to 18px and make it bold

    # Create a layout for the popup
    layout = QVBoxLayout()
    layout.addWidget(error_label)
    error_popup.setLayout(layout)

    # Connect the connection restored signal to close the popup
    connection_restored_signal.connect(error_popup.accept)

    # Show the popup as a modal dialog
    error_popup.exec()