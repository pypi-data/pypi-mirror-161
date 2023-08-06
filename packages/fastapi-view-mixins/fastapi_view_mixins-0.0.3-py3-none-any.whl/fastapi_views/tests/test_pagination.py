import pytest
from sqlalchemy import select
from fastapi.requests import Request

from fastapi_views.pagination.annotations import CursorResponse
from fastapi_views.tests._db_sessions import DatabaseSession
from fastapi_views.utils import encode_value
from fastapi_views.pagination.core import (
    paginate_api,
    PaginatorAPI,
    PaginationLimitOffset,
    PaginationCursor,
)
from unittest.mock import (patch, MagicMock)

from fastapi_views.tests._tmp_db import SimpleTestOrm


class MockRequest:
    """Request cls required to test pagination."""

    class State:
        def __init__(self):
            self.paginate_by = None

    def __init__(self):
        self.state = self.State()
        self.query_params = None
        self.url = None


@pytest.fixture()
def request_fixture():
    mock = MagicMock(spec=Request, return_value=MockRequest())
    mock.url = 'https://example.com'
    return mock


@pytest.fixture
def session():
    db_session = DatabaseSession(number=10)
    db_session.init()
    db_session.create_all()
    yield db_session.session
    db_session.close_and_drop()


@pytest.fixture()
def limit_offset_api(request_fixture, request, session):
    request_fixture.query_params = {
        'page': request.param,
        'limit': 3,
    }
    yield paginate_api(
        statement=select(SimpleTestOrm),
        request=request_fixture,
        session=session,
    )


@pytest.fixture()
def cursor_api(request_fixture, request, session):
    cursor, ordering = request.param
    request_fixture.query_params = {
        'limit': 2,
        'cursor': cursor,
    }
    yield paginate_api(
        statement=select(SimpleTestOrm),
        request=request_fixture,
        session=session,
        strategy=PaginationCursor,
        kwargs={
            'model': SimpleTestOrm,
            'ordering': ordering,
            'cursor_prefixes': ['custom_next__', 'custom_prev__']
        }
    )


class TestPaginatorAPI:

    @patch('fastapi_views.pagination.core.PaginatorAPI.strategy_response')
    def test_init(self, response_mock, request_fixture, session):
        """Test if values are initialized as expected."""
        response_mock.return_value = {}

        paginator = PaginatorAPI(
            statement=select(SimpleTestOrm),
            request=request_fixture,
            session=session,
            paginate_by=2
        )
        assert paginator.statement is not None
        assert paginator.request is not None
        assert paginator.session is not None
        assert paginator.strategy is not None
        assert paginator.paginate_by is not None
        assert paginator.strategy == PaginationLimitOffset
        assert paginator.paginate_by == 2
        assert paginator.kwargs == {
            'model': None,
            'ordering': None,
            'cursor_prefixes': None,
        }


class TestLimitOffset:

    @pytest.mark.parametrize('limit_offset_api', [0, 1, 2, 3], indirect=['limit_offset_api'])
    def test_strategy_response_common(self, limit_offset_api: dict):
        """Test pagination response the same common values in every page."""
        assert limit_offset_api['total'] == 10
        assert limit_offset_api['total_pages'] == 3
        assert limit_offset_api['page_limit'] == 3

    @pytest.mark.parametrize('limit_offset_api', [0], indirect=['limit_offset_api'])
    def test_strategy_response(self, limit_offset_api: dict):
        """Test pagination response starting at page 0."""
        assert limit_offset_api['count'] == 3
        assert limit_offset_api['next_page'] == 'https://example.com?page=1&limit=3'
        assert limit_offset_api['previous_page'] is None
        assert limit_offset_api['last_page'] == 'https://example.com?page=3&limit=3'

    @pytest.mark.parametrize('limit_offset_api', [1], indirect=['limit_offset_api'])
    def test_strategy_response_1(self, limit_offset_api: dict):
        """Test pagination response starting at page 1."""
        assert limit_offset_api['count'] == 3
        assert limit_offset_api['next_page'] == 'https://example.com?page=2&limit=3'
        assert limit_offset_api['previous_page'] == 'https://example.com?page=0&limit=3'
        assert limit_offset_api['last_page'] == 'https://example.com?page=3&limit=3'

    @pytest.mark.parametrize('limit_offset_api', [3], indirect=['limit_offset_api'])
    def test_strategy_response_last(self, limit_offset_api: dict):
        """Test pagination response starting at last page."""
        assert limit_offset_api['count'] == 1
        assert limit_offset_api['next_page'] is None
        assert limit_offset_api['previous_page'] == 'https://example.com?page=2&limit=3'
        assert limit_offset_api['last_page'] == 'https://example.com?page=3&limit=3'


cursor_to_load_last_page = encode_value('custom_next__8&page__4').decode("utf-8")
cursor_to_load_last_page_reverse = encode_value('custom_next__3&page__4').decode("utf-8")


def assert_result(result: CursorResponse, next_cursor=None, prev_cursor=None):
    """
    Count is the same for all results because in our test we have 10 objects,
    which paginated by 2 gives equal number of objects per page.
    """
    assert result['count'] == 2
    assert result['page_limit'] == 2
    assert result['first_page'] == 'https://example.com?limit=2'
    if next_cursor is not None:
        next_page_url = f'https://example.com?limit=2&cursor={next_cursor.decode("utf-8")}'
        assert result['next_page'] == next_page_url
    else:
        assert result['next_page'] is None

    if prev_cursor is not None:
        prev_url = f'https://example.com?limit=2&cursor={prev_cursor.decode("utf-8")}'
        assert result['previous_page'] == prev_url
    else:
        assert result['previous_page'] is None


class TestCursorAscendingOrder:
    """We assume in tests that we have 10 objects ordered by id paginated by 2."""

    @staticmethod
    def _get_orm_id(orm):
        return getattr(orm, 'id')

    @staticmethod
    def assert_common(result):
        assert result['count'] == 2
        assert result['page_limit'] == 2
        assert result['first_page'] == 'https://example.com?limit=2'

    @pytest.mark.parametrize('cursor_api', [(None, ['id'])], indirect=['cursor_api'])
    def test_strategy_response(self, cursor_api: dict):
        """Test pagination response."""
        next_page_cursor = encode_value('custom_next__2&page__1')
        assert_result(cursor_api, next_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [1, 2]

    @pytest.mark.parametrize(
        'cursor_api',
        [('Y3VzdG9tX25leHRfXzImcGFnZV9fMQ==', ['id'])],
        indirect=['cursor_api'],
    )
    def test_strategy_response_with_cursor(self, cursor_api: dict):
        """Test pagination response 'at page 1'."""
        next_page_cursor = encode_value('custom_next__4&page__2')
        previous_page_cursor = encode_value('custom_prev__3&page__0')
        assert_result(cursor_api, next_page_cursor, previous_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [3, 4]

    @pytest.mark.parametrize(
        'cursor_api', [(cursor_to_load_last_page, ['id'])],
        indirect=['cursor_api'],
    )
    def test_strategy_response_with_cursor_last_page(self, cursor_api: dict):
        """Test pagination response 'on last page'."""
        previous_page_cursor = encode_value('custom_prev__9&page__3')
        assert_result(cursor_api, prev_cursor=previous_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [9, 10]


class TestCursorDescendingOrder:
    """We assume in tests that we have 10 objects ordered by id desc paginated by 2."""

    @staticmethod
    def _get_orm_id(orm):
        return getattr(orm, 'id')

    @pytest.mark.parametrize('cursor_api', [(None, ['-id'])], indirect=['cursor_api'])
    def test_strategy_response(self, cursor_api: dict):
        """Test pagination response."""
        next_page_cursor = encode_value('custom_next__9&page__1')
        assert_result(cursor_api, next_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [10, 9]

    @pytest.mark.parametrize(
        'cursor_api',
        [('Y3VzdG9tX25leHRfXzkmcGFnZV9fMQ==', ['-id'])],
        indirect=['cursor_api'],
    )
    def test_strategy_response_with_cursor(self, cursor_api: dict):
        """Test pagination response 'at page 1'."""
        next_page_cursor = encode_value('custom_next__7&page__2')
        previous_page_cursor = encode_value('custom_prev__8&page__0')
        assert_result(cursor_api, next_page_cursor, previous_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [8, 7]

    @pytest.mark.parametrize(
        'cursor_api',
        [(cursor_to_load_last_page_reverse, ['-id'])],
        indirect=['cursor_api'],
    )
    def test_strategy_response_with_cursor_last_page(self, cursor_api: dict):
        """Test pagination response 'on last page'."""
        previous_page_cursor = encode_value('custom_prev__2&page__3')
        assert_result(cursor_api, prev_cursor=previous_page_cursor)

        api_ids = list(map(self._get_orm_id, cursor_api['results']))
        assert api_ids == [2, 1]
