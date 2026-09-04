import math
import os

from PySide6.QtCore import QObject, QThreadPool, Signal

from .sheet_worker import SheetWorker
import pandas as pd

class ProductsLoader(QObject):
    all_done = Signal(list)   # финальный список dict-ов (records)

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.pool = QThreadPool.globalInstance()
        self.results: dict[str, pd.DataFrame] = {}
        self.errors: dict[str, str] = {}
        self.total_sheets = 0

    def start(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")

        excel_file = pd.ExcelFile(self.file_path)
        sheets = excel_file.sheet_names
        self.total_sheets = len(sheets)

        for sheet in sheets:
            worker = SheetWorker(sheet, self.file_path)
            worker.signals.finished.connect(self._on_sheet_done)
            worker.signals.error.connect(self._on_sheet_error)
            self.pool.start(worker)

    def _on_sheet_done(self, sheet_name, df):
        self.results[sheet_name] = df
        self._check_complete()

    def _on_sheet_error(self, sheet_name, msg):
        print("Error",msg)
        self.errors[sheet_name] = msg
        self._check_complete()

    def _check_complete(self):
        if len(self.results) + len(self.errors) == self.total_sheets:
            merged = pd.concat(self.results.values(), ignore_index=True)
            # records = merged.to_dict("records")
            # records = [
            #     {
            #         "part_weight": int(record["weight_g"]) if pd.notna(record.get("weight_g")) else 0,
            #         "sku": str(record["PNUS"]) if pd.notna(record.get("PNUS")) else "",
            #         "part_id": str(record["номер"]) if pd.notna(record.get("номер")) else "",
            #         "name": str(record["local_part_name"]) if pd.notna(record.get("local_part_name")) else "",
            #     } for record in records
            # ]

            records = self.__merge_records(merged)
            
            self.all_done.emit(records)

    def __merge_records(self,merged):
        merged["part_weight"] = merged["weight_g"].fillna(0).astype(int)
        merged["sku"] = merged["PNUS"].fillna("").astype(str)
        merged["part_id"] = merged["номер"].fillna("").astype(str)
        merged["name"] = merged["local_part_name"].fillna("").astype(str)
        records = merged[["part_weight", "sku", "part_id", "name"]].to_dict("records")
        return records