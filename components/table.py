from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHeaderView, QLabel, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


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


        self.empty_label = QLabel("Пока нет товаров, загрузите файл для расчета")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; padding: 20px;")

        self._resize_to_contents()

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.table)
        layout.addWidget(self.empty_label)
        self.setLayout(layout)
        self._show_empty_state()



    def handle_loading(self,is_loading:bool):
        if is_loading:
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
            self._show_empty_state("Нет товаров")
            self.table.setRowCount(0)
            return
        self._hide_empty_state()

        self.table.setRowCount(len(products))
        self.table.setColumnCount(len(self.keys))

        for row_idx, row_data in enumerate(products):
            for col_idx, key in enumerate(self.keys):
                value = row_data.get(key, "")
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

        self._resize_to_contents()