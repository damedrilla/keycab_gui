from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect, QLineEdit, QGridLayout, QFrame, QMessageBox
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QFont, QIntValidator, QColor
import requests  # Import the requests library for API calls

class APIWorker(QObject):
    data_fetched = Signal(list)  # Signal to emit the fetched data
    error_occurred = Signal(str)  # Signal to emit in case of an error

    @Slot()
    def fetch_key_data(self):
        """Fetch key data from the API."""
        try:
            headers = {"X-API-KEY": "keycab.api.key"}
            response = requests.get("https://keycabinet.cspc.edu.ph/api/key", headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            key_data = response.json()  # Parse the JSON response
            self.data_fetched.emit(key_data)  # Emit the fetched data
        except requests.RequestException as e:
            self.error_occurred.emit(str(e))  # Emit the error message

class ReturnKeyPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.key_data = []  # Initialize key data as an empty list

        # Create a loading indicator
        self.loading_label = QLabel("Getting key status...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 20px; color: white;")
        self.loading_label.hide()  # Initially hide the loading label

        # Set the background color of the borrow key page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Create a label and set its text
        label = QLabel("Enter the key number to return (enter 0 to exit)")
        label.setAlignment(Qt.AlignCenter)
        label_font = QFont("Arial", 30, QFont.Bold)  # Set font to Arial, size 30, bold
        label.setFont(label_font)

        # Create a text field with a validator to accept only numbers 0-9
        self.text_field = QLineEdit()
        self.text_field.setValidator(QIntValidator(0, 9))  # Accept only numbers between 0 and 9
        self.text_field.setMaxLength(1)  # Restrict input to only one character
        self.text_field.setAlignment(Qt.AlignCenter)

        # Style the text field
        self.text_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #0074D9;
                border-radius: 10px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        self.text_field.setFixedHeight(50)

        # Create a "Proceed" button
        proceed_button = QPushButton("[Enter] Proceed")
        self.style_button(proceed_button)
        proceed_button.clicked.connect(self.confirm_selection)
        proceed_button.setShortcut(Qt.Key_Enter)

        # Create the key status grid
        self.key_status_grid = QGridLayout()

        # Wrap the grid in a QWidget to apply rounded corners
        grid_container = QWidget()
        grid_container.setStyleSheet("""
            QWidget {
                background-color: #004080;  /* Slightly darker blue */
                border-radius: 15px;       /* Rounded corners */
                padding: 10px;
            }
        """)
        grid_container.setLayout(self.key_status_grid)

        # Create a layout for the page
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.text_field)
        layout.addWidget(proceed_button)
        layout.addWidget(self.loading_label)  # Add the loading label to the layout
        layout.addWidget(grid_container)
        self.setLayout(layout)

        # Create a thread and worker for the API call
        self.api_thread = QThread()
        self.api_worker = APIWorker()
        self.api_worker.moveToThread(self.api_thread)

        # Connect signals and slots
        self.api_worker.data_fetched.connect(self.on_key_data_fetched)
        self.api_worker.error_occurred.connect(self.on_api_error)
        self.api_thread.started.connect(self.api_worker.fetch_key_data)

    def showEvent(self, event):
        """Reset the text field, focus the cursor, and fetch the latest key data when the page is shown."""
        super().showEvent(event)
        self.text_field.clear()  # Clear the text field
        self.text_field.setFocus()  # Focus the cursor on the text field

        # Show the loading indicator and hide the grid
        self.loading_label.show()
        self.key_status_grid.setEnabled(False)

        # Start the API call in a separate thread
        self.api_thread.start()

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
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid number.")
            return

        # Convert the input to an integer
        try:
            key_id = int(value)
        except ValueError:
            print("Invalid input: Not a number.")  # Debugging message
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid number.")
            return

        # Check if the key ID exists in the fetched key data
        selected_key = next((key for key in self.key_data if key["key_id"] == key_id), None)
        if not selected_key:
            print(f"Key {key_id} does not exist.")  # Debugging message
            QMessageBox.critical(self, "Invalid Key", f"Key {key_id} does not exist.")
            return

        # Check if the selected key is "Available" (prevent selection)
        if selected_key["status"] == "Available":
            print(f"Key {key_id} is available and cannot be returned.")  # Debugging message
            QMessageBox.critical(self, "Invalid Selection", f"Key {key_id} is available and cannot be returned.")
            return

        # Show a confirmation prompt
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirm Selection")
        confirmation.setText(f"Are you sure you want to return key {value}?")
        confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Add hotkey for QMessageBox.No (Numpad 0)
        no_button = confirmation.button(QMessageBox.No)
        no_button.setShortcut(Qt.Key_0)  # Set Numpad 0 as the shortcut for "No"

        result = confirmation.exec()
        if result == QMessageBox.Yes:
            print(f"User confirmed selection: {value}")  # Debugging message
            self.proceed_to_borrow_id_scan_page(value)
        else:
            print("User canceled the selection.")  # Debugging message

    def proceed_to_borrow_id_scan_page(self, value):
        # Print the value to the terminal for debugging
        print(f"Proceeding to borrow ID scan page with value: {value}")

        # Pass the value to the borrow ID scan page
        borrow_id_scan_page = self.stacked_widget.widget(4)  # Get the BorrowIDScanPage instance
        borrow_id_scan_page.set_selected_value(value)  # Pass the value to BorrowIDScanPage

        # Navigate to the borrow ID scan page
        self.stacked_widget.setCurrentIndex(4)

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
                padding: 15px;             /* Increase padding for a taller button */
                font-size: 20px;           /* Larger font size for better visibility */
                font-weight: bold;         /* Bold text */
            }
            QPushButton:hover {
                background-color: #005bb5; /* Darker blue on hover */
            }
        """)

        # Set a fixed height for the button to make it taller
        button.setFixedHeight(70)  # Increase the height to 70px for better visibility

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(Qt.black)
        button.setGraphicsEffect(shadow)

    def populate_key_status_grid(self):
        """Populate the key status grid with tiles."""

        # Clear the grid layout before populating it
        while self.key_status_grid.count():
            item = self.key_status_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Populate the grid with tiles
        for index, key in enumerate(self.key_data):
            tile = QFrame()
            tile.setFixedSize(100, 100)
            is_available = key['status'] == 'Available'
            tile.setStyleSheet(f"""
                QFrame {{
                    background-color: {'blue' if is_available else 'red'};
                    border-radius: 10px;
                }}
            """)

            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(0, 0, 0, 0)
            tile_layout.setAlignment(Qt.AlignCenter)

            label = QLabel(f"Key {key['key_id']}\n{key['laboratory']}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
            tile_layout.addWidget(label)

            if not is_available:
                tile.setEnabled(False)

            row = index // 3
            col = index % 3
            self.key_status_grid.addWidget(tile, row, col)

    def on_key_data_fetched(self, key_data):
        """Handle the fetched key data."""
        self.key_data = key_data  # Update the key data
        self.api_thread.quit()  # Stop the thread

        # Hide the loading indicator and enable the grid
        self.loading_label.hide()
        self.key_status_grid.setEnabled(True)

        self.populate_key_status_grid()  # Populate the grid with the new data

    def on_api_error(self, error_message):
        """Handle API errors."""
        self.api_thread.quit()  # Stop the thread

        # Hide the loading indicator and enable the grid
        self.loading_label.hide()
        self.key_status_grid.setEnabled(True)

        QMessageBox.critical(self, "Error", f"Failed to fetch key data: {error_message}")
        self.key_data = []  # Clear the key data
        self.populate_key_status_grid()  # Clear the grid