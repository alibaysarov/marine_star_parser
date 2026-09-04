import pytest

from exceptions.exceptions import TableNotFoundError
from pdf_parser.parse import calculate_products_from_file

def test_get_all_items_needed():
    test_path = "files/test_file.pdf"
    records = calculate_products_from_file(test_path,22)
    expected = 7
    assert len(records)== expected

def test_parser_throws_exception_on_table_not_found():
    test_path = "files/empty_pdf.pdf"
    with pytest.raises(TableNotFoundError):
        _ = calculate_products_from_file(test_path,22)