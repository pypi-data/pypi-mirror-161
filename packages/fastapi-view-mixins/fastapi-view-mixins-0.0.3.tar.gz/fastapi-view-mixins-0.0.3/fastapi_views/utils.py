import base64
import re
from binascii import Error
from typing import Union

from fastapi import HTTPException
from sqlalchemy.engine import Row
from fastapi import status


def scalars(response: Union[dict, list], data_key: str = 'results'):
    """
    Get object list from response and return first value from each row.

    ex. dict input
        {
            '[data_key]': [(sqlAlchemyRowObject, ), (sqlAlchemyRowObject, )],
            'total_pages': 10,
            'count':2,
            ...
        }

        output
        {
            '[data_key]': [sqlAlchemyRowObject, sqlAlchemyRowObject],
            'total_pages': 10,
            'count':2,
            ...
        }

    ex. list input
        [(sqlAlchemyRowObject, ), (sqlAlchemyRowObject, )]

        output
        [sqlAlchemyRowObject, sqlAlchemyRowObject]
    """
    if isinstance(response, dict):
        object_list: list[Row] = response.get(data_key, list())
        if object_list and any(isinstance(row, Row) for row in object_list):
            response[data_key] = [row[0] for row in object_list]
    elif isinstance(response, list):
        response = [row[0] for row in response]
    return response


def get_regex_group(regex: str, search_in: str):
    url_regex = re.compile(f"{regex}")
    mo = url_regex.search(search_in)
    if mo is not None:
        return mo.group()
    raise ValueError('No result found')


def encode_value(value):
    return base64.b64encode(bytes(str(value), "utf-8"))


def decode_value(value):
    try:
        base64.b64decode(value.encode("utf-8")).decode("utf-8", "ignore")
    except Error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect cursor')
    return base64.b64decode(value.encode("utf-8")).decode("utf-8", "ignore")


def dict_to_query_string(new_query_params) -> str:
    new_string = ''
    for index, (k, v) in enumerate(new_query_params.items()):
        new_string = f'{new_string}{k}={v}'
        if len(new_query_params) - 1 != index:
            new_string = f'{new_string}&'
    return new_string
