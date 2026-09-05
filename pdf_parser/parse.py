import re
from decimal import Decimal
from typing import List

import pandas as pd
import pdfplumber
from pdfplumber.page import Page

from db.session import SessionLocal
from decorators.time import timeit
from exceptions.exceptions import InvalidArgumentError, TableNotFoundError
from repository import PartsRepository

from .translate import get_translated_results

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")

TOTAL_PRICE = "final_total"
MARGE_PRICE = "marge_price"
QTY = "qty"

HEADERS = [
    "row_num",
    "brand",
    "part_no",
    "description",
    "unit_price",
    "qty",
    "gross",
    "discount",
    "total_price",
    "vat_rate",
    "vat_amount",
    "final_total",
]

DROP_COLUMNS = [
    "row_num",
    "brand",
    "discount",
    "total_price",
    "vat_rate",
    "vat_amount",
    "gross",
]


def remove_arabic(input: str) -> str:
    return ARABIC_PATTERN.sub("", input).strip()


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
    input["marge"] = margin
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


def update_product_price(
    products: list[dict] | pd.DataFrame, margin: int
) -> list[dict] | pd.DataFrame:
    """
    Берет старые продукты и обновляет цену без перевода названия
    """
    if isinstance(products, pd.DataFrame):
        products = products.copy()
        k = (100 + margin) / 100
        products["unit_price"] = round(k * products["final_total"] / products["qty"], 2)
        products["marge"] = margin
        return products

    new_products = [process_values(product, margin) for product in products]
    return new_products


# def translate_names(df: pd.DataFrame)->pd.DataFrame:
#     get_translated_results


def translate_missing(df: pd.DataFrame) -> pd.DataFrame:
    texts = df["description"].tolist()
    map = get_translated_results(texts)

    def get_name(name: str) -> str:
        key = f"key_{name}"
        return map.get(key, "")

    df["translated"] = df["description"].map(get_name)
    return df


def resolve_product_names_pd(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    part_ids = df["part_no"].tolist()

    with SessionLocal() as session:
        parts_by_part_id = PartsRepository(session).get_parts_by_part_ids(part_ids)

    def get_name(part_id: str) -> str | None:
        part = parts_by_part_id.get(part_id)
        return part[0] if part is not None else None

    def get_weight(part_id: str) -> str | int:
        part = parts_by_part_id.get(part_id)
        if part is None:
            return "-"
        return part[1] if part[1] is not None else "-"

    found_parts = df["part_no"].map(parts_by_part_id.get)
    has_part = found_parts.notna()

    df["translated"] = df["part_no"].map(get_name)
    df["part_weight"] = df["part_no"].map(get_weight)

    missing_mask = ~has_part
    return df, missing_mask


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


def _is_valid_row(rows: list[str]) -> bool:
    if len(rows) < 0:
        return False
    if rows[0] is None:
        return False
    is_num = rows[0].isnumeric()
    return is_num


def _clear_none_fields(rows: list) -> list[str]:
    return [row for row in rows if row is not None]


def _get_products_table(pages: List[Page], column_number: int) -> list[list]:
    merged_rows = []
    for page in pages:
        tables = page.extract_tables()
        for table in tables:
            merged_rows.extend(table)

    product_rows = [_clear_none_fields(row) for row in merged_rows if _is_valid_row(row)]
    product_rows = [row for row in product_rows if len(row) == column_number]
    return product_rows


@timeit
def calculate_products_from_file(path: str, margin: int) -> pd.DataFrame:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    with pdfplumber.open(path) as pdf:
        result = _get_products_table(pdf.pages, len(HEADERS))
        if not result:
            raise TableNotFoundError("Таблица не найдена!")

        df = pd.DataFrame(result, columns=HEADERS)

        if (df["qty"] == 0).any():
            print("Внимание: есть строки с нулевым qty")

        df["final_total"] = pd.to_numeric(df["final_total"].str.replace(",", ""), errors="coerce")
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce")

        df["description"] = (
            df["description"].str.replace(ARABIC_PATTERN, "", regex=True).str.strip()
        )
        k = (100 + margin) / 100
        df["unit_price"] = 0.0
        non_zero_qty = df["qty"] != 0
        df.loc[non_zero_qty, "unit_price"] = (
            k * df.loc[non_zero_qty, "final_total"] / df.loc[non_zero_qty, "qty"]
        ).round(2)

        # print(df)

        [df, missing] = resolve_product_names_pd(df)

        df.drop(columns=DROP_COLUMNS, inplace=True)
        if missing.any():
            print("Есть записи без совпадения в БД")
            df = translate_missing(df)
        df["marge"] = 0
        return df[
            [
                "part_no",
                "description",
                "translated",
                "final_total",
                "part_weight",
                "qty",
                "unit_price",
                "marge",
            ]
        ]
