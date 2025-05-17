from pydantic import BaseModel
from typing import List


class AmenityBase(BaseModel):
    name: str


class AmenityOut(AmenityBase):
    amenity_id: int

    class Config:
        orm_mode = True
