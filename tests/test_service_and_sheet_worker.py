import pandas as pd

from excel_parser.sheet_worker import SheetWorker
from helpers.get_selected_file import get_selected_file_path
from service import parts_service


class FakeContext:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, **kwargs):
        return kwargs

    def batch_import(self, products):
        return len(products)


class ImmediatePool:
    def start(self, worker):
        worker.run()


def test_selected_file_path():
    assert get_selected_file_path("") == ""
    assert get_selected_file_path("C:/files/items.xlsx") == "Выбранный файл:\nitems.xlsx"


def test_parts_service_database_helpers(monkeypatch):
    session = object()
    monkeypatch.setattr(parts_service, "SessionLocal", lambda: FakeContext(session))
    monkeypatch.setattr(parts_service, "PartsRepository", FakeRepository)

    assert parts_service.PartsService._get_all("цепь", 2, 10) == {
        "search": "цепь",
        "page": 2,
        "per_page": 10,
    }
    assert parts_service.PartsService._batch_upload([{"sku": "1"}]) == 1


def test_parts_service_upload_and_load_callbacks(monkeypatch):
    monkeypatch.setattr(parts_service, "SessionLocal", lambda: FakeContext(object()))
    monkeypatch.setattr(parts_service, "PartsRepository", FakeRepository)
    service = parts_service.PartsService()
    service._pool = ImmediatePool()
    loaded = []
    uploaded = []
    errors = []

    service.upload_parts_async([{"sku": "1"}], uploaded.append, errors.append)
    service.load_parts_async("цепь", 1, 50, loaded.append, errors.append)

    assert uploaded == [1]
    assert loaded == [{"search": "цепь", "page": 1, "per_page": 50}]
    assert errors == []


def test_sheet_worker_emits_filtered_dataframe(monkeypatch):
    frame = pd.DataFrame(
        {
            "PNUS": ["A", None],
            "номер": ["1", "2"],
            "local_part_name": ["Цепь", "Прокладка"],
        }
    )
    monkeypatch.setattr("excel_parser.sheet_worker.pd.read_excel", lambda *args, **kwargs: frame)
    worker = SheetWorker("Sheet1", "items.xlsx")
    finished = []
    worker.signals.finished.connect(lambda name, result: finished.append((name, result)))

    worker.run()

    assert finished[0][0] == "Sheet1"
    assert len(finished[0][1]) == 1


def test_sheet_worker_emits_error(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("bad workbook")

    monkeypatch.setattr("excel_parser.sheet_worker.pd.read_excel", fail)
    worker = SheetWorker("Sheet1", "items.xlsx")
    errors = []
    worker.signals.error.connect(lambda name, message: errors.append((name, message)))

    worker.run()

    assert errors == [("Sheet1", "bad workbook")]
