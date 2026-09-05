from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from helpers.excel_export import export_rows_to_excel


class ResultTable(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.table = QTableWidget()

        self.keys = [
            "part_no",
            "description",
            "translated",
            "part_weight",
            "qty",
            "final_total",
            "unit_price",
            "marge",
        ]
        self.headers = [
            "№ Запчасти",
            "Название",
            "Перевод",
            "Вес (гр.)",
            "Кол-во",
            "Итого",
            "Цена за ед. с маржой",
            "% Маржи",
        ]

        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.page_size = 10
        self.products = []
        self.current_page = 0

        self.export_button = QPushButton("Экспортировать в Excel", self)
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setVisible(False)

        self.previous_page_button = QPushButton("Назад", self)
        self.previous_page_button.clicked.connect(self._show_previous_page)
        self.next_page_button = QPushButton("Вперёд", self)
        self.next_page_button.clicked.connect(self._show_next_page)
        self.page_label = QLabel("Страница 0 из 0", self)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(self.previous_page_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_page_button)

        self.empty_label = QLabel("Пока нет товаров, загрузите файл для расчета")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; padding: 20px;")

        self._resize_to_contents()

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)
        layout.addWidget(self.export_button)
        layout.addWidget(self.empty_label)
        self.setLayout(layout)
        self._set_pagination_enabled(False)
        self._show_empty_state()

    def handle_loading(self, is_loading: bool):
        if is_loading:
            self.export_button.setVisible(False)
            self._set_pagination_enabled(False)
            self._show_empty_state("Загрузка...")
        else:
            self._hide_empty_state()

    def _show_empty_state(self, text="Пока нет товаров, загрузите файл для расчета"):
        self.empty_label.setText(text)
        self.empty_label.setVisible(True)
        self.table.setVisible(False)

    def _hide_empty_state(self):
        self.empty_label.setVisible(False)
        self.table.setVisible(True)

    def _resize_to_contents(self):
        header_height = self.table.horizontalHeader().height()
        rows_height = sum(self.table.rowHeight(r) for r in range(self.table.rowCount()))
        frame = self.table.frameWidth() * 2
        total_height = header_height + rows_height + frame
        self.table.setFixedHeight(total_height)

    def _set_pagination_enabled(self, enabled: bool):
        self.previous_page_button.setEnabled(enabled and self.current_page > 0)
        self.next_page_button.setEnabled(
            enabled and (self.current_page + 1) * self.page_size < len(self.products)
        )
        page_count = (len(self.products) + self.page_size - 1) // self.page_size
        self.page_label.setText(
            f"Страница {self.current_page + 1} из {page_count}" if enabled else "Страница 0 из 0"
        )

    def _render_current_page(self):
        start = self.current_page * self.page_size
        page_products = self.products[start : start + self.page_size]
        self.table.setRowCount(len(page_products))
        self.table.setColumnCount(len(self.keys))

        for row_idx, row_data in enumerate(page_products):
            for col_idx, key in enumerate(self.keys):
                value = row_data.get(key, "")
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self._set_pagination_enabled(bool(self.products))
        self._resize_to_contents()

    def _show_previous_page(self):
        if self.current_page == 0:
            return
        self.current_page -= 1
        self._render_current_page()

    def _show_next_page(self):
        if (self.current_page + 1) * self.page_size >= len(self.products):
            return
        self.current_page += 1
        self._render_current_page()

    def on_cell_clicked(self, row, column):
        item = self.table.item(row, column)
        if item:
            print(f"Clicked cell at Row {row}, Column {column}. Value: {item.text()}")

    def handle_signal(self, products):
        if hasattr(products, "to_dict"):
            products = products.to_dict("records")

        self.products = products or []
        self.current_page = 0
        if not self.products:
            self.export_button.setVisible(False)
            self._set_pagination_enabled(False)
            self._show_empty_state("Нет товаров")
            self.table.setRowCount(0)
            return
        self._hide_empty_state()
        self.export_button.setVisible(True)
        self._render_current_page()

    def export_to_excel(self):
        if not self.products:
            return

        default_name = datetime.now().strftime("marine_star_export_%Y-%m-%d_%H-%M-%S.xlsx")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить таблицу Excel",
            default_name,
            "Excel файлы (*.xlsx)",
        )
        if not file_path:
            return

        rows = [[str(product.get(key, "")) for key in self.keys] for product in self.products]

        try:
            output_path = export_rows_to_excel(self.headers, rows, file_path)
        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(self, "Ошибка экспорта", str(error))
            return

        QMessageBox.information(
            self,
            "Экспорт завершён",
            f"Файл сохранен в {output_path}",
        )
