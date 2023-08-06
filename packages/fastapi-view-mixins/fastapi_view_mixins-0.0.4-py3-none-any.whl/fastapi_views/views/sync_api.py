from typing import Any, TypeVar, Generic

from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import status
from fastapi.responses import Response

from pydantic.dataclasses import dataclass

from fastapi_views.views.base import BaseAPI
from fastapi_views.settings import BaseConfig
from sqlalchemy.sql import Select

Table = TypeVar("Table")
Record = TypeVar('Record')


@dataclass(config=BaseConfig)
class BaseSyncAPI(BaseAPI, Generic[Table]):
    """Sync API with default methods to get, create, update, delete objects."""

    @staticmethod
    def _count(session: Session, statement: Select) -> int:
        count_statement = select(func.count()).select_from(statement.subquery())
        return session.scalar(count_statement)

    def get_all(self, session: Session) -> list[Record]:
        self._validate_session(session)
        self._validate_statement()
        return session.execute(self.statement).all()

    def get_detail(self, session: Session, field_value: Any = None) -> Table:
        self._validate_session(session)

        if self.statement is not None:
            statement = self.statement
        else:
            self._validate_field_value(field_value)
            statement = select(self.model).where(getattr(self.model, self.pk_field) == field_value)

        if self._count(session, statement) > 1:
            raise ValueError('Multiple objects returned')
        result = session.scalar(statement)

        if result is None:
            self.not_found_exception(field_value)
        return result

    def create(self, session: Session, data: dict[str, Any] = None) -> Table:
        self._validate_session(session)
        if data is None:
            data = {}
        entry = self.model(**data)
        try:
            session.add(entry)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            self.integrity_error(str(e.orig))

        session.refresh(entry)
        return entry

    def delete(self, session: Session, field_value: Any) -> Response:
        if self.pk_field is None:
            self._attribute_error('pk_field')
        self._validate_session(session)
        self._validate_field_value(field_value)

        statement = delete(self.model).where(getattr(self.model, self.pk_field) == field_value)
        session.execute(statement)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def update_single(
            self,
            session: Session,
            field_value: Any,
            data: dict[str, Any] = None,
            synchronize_session='fetch',
    ) -> None:
        self._validate_session(session)
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
            session.execute(statement)
        except IntegrityError as e:
            session.rollback()
            self.integrity_error(str(e.orig))
        else:
            session.commit()
