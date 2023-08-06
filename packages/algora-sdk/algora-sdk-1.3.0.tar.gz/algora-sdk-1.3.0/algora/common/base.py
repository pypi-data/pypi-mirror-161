"""
Base implementation classes for passing on inherited attributes.
"""
from abc import ABC
from datetime import date
from enum import Enum

from pydantic import BaseModel, create_model

from algora.common.function import date_to_timestamp


class BaseEnum(str, Enum):
    """
    Base class for all enum classes.

    Note: Inheriting from str is necessary to correctly serialize output of enum
    """
    pass


class Base(ABC, BaseModel):
    class Config:
        # use enum values when using .dict() on object
        use_enum_values = True
        json_encoders = {
            date: date_to_timestamp
        }

    @classmethod
    def cls_name(cls) -> str:
        return cls.__name__

    @classmethod
    def new_fields(cls, *args, **kwargs):
        """

        Args:
            *args:
            **kwargs:

        Returns:

        """
        return {}

    @classmethod
    def update(cls, *args, **kwargs):
        """

        Args:
            *args:
            **kwargs:

        Returns:

        """
        new_fields = cls.new_fields(*args, **kwargs)
        return create_model(cls.__name__, __base__=cls, **new_fields)
