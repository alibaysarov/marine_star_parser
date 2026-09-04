from abc import abstractmethod

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget


class CustomTab(QWidget):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_name(self) -> str:
        pass


class TabWidget(QWidget):
    def __init__(self, parent, tab_items: list[CustomTab]):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()

        for tab in tab_items:
            self.tabs.addTab(tab, tab.get_name())

        # Add tabs to widget
        layout.addWidget(self.tabs)
        self.setLayout(layout)
