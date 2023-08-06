import abc
import random
import string
from typing import TypeVar, Type, Dict

from pydantic import create_model, BaseModel

from fastapi_views.pagination.annotations import (LimitOffsetPageParams, CursorPageParams)

P = TypeVar('P', bound=BaseModel)
S = TypeVar('S', bound=BaseModel)
AnyClassMethod = TypeVar('AnyClassMethod')


class AbstractPage(abc.ABC):
    result_key: str = 'results'

    @property
    @abc.abstractmethod
    def params_cls(self) -> Type[S]:
        """Page params. Expect to return pydantic model cls."""

    def create_page(self, pydantic_model: Type[S]) -> Type[P]:
        """Creates pydantic model Page that is going to be used as response_model in router."""
        field_definitions = self._get_result_field(pydantic_model)
        unique_value = ''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(12)
        )
        return create_model(
            f'Page_{unique_value}',
            __validators__=self.set_new_model_validators(),
            __base__=self.params_cls,
            **field_definitions,
        )

    @classmethod
    def include(cls, pydantic_model: Type[S]) -> Type[P]:
        """
        Takes as input pydantic model that will be used as type for result list.
        Returns new pydantic Page object.
        """
        return cls().create_page(pydantic_model)

    def _get_result_field(self, pydantic_model: Type[S]) -> dict[str, tuple[list[Type[S]], None]]:
        """Responsible for setting type of 'list of results' for page."""
        return {
            self.result_key: (list[pydantic_model], None),
        }

    def set_new_model_validators(self, *args, **kwargs) -> Dict[str, AnyClassMethod]:
        """
        Override if there is a need to put some validators to new Page.

        Usage example:

            from pydantic import validator

            def username_alphanumeric(cls, v):
                assert v.isalnum(), 'must be alphanumeric'
                return v

            validators = {
                'username_validator': validator('username')(username_alphanumeric),
                ...
            }
        """


class LimitOffsetPage(AbstractPage):

    @property
    def params_cls(self):
        return LimitOffsetPageParams


class CursorPage(AbstractPage):

    @property
    def params_cls(self):
        return CursorPageParams
