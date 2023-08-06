import abc
from typing import Any, TypeVar, Type, Generic, Union

from fastapi import HTTPException
from pydantic import validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (selectinload, Session)
from sqlalchemy.sql import Select
from fastapi import status
from fastapi.requests import Request

from pydantic.dataclasses import dataclass

from fastapi_views.settings import BaseConfig
from fastapi_views.pagination.core import (paginate_api, PaginationBase)

Table = TypeVar("Table")
Record = TypeVar('Record')


@dataclass(config=BaseConfig)
class BaseAPI(Generic[Table], abc.ABC):
    """Base repository API class."""

    model: Type[Table] = None
    pk_field: str = None
    related_fk_fields: list[str] = None
    paginate_by: int = None
    pagination_strategy: Type[PaginationBase] = None
    pagination_kwargs: Union[dict[str, Any], None] = None
    statement: Select = None

    @validator('model')
    def model_can_not_be_empty(cls, value: Table):
        """Model field validator."""
        if not value or value is None:
            raise ValueError('Model field is required.')
        return value

    def _attribute_error(self, field_name: str) -> None:
        raise AttributeError(f'{field_name} can not be none')

    def _statement_type_error(self) -> None:
        raise TypeError('Statement must be type of sqlalchemy.sql Select')

    def _session_type_error(self) -> None:
        raise TypeError('Session must be type of sqlalchemy.orm Session')

    def _async_session_type_error(self) -> None:
        raise TypeError('Session must be type of sqlalchemy.ext.asyncio AsyncSession')

    def _request_type_error(self) -> None:
        raise TypeError('Request must be type of fastapi.requests Request')

    def _validate_session(self, session: Session) -> None:
        if session is None:
            self._attribute_error('session')
        if not isinstance(session, Session):
            self._session_type_error()

    def _validate_async_session(self, session: AsyncSession) -> None:
        if session is None:
            self._attribute_error('session')
        if not isinstance(session, AsyncSession):
            self._async_session_type_error()

    def _validate_request(self, request) -> None:
        if request is None:
            self._attribute_error('request')
        if not isinstance(request, Request):
            self._request_type_error()

    def _validate_statement(self) -> None:
        if self.statement is None:
            self._attribute_error('statement')
        if not isinstance(self.statement, Select):
            self._statement_type_error()

    def _validate_field_value(self, unique: Any) -> None:
        if unique is None:
            self._attribute_error('pk')

    def not_found_exception(self, unique: Any):
        """Object not found exception."""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{self.model.__name__} with <{type(unique)}:{unique}> does not exist.'
        )

    @staticmethod
    def integrity_error(error):
        """Integrity exception."""
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error,
        )

    @staticmethod
    def empty_update_error():
        """Integrity exception."""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Nothing to update.',
        )

    def get_all_with_pagination(self, request: Request, session: Session):
        """
        Returns multiple objects using pagination.
        ** Sync session **  is required.
        """
        self._validate_session(session)
        self._validate_request(request)
        if self.paginate_by is None:
            self._attribute_error('paginate_by')
        if not isinstance(self.paginate_by, int) or isinstance(self.paginate_by, bool):
            raise TypeError('paginate_by must be type of int')
        if self.paginate_by <= 0:
            raise ValueError('paginate_by value should be higher than 0')

        paginate_response = paginate_api(
            statement=self.statement,
            request=request,
            session=session,
            paginate_by=self.paginate_by,
            strategy=self.pagination_strategy,
            kwargs=self.pagination_kwargs,
        )
        return paginate_response

    @abc.abstractmethod
    def get_all(self, session: Union[Session, AsyncSession]) -> list[Record]:
        """Returns multiple objects."""

    @abc.abstractmethod
    def get_detail(self, db: Union[Session, AsyncSession], pk: int):
        """Return single object."""

    @abc.abstractmethod
    def create(self, db: Union[Session, AsyncSession], data: dict[str, Any]):
        """Perform object creation."""

    @abc.abstractmethod
    def delete(self, db: Union[Session, AsyncSession], pk: int):
        """Remove object."""

    @abc.abstractmethod
    def update_single(
            self,
            db: Union[Session, AsyncSession],
            pk: int,
            data: dict[str, Any],
            synchronize_session='fetch',
    ):
        """
        Perform single object update.

        synchronize_session: check sqlalchemy doc for details.
        """
