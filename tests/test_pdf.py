import pytest

from exceptions.exceptions import TableNotFoundError
from pdf_parser import parse
from pdf_parser.parse import calculate_products_from_file


def test_get_all_items_needed():
    test_path = "files/test_file.PDF"
    records = calculate_products_from_file(test_path, 22)
    expected = 7
    assert len(records) == expected


def test_parser_throws_exception_on_table_not_found():
    test_path = "files/empty_pdf.pdf"
    with pytest.raises(TableNotFoundError):
        _ = calculate_products_from_file(test_path, 22)


def test_resolve_product_names_uses_database_and_returns_missing(monkeypatch):
    class FakeContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, traceback):
            return False

    class FakeRepository:
        def __init__(self, session):
            pass

        def get_parts_by_part_ids(self, part_ids):
            assert part_ids == ["P-001", "P-404"]
            return {"P-001": ("Цепь", 10)}

    monkeypatch.setattr(parse, "SessionLocal", lambda: FakeContext())
    monkeypatch.setattr(parse, "PartsRepository", FakeRepository)
    records = [
        {"col_0": "P-001", "col_5": "CHAIN"},
        {"col_0": "P-404", "col_5": "UNKNOWN"},
    ]

    missing = parse.resolve_product_names(records)

    assert records[0]["col_5"] == "Цепь"
    assert records[0]["part_weight"] == 10
    assert records[1]["part_weight"] == "-"
    assert missing == [records[1]]


def test_calculate_does_not_translate_when_all_names_are_in_database(monkeypatch):
    records = [{"col_0": "P-001", "col_5": "CHAIN"}]
    monkeypatch.setattr(parse, "resolve_product_names", lambda records: [])

    def fail_translation(names):
        raise AssertionError("translation should not be called")

    monkeypatch.setattr(parse, "get_translated_results", fail_translation)
    monkeypatch.setattr(parse.pdfplumber, "open", lambda path: FakePdf(records))

    result = calculate_products_from_file("test.pdf", 22)
    assert result[0]["col_5"] == "CHAIN"


class FakePdf:
    def __init__(self, records):
        self.pages = [FakePage(records)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakePage:
    def __init__(self, records):
        self.records = records

    def extract_table(self):
        rows = [["id", "", "", "", "", "name", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]]
        rows.extend([["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]] * 11)
        row = [""] * 21
        row[0] = "P-001"
        row[5] = "CHAIN"
        row[10] = "1"
        row[20] = "100"
        rows.append(row)
        return rows
