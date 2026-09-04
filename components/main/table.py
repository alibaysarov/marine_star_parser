from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
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

        self.headers = ["№", "ID", "Название", "Кол-во", "Цена","Цена за штуку (с маржой)"]
        self.keys    = ["col_0", "col_2", "col_5", "col_10", "col_20","marge_price"]

        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.on_cell_clicked)

        self.export_button = QPushButton("Экспортировать в Excel", self)
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setVisible(False)

        self.empty_label = QLabel("Пока нет товаров, загрузите файл для расчета")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; padding: 20px;")

        self._resize_to_contents()

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.table)
        layout.addWidget(self.export_button)
        layout.addWidget(self.empty_label)
        self.setLayout(layout)
        self._show_empty_state()



    def handle_loading(self,is_loading:bool):
        if is_loading:
            self.export_button.setVisible(False)
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

    def on_cell_clicked(self, row, column):
        item = self.table.item(row, column)
        if item:
            print(f"Clicked cell at Row {row}, Column {column}. Value: {item.text()}")

    def handle_signal(self, products: list[dict]):
        if not products:
            self.export_button.setVisible(False)
            self._show_empty_state("Нет товаров")
            self.table.setRowCount(0)
            return
        self._hide_empty_state()
        self.export_button.setVisible(True)

        self.table.setRowCount(len(products))
        self.table.setColumnCount(len(self.keys))

        for row_idx, row_data in enumerate(products):
            for col_idx, key in enumerate(self.keys):
                value = row_data.get(key, "")
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

        self._resize_to_contents()

    def export_to_excel(self):
        if self.table.rowCount() == 0:
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

        rows = [
            [
                self.table.item(row, column).text()
                if self.table.item(row, column) is not None
                else ""
                for column in range(self.table.columnCount())
            ]
            for row in range(self.table.rowCount())
        ]

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