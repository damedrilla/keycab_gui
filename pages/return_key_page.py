from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator  # Import QPixmap for handling images and QFont for setting the font
from PySide6.QtWidgets import QDialog, QMessageBox


class ReturnKeyPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set the background color of the borrow key page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Create a label and set its text
        label = QLabel("Enter the key number (1-9), enter 0 to go back:")
        label.setAlignment(Qt.AlignCenter)
        label_font = QFont("Arial", 30, QFont.Bold)  # Set font to Arial, size 30, bold
        label.setFont(label_font)

        # Create a text field with a validator to accept only numbers 0-9
        self.text_field = QLineEdit()  # Use self to access it in other methods
        self.text_field.setValidator(QIntValidator(0, 9))  # Accept only numbers between 0 and 9
        self.text_field.setMaxLength(1)  # Restrict input to only one character
        self.text_field.setAlignment(Qt.AlignCenter)  # Center-align the text

        # Style the text field
        self.text_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #0074D9;
                border-radius: 10px;
                padding: 10px;             /* Increase padding for better spacing */
                font-size: 20px;           /* Larger font size for better visibility */
                font-weight: bold;         /* Bold text */
            }
        """)

        # Set a fixed height for the text field to make it taller
        self.text_field.setFixedHeight(50)  # Increase the height to 50px for better visibility

        # Create a "Proceed" button
        proceed_button = QPushButton("[Enter] Proceed")
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
        """Reset the text field and focus the cursor when the page is shown."""
        super().showEvent(event)
        self.text_field.clear()  # Clear the text field
        self.text_field.setFocus()  # Focus the cursor on the text field

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
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirm Selection")
        confirmation.setText(f"Are you sure you want to select key {value}?")
        confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Resize the confirmation popup
        confirmation.resize(750, 450)  # Set the size to 750x450

        # Add hotkeys for Yes and No buttons
        yes_button = confirmation.button(QMessageBox.Yes)
        yes_button.setShortcut(Qt.Key_Enter)  # Numpad Enter for Yes

        no_button = confirmation.button(QMessageBox.No)
        no_button.setShortcut(Qt.Key_0)  # Numpad 0 for No

        # Show the confirmation dialog
        result = confirmation.exec()

        if result == QMessageBox.Yes:
            # If the user confirms, proceed to the borrow ID scan page
            print(f"User confirmed selection: {value}")  # Debugging message
            self.proceed_to_borrow_id_scan_page(value)
        else:
            # If the user cancels, stay on the current page
            print("User canceled the selection.")  # Debugging message

    def proceed_to_borrow_id_scan_page(self, value):
        # Print the value to the terminal for debugging
        print(f"Proceeding to borrow ID scan page with value: {value}")

        # Pass the value to the borrow ID scan page
        borrow_id_scan_page = self.stacked_widget.widget(2)  # Get the BorrowIDScanPage instance
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