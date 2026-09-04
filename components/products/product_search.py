from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget


class ProductSearch(QWidget):
    searchStarted = Signal(str)

    def __init__(self):
        super().__init__()

        self.debounce_timer = QTimer()

        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Поиск по названию, SKU или номеру детали...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 16px;
                border: 1px solid #D0D5DD;
                border-radius: 19px;
                background-color: #FFFFFF;
                font-size: 14px;
                color: #101828;
            }
            QLineEdit:hover {
                border: 1px solid #98A2B3;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
                outline: none;
            }
        """)

        self.debounce_timer.timeout.connect(self.apply_search)
        self.text_input.textChanged.connect(self._start_search_timer)

        layout = QVBoxLayout()
        layout.addWidget(self.text_input)
        self.setLayout(layout)

    def _start_search_timer(self, _text: str) -> None:
        self.debounce_timer.start()

    def apply_search(self):
        text = self.text_input.text()
        self.searchStarted.emit(text)
