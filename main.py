import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QStackedWidget, QGridLayout, QHBoxLayout, QGraphicsDropShadowEffect, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QIntValidator  # Import QPixmap for handling images and QFont for setting the font
import requests
from PySide6.QtWidgets import QDialog, QProgressBar, QMessageBox
from PySide6.QtCore import QTimer
from py122u import nfc
from PySide6.QtCore import QThread, Signal
import datetime
from threading import Event
from lock_controller import changeLockState

############################### MAIN PAGE ###############################
class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set the background color of the main page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Create a label and set an image
        image_label = QLabel()
        pixmap = QPixmap("/home/cyrene/keycab_gui/img/CSS.png")  # Replace with the path to your image
        scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Scale the image
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)  # Center-align the image

        # Create a label for the text below the image
        text_label = QLabel("CCS KeyCabinet")
        text_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        text_font = QFont("Times New Roman", 22)  # Set font to Times New Roman, size 22
        text_label.setFont(text_font)

        # Create a vertical layout for the image and text
        image_text_layout = QVBoxLayout()
        image_text_layout.addSpacing(20)  # Add spacing above the image
        image_text_layout.addWidget(image_label)
        image_text_layout.addWidget(text_label)

        # Create a button to go to the keypad page
        keypad_button = QPushButton("[1] Borrow Key")
        keypad_button.setFixedHeight(50)  # Make the button thicker
        keypad_button.clicked.connect(self.go_to_second_page)
        keypad_button.setShortcut("1")  # Assign hotkey '1'

        # Create a button to go to the third page
        third_page_button = QPushButton("[2] Return Key")
        third_page_button.setFixedHeight(50)  # Make the button thicker
        third_page_button.clicked.connect(self.go_to_third_page)
        third_page_button.setShortcut("0")  # Assign hotkey '0'

        # Apply rounded corners, drop shadows, and light blue color to the buttons
        self.style_button(keypad_button)
        self.style_button(third_page_button)

        # Create a vertical layout for the buttons
        button_layout = QVBoxLayout()
        button_layout.addStretch()  # Add stretch above the buttons
        button_layout.addWidget(keypad_button)
        button_layout.addWidget(third_page_button)
        button_layout.addStretch()  # Add stretch below the buttons

        # Add horizontal margins
        button_with_margin_layout = QHBoxLayout()
        button_with_margin_layout.addSpacing(20)  # Add left margin
        button_with_margin_layout.addLayout(button_layout)
        button_with_margin_layout.addSpacing(20)  # Add right margin

        # Create a horizontal layout for the main content
        main_layout = QHBoxLayout()
        main_layout.addLayout(image_text_layout)  # Add the image and text to the left
        main_layout.addLayout(button_with_margin_layout)  # Add the buttons with margins to the right

        # Wrap the main layout in a QWidget to apply rounded corners
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #004080;  /* Slightly darker blue */
                border-radius: 15px;       /* Rounded corners */
                padding: 10px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.addLayout(main_layout)

        # Use a layout to add the container to the main page
        layout = QVBoxLayout()
        layout.addWidget(container)
        self.setLayout(layout)

    def style_button(self, button):
        # Apply rounded corners, light blue color, and hover effect using QSS
        button.setStyleSheet("""
            QPushButton {
                background-color: #0074D9;  /* Light blue background */
                color: white;              /* White text */
                border: none;
                border-radius: 15px;       /* Rounded corners */
                padding: 10px;
                font-size: 16px;           /* Slightly larger font size */
                font-weight: bold;         /* Bold text */
            }
            QPushButton:hover {
                background-color: #005bb5; /* Darker blue on hover */
            }
        """)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(Qt.black)
        button.setGraphicsEffect(shadow)

    def go_to_second_page(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to the keypad page

    def go_to_third_page(self):
        self.stacked_widget.setCurrentIndex(2)  # Switch to the third page
        

############################### KEY SELECT PAGE ###############################
class SecondPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set the background color of the second page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Create a label and set its text
        label = QLabel("Enter the key number (1-9), enter 0 to go back:")
        label.setAlignment(Qt.AlignCenter)
        label_font = QFont("Arial", 30, QFont.Bold)  # Set font to Arial, size 30, bold
        label.setFont(label_font)

        # Create a text field with a validator to accept only numbers 1-9
        self.text_field = QLineEdit()  # Use self to access it in other methods
        self.text_field.setValidator(QIntValidator(0, 9))  # Accept only numbers between 0 and 9
        self.text_field.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.text_field.setFixedHeight(50)  # Make the text field taller
        self.text_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #0074D9;
                border-radius: 10px;
                padding: 5px;
                font-size: 18px;  /* Larger font size */
                font-weight: bold; /* Bold text */
            }
        """)

        # Create a "Proceed" button
        proceed_button = QPushButton("[Numpad Enter] Proceed")
        self.style_button(proceed_button)  # Apply button styling
        proceed_button.clicked.connect(self.confirm_selection)  # Connect to confirmation prompt
        proceed_button.setShortcut(Qt.Key_Enter)  # Assign hotkey [Numpad Enter]

        # Wrap the grid in a QWidget to apply rounded corners
        grid_container = QWidget()
        grid_container.setStyleSheet("""
            QWidget {
                background-color: #004080;  /* Slightly darker blue */
                border-radius: 15px;       /* Rounded corners */
                padding: 10px;
            }
        """)

        # Create a layout for the grid container
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.addWidget(label)
        grid_layout.addWidget(self.text_field)
        grid_layout.addWidget(proceed_button)

        # Use a layout to add the grid container
        layout = QVBoxLayout()
        layout.addWidget(grid_container)
        self.setLayout(layout)

    def showEvent(self, event):
        """Reset the text field when the page is shown."""
        super().showEvent(event)
        self.text_field.clear()  # Clear the text field

    def confirm_selection(self):
        # Get the value from the text field
        value = self.text_field.text()

        # Check if the input is 0
        if value == "0":
            print("User entered 0: Navigating back to the main page.")  # Debugging message
            self.go_to_main_page()
            return

        # Validate the input
        if not value:
            print("Invalid input: Cannot proceed with empty value.")  # Debugging message
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Invalid Input")
            error_dialog.setModal(True)
            error_dialog.setFixedSize(300, 150)

            # Create a label for the error message
            error_label = QLabel("Please enter a valid number (1-9) to proceed.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)

            # Create a button to close the error dialog
            close_button = QPushButton("OK")
            close_button.clicked.connect(error_dialog.accept)

            # Create a layout for the error dialog
            error_layout = QVBoxLayout()
            error_layout.addWidget(error_label)
            error_layout.addWidget(close_button, alignment=Qt.AlignCenter)
            error_dialog.setLayout(error_layout)

            # Show the error dialog
            error_dialog.exec()
            return

        # Show a confirmation prompt
        confirmation = QMessageBox.question(
            self,
            "Confirm Selection",
            f"Are you sure you want to select key {value}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirmation == QMessageBox.Yes:
            # If the user confirms, proceed to the third page
            print(f"User confirmed selection: {value}")  # Debugging message
            self.proceed_to_third_page(value)
        else:
            # If the user cancels, stay on the current page
            print("User canceled the selection.")  # Debugging message

    def proceed_to_third_page(self, value):
        # Print the value to the terminal for debugging
        print(f"Proceeding to third page with value: {value}")

        # Pass the value to the third page
        third_page = self.stacked_widget.widget(2)  # Get the ThirdPage instance
        third_page.set_selected_value(value)  # Pass the value to ThirdPage

        # Navigate to the third page
        self.stacked_widget.setCurrentIndex(2)

    def go_to_main_page(self):
        self.stacked_widget.setCurrentIndex(0)  # Switch back to the main page

    def style_button(self, button):
        # Apply rounded corners, light blue color, and hover effect using QSS
        button.setStyleSheet("""
            QPushButton {
                background-color: #0074D9;  /* Light blue background */
                color: white;              /* White text */
                border: none;
                border-radius: 15px;       /* Rounded corners */
                padding: 10px;
                font-size: 16px;           /* Slightly larger font size */
                font-weight: bold;         /* Bold text */
            }
            QPushButton:hover {
                background-color: #005bb5; /* Darker blue on hover */
            }
        """)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(Qt.black)
        button.setGraphicsEffect(shadow)


############################### CARD SCANNING PAGE ###############################
class ThirdPage(QWidget):
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
        self.label.setText("Getting cardreader data from the server...")

        # Simulate a server request to fetch cardholder data
        try:
            result = getIDholder(uid)
            print(uid + " " + str(result))
            if result[0] == 200:
                self.setStyleSheet("background-color: green; color: white;")  # Set background to green
                self.label.setText("Access granted!")
                changeLockState('unlock')
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


class NFCReaderThread(QThread):
    uid_signal = Signal(str)  # Signal to send the UID to the main thread
    error_signal = Signal(str)  # Signal to send error messages

    def __init__(self):
        super().__init__()
        self.stop_flag = Event()  # Create a stop flag

    def run(self):
        try:
            uid = getUID(self.stop_flag)  # Pass the stop flag to getUID
            if uid:
                self.uid_signal.emit(uid)  # Emit the UID if found
            else:
                self.error_signal.emit("Scanning canceled.")
        except Exception as e:
            self.error_signal.emit(str(e))

    def stop(self):
        """Stop the thread gracefully."""
        self.stop_flag.set()  # Set the stop flag to interrupt getUID


############################### CONNECTION CHECKER ###############################
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


def getIDholder(uid):
    headers = {"X-API-KEY": "keycab.api.key"}
    req = requests.get("https://keycabinet.cspc.edu.ph/api/faculty", headers = headers)
    result = req.json()
    print(result)
    for _faculty in range(len(result)):
        if(str(uid) == result[_faculty]['rfid_uid']):
            if (result[_faculty]['status'] == "Disabled"):
                return [403, result[_faculty]["faculty_id"]]
            else:
                return [200, result[_faculty]["faculty_id"]]
        else:
            continue
    return [404, None]

def getUID(stop_flag): 
    def getID():
        uid_parsed = ""
        try:
            reader = nfc.Reader()
            reader.connect()
            raw_uid = reader.get_uid()
            for _byte in range(len(raw_uid)):
                uid_parsed += f'{raw_uid[_byte]:02x}'  # Ensure two-character hex with leading zeroes
            return uid_parsed
        except Exception as e:
            return None

    while not stop_flag.is_set():  # Check if the stop flag is set
        uid = getID()
        if uid is not None:
            return uid
    return None  # Return None if the stop flag is set

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the connection popup
    server_url = "https://keycabinet.cspc.edu.ph/"
    popup = ConnectionPopup(server_url)
    popup.exec()  # Show the popup as a modal dialog

    # Create a QStackedWidget to manage multiple pages
    stacked_widget = QStackedWidget()

    # Create the main page, second page, and third page
    main_page = MainPage(stacked_widget)
    second_page = SecondPage(stacked_widget)
    third_page = ThirdPage(stacked_widget)

    # Add pages to the stacked widget
    stacked_widget.addWidget(main_page)
    stacked_widget.addWidget(second_page)
    stacked_widget.addWidget(third_page)

    # Set the initial page
    stacked_widget.setCurrentIndex(0)

    # Show the stacked widget in full-screen mode
    stacked_widget.showFullScreen()  # Change from setFixedSize to showFullScreen()

    sys.exit(app.exec())