from pydantic import Field, BaseModel

class Promt(BaseModel):
  text: str = Field(
    min_length = 100,
    max_length = 1000
  )