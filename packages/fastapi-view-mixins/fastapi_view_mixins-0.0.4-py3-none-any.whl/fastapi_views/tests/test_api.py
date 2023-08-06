"""Tests for BaseSyncAPI and mixins."""
import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException
from fastapi.requests import Request
from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.sql import Select

from fastapi_views.views.async_api import BaseAsyncAPI
from fastapi_views.views.mixins import (
    BaseAPIListMixin,
    BaseAPIDetailMixin,
    BaseAPICreateMixin,
    BaseAPIUpdateMixin,
    BaseAPIDestroyMixin,
    BaseAPIMixin,
)
from fastapi_views.views.sync_api import BaseSyncAPI
from fastapi_views.tests._db_sessions import DatabaseSession
from fastapi_views.tests._tmp_db import SimpleTestOrm
from fastapi_views.pagination.core import PaginationCursor

NUMBER_OF_OBJECTS = 50  # number of objects created by sync db


class MockRequest:
    """Request cls required to test pagination."""

    class State:
        def __init__(self):
            self.paginate_by = None

    def __init__(self):
        self.state = self.State()
        self.query_params = None
        self.url = None


@pytest.fixture
def request_fixture():
    mock = MagicMock(spec=Request, return_value=MockRequest())
    mock.url = 'https://example.com'
    return mock


@pytest.fixture
def session():
    db_session = DatabaseSession()
    db_session.init()
    db_session.create_all()
    yield db_session.session
    db_session.close_and_drop()


@pytest.fixture
def api(request):
    model, pk_field, _, paginate_by, strategy, kwargs, statement = request.param
    return BaseSyncAPI(
        model=model,
        pk_field=pk_field,
        paginate_by=paginate_by,
        pagination_strategy=strategy,
        pagination_kwargs=kwargs,
        statement=statement,
    )


@pytest.fixture
def base_mixin_instance(request):
    _async_api = request.param
    args = ['a', 1, 'c', {'d'}]
    kwargs = {'a': 1}

    class BaseView(BaseAPIMixin):
        model = SimpleTestOrm
        async_api = _async_api

    return BaseView(*args, **kwargs)


@pytest.fixture
def list_mixin_instance(request):
    _model, _, _paginate_by, _strategy = request.param

    class ListView(BaseAPIListMixin):
        model = _model
        paginate_by = _paginate_by
        pagination_strategy = _strategy

    return ListView()


@pytest.fixture
def list_mixin_instance_override_get_statement(request):
    _model = request.param

    class ListView(BaseAPIListMixin):
        model = _model

        def get_statement(self) -> Select:
            return select(self.model).where(self.model.id > 48)

    return ListView()


@pytest.fixture
def detail_mixin_instance(request):
    _model = request.param

    class DetailView(BaseAPIDetailMixin):
        model = _model

    return DetailView()


@pytest.fixture
def detail_mixin_instance_override_get_statement(request):
    _model = request.param

    class DetailView(BaseAPIDetailMixin):
        model = _model

        def get_statement(self) -> Select:
            return select(self.model).where(self.model.id == 10)

    return DetailView()


@pytest.fixture
def create_mixin_instance(request):
    _model = request.param

    class CreateView(BaseAPICreateMixin):
        model = _model

    return CreateView()


@pytest.fixture
def update_mixin_instance(request):
    _model = request.param

    class UpdateView(BaseAPIUpdateMixin):
        model = _model

    return UpdateView()


@pytest.fixture
def delete_mixin_instance(request):
    _model = request.param

    class DeleteView(BaseAPIDestroyMixin):
        model = _model

    return DeleteView()


class TestBaseSyncAPI:
    """Test BaseSyncAPI cls."""

    @pytest.mark.parametrize('test_input', [None, ''])
    def test_init_model_raise_value_error(self, test_input):
        """Test if value error occurs on given inputs."""
        with pytest.raises(ValueError):
            assert BaseSyncAPI(model=test_input)

    @pytest.mark.parametrize('test_input', ['not_cls', 1, True, {'a': 'b'}, {1}])
    def test_init_model_raise_validation_error(self, test_input):
        """Test if pydantic validation error occurs on given inputs."""
        with pytest.raises(ValidationError):
            assert BaseSyncAPI(model=test_input)

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_get_all_missing_session(self, api):
        """Test session attr in get_all method."""
        with pytest.raises(AttributeError):
            api.get_all(None)
        with pytest.raises(TypeError):
            api.get_all(False)
        with pytest.raises(TypeError):
            api.get_all('not_session')

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_get_all_statement_error(self, session, api):
        """Test statement attr in get_all method."""
        with pytest.raises(AttributeError):
            api.get_all(session=session)
        with pytest.raises(TypeError):
            api.statement = 'invalid'
            api.get_all(session=session)

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, select(SimpleTestOrm))],
        indirect=['api'],
    )
    def test_get_all(self, session, api):
        """Test if returns all created objects."""
        assert len(api.get_all(session=session)) == NUMBER_OF_OBJECTS

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_count(self, session, api):
        """Test if returns correct number related to statement."""
        assert api._count(
            session=session,
            statement=select(SimpleTestOrm).where(SimpleTestOrm.id < 25),
        ) == 24

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_count_missing_attrs(self, session, api):
        """Test attrs in _count method."""
        with pytest.raises(TypeError):
            api._count()

        with pytest.raises(TypeError):
            api._count(session=session)

        with pytest.raises(TypeError):
            api._count(statement=select(SimpleTestOrm))

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_get_detail_statement_none_fk_fields_none(self, session, api):
        """Test get_detail method when statement and fk fields are not provided."""
        result = api.get_detail(
            session=session,
            field_value=1,
        )
        assert result.id == 1
        assert type(result).__name__ == 'SimpleTestOrm'

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, select(SimpleTestOrm).where(
            SimpleTestOrm.id == 5,
        ))],
        indirect=['api'],
    )
    def test_get_detail_statement_not_none_fk_fields_none(self, session, api):
        """Test get_detail method when fk fields are not provided."""
        result = api.get_detail(
            session=session,
        )
        assert result.id == 5
        assert type(result).__name__ == 'SimpleTestOrm'

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, select(SimpleTestOrm))],
        indirect=['api'],
    )
    def test_get_detail_multiple_objects_returned(self, session, api):
        """Test get_detail method when multiple objects are returned."""
        with pytest.raises(ValueError):
            api.get_detail(
                session=session,
            )

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_get_detail_not_found(self, session, api):
        """Test get_detail method when object is not found."""
        with pytest.raises(HTTPException):
            api.get_detail(
                session=session,
                field_value=51,
            )

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_get_detail_missing_attrs(self, session, api):
        """Test get_detail attrs."""
        with pytest.raises(TypeError):
            api.get_detail()

        with pytest.raises(AttributeError):
            api.get_detail(
                session=None,
                field_value=10,
            )
        with pytest.raises(AttributeError):
            api.get_detail(
                session=session,
                field_value=None,
            )

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_create(self, session, api):
        """Test create method when new object is created."""
        result = api.create(
            session=session
        )
        assert result.id > NUMBER_OF_OBJECTS
        assert type(result).__name__ == 'SimpleTestOrm'

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_create_attrs(self, session, api):
        """Test create method attrs."""
        with pytest.raises(AttributeError):
            api.create(
                session=None,
            )
        with pytest.raises(TypeError):
            api.create(
                session='not_session',
            )
        with pytest.raises(TypeError):
            api.create(
                session=2,
            )
        with pytest.raises(TypeError):
            api.create(
                session=True,
            )
        with pytest.raises(TypeError):
            api.create(
                session=session,
                data={
                    'invalid': 'invalid'
                }
            )

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, None)],
        indirect=['api'],
    )
    def test_create_integrity_error(self, session, api):
        """Test create method integrity error."""
        with pytest.raises(HTTPException):
            api.create(
                session=session,
                data={
                    'id': 'invalid'
                }
            )

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_delete(self, session, api):
        """Test delete method."""
        assert api._count(session, select(SimpleTestOrm)) == NUMBER_OF_OBJECTS
        api.delete(
            session=session,
            field_value=50,
        )
        # check if delete removed object
        with pytest.raises(HTTPException):
            api.get_detail(session, 50)

        assert api._count(session, select(SimpleTestOrm)) == NUMBER_OF_OBJECTS - 1

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_delete_missing_attrs(self, session, api):
        """Test delete method attrs."""
        with pytest.raises(TypeError):
            api.delete()
        with pytest.raises(AttributeError):
            api.delete(session=None, field_value=2)

        with pytest.raises(TypeError):
            api.delete(session='not_valid_type', field_value=2)

        api.pk_field = None
        with pytest.raises(AttributeError):
            api.delete(session=session, field_value=2)

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_update_single(self, session, api):
        """Test update_single method."""
        api.update_single(
            session=session,
            field_value=1,
            data={
                'id': 100
            }
        )
        assert api.get_detail(session, 100) is not None
        with pytest.raises(HTTPException):
            api.get_detail(session, 1)

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, 'id', None, None, None, None, None)],
        indirect=['api'],
    )
    def test_update_single_missing_attrs(self, session, api):
        """Test update_single method attrs."""
        with pytest.raises(TypeError):
            api.update_single()
        with pytest.raises(AttributeError):
            api.update_single(session=None, field_value=2)

        with pytest.raises(TypeError):
            api.update_single(session='not_valid_type', field_value=2)

        with pytest.raises(HTTPException):
            api.update_single(session=session, field_value=2)

        api.pk_field = None
        with pytest.raises(AttributeError):
            api.update_single(session=session, field_value=2, data={'id': 100})

        api.pk_field = 'id'
        with pytest.raises(HTTPException):
            api.update_single(session=session, field_value=2, data={'id': 'invalid'})

        assert api.get_detail(session, 2).id == 2

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, 4, None, None, select(SimpleTestOrm))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_limit_offset(self, session, api, request_fixture):
        """Test get_all limit, offset pagination."""
        request_fixture.query_params = {}
        response = api.get_all_with_pagination(
            request=request_fixture,
            session=session,
        )
        assert response is not None
        assert isinstance(response, dict)
        assert response['count'] == 4
        assert response['page_limit'] == 4
        assert response['total'] == NUMBER_OF_OBJECTS

        # last page
        request_fixture.query_params = {
            'page': 12,
        }
        response = api.get_all_with_pagination(
            request=request_fixture,
            session=session,
        )
        assert response is not None
        assert isinstance(response, dict)
        assert response['count'] == 2
        assert response['next_page'] is None

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, 4, PaginationCursor, {
            'model': SimpleTestOrm,
            'ordering': ['id'],
            'cursor_prefixes': ['next__', 'prev__']
        }, select(SimpleTestOrm).where(SimpleTestOrm.id > 48))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_cursor(self, session, api, request_fixture):
        """Test get_all cursor pagination."""
        request_fixture.query_params = {}
        response = api.get_all_with_pagination(
            request=request_fixture,
            session=session,
        )
        assert response is not None
        assert isinstance(response, dict)
        assert response['count'] == 2
        assert response['page_limit'] == 4
        assert response['next_page'] is None
        assert response['previous_page'] is None

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, 4, PaginationCursor, {
            'model': SimpleTestOrm,
            'ordering': ['time_created'],
            'cursor_prefixes': ['next__', 'prev__']
        }, select(SimpleTestOrm).where(SimpleTestOrm.id > 43))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_cursor_datetime_ordering(self, session, api, request_fixture):
        """Test get_all cursor pagination using datetime field in ordering."""
        request_fixture.query_params = {}
        assert api.pagination_kwargs['ordering'] == ['time_created']
        response = api.get_all_with_pagination(
            request=request_fixture,
            session=session,
        )
        assert response is not None
        assert isinstance(response, dict)
        assert response['next_page'] is not None
        assert response['previous_page'] is None
        assert response['results'][0].id == 44  # first found
        assert response['count'] == 4

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, 5, PaginationCursor, {
            'model': SimpleTestOrm,
            'ordering': ['-time_created'],
            'cursor_prefixes': ['next__', 'prev__']
        }, select(SimpleTestOrm).where(SimpleTestOrm.id > 43))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_cursor_datetime_ordering_reverted(
            self,
            session,
            api,
            request_fixture,
    ):
        """
        Test get_all cursor pagination using descending datetime field in ordering.

        In case the time hour, minute and second would be the same for all objects from statement,
        then id found would be equal to 44, because it would be no difference in ordering.

        This case is showed in test_async_api.py file along with ordering with 2 fields.
        """
        request_fixture.query_params = {}
        assert api.pagination_kwargs['ordering'] == ['-time_created']
        response = api.get_all_with_pagination(
            request=request_fixture,
            session=session,
        )
        assert response['results'][0].id == 50  # first found

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, 4, None, None, select(SimpleTestOrm))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_missing_attrs(self, session, api, request_fixture):
        """Test get_all pagination attrs."""
        with pytest.raises(TypeError):
            api.get_all_with_pagination()
        with pytest.raises(AttributeError):
            api.get_all_with_pagination(session=None, request=request_fixture)

        with pytest.raises(AttributeError):
            api.get_all_with_pagination(session=session, request=None)
        with pytest.raises(TypeError):
            api.get_all_with_pagination(session=session, request='2')

        with pytest.raises(TypeError):
            api.get_all_with_pagination(session='not_valid_type', request=request_fixture)

    @pytest.mark.parametrize(
        'api',
        [(SimpleTestOrm, None, None, None, None, None, select(SimpleTestOrm))],
        indirect=['api'],
    )
    def test_get_all_with_pagination_invalid_paginate_by(self, session, api, request_fixture):
        """Test get_all pagination, paginate_by attr."""
        with pytest.raises(AttributeError):
            api.get_all_with_pagination(session=session, request=request_fixture)

        api.paginate_by = False
        with pytest.raises(TypeError):
            api.get_all_with_pagination(session=session, request=request_fixture)

        api.paginate_by = 'str'
        with pytest.raises(TypeError):
            api.get_all_with_pagination(session=session, request=request_fixture)

        api.paginate_by = 0
        with pytest.raises(ValueError):
            api.get_all_with_pagination(session=session, request=request_fixture)

        api.paginate_by = -1
        with pytest.raises(ValueError):
            api.get_all_with_pagination(session=session, request=request_fixture)


class TestMixins:
    """Test mixin classes."""

    @pytest.mark.parametrize(
        'base_mixin_instance',
        [False, True],
        indirect=['base_mixin_instance'],
    )
    def test_init(self, base_mixin_instance: BaseAPIMixin):
        """Test base mixin initialized as expected."""
        assert base_mixin_instance.args == ('a', 1, 'c', {'d'})
        assert base_mixin_instance.kwargs == {'a': 1}
        assert base_mixin_instance.api_view.statement is None
        assert base_mixin_instance.api_view.pagination_kwargs is None

    @pytest.mark.parametrize('input_value', ['some_str', 0, 1, {'a': 'b'}, {1}])
    def test_init_async_api_type_error(self, input_value):
        """Test base mixin async_api attr."""
        with pytest.raises(TypeError):
            class BaseView(BaseAPIMixin):
                model = SimpleTestOrm
                async_api = input_value

            BaseView()

    @pytest.mark.parametrize('base_mixin_instance', [False], indirect=['base_mixin_instance'])
    def test_init_async_false(self, base_mixin_instance: BaseAPIMixin):
        """Test if api_view is instance of sync API when async_api set to False."""
        assert isinstance(base_mixin_instance.api_view, BaseSyncAPI)

    @pytest.mark.parametrize('base_mixin_instance', [True], indirect=['base_mixin_instance'])
    def test_init_async_true(self, base_mixin_instance: BaseAPIMixin):
        """Test if api_view is instance of async API when async_api set to True."""
        assert isinstance(base_mixin_instance.api_view, BaseAsyncAPI)

    @pytest.mark.parametrize(
        'list_mixin_instance',
        [(SimpleTestOrm, None, None, None)],
        indirect=['list_mixin_instance'],
    )
    def test_list_mixin(self, session, list_mixin_instance):
        """Test list mixin."""
        assert len(list_mixin_instance.get_all(session=session)) == NUMBER_OF_OBJECTS

        assert isinstance(list_mixin_instance.api_view.statement, Select)
        assert list_mixin_instance.async_api is False
        assert list_mixin_instance.api_view.pagination_kwargs == {
            'model': SimpleTestOrm,
            'ordering': ['id'],
            'cursor_prefixes': ['next__', 'prev__']
        }

        with pytest.raises(AttributeError):
            list_mixin_instance.get_detail()
        with pytest.raises(AttributeError):
            list_mixin_instance.create()
        with pytest.raises(AttributeError):
            list_mixin_instance.delete()
        with pytest.raises(AttributeError):
            list_mixin_instance.update_single()

    @pytest.mark.parametrize(
        'list_mixin_instance',
        [(SimpleTestOrm, None, 10, None)],
        indirect=['list_mixin_instance'],
    )
    def test_list_mixin_paginate_by(self, session, list_mixin_instance, request_fixture):
        """Test list mixin with pagination."""
        request_fixture.query_params = {}

        assert list_mixin_instance.paginate_by == 10

        response = list_mixin_instance.get_all_with_pagination(
            session=session,
            request=request_fixture,
        )
        assert response['count'] == 10
        assert response['total_pages'] == NUMBER_OF_OBJECTS / 10 - 1

    @pytest.mark.parametrize(
        'list_mixin_instance',
        [(SimpleTestOrm, None, 10, PaginationCursor)],
        indirect=['list_mixin_instance'],
    )
    def test_list_mixin_cursor_strategy(self, session, list_mixin_instance, request_fixture):
        """Test list mixin pagination with cursor strategy."""
        request_fixture.query_params = {}

        response = list_mixin_instance.get_all_with_pagination(
            session=session,
            request=request_fixture,
        )
        assert isinstance(response, dict)
        assert list_mixin_instance.pagination_strategy == PaginationCursor

    @pytest.mark.parametrize(
        'detail_mixin_instance',
        [SimpleTestOrm],
        indirect=['detail_mixin_instance'],
    )
    def test_detail_mixin(self, session, detail_mixin_instance):
        """Test detail mixin."""
        response = detail_mixin_instance.get_detail(session=session, field_value=1)
        assert response.id == 1
        assert type(response).__name__ == 'SimpleTestOrm'

        assert detail_mixin_instance.api_view.statement is None
        assert detail_mixin_instance.async_api is False
        assert detail_mixin_instance.api_view.pagination_kwargs is None

        with pytest.raises(AttributeError):
            detail_mixin_instance.get_all()
        with pytest.raises(AttributeError):
            detail_mixin_instance.get_all_with_pagination()
        with pytest.raises(AttributeError):
            detail_mixin_instance.create()
        with pytest.raises(AttributeError):
            detail_mixin_instance.delete()
        with pytest.raises(AttributeError):
            detail_mixin_instance.update_single()

    @pytest.mark.parametrize(
        'list_mixin_instance_override_get_statement',
        [SimpleTestOrm],
        indirect=['list_mixin_instance_override_get_statement'],
    )
    def test_list_mixin_get_statement(self, session, list_mixin_instance_override_get_statement):
        """Test list mixin override get_statement method."""
        response = list_mixin_instance_override_get_statement.get_all(session=session)
        assert len(response) == 2

    @pytest.mark.parametrize(
        'detail_mixin_instance_override_get_statement',
        [SimpleTestOrm],
        indirect=['detail_mixin_instance_override_get_statement'],
    )
    def test_detail_mixin_get_statement(
            self, session,
            detail_mixin_instance_override_get_statement,
    ):
        """Test detail mixin override get_statement method."""
        response = detail_mixin_instance_override_get_statement.get_detail(session=session)
        assert response.id == 10

    @pytest.mark.parametrize(
        'create_mixin_instance',
        [SimpleTestOrm],
        indirect=['create_mixin_instance'],
    )
    def test_create_mixin(self, session, create_mixin_instance):
        """Test create mixin."""
        response = create_mixin_instance.create(session=session)
        assert response.id > NUMBER_OF_OBJECTS
        assert type(response).__name__ == 'SimpleTestOrm'

        assert create_mixin_instance.api_view.pk_field is None
        assert create_mixin_instance.api_view.statement is None
        assert create_mixin_instance.async_api is False
        assert create_mixin_instance.api_view.pagination_kwargs is None

        with pytest.raises(AttributeError):
            create_mixin_instance.get_all()
        with pytest.raises(AttributeError):
            create_mixin_instance.get_all_with_pagination()
        with pytest.raises(AttributeError):
            create_mixin_instance.get_detail()
        with pytest.raises(AttributeError):
            create_mixin_instance.delete()
        with pytest.raises(AttributeError):
            create_mixin_instance.update_single()

    @pytest.mark.parametrize(
        'update_mixin_instance',
        [SimpleTestOrm],
        indirect=['update_mixin_instance'],
    )
    def test_update_mixin(self, session, update_mixin_instance):
        """Test update mixin."""
        update_mixin_instance.update_single(session=session, field_value=1, data={'id': 100})

        api = BaseSyncAPI(
            model=SimpleTestOrm,
            pk_field='id'
        )
        with pytest.raises(HTTPException):
            api.get_detail(session=session, field_value=1)
        api.get_detail(session=session, field_value=100)

        assert update_mixin_instance.api_view.pk_field is not None
        assert update_mixin_instance.api_view.statement is None
        assert update_mixin_instance.async_api is False
        assert update_mixin_instance.api_view.pagination_kwargs is None

        with pytest.raises(AttributeError):
            update_mixin_instance.get_all()
        with pytest.raises(AttributeError):
            update_mixin_instance.get_all_with_pagination()
        with pytest.raises(AttributeError):
            update_mixin_instance.get_detail()
        with pytest.raises(AttributeError):
            update_mixin_instance.create()
        with pytest.raises(AttributeError):
            update_mixin_instance.delete()

    @pytest.mark.parametrize(
        'delete_mixin_instance',
        [SimpleTestOrm],
        indirect=['delete_mixin_instance'],
    )
    def test_delete_mixin(self, session, delete_mixin_instance):
        """Test delete mixin."""
        delete_mixin_instance.delete(session=session, field_value=1)

        api = BaseSyncAPI(
            model=SimpleTestOrm,
            pk_field='id'
        )
        with pytest.raises(HTTPException):
            api.get_detail(session=session, field_value=1)

        assert delete_mixin_instance.api_view.pk_field is not None
        assert delete_mixin_instance.api_view.statement is None
        assert delete_mixin_instance.async_api is False
        assert delete_mixin_instance.api_view.pagination_kwargs is None

        with pytest.raises(AttributeError):
            delete_mixin_instance.get_all()
        with pytest.raises(AttributeError):
            delete_mixin_instance.get_all_with_pagination()
        with pytest.raises(AttributeError):
            delete_mixin_instance.get_detail()
        with pytest.raises(AttributeError):
            delete_mixin_instance.create()
        with pytest.raises(AttributeError):
            delete_mixin_instance.update_single()
