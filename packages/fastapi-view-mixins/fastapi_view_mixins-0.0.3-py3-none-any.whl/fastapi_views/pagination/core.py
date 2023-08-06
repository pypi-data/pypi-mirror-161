import abc
import math
import operator
from dataclasses import field
from functools import cached_property
from typing import (Any, Union, Type, Mapping, TypeVar)
from pydantic.dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.orm import (Session, InstrumentedAttribute)
from sqlalchemy.sql import Select
from fastapi import (HTTPException, status)
from fastapi.datastructures import QueryParams
from fastapi.requests import Request

from fastapi_views.pagination.annotations import (
    LimitOffsetResponse,
    CursorResponse,
    Table,
    PaginationKwargs,
)
from fastapi_views.utils import (
    get_regex_group,
    encode_value,
    decode_value,
    dict_to_query_string,
)
from fastapi_views.settings import BaseConfig

Record = TypeVar('Record')


class PaginationBase(abc.ABC):

    @abc.abstractmethod
    def paginate_object_list(self, session, statement, request, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get_paginated_response(self, object_list):
        raise NotImplementedError


class PaginationCursor(PaginationBase):
    """
    Pagination of Ordered Queries.

    Requires model and ordering to be sent via kwargs when calling paginate_api function, like {
            'model': sqlalchemy Model = modelName,
            'ordering': list[str] = ['-id'],
        }
    Negative '-' means descending order when objects are loaded.
    """

    session: Session
    statement: Select
    request: Request
    paginate_by: int
    limit: int
    kwargs: Mapping[Any, Any]
    cursor: str
    model_ordering: list[Any]
    object_list: list[Record] = None
    reverse: bool = False

    def __init__(self):
        self.lt = 'lt'
        self.gt = 'gt'
        self.next_prefix = 'next__'
        self.previous_prefix = 'previous__'

    @cached_property
    def model(self) -> Type[Table]:
        return self.kwargs.get('model')

    @property
    def first_order_field(self) -> str:
        return self.kwargs['ordering'][0]

    @cached_property
    def decoded_cursor(self) -> str:
        if self.cursor:
            return decode_value(self.cursor)
        raise ValueError(f'Can not decode {self.cursor}')

    def _get_limit(self, query_params: QueryParams) -> int:
        param = 'limit'
        try:
            limit = int(query_params.get(param, self.paginate_by))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Invalid query type, <:{param}> should be type of int.',
            )
        else:
            if limit <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f'Invalid query value, <:{param}> should be higher than 0.',
                )
            return limit

    def _setup_next_page_filter_data(self, field_name: str) -> (str, str):
        op = self.lt if field_name.startswith('-') else self.gt
        return self.next_prefix, op

    def _update_first_ordering_field(self, value: str) -> None:
        self.kwargs['ordering'][0] = value

    def _setup_previous_page_filter_data(self, field_name: str) -> (str, str):
        if field_name.startswith('-'):  # start point desc
            value = get_regex_group('(?<=-).*', field_name)
            op = self.gt
        else:  # start point asc
            value = f'-{field_name}'
            op = self.lt

        self._update_first_ordering_field(value)
        self._create_model_ordering()
        self.reverse = True
        return self.previous_prefix, op

    def _filter_query(self) -> Union[Select, None]:
        decoded_cursor = self.decoded_cursor
        is_next_page = decoded_cursor.startswith(self.next_prefix)
        if is_next_page:
            prefix, op = self._setup_next_page_filter_data(self.first_order_field)
        else:
            prefix, op = self._setup_previous_page_filter_data(self.first_order_field)

        python_operator = getattr(operator, op)
        regex_result = get_regex_group(f'(?<={prefix})(.*)(?=&page__)', decoded_cursor)
        return self.statement.where(
            python_operator(
                getattr(self.model, self.get_first_order_field()),
                regex_result,
            )
        )

    def _get_query_result(self) -> list[Record]:
        statement = self.statement if self.cursor is None else self._filter_query()
        return (self.session.scalars(
            statement.order_by(
                *self.model_ordering,
            ).limit(self.limit + 1))
        ).all()

    @cached_property
    def get_objects(self) -> list[Record]:
        result = self._get_query_result()

        if self.reverse:
            return list(reversed(result))
        return result

    def get_first_order_field(self) -> str:
        is_negative = self.first_order_field.startswith('-')
        if is_negative:
            model_field = get_regex_group('(?<=-).*', self.first_order_field)
        else:
            model_field = self.first_order_field
        return model_field

    @property
    def count(self) -> int:
        # count default
        if self.object_list is not None:
            return len(self.object_list)
        return 0

    @cached_property
    def additional_count(self) -> int:
        # count of limit + 1
        return len(self.get_objects)

    @property
    def has_next(self) -> bool:
        # at least one additional result exists.
        if self.cursor is not None and self.get_current_decoded_page == 0:
            return True
        return self.additional_count > self.limit

    @property
    def has_previous(self) -> bool:
        if self.cursor is None:
            return False
        return self.get_current_decoded_page > 0

    @cached_property
    def get_current_decoded_page(self) -> int:
        return int(get_regex_group('(?<=page__).*', self.decoded_cursor))

    @property
    def _get_next_page(self) -> int:
        if self.cursor is None:
            return 1
        return self.get_current_decoded_page + 1

    @property
    def _get_previous_page(self) -> int:
        if self.cursor is None:
            return 0
        return self.get_current_decoded_page - 1

    def _get_next_url(self) -> Union[str, None]:
        if self.has_next:
            last_object = self.object_list[-1]
            return encode_value(
                f'{self.next_prefix}{getattr(last_object, self.get_first_order_field())}'
                f'&page__{self._get_next_page}')
        return None

    def _get_previous_url(self) -> Union[str, None]:
        if self.has_previous:
            first_object = self.object_list[0]
            return encode_value(
                f'{self.previous_prefix}{getattr(first_object, self.get_first_order_field())}'
                f'&page__{self._get_previous_page}')
        return None

    def _build_uri(self, encoded_value=None) -> Union[str, None]:
        regex_result = get_regex_group('^[^?]*', str(self.request.url))
        if encoded_value is None:
            return
        new_query_params = {**self.request.query_params, 'cursor': encoded_value.decode("utf-8")}

        return f'{regex_result}?{dict_to_query_string(new_query_params)}'

    def _get_first_url(self) -> str:
        regex_result = get_regex_group('^[^?]*', str(self.request.url))
        q = {**self.request.query_params, 'limit': self.limit}
        q.pop('cursor', None)
        return f'{regex_result}?{dict_to_query_string(q)}'

    def _get_ordering_model_field(self, f_name: str) -> InstrumentedAttribute:
        model = self.kwargs['model']
        if self.is_ordering_model_field_negative(f_name):
            regex_result = get_regex_group('(?<=-).*', f_name)
            return getattr(model, regex_result)

        return getattr(model, f_name)

    @staticmethod
    def is_ordering_model_field_negative(f_name) -> bool:
        return f_name.startswith('-')

    def validate_first_ordering_field(self) -> None:
        ordering = self.kwargs.get('ordering')
        first_order = ordering[0]
        first_model_field = self._get_ordering_model_field(
            first_order
        )
        if str(first_model_field.type) in ('BOOLEAN',):
            raise TypeError(f'{first_model_field.type} should can not be used as comparison')

    def _create_model_ordering(self) -> None:
        self.validate_first_ordering_field()
        result = list()

        for f_name in self.kwargs.get('ordering'):
            model_field = self._get_ordering_model_field(f_name)

            if self.is_ordering_model_field_negative(f_name):
                model_field = model_field.desc()
            result.append(model_field)
        self.model_ordering = result

    def paginate_object_list(
            self,
            session,
            statement,
            request,
            **kwargs: PaginationKwargs,
    ) -> list[Record]:
        self.session = session
        self.statement = statement
        self.request = request
        self.paginate_by = request.state.paginate_by

        query_params = self.request.query_params

        self.limit = self._get_limit(query_params)
        self.kwargs = kwargs
        if 'cursor_prefixes' in self.kwargs:
            self.next_prefix, self.previous_prefix = self.kwargs['cursor_prefixes']
        self.cursor = query_params.get('cursor')
        self._create_model_ordering()

        if self.additional_count <= self.limit:
            self.object_list = self.get_objects
        else:
            if not self.reverse:
                self.object_list = self.get_objects[:self.additional_count - 1]
            else:
                self.object_list = self.get_objects[1:]
        return self.object_list

    def get_paginated_response(self, object_list) -> CursorResponse:
        return {
            'results': object_list,
            'count': self.count,
            'page_limit': self.limit,
            'first_page': self._get_first_url(),
            'next_page': self._build_uri(self._get_next_url()),
            'previous_page': self._build_uri(self._get_previous_url()),
        }


class PaginationLimitOffset(PaginationBase):
    """
    Returns list of objects based on request's query parameters [ limit and page ].

    Big page number slows getting query result due to how OFFSET works in sql.
    The rows skipped by an OFFSET clause still have to be computed inside the server,
    therefore a large OFFSET might be inefficient.
    """

    page: int
    limit: int
    session: Session
    statement: Select
    request: Request
    paginate_by: int

    def query_type_exception(self, param: str, expected_type: str) -> Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Invalid query type, <:{param}> should be type of {expected_type}.',
        )

    def query_int_value_exception(self, param: str, condition: str) -> Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Invalid query value, <:{param}> should be {condition}.',
        )

    def _get_page(self, query_params: QueryParams) -> int:
        param = 'page'
        try:
            page = int(query_params.get(param, 0))
        except ValueError:
            self.query_type_exception(param, 'int')
        else:
            if page < 0:
                self.query_int_value_exception(param, 'higher or equal 0')
            return page

    def _get_limit(self, query_params: QueryParams) -> int:
        param = 'limit'
        try:
            limit = int(query_params.get('limit', self.paginate_by))
        except ValueError:
            self.query_type_exception(param, 'int')
        else:
            if limit <= 0:
                self.query_int_value_exception(param, 'higher than 0')
            return limit

    def _get_objects(self) -> list[Record]:
        return (self.session.execute(
            self.statement.limit(self.limit).offset(self.limit * self.page),
        )).all()

    @cached_property
    def count(self) -> int:
        statement = select(func.count()).select_from(self.statement.subquery())
        return self.session.scalar(statement)

    @cached_property
    def total_pages(self) -> int:
        if self.count == 0:
            return 0
        return math.ceil(self.count / self.limit) - 1

    @property
    def _get_next_url(self) -> Union[str, None]:
        if not self.page < self.total_pages:
            return None
        return self._build_uri(self.page + 1)

    @property
    def _get_previous_url(self) -> Union[str, None]:
        if not self.page > 0:
            return None
        return self._build_uri(self.page - 1)

    @property
    def _get_last_url(self) -> str:
        return self._build_uri(self.total_pages)

    def _build_uri(self, new_page: int) -> str:
        # catch all until first "?" occurrence
        regex_result = get_regex_group('^[^?]*', str(self.request.url))
        new_query_params = {**self.request.query_params, 'limit': self.limit, 'page': new_page}

        return f'{regex_result}?{dict_to_query_string(new_query_params)}'

    def paginate_object_list(
            self,
            session: Session,
            statement: Select,
            request: Request,
            **kwargs,
    ) -> list[Record]:
        self.session = session
        self.statement = statement
        self.request = request
        self.paginate_by = request.state.paginate_by

        self.page = self._get_page(request.query_params)
        self.limit = self._get_limit(request.query_params)

        return self._get_objects()

    def get_paginated_response(self, object_list: list[Record]) -> LimitOffsetResponse:
        return {
            'results': object_list,
            'count': len(object_list),
            'total': self.count,
            'total_pages': self.total_pages,
            'page_limit': self.limit,
            'next_page': self._get_next_url,
            'previous_page': self._get_previous_url,
            'last_page': self._get_last_url,
        }


@dataclass(config=BaseConfig)
class PaginatorAPI:
    """
    Paginator API.

    Arguments:
        ** statement **: sqlalchemy selectable select.
        ** request **: fastapi / starlette Request object.
        ** session **: sqlalchemy orm sync session.
        ** strategy **: pagination strategy. If not set then PaginationLimitOffset is used.
        ** paginate_by **: number of objects per page.
        ** kwargs **: additional params passed to paginate_object_list method of
                      pagination strategy, ex. kwargs = { 'key': value, 'key2': value2 }.
    """
    statement: Select
    request: Request
    session: Session
    strategy: Type[PaginationBase] = None
    paginate_by: int = 100
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.strategy is None:
            self.strategy = PaginationLimitOffset
        self.strategy_instance: PaginationBase = self.strategy()

        if self.kwargs is None or not self.kwargs or not isinstance(self.kwargs, dict):
            self.kwargs = {
                'model': None,
                'ordering': None,
                'cursor_prefixes': None
            }

        self.request.state.paginate_by = self.paginate_by

    @property
    def _strategy_data(self) -> list[Any]:
        """Returns only list of current page objects data."""
        return self.strategy_instance.paginate_object_list(
            self.session,
            self.statement,
            self.request,
            **self.kwargs,
        )

    def strategy_response(self) -> dict[str, Any]:
        """Create and return response."""
        return self.strategy_instance.get_paginated_response(self._strategy_data)


def paginate_api(
        statement: Select,
        request: Request,
        session: Session,
        paginate_by: int = 100,
        strategy: Type[PaginationBase] = None,
        kwargs: Union[dict[str, Any], None] = None,
):
    paginator = PaginatorAPI(
        statement=statement,
        request=request,
        session=session,
        strategy=strategy,
        paginate_by=paginate_by,
        kwargs=kwargs,
    )
    return paginator.strategy_response()
