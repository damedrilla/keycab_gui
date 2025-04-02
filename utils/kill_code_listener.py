from PySide6.QtCore import QThread, Signal

class KillCodeListener(QThread):
    kill_signal = Signal()  # Signal to trigger the kill action

    def __init__(self, text_field, kill_code):
        super().__init__()
        self.text_field = text_field
        self.kill_code = kill_code
        self.running = True

    def run(self):
        while self.running:
            # Check if the text field contains the kill code
            if self.text_field.text() == self.kill_code:
                self.kill_signal.emit()  # Emit the kill signal
                self.running = False  # Stop the thread