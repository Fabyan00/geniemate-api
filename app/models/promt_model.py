"""Module for setting promt model"""

from pydantic import Field, BaseModel


class Promt(BaseModel):
    """Set promt model config"""

    prompt: str = Field(max_length=1000)
