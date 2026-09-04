import pandas as pd

from excel_parser.product_loader import ProductsLoader


def test_product_loader_merges_sheet_into_records():
    loader = ProductsLoader("unused.xlsx")
    loader.total_sheets = 1
    loaded = []
    loader.all_done.connect(loaded.append)

    frame = pd.DataFrame(
        {
            "weight_g": [10, None],
            "PNUS": ["SKU-1", "SKU-2"],
            "номер": ["P-1", "P-2"],
            "local_part_name": ["Цепь", "Прокладка"],
        }
    )
    loader._on_sheet_done("Sheet1", frame)

    assert loaded == [
        [
            {"part_weight": 10, "sku": "SKU-1", "part_id": "P-1", "name": "Цепь"},
            {"part_weight": 0, "sku": "SKU-2", "part_id": "P-2", "name": "Прокладка"},
        ]
    ]


def test_product_loader_reports_missing_file():
    loader = ProductsLoader("missing.xlsx")
    errors = []
    loader.error.connect(errors.append)

    loader.start()

    assert len(errors) == 1
    assert isinstance(errors[0], FileNotFoundError)


def test_product_loader_reports_when_all_sheets_fail():
    loader = ProductsLoader("unused.xlsx")
    loader.total_sheets = 1
    errors = []
    loader.error.connect(errors.append)

    loader._on_sheet_error("Sheet1", "invalid columns")

    assert len(errors) == 1
    assert "ни одного листа" in str(errors[0])
