import re
from decimal import Decimal

import pandas as pd
import pdfplumber

from db.session import SessionLocal
from exceptions.exceptions import InvalidArgumentError, TableNotFoundError
from repository import PartsRepository

from .translate import get_translated_results

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")

TOTAL_PRICE = "col_20"
MARGE_PRICE = "marge_price"
QTY = "col_10"


def sanitize_arabic(input: dict) -> dict:
    for key, value in input.items():
        if isinstance(value, str):
            input[key] = ARABIC_PATTERN.sub("", value).strip()
    return input


def get_price(input: dict, margin: int) -> dict:
    amount = Decimal(input[TOTAL_PRICE])
    qty = input.get(QTY, 0)
    unit_price = get_unit_price(amount, int(qty))
    result_price = add_margin(unit_price, margin)
    input[MARGE_PRICE] = round(result_price, 2)
    return input


def get_unit_price(amount: Decimal, qty: int) -> Decimal:
    if qty <= 0:
        raise InvalidArgumentError("Кол-во не может быть меньше 0 или равным 0")
    return amount / qty


def add_margin(input_price: Decimal, margin: int) -> Decimal:
    if margin < 0:
        raise InvalidArgumentError("Маржа не может быть равна 0")
    k = (100 + margin) / 100
    k = Decimal(k)
    result = Decimal(input_price * k)
    return result


def process_values(input: dict, margin: int) -> dict:
    input = sanitize_arabic(input)
    input = get_price(input, margin)

    return input


def update_product_price(products: list[dict], margin: int) -> list[dict]:
    """
    Берет старые продукты и обновляет цену без перевода названия
    """
    new_products = [process_values(product, margin) for product in products]
    return new_products


def resolve_product_names(records: list[dict]) -> list[dict]:
    part_ids = [record["col_0"] for record in records]
    with SessionLocal() as session:
        parts_by_part_id = PartsRepository(session).get_parts_by_part_ids(part_ids)

    missing_records = []
    for record in records:
        part_id = record["col_0"]
        part = parts_by_part_id.get(part_id)
        if part is not None:
            record["col_5"] = part[0]
            record["part_weight"] = part[1] if part[1] is not None else "-"
        else:
            record["part_weight"] = "-"
            missing_records.append(record)
    return missing_records


def calculate_products_from_file(path: str, margin: int) -> list[dict]:
    records = []
    with pdfplumber.open(path) as pdf:
        first_page = pdf.pages[0]
        table = first_page.extract_table()
        if table is None:
            raise TableNotFoundError("Таблица не найдена!")
        if table is not None:
            headers = [str(h) if h is not None else "" for h in table[0]]
            rows = [[cell if cell is not None else "" for cell in row] for row in table[1:]]
            column_start = 11
            df = pd.DataFrame(rows[column_start:], columns=headers)

            df.columns = [f"col_{i}" for i in range(len(df.columns))]
            pd.set_option("display.max_columns", None)
            pd.set_option("display.width", 200)

            target_table = df[["col_0", "col_2", "col_5", "col_10", "col_20"]]
            last_item_mask = (
                target_table["col_0"].str.lower().str.contains("invoice value", na=False)
            )
            df_filtered = target_table[~last_item_mask.cummax()]
            records = df_filtered.to_dict("records")

            records = [process_values(record, margin) for record in records]

            missing_records = resolve_product_names(records)
            if missing_records:
                names = [record["col_5"] for record in missing_records]
                translated_names = get_translated_results(names)
                for record, translated in zip(missing_records, translated_names):
                    record["col_5"] = translated
    return records
