from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PropertyType(str, Enum):
    apartment = "apartment"
    villa = "villa"
    house = "house"
    condo = "condo"


class PropertyBase(BaseModel):
    title: str
    description: Optional[str]
    price_per_night: float
    address: str
    city: str
    country: str
    latitude: Optional[float]
    longitude: Optional[float]
    max_guests: int
    property_type: PropertyType
    is_available: Optional[int] = 1


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price_per_night: Optional[float]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    max_guests: Optional[int]
    property_type: Optional[PropertyType]
    is_available: Optional[int]


class PropertyOut(PropertyBase):
    property_id: int
    owner_id: int

    class Config:
        orm_mode = True