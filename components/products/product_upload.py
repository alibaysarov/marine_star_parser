from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app_logging import logger
from excel_parser import ProductsLoader
from helpers.get_selected_file import get_selected_file_path
from service.parts_service import PartsService


class ProductUpload(QWidget):
    productsLoaded = Signal(list)
    is_loading = Signal(bool)

    def __init__(self):
        super().__init__()
        self.loader = None
        self._records = []
        self.parts_service = PartsService()
        layout = QVBoxLayout()

        self.file_label = QLabel("Файл не выбран", self)
        self.file_label.setStyleSheet("""
            padding:5px 20px;
            padding-left:0px;
            border-radius:45px;
            width:25%;
        """)
        layout.addWidget(self.file_label)

        self.upload_btn = QPushButton("Загрузить номенклатуру", self)
        self.upload_btn.clicked.connect(self.open_file_dialog)

        self.upload_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def open_file_dialog(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Файлы таблиц (*.xlsx *.xls *.csv);;Excel файлы (*.xlsx *.xls);;CSV файлы (*.csv);;Все файлы (*)",
        )
        selected_file = get_selected_file_path(self.file_path)
        self.file_label.setText(selected_file)
        if selected_file:
            print("File is ", selected_file)
            self.is_loading.emit(True)
            self.loader = ProductsLoader(self.file_path)
            self.loader.all_done.connect(self.handle_load)
            self.loader.error.connect(self._on_upload_error)
            try:
                self.loader.start()
            except Exception as error:
                logger.exception("Ошибка запуска загрузки номенклатуры: %s", self.file_path)
                self.is_loading.emit(False)
                self._on_upload_error(error)

    def handle_load(self, records: list):
        print("Loading files...")
        self._records = records
        self.parts_service.upload_parts_async(
            records,
            on_success=self._on_parts_upload,
            on_error=self._on_upload_error,
        )

    def _on_parts_upload(self, _result=None):
        self.is_loading.emit(False)
        self.productsLoaded.emit(self._records)
        QMessageBox.information(self, "Товары загружены", "товары загружены")

    def _on_upload_error(self, error: Exception):
        logger.error("Ошибка загрузки номенклатуры: %s", error)
        self.is_loading.emit(False)
        QMessageBox.critical(self, "Ошибка", str(error))
