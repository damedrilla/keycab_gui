import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
from utils.connection import ConnectionPopup, ConnectionMonitor
from utils.nfc_utils import NFCReaderPopup  # Import the NFC reader popup
from pages.main_page import MainPage
from pages.borrow_key_page import BorrowKeyPage
from pages.borrow_id_scan_page import BorrowIDScanPage
from utils.connection import show_connection_error_popup

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the NFC reader popup
    nfc_popup = NFCReaderPopup()
    nfc_popup.exec()  # Show the popup as a modal dialog

    # Create and show the connection popup
    server_url = "https://keycabinet.cspc.edu.ph/"
    popup = ConnectionPopup(server_url)
    popup.exec()  # Show the popup as a modal dialog

    # Create a QStackedWidget to manage multiple pages
    stacked_widget = QStackedWidget()

    # Create the main page, borrow key page, and borrow ID scan page
    main_page = MainPage(stacked_widget)
    borrow_key_page = BorrowKeyPage(stacked_widget)
    borrow_id_scan_page = BorrowIDScanPage(stacked_widget)

    # Add pages to the stacked widget
    stacked_widget.addWidget(main_page)
    stacked_widget.addWidget(borrow_key_page)
    stacked_widget.addWidget(borrow_id_scan_page)

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