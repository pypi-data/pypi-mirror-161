from typing import Callable, Union

from pydantic import Field
from typing_extensions import Literal, Annotated

from algora.common.base import Base


def serializable(
        _cls: Base = None
) -> Union[Callable, Base]:
    """
    A decorator that sets the descriptor field for a serializable class

    NOTE: This is used for class contained in Annotations (look at the create_annotation method)

    Args:
        _cls (object): The class being decorated

    Returns:
        cls: The updated class with the descriptor field
    """

    def wrap(cls):
        annotations = {"descriptor": Literal[cls.cls_name()]}
        return type(cls.cls_name(), (cls,), {'__annotations__': annotations, 'descriptor': Field(cls.cls_name())})

    if _cls is None:
        return wrap

    return wrap(_cls)


def create_annotation(*types):
    """
    Creates an annotation used in type hinting that contains classes that are decorated with @serializable

    Args:
        *types: A tuple of all the serializable class types

    Returns:
        A annotation class used in type hinting
    """

    class Annotation:
        types = ()

        @classmethod
        def annotation(cls):
            return Annotated[Union[cls.types], Field(discriminator='descriptor')]

        @classmethod
        def add_types(cls, *new_types):
            updated_types = cls.types + new_types
            cls.types = updated_types

    annotation = Annotation()
    annotation.add_types(*types)
    return Annotation
