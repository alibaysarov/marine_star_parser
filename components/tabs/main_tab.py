from PySide6.QtWidgets import QVBoxLayout

from components.loading import LoadingIndicator
from components.main.input import InputComponent
from components.tab_widget import CustomTab
from components.main.table import ResultTable


class MainTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.__init_widgets()
        self.__connect_signals()

    def get_name(self) -> str:
        return "Главная"

    def __init_widgets(self):
        layout = QVBoxLayout()
        
        self.input_component = InputComponent()
        self.result_table = ResultTable()
        self.loading_indicator = LoadingIndicator()
        layout.addWidget(self.input_component)
        layout.addWidget(self.loading_indicator)
        layout.addWidget(self.result_table)
        layout.addStretch()
        self.setLayout(layout)

    def __connect_signals(self):
        self.input_component.file_uploader.is_loading.connect(
            self.loading_indicator.set_loading
        )
        self.input_component.file_uploader.is_loading.connect(self.result_table.handle_loading)
        self.input_component.productsLoaded.connect(self.result_table.handle_signal)

    
    