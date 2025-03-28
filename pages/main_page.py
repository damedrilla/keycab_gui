import platform  # Import platform to check the operating system
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set the background color of the main page
        self.setStyleSheet("background-color: #001f3f; color: white;")  # Dark blue background, white text

        # Determine the image path based on the operating system
        image_path = self.get_image_path()

        # Create a label and set an image
        image_label = QLabel()
        pixmap = QPixmap(image_path)  # Use the determined image path
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

    def get_image_path(self):
        """Determine the image path based on the operating system."""
        if platform.system() == "Windows":
            return "img/CSS.png"  # Windows path
        else:
            return "/home/cyrene/keycab_gui/img/CSS.png"  # Linux path

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

    def go_to_second_page(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to the keypad page

    def go_to_third_page(self):
        self.stacked_widget.setCurrentIndex(2)  # Switch to the third page