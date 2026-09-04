from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from service.parts_service import PartsService


class ProductTable(QWidget):
    HEADERS = ["ID", "Наименование", "SKU", "Номер детали", "Вес, г"]

    def __init__(self):
        super().__init__()
        self.parts_service = PartsService()
        self.search_text = ""
        self.page = 1
        self.per_page = 50

        self.table = QTableWidget(0, len(self.HEADERS), self)
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(False)

        self.previous_btn = QPushButton("Назад", self)
        self.next_btn = QPushButton("Далее", self)
        self.page_label = QLabel("Страница 1", self)
        self.previous_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)
        self.previous_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

        pagination = QHBoxLayout()
        pagination.addWidget(self.previous_btn)
        pagination.addWidget(self.page_label)
        pagination.addWidget(self.next_btn)
        pagination.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(pagination)

    def load_page(self, page: int = 1) -> None:
        self.page = max(page, 1)
        self.previous_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.parts_service.load_parts_async(
            search=self.search_text or None,
            page=self.page,
            per_page=self.per_page,
            on_success=self._show_page,
            on_error=self._show_error,
        )

    def set_search(self, search: str) -> None:
        self.search_text = search.strip()
        self.load_page()

    def refresh(self) -> None:
        self.load_page(self.page)

    def previous_page(self) -> None:
        if self.page > 1:
            self.load_page(self.page - 1)

    def next_page(self) -> None:
        self.load_page(self.page + 1)

    def _show_page(self, parts: list) -> None:
        self.table.setRowCount(len(parts))
        for row, part in enumerate(parts):
            values = [part.id, part.name, part.sku, part.part_id, part.part_weight]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column in (0, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, column, item)

        self.page_label.setText(f"Страница {self.page}")
        self.previous_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(len(parts) == self.per_page)

    def _show_error(self, error: Exception) -> None:
        self.previous_btn.setEnabled(self.page > 1)
        QMessageBox.critical(self, "Ошибка загрузки", str(error))