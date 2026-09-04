import os
import pandas as pd
from PySide6.QtCore import QObject, QRunnable, Signal, Slot, QThreadPool


class SheetSignals(QObject):
    # QRunnable сам не умеет эмитить сигналы, поэтому нужен отдельный QObject
    finished = Signal(str, object)   # имя листа, DataFrame
    error = Signal(str, str)         # имя листа, текст ошибки


class SheetWorker(QRunnable):
    def __init__(self, sheet_name: str, file_path: str):
        super().__init__()
        self.sheet_name = sheet_name
        self.file_path = file_path
        self.signals = SheetSignals()

    @Slot()
    def run(self):
        try:
            
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name,engine="calamine")
            # Удаляем строки только если пуст ключевой идентификатор детали.
            # Остальные поля (supersession, packing, volume_cm3 и т.д.)
            # необязательны и не должны выбрасывать строку целиком.
            df = df.dropna(subset=["PNUS", "номер","local_part_name"])
            self.signals.finished.emit(self.sheet_name, df)
        except Exception as e:
            self.signals.error.emit(self.sheet_name, str(e))
