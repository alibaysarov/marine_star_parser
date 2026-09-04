

from PySide6.QtWidgets import QVBoxLayout

from components import CustomTab
from components.loading import LoadingIndicator
from components.products.product_search import ProductSearch
from components.products.product_table import ProductTable
from components.products.product_upload import ProductUpload


class ProductsTab(CustomTab):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.search = ProductSearch()
        self.product_upload = ProductUpload()
        self.product_table = ProductTable()
        self.loading_indicator = LoadingIndicator()
        layout.addWidget(self.product_upload)
        layout.addWidget(self.loading_indicator)
        layout.addWidget(self.search)
        layout.addWidget(self.product_table)
        self.setLayout(layout)

        self.search.searchStarted.connect(self.product_table.set_search)
        self.product_upload.is_loading.connect(self.loading_indicator.set_loading)
        self.product_upload.productsLoaded.connect(self._on_products_loaded)
        self.product_table.load_page()

    def _on_products_loaded(self, _records: list) -> None:
        self.product_table.refresh()
        
    def get_name(self) -> str:
        return "Номенклатура"
