import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from utils.connection import ConnectionPopup, ConnectionMonitor
from utils.nfc_utils import NFCReaderPopup  # Import the NFC reader popup
from pages.main_page import MainPage
from pages.borrow_key_page import BorrowKeyPage
from pages.borrow_id_scan_page import BorrowIDScanPage
from pages.return_key_page import ReturnKeyPage  # Import the ReturnKeyPage
from pages.return_id_scan_page import ReturnIDScanPage  # Import the ReturnIDScanPage
from utils.connection import show_connection_error_popup

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the NFC reader popup
    nfc_popup = NFCReaderPopup()  # Set font size and weight
    nfc_popup.adjustSize()  # Adjust the size to fit the content
    nfc_popup.exec()  # Show the popup as a modal dialog

    # Create and show the connection popup
    server_url = "https://keycabinet.cspc.edu.ph/"
    popup = ConnectionPopup(server_url)  # Set font size and weight
    popup.adjustSize()  # Adjust the size to fit the content
    popup.exec()  # Show the popup as a modal dialog

    # Create a QStackedWidget to manage multiple pages
    stacked_widget = QStackedWidget()

    # Create the main page, borrow key page, borrow ID scan page, return key page, and return ID scan page
    main_page = MainPage(stacked_widget)
    borrow_key_page = BorrowKeyPage(stacked_widget)
    borrow_id_scan_page = BorrowIDScanPage(stacked_widget)
    return_key_page = ReturnKeyPage(stacked_widget)
    return_id_scan_page = ReturnIDScanPage(stacked_widget)  # Add the return ID scan page

    # Add pages to the stacked widget
    stacked_widget.addWidget(main_page)
    stacked_widget.addWidget(borrow_key_page)
    stacked_widget.addWidget(borrow_id_scan_page)
    stacked_widget.addWidget(return_key_page)
    stacked_widget.addWidget(return_id_scan_page)  # Add the return ID scan page to the stack

    # Set the initial page
    stacked_widget.setCurrentIndex(0)

    # Show the stacked widget in full-screen mode
    stacked_widget.showFullScreen()

    # Start the connection monitor
    connection_monitor = ConnectionMonitor(server_url)
    connection_monitor.connection_lost_signal.connect(
        lambda: show_connection_error_popup(app, connection_monitor.connection_restored_signal)
    )
    connection_monitor.start()

    # Ensure the connection monitor stops when the app exits
    app.aboutToQuit.connect(connection_monitor.stop)

    sys.exit(app.exec())