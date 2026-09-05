import re

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from components.main.file_uploader import FileUploaderWidget


class InputComponent(QWidget):
    productsLoaded = Signal(object)
    marginInputChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # 1. Create a vertical layout
        layout = QVBoxLayout()
        self.debounce_timer = QTimer()

        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)

        self.file_uploader = FileUploaderWidget()
        layout.addWidget(self.file_uploader)
        self.file_uploader.productsLoaded.connect(self.productsLoaded.emit)
        # 2. Create the text input widget (QLineEdit)
        self.text_input = QLineEdit(self)
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

        self.text_input.setPlaceholderText("Введи % маржи...")
        self.text_input.setValidator(QIntValidator(0, 999))
        layout.addWidget(self.text_input)
        self.text_input.textChanged.connect(self.filter_digits)

        self.debounce_timer.timeout.connect(self.apply_calc)

        self.marginInputChanged.connect(self.file_uploader.handle_margin)

        # Set window properties
        self.setLayout(layout)

    def apply_calc(self):
        text = self.text_input.text()
        margin_value = int(text) if text else 0
        print("marge ", margin_value)
        self.marginInputChanged.emit(margin_value)

    def filter_digits(self, text):
        self.debounce_timer.stop()
        self.debounce_timer.start()
        filtered = re.sub(r"\D", "", text)
        if filtered != text:
            # setText спровоцирует повторный textChanged → filter_digits
            # уже с чистым текстом, и вторым проходом сработает ветка emit ниже.
            self.text_input.setText(filtered)
            return
