from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.session import get_db
from database.models import Property
from routers.request_models.property_models import PropertyCreate, PropertyUpdate, PropertyOut
from decorator.jwt_decorator import jwt_authorization

router = APIRouter()


@router.post("/properties", response_model=PropertyOut)
def create_property(
    property_in: PropertyCreate,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if not token_data.get("is_admin") and not token_data.get("is_staff"):
        raise HTTPException(status_code=403, detail="Only property owners or admins can create properties")

    new_property = Property(owner_id=token_data["user_id"], **property_in.dict())
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


@router.get("/properties/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.put("/properties/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int,
    updates: PropertyUpdate,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if token_data["user_id"] != prop.owner_id and not token_data.get("is_admin", 0):
        raise HTTPException(status_code=403, detail="You are not allowed to update this property")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(prop, key, value)

    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/properties/{property_id}")
def delete_property(
    property_id: int,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if token_data["user_id"] != prop.owner_id and not token_data.get("is_admin", 0):
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")

    db.delete(prop)
    db.commit()
    return {"msg": "Property deleted successfully"}


@router.get("/properties", response_model=List[PropertyOut])
def list_properties(
    city: Optional[str] = None,
    country: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_available: Optional[int] = 1,
    db: Session = Depends(get_db)
):
    query = db.query(Property)

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(Property.country.ilike(f"%{country}%"))
    if min_price:
        query = query.filter(Property.price_per_night >= min_price)
    if max_price:
        query = query.filter(Property.price_per_night <= max_price)
    if is_available is not None:
        query = query.filter(Property.is_available == is_available)

    return query.all()


