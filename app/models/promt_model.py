from pydantic import Field, BaseModel

class Promt(BaseModel):
  prompt: str = Field(
    min_length = 100,
    max_length = 1000
  )