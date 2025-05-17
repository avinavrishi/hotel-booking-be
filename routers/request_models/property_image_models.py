from pydantic import BaseModel
from typing import Optional


class PropertyImageCreate(BaseModel):
    image_url: str
    is_cover: Optional[int] = 0


class PropertyImageUpdate(BaseModel):
    image_url: Optional[str]
    is_cover: Optional[int]


class PropertyImageOut(BaseModel):
    image_id: int
    property_id: int
    image_url: str
    is_cover: int

    class Config:
        orm_mode = True
