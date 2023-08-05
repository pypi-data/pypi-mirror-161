__all__ = ['OvitoObjectTrait', 'ColorTrait']
from typing import Tuple, Type, Any
import traits.api

class OvitoObjectTrait(traits.api.Instance):
    """A trait type whose value is an instance of a class from the OVITO package."""

    def __init__(self, klass: Type[Any], **params) -> None:
        """:param klass: The object class type to instantiate.
:param params: All other keyword parameters are forwarded to the constructor of the object class."""
        ...

class ColorTrait(traits.api.BaseTuple):
    """A trait type whose value is a tuple with three floats that represent the RGB values of a color."""

    def __init__(self, default: Tuple[float, float, float]=(1.0, 1.0, 1.0), **metadata) -> None:
        """:param default: The initial color value to be assigned to the parameter trait."""
        ...