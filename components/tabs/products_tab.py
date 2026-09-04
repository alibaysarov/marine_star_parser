

from PySide6.QtWidgets import QVBoxLayout

from components import CustomTab
from components.products.product_search import ProductSearch
from components.products.product_upload import ProductUpload


class ProductsTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.search = ProductSearch()
        self.product_upload = ProductUpload()
        layout.addWidget(self.product_upload)
        layout.addWidget(self.search)

        layout.addStretch()
        self.setLayout(layout)
        
    def get_name(self) -> str:
        return "Номенклатура"
