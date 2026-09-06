import re

from pandas import DataFrame


def remove_zeroes_pd(df: DataFrame, key: str):
    df[key] = df[key].astype(str).str.replace(r"[^0-9A-Za-z]|0+$", "", regex=True)
    return df


def remove_zeroes(input: str) -> str:
    pattern = "[^0-9A-Za-z]|0+$"
    replaced = re.sub(pattern, "", input)
    return replaced
