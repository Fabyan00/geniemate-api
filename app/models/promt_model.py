from pydantic import Field, BaseModel

class Promt(BaseModel):
  text: str = Field(
    min_length = 10,
    max_length = 100
  )