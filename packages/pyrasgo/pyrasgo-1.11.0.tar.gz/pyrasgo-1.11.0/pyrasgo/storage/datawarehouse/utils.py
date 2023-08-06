from typing import Optional


def is_select_statement(
    sql: str,
) -> bool:
    """
    Determine if a string is a valid SQL select statement and return a boolean
    """
    if sql.lower().startswith("with") and "select" in sql.lower():
        return True
    if sql.lower().startswith("select"):
        return True
    return False


def convert_to_type(type_code: int, precision: int, scale: int) -> str:
    """
    Accepts values from a Snowflake ResultMetadata record
    and returns a Snowflake data type

    https://docs.snowflake.com/en/user-guide/python-connector-api.html#type-codes
    ResultMetadata(name='', type_code=, display_size=, internal_size=, precision=, scale=, is_nullable=)
    """
    type_code_map = {
        0: "FIXED",  # NUMBER/INT
        1: "REAL",  # REAL
        2: "TEXT",  # VARCHAR/STRING
        3: "DATE",  # DATE
        4: "TIMESTAMP",  # TIMESTAMP
        5: "VARIANT",  # VARIANT
        6: "TIMESTAMP_LTZ",  # TIMESTAMP_LTZ
        7: "TIMESTAMP_TZ",  # TIMESTAMP_TZ
        8: "TIMESTAMP_NTZ",  # TIMESTAMP_TZ
        9: "OBJECT",  # OBJECT
        10: "ARRAY",  # ARRAY
        11: "BINARY",  # BINARY
        12: "TIME",  # TIME
        13: "BOOLEAN",  # BOOLEAN
    }
    data_type = type_code_map[type_code]
    if data_type == 'REAL':
        return 'FLOAT'
    if data_type == 'FIXED':
        return f'NUMBER({precision or 0},{scale or 0})'
    if 'TIMESTAMP' in data_type:
        return f'{data_type}({scale or 0})'
    return data_type
