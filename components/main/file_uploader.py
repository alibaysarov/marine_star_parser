from PySide6.QtWidgets import QHBoxLayout, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,QSizePolicy
from PySide6.QtCore import QObject, QThread, Qt, Signal
from components.labels.toast import Toast, ToastType
from exceptions.exceptions import TableNotFoundError
from pdf_parser.parse import calculate_products_from_file, update_product_price



class ProductWorker(QObject):
    finished = Signal(list)
    error = Signal(Exception)

    def __init__(self, file_path, margin, need_translation, products=None):
        super().__init__()
        self.file_path = file_path
        self.margin = margin
        self.need_translation = need_translation
        self.products = products

    def run(self):
        try:
            if self.need_translation:
                result = calculate_products_from_file(self.file_path, self.margin)
            else:
                result = update_product_price(self.products if self.products else [], self.margin)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


class FileUploaderWidget(QWidget):
    productsLoaded = Signal(list)
    marginChanged = Signal(int)
    is_loading = Signal(bool)
    def __init__(self):
        super().__init__()
        self.initUI()

    def handle_margin(self,margin:int):
        self.margin = margin
        print("Margin handled")
        self.update_products(False,"Маржа обновлена!")

    def initUI(self):
        self.file_path = ""
        self.margin = 0
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # Set up window properties
        self.setGeometry(100, 100, 400, 200)
        self.marginChanged.connect(self.handle_margin)
        # Create a layout
        layout = QVBoxLayout()

        # Create a label to display the selected file path
        self.file_label = QLabel('Файл не выбран', self)
        self.file_label.setStyleSheet("""
            padding:5px 20px;
            padding-left:0px;
            border-radius:45px;
            width:25%;
        """)
        layout.addWidget(self.file_label)

        # Create the upload button
        self.upload_btn = QPushButton('Загрузить файл', self)
        # Connect the button click event to the file picker function
        self.upload_btn.clicked.connect(self.open_file_dialog)

        self.upload_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addWidget(self.upload_btn)

        layout.addStretch()
        # Apply layout to the window
        self.setLayout(layout)

    def open_file_dialog(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if self.file_path:
            self.file_label.setText(f"Selected File:\n{self.file_path.split('/')[-1]}")
            self.update_products(True)
                
    def update_products(self, need_translation=True, notification_message="Товары загружены"):
        if not self.file_path:
            return

        self._pending_message = notification_message
        self.is_loading.emit(True)

        self._thread = QThread()
        self._worker = ProductWorker(
            self.file_path, self.margin, need_translation,
            getattr(self, "products", None)
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        # ВАЖНО: явная QueuedConnection вместо lambda,
        # чтобы слоты гарантированно выполнялись в главном потоке
        self._worker.finished.connect(self._on_success, Qt.ConnectionType.QueuedConnection)
        self._worker.error.connect(self._on_error, Qt.ConnectionType.QueuedConnection)

        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
    
    def _on_success(self, products):
        self.products = products
        self.is_loading.emit(False)
        self.productsLoaded.emit(products)
        self.show_notification(self._pending_message)

    def _on_error(self, e):
        self.is_loading.emit(False)
        if isinstance(e, TableNotFoundError):
            Toast(self.window(), f"Ошибка обработки файла: {e}", type=ToastType.ERROR)
        else:
            print(e)
            Toast(self.window(), "Ошибка обработки файла: попробуйте позже", type=ToastType.ERROR)

    def show_notification(self, message: str, duration_ms: int = 3000):
        Toast(self.window(), message, duration_ms, type=ToastType.INFO)
        