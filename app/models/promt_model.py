"""Module for setting promt model"""

from pydantic import Field, BaseModel


class Promt(BaseModel):
    """Set promt model config"""

    prompt: str = Field(min_length=100, max_length=1000)
