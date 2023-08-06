"""Pydantic base with Frantic capabilities
"""

from typing import ClassVar, Optional

from pydantic import BaseModel as _BaseModel  # pylint: disable=no-name-in-module


# pylint: disable=too-few-public-methods
class BaseModel(_BaseModel):
    """Frantic base model"""

    collection: ClassVar[Optional[str]] = None
    id: Optional[str] = None
