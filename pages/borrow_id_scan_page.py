from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt
import requests
from PySide6.QtCore import QTimer
import datetime
from utils.nfc_reader import NFCReaderThread
from utils.api_utils import getIDholder
class BorrowIDScanPage(QWidget):
    # The BorrowIDScanPage class remains the same as the original ThirdPage class.
    # Simply replace all references to "ThirdPage" with "BorrowIDScanPage".
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set the default background color of the third page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Create a label to display messages
        self.label = QLabel("Please scan your ID (Press 0 to go back)")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 30px; font-weight: bold;")  # Set font size to 30

        # Create a layout for the page
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Initialize a variable to store the selected value
        self.selected_value = None

    def set_selected_value(self, value):
        """Set the selected key value from the SecondPage."""
        self.selected_value = value
        print(f"Selected key value received: {value}")  # Debugging message

        # Update the label to display the selected key
        self.label.setText(f"Selected Key: {value}. Please scan your ID.")

    def showEvent(self, event):
        """Reset the page state when it is shown."""
        super().showEvent(event)
        self.label.setText("Please scan your ID")  # Reset the label text
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Reset the background color
        self.start_card_scanning()  # Restart the card scanning process

    def start_card_scanning(self):
        # Update the label to prompt the user to scan their ID
        self.label.setText("Please scan your ID")

        # Start a thread to read the card UID
        self.nfc_thread = NFCReaderThread()
        self.nfc_thread.uid_signal.connect(self.handle_uid)
        self.nfc_thread.error_signal.connect(self.handle_error)
        self.nfc_thread.start()

    def handle_uid(self, uid):
        # Update the label to indicate data is being fetched
        self.setStyleSheet("background-color: black; color: white;")
        self.label.setText("Getting cardholder data from the server...")
        QApplication.processEvents()  # Process UI updates before making the server request

        # Simulate a server request to fetch cardholder data
        try:
            result = getIDholder(uid)
            print(uid + " " + str(result))
            if result[0] == 200:
                self.setStyleSheet("background-color: green; color: white;")  # Set background to green
                self.label.setText("Access granted!")
                self.log_transaction(result[1])  # Log the transaction
            else:
                self.setStyleSheet("background-color: red; color: white;")  # Set background to red
                self.label.setText("Access denied. Cardholder not found or disabled")
        except Exception as e:
            self.setStyleSheet("background-color: red; color: white;")  # Set background to red
            self.label.setText(f"Error: {str(e)}")

        # Ensure the font size remains consistent
        self.label.setStyleSheet("font-size: 30px; font-weight: bold;")

        # Return to the main page after 2 seconds
        QTimer.singleShot(2000, self.go_to_main_page)

    def log_transaction(self, uid):
        # Simulate logging the transaction to the server
        headers = {"X-API-KEY": "keycab.api.key"}
        try:
            # Use self.selected_value to access the selected key value
            res = requests.post('https://keycabinet.cspc.edu.ph/logs/borrowed', json={
                "faculty_id": uid,
                "key_id": self.selected_value,  # Use the selected key value
                "details": "Borrowed laboratory key",
                "date_time_borrowed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, headers=headers)
            print(res.content)
            if res.status_code == 201:
                print("Transaction logged successfully.")
            else:
                print("Failed to log transaction.")
        except Exception as e:
            print(f"Error logging transaction: {str(e)}")

    def handle_error(self, error_message):
        # Display error messages
        self.setStyleSheet("background-color: red; color: white;")  # Set background to red
        self.label.setText(f"Error: {error_message}")

        # Ensure the font size remains consistent
        self.label.setStyleSheet("font-size: 30px; font-weight: bold;")

        # Return to the main page after 2 seconds
        QTimer.singleShot(2000, self.go_to_main_page)

    def go_to_main_page(self):
        # Navigate back to the main page
        self.stacked_widget.setCurrentIndex(0)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_0:  # Check if the '0' key is pressed
            print("User pressed 0: Cancelling scanning and navigating back to the main page.")  # Debugging message
            if hasattr(self, 'nfc_thread') and self.nfc_thread.isRunning():
                self.nfc_thread.stop()  # Stop the NFC thread gracefully
                self.nfc_thread.wait()  # Wait for the thread to finish
            self.go_to_main_page()  # Navigate back to the main page
        else:
            super().keyPressEvent(event)  # Call the base class implementation for other keys
