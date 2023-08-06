from unittest.mock import Mock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.engine import Row

from .. import utils


def test_scalars():
    empty_response = {}
    assert utils.scalars(empty_response) == {}
    mocks = [MagicMock(spec=Row, return_value=(x, )) for x in range(0, 2)]
    response = {'results': [mocks[0], mocks[1]]}
    assert utils.scalars(response) == {
        'results': [mocks[0][0], mocks[1][0]],
    }
    assert utils.scalars(response, data_key='invalid') == response

    response = [(mocks[0],), (mocks[1],)]
    assert utils.scalars(response) == [mocks[0], mocks[1]]

    assert utils.scalars(response, data_key='invalid') == mocks


@pytest.mark.parametrize('test_input, expected', [('(?<=-).*', '=2a?cb'), ('^[^?]*', 'ran89-=2a')])
def test_regex_group(test_input, expected):
    search_value = 'ran89-=2a?cb'
    assert utils.get_regex_group(test_input, search_value) == expected

    with pytest.raises(ValueError):
        utils.get_regex_group('(?<=-)', '')


def test_encode_decode():
    value = 'test'
    assert utils.encode_value(value) == b'dGVzdA=='
    assert utils.decode_value('dGVzdA==') == value

    with pytest.raises(HTTPException):
        utils.decode_value('invalid')


def test_dict_to_query_string():
    assert utils.dict_to_query_string({'some_value': 1, 'next__': 'x'}) == 'some_value=1&next__=x'
