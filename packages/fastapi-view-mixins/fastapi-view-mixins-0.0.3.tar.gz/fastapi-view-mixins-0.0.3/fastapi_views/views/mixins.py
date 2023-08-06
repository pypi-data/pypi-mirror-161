from typing import Type, Any, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.sql import Select

from fastapi_views.pagination.core import PaginationBase
from .async_api import Table, BaseAsyncAPI
from .base import BaseAPI
from .sync_api import BaseSyncAPI

API_CLS = TypeVar('API_CLS', bound=BaseAPI)


class BaseAPIMixin:
    """Base API mixin."""

    model: Type[Table] = None
    """A SQLAlchemy model class."""
    pk_field: Union[str, None] = None
    """Unique field like model id."""
    paginate_by: Union[int, None] = None
    """Page objects limit."""
    pagination_strategy: Union[Type[PaginationBase], None] = None
    """PaginationCursor / PaginationLimitOffset, default set to limit offset."""
    async_api: bool = False
    """When set to True then will be used async repository."""

    @property
    def _get_api_cls(self) -> Type[API_CLS]:
        """Get repository API cls."""
        return BaseSyncAPI[self.model] if not self.async_api else BaseAsyncAPI[self.model]

    def __init__(self, *args, **kwargs) -> None:
        attrs = kwargs.pop('attrs', {})
        self.args = args
        self.kwargs = kwargs

        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f'{key} is not a valid attribute')

        if not isinstance(self.async_api, bool):
            raise TypeError(f'{self.async_api} expected to be boolean value.')

        self.api_view = self._get_api_cls(
            model=self.model,
            pk_field=self.pk_field,
            paginate_by=self.paginate_by,
            pagination_strategy=self.pagination_strategy,
        )

        # assigned after, so we can reference to api_view in both of the methods if needed
        self.api_view.pagination_kwargs = self.get_pagination_kwargs()
        self.api_view.statement = self.get_statement()

    def get_statement(self) -> Select:
        """Return sqlalchemy orm statement."""

    def get_pagination_kwargs(self) -> dict[str, Any]:
        """Return pagination kwargs"""


class BaseAPIListMixin(BaseAPIMixin):
    """Retrieve object list mixin."""

    pk_field = None

    def get_all(self, *args, **kwargs):
        return self.api_view.get_all(*args, **kwargs)

    def get_all_with_pagination(self, *args, **kwargs):
        return self.api_view.get_all_with_pagination(*args, **kwargs)

    def get_statement(self) -> Select:
        return select(self.model)

    def get_pagination_kwargs(self) -> dict[str, Any]:
        return {
            'model': self.model,
            'ordering': ['id'],
            'cursor_prefixes': ['next__', 'prev__']
        }


class BaseAPIDetailMixin(BaseAPIMixin):
    """Retrieve object mixin."""

    pk_field = 'id'

    def get_detail(self, *args, **kwargs):
        return self.api_view.get_detail(*args, **kwargs)


class BaseAPIUpdateMixin(BaseAPIMixin):
    """Update objects mixin."""

    pk_field = 'id'

    def update_single(self, *args, **kwargs):
        return self.api_view.update_single(*args, **kwargs)


class BaseAPICreateMixin(BaseAPIMixin):
    """Post objects mixin."""
    pk_field = None

    def create(self, *args, **kwargs):
        return self.api_view.create(*args, **kwargs)


class BaseAPIDestroyMixin(BaseAPIMixin):
    """Delete objects mixin."""

    pk_field = 'id'

    def delete(self, *args, **kwargs):
        return self.api_view.delete(*args, **kwargs)
