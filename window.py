from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow

from components import CustomTab
from components.tab_widget import TabWidget
from components.tabs.main_tab import MainTab
from components.tabs.products_tab import ProductsTab

class MainWindow(QMainWindow):


    def __setup_window(self):
        self.setWindowTitle("Marine star parser")
        icon = QIcon("assets/logo.jpg")
        self.setWindowIcon(icon)
        self.resize(1024, 800)

    def __init__(self):
        super().__init__()
        self.__setup_window()
        # widgets
        self.__setup_widgets()

    def __setup_widgets(self):
        self.tab_widget = TabWidget(self,self.__get_tabs())
        self.setCentralWidget(self.tab_widget)


    def __get_tabs(self)->list[CustomTab]:
        main_tab = MainTab()
        product_tab = ProductsTab()
        return [main_tab,product_tab]
