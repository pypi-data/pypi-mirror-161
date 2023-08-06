from typing import Any, TypeVar, Generic, Union

from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from fastapi import status
from fastapi.responses import Response

from pydantic.dataclasses import dataclass

from fastapi_views.views.base import BaseAPI
from fastapi_views.settings import BaseConfig

Table = TypeVar("Table")
Record = TypeVar('Record')


@dataclass(config=BaseConfig)
class BaseAsyncAPI(BaseAPI, Generic[Table]):
    """Async API with default methods to get, create, update, delete objects."""

    @staticmethod
    async def _count(session: AsyncSession, statement: Select) -> int:
        count_statement = select(func.count()).select_from(statement.subquery())
        return await session.scalar(count_statement)

    async def get_all(self, session: Union[Session, AsyncSession]) -> list[Record]:
        self._validate_async_session(session)
        self._validate_statement()
        return (await session.execute(self.statement)).all()

    async def get_detail(self, session: AsyncSession, field_value: Any = None) -> Table:
        self._validate_async_session(session)

        if self.statement is not None:
            statement = self.statement
        else:
            self._validate_field_value(field_value)
            statement = select(self.model).where(getattr(self.model, self.pk_field) == field_value)

        if await self._count(session, statement) > 1:
            raise ValueError('Multiple objects returned')
        result = await session.scalar(statement)

        if result is None:
            self.not_found_exception(field_value)
        return result

    async def create(self, session: AsyncSession, data: dict[str, Any] = None) -> Table:
        self._validate_async_session(session)
        if data is None:
            data = {}
        entry = self.model(**data)
        try:
            session.add(entry)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            self.integrity_error(str(e.orig))

        await session.refresh(entry)
        return entry

    async def delete(self, session: AsyncSession, field_value: Any) -> Response:
        if self.pk_field is None:
            self._attribute_error('pk_field')
        self._validate_async_session(session)
        self._validate_field_value(field_value)

        statement = delete(self.model).where(getattr(self.model, self.pk_field) == field_value)
        await session.execute(statement)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def update_single(
            self,
            session: AsyncSession,
            field_value: Any,
            data: dict[str, Any] = None,
            synchronize_session='fetch',
    ) -> None:
        self._validate_async_session(session)
        self._validate_field_value(field_value)
        if self.pk_field is None:
            self._attribute_error('pk_field')
        if data is None or not data:
            self.empty_update_error()

        statement = update(self.model) \
            .where(getattr(self.model, self.pk_field) == field_value) \
            .values(**data) \
            .execution_options(synchronize_session=synchronize_session)
        try:
            await session.execute(statement)
        except IntegrityError as e:
            await session.rollback()
            self.integrity_error(str(e.orig))
        else:
            await session.commit()
