from PySide6.QtCore import Slot
from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QWidget


class LoadingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Загрузка...")
        self.progress_bar.setFixedHeight(22)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.progress_bar)
        self.setVisible(False)

    @Slot(bool)
    def set_loading(self, is_loading: bool) -> None:
        self.setVisible(is_loading)